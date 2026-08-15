"""A fake Gemini used ONLY in unit tests.

Production uses the real Gemini Interactions API (no deterministic fallback).
Tests inject this fake via ``gemini_service._generate_fn`` so the engine can
be exercised without a key or network. It returns JSON strings matching the
Pydantic AI contracts, simulating an LLM that produces structured output.
"""

from __future__ import annotations

import json
import re
from collections import deque

DIMENSIONS = [
    "Engineering Fundamentals",
    "Problem Solving",
    "AI Fluency",
    "Agentic Engineering",
    "Practical Reasoning",
    "Communication",
]

_TECH_KEYWORDS = {
    "test",
    "tests",
    "testing",
    "verify",
    "verification",
    "validation",
    "schema",
    "parameterized",
    "injection",
    "async",
    "await",
    "retry",
    "idempotent",
    "transaction",
    "rollback",
    "ci",
    "deploy",
    "log",
    "metrics",
    "agent",
    "prompt",
    "model",
    "fine-tune",
    "eval",
    "guardrail",
    "checkpoint",
}


class FakeGemini:
    """Callable fake. ``generate(instruction)`` returns raw JSON text."""

    def __init__(self) -> None:
        self._dim_queue: deque[str] = deque(DIMENSIONS)

    def __call__(self, instruction: str) -> str:
        if "Extract structured candidate facts" in instruction:
            return self._resume(instruction)
        if "Generate ONE high-information assessment question" in instruction:
            return self._question(instruction)
        if "Evaluate the candidate's response" in instruction:
            return self._evaluation(instruction)
        if "Write the narrative for the candidate's readiness report" in instruction:
            return self._synthesis(instruction)
        return "{}"

    def _resume(self, instruction: str) -> str:
        github = _find_url(instruction, "github.com")
        linkedin = _find_url(instruction, "linkedin.com")
        background = " ".join(instruction.split()[:50])
        return json.dumps(
            {
                "name": None,
                "education": None,
                "graduation_year": None,
                "experience": None,
                "target_role": None,
                "technical_skills": [],
                "projects": [],
                "ai_tools": [],
                "github": github,
                "linkedin": linkedin,
                "professional_links": [],
                "background": background or None,
            }
        )

    def _question(self, instruction: str) -> str:
        # Rotate through dimensions so coverage spans multiple areas.
        target = self._dim_queue.popleft()
        self._dim_queue.append(target)
        return json.dumps(
            {
                "dimension": target,
                "format": "written",
                "prompt": f"Explain your practical approach to a {target} challenge you have faced.",
                "context": None,
                "options": [],
                "assessment_objective": f"Probe applied {target}.",
                "evaluation_criteria": [
                    "Specifics over generalities",
                    "Reasoning about trade-offs",
                    "Awareness of failure modes",
                ],
                "more_evidence_needed_hint": True,
            }
        )

    def _evaluation(self, instruction: str) -> str:
        response = _extract_response(instruction)
        words = len(response.split())
        length_signal = min(1.0, words / 60.0)
        keyword_signal = _keyword_signal(response)
        score = max(20, min(92, round(35 + 40 * max(length_signal, keyword_signal))))
        confidence = round(min(0.9, 0.45 + 0.4 * min(1.0, words / 80.0)), 2)
        strengths: list[str] = []
        gaps: list[str] = []
        evidence: list[dict[str, str]] = []
        if words >= 20:
            evidence.append({"statement": response[:140], "supports": "demonstrated reasoning"})
            strengths.append("Engaged directly with the question.")
        if keyword_signal > 0.5:
            strengths.append("Used relevant technical framing.")
            score = min(92, score + 6)
        else:
            gaps.append("Could be more concrete about the mechanism.")
        if words < 25:
            gaps.append("Brief; limited evidence of depth.")
            score = max(20, score - 10)
        return json.dumps(
            {
                "evidence": evidence,
                "strengths": strengths or ["Attempted the question."],
                "gaps": gaps,
                "dimension_score": score,
                "confidence": confidence,
                "rationale": f"Fake evaluation of a {words}-word answer.",
                "more_evidence_needed": confidence < 0.75,
            }
        )

    def _synthesis(self, instruction: str) -> str:
        names = [d for d in DIMENSIONS if d in instruction]
        return json.dumps(
            {
                "overall_summary": "You show a developing profile with both strengths and clear growth areas.",
                "dimension_summaries": {d: f"You were assessed in {d}." for d in names},
                "recommendation_rationale": "The pathway reflects the balance of demonstrated strengths and gaps.",
                "next_action": "Focus on your highest-priority gap with a deliberate project.",
                "learning_priorities": [
                    "Applied AI agents",
                    "Testing and verification",
                    "Production debugging",
                ],
            }
        )


def _extract_response(instruction: str) -> str:
    match = re.search(r"Candidate response:\n<<<\n(.*?)\n>>>", instruction, re.DOTALL)
    return match.group(1) if match else ""


def _find_url(text: str, host: str) -> str | None:
    match = re.search(rf"https?://[^\s]*{re.escape(host)}[^\s]*", text, re.IGNORECASE)
    return match.group(0) if match else None


def _keyword_signal(text: str) -> float:
    tokens = re.findall(r"[a-zA-Z_-]+", text.lower())
    if not tokens:
        return 0.0
    hits = sum(1 for t in tokens if t in _TECH_KEYWORDS)
    return min(1.0, hits / 12.0)
