"""Gemini service — the single place that talks to the LLM.

Uses the Google GenAI SDK Interactions API:

    from google import genai
    client = genai.Client(api_key=settings.gemini_api_key)
    interaction = client.interactions.create(model=..., input=prompt)
    interaction.output_text

Each use case has its own prompt + Pydantic schema. The model is asked to
return JSON; ``output_text`` is parsed and validated with Pydantic before it
touches assessment state. Provider details are never leaked.

There is NO deterministic fallback in production: if GEMINI_API_KEY is not set,
assessment calls raise a clear application error. Unit tests inject a fake
``generate`` callable so the engine can be exercised without a key or network.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from ..core.config import Settings
from ..core.config import settings as global_settings
from ..core.errors import GeminiError
from . import prompts
from .ai_contracts import (
    GeneratedQuestion,
    ResponseEvaluation,
    ResultSynthesis,
    ResumeExtraction,
)

logger = logging.getLogger("aura.gemini")

T = TypeVar("T", bound=BaseModel)

_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 0.8

# A generate function takes a prompt instruction and returns the model's text
# (expected to be JSON matching the requested schema). Injected only by tests.
GenerateFn = Callable[[str], str]


class GeminiService:
    """Wraps the Google GenAI Interactions client with typed, validated outputs."""

    def __init__(
        self, settings: Settings | None = None, generate: GenerateFn | None = None
    ) -> None:
        self._settings = settings or global_settings
        self.model = self._settings.gemini_model
        self._client: Any | None = None
        # Injected only by tests; production leaves this None and uses the real
        # google-genai Interactions client.
        self._generate_fn: GenerateFn | None = generate

    @property
    def configured(self) -> bool:
        return self._generate_fn is not None or self._settings.gemini_configured

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from google import genai  # type: ignore[import-not-found]
            except Exception as exc:
                raise GeminiError("The Gemini SDK is not installed.") from exc
            self._client = genai.Client(api_key=self._settings.gemini_api_key)
        return self._client

    def _sync_generate(self, instruction: str) -> str:
        """Call the real Gemini Interactions API and return output_text."""
        client = self._get_client()
        interaction = client.interactions.create(
            model=self.model,
            input=instruction,
        )
        return getattr(interaction, "output_text", "") or ""

    async def _call(self, instruction: str, schema_model: type[T]) -> T:
        """Call Gemini (or the injected test fake), parse JSON, validate."""
        if not self.configured:
            raise GeminiError(
                "Gemini is not configured. Set GEMINI_API_KEY in your .env to run assessments."
            )

        last_exc: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                if self._generate_fn is not None:
                    raw = self._generate_fn(instruction)
                else:
                    raw = await asyncio.to_thread(self._sync_generate, instruction)
                data = _parse_json(raw)
                return schema_model.model_validate(data)
            except ValidationError as exc:
                logger.warning("Gemini output failed validation (attempt %d): %s", attempt, exc)
                last_exc = exc
            except GeminiError:
                raise
            except Exception as exc:  # noqa: BLE001 - provider surface is broad
                last_exc = exc
                logger.warning("Gemini call failed (attempt %d): %s", attempt, exc)
            if attempt < _MAX_RETRIES:
                await asyncio.sleep(_RETRY_BASE_DELAY * attempt)

        raise GeminiError(
            "The assessment service is temporarily unavailable. Please try again."
            + (f" (last error: {last_exc})" if last_exc else "")
        )

    # --- Public use-case API ---
    async def parse_resume(self, resume_text: str) -> ResumeExtraction:
        return await self._call(prompts.resume_prompt(resume_text), ResumeExtraction)

    async def generate_question(
        self,
        candidate_context: dict[str, Any],
        evidence_summary: dict[str, Any],
        prior_questions: list[dict[str, Any]],
        dimensions: list[str],
    ) -> GeneratedQuestion:
        instruction = prompts.question_prompt(
            candidate_context, evidence_summary, prior_questions, dimensions
        )
        return await self._call(instruction, GeneratedQuestion)

    async def evaluate_response(
        self,
        question_prompt_text: str,
        dimension: str,
        criteria: list[str],
        candidate_context: dict[str, Any],
        response_text: str,
    ) -> ResponseEvaluation:
        instruction = prompts.evaluation_prompt(
            question_prompt_text, dimension, criteria, candidate_context, response_text
        )
        return await self._call(instruction, ResponseEvaluation)

    async def synthesize_result(
        self,
        overall_score: int,
        classification: str,
        pathway: str,
        dimension_results: list[dict[str, Any]],
        key_strengths: list[str],
        capability_gaps: list[str],
    ) -> ResultSynthesis:
        instruction = prompts.synthesis_prompt(
            overall_score,
            classification,
            pathway,
            dimension_results,
            key_strengths,
            capability_gaps,
        )
        return await self._call(instruction, ResultSynthesis)


def _parse_json(text: str) -> Any:
    text = (text or "").strip()
    if not text:
        raise GeminiError("Empty response from assessment service.")
    # The Interactions API returns free text; we instruct JSON and tolerate
    # markdown code fences if the model wraps the output.
    fenced = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise GeminiError("The assessment service returned an unreadable response.") from exc


# Shared production instance. Tests inject a fake via ``gemini_service._generate_fn``.
gemini_service = GeminiService()
