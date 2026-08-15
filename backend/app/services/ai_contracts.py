"""Pydantic schemas for Gemini structured outputs — the AI contracts.

Each Gemini use case has its own prompt and its own output schema. The
Interactions API returns free text (JSON); these schemas validate it and coerce
the model's realistic structured forms into the flat domain types. Deterministic
engine logic (scoring, classification, pathway selection) is owned by application
code, not by these models.
"""

from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from ..models.enums import Dimension, QuestionFormat


def _coerce_str(value: Any) -> str | None:
    """Coerce common structured forms into a single string (or None)."""
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        parts = [_flatten(v) for v in value]
        joined = ", ".join(p for p in parts if p)
        return joined or None
    if isinstance(value, dict):
        return _flatten(value) or None
    return str(value)


def _flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        # Prefer common resume keys, then fall back to a key:value join.
        for k in ("degree", "title", "name", "role", "school", "company", "description"):
            if value.get(k):
                return str(value[k]).strip()
        return ", ".join(f"{k}: {v}" for k, v in value.items() if v not in (None, "", []))
    if isinstance(value, list):
        return ", ".join(_flatten(v) for v in value if v is not None)
    return str(value)


def _coerce_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            s = _flatten(item)
            if s:
                out.append(s)
        return out
    if isinstance(value, dict):
        s = _flatten(value)
        return [s] if s else []
    return [str(value)]


class ExtractedProject(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    url: str | None = None

    @field_validator("name", "description", mode="before")
    @classmethod
    def _str(cls, v: Any) -> Any:
        return _coerce_str(v)

    @field_validator("technologies", mode="before")
    @classmethod
    def _tech(cls, v: Any) -> Any:
        return _coerce_str_list(v)

    @field_validator("url", mode="before")
    @classmethod
    def _url(cls, v: Any) -> Any:
        return _coerce_str(v)


class ResumeExtraction(BaseModel):
    """Gemini output for resume parsing. Nulls where facts are absent."""

    name: str | None = None
    education: str | None = None
    graduation_year: int | None = None
    experience: str | None = None
    target_role: str | None = None
    technical_skills: list[str] = Field(default_factory=list)
    projects: list[ExtractedProject] = Field(default_factory=list)
    ai_tools: list[str] = Field(default_factory=list)
    github: str | None = None
    linkedin: str | None = None
    professional_links: list[str] = Field(default_factory=list)
    background: str | None = None

    @field_validator(
        "name",
        "education",
        "experience",
        "target_role",
        "github",
        "linkedin",
        "background",
        mode="before",
    )
    @classmethod
    def _coerce_text(cls, v: Any) -> Any:
        return _coerce_str(v)

    @field_validator("technical_skills", "ai_tools", "professional_links", mode="before")
    @classmethod
    def _coerce_list(cls, v: Any) -> Any:
        return _coerce_str_list(v)

    @field_validator("graduation_year", mode="before")
    @classmethod
    def _coerce_year(cls, v: Any) -> Any:
        if v is None:
            return None
        if isinstance(v, str):
            digits = "".join(ch for ch in v if ch.isdigit())
            return int(digits) if len(digits) == 4 else None
        if isinstance(v, (int, float)):
            return int(v)
        # Pulled from a structured object: scan for a 4-digit year.
        text = _flatten(v)
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits) if len(digits) == 4 else None


class GeneratedOption(BaseModel):
    id: str
    text: str

    @field_validator("id", "text", mode="before")
    @classmethod
    def _str(cls, v: Any) -> Any:
        return _coerce_str(v) or ""


def _coerce_dimension(v: Any) -> Dimension:
    s = _coerce_str(v) or ""
    lowered = s.lower()
    for d in Dimension:
        if d.value.lower() in lowered or lowered in d.value.lower():
            return d
    return Dimension.ENGINEERING_FUNDAMENTALS


def _coerce_format(v: Any) -> QuestionFormat:
    s = _coerce_str(v) or ""
    lowered = s.lower().replace("-", "_").replace(" ", "_")
    for f in QuestionFormat:
        if f.value.lower() in lowered or lowered in f.value.lower():
            return f
    return QuestionFormat.WRITTEN


class GeneratedQuestion(BaseModel):
    """Gemini output for adaptive question generation."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    dimension: Dimension = Field(validation_alias=AliasChoices("dimension", "target_dimension"))
    format: QuestionFormat = QuestionFormat.WRITTEN
    prompt: str = Field(validation_alias=AliasChoices("prompt", "question"))
    context: str | None = None
    options: list[GeneratedOption] = Field(default_factory=list)
    assessment_objective: str = Field(
        validation_alias=AliasChoices("assessment_objective", "objective")
    )
    evaluation_criteria: list[str] = Field(
        default_factory=list, validation_alias=AliasChoices("evaluation_criteria", "criteria")
    )
    more_evidence_needed_hint: bool = Field(
        default=True,
        validation_alias=AliasChoices("more_evidence_needed_hint", "more_evidence_needed"),
    )

    @field_validator("dimension", mode="before")
    @classmethod
    def _dim(cls, v: Any) -> Any:
        return _coerce_dimension(v)

    @field_validator("format", mode="before")
    @classmethod
    def _fmt(cls, v: Any) -> Any:
        return _coerce_format(v)

    @field_validator("prompt", "assessment_objective", "context", mode="before")
    @classmethod
    def _str(cls, v: Any) -> Any:
        return _coerce_str(v)

    @field_validator("options", mode="before")
    @classmethod
    def _opts(cls, v: Any) -> Any:
        if v is None:
            return []
        if isinstance(v, dict):
            v = [v]
        if not isinstance(v, list):
            return []
        out: list[dict[str, str]] = []
        for item in v:
            if isinstance(item, dict):
                out.append(
                    {
                        "id": _coerce_str(item.get("id") or item.get("value") or "a") or "",
                        "text": _coerce_str(item.get("text") or item.get("label") or "") or "",
                    }
                )
            elif isinstance(item, str):
                out.append({"id": "a", "text": item})
        return out

    @field_validator("evaluation_criteria", mode="before")
    @classmethod
    def _crit(cls, v: Any) -> Any:
        return _coerce_str_list(v)


class EvidenceStatement(BaseModel):
    statement: str
    supports: str

    @field_validator("statement", "supports", mode="before")
    @classmethod
    def _str(cls, v: Any) -> Any:
        return _coerce_str(v) or ""


def _coerce_evidence(v: Any) -> list[dict[str, str]]:
    if v is None:
        return []
    if isinstance(v, dict):
        v = [v]
    if not isinstance(v, list):
        return []
    out: list[dict[str, str]] = []
    for item in v:
        if isinstance(item, str):
            out.append({"statement": item, "supports": "response"})
        elif isinstance(item, dict):
            out.append(
                {
                    "statement": _coerce_str(item.get("statement") or item.get("evidence") or item)
                    or "",
                    "supports": _coerce_str(
                        item.get("supports") or item.get("capability") or "response"
                    )
                    or "",
                }
            )
    return out


class ResponseEvaluation(BaseModel):
    """Gemini output for evaluating one response."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    evidence: list[EvidenceStatement] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    dimension_score: int = Field(
        ge=0,
        le=100,
        default=50,
        validation_alias=AliasChoices("dimension_score", "score", "capability_score"),
    )
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    rationale: str = ""
    more_evidence_needed: bool = Field(
        default=True,
        validation_alias=AliasChoices("more_evidence_needed", "needs_more_evidence", "needs_more"),
    )

    @field_validator("evidence", mode="before")
    @classmethod
    def _ev(cls, v: Any) -> Any:
        return _coerce_evidence(v)

    @field_validator("strengths", "gaps", mode="before")
    @classmethod
    def _coerce_findings(cls, v: Any) -> Any:
        return _coerce_str_list(v)

    @field_validator("rationale", mode="before")
    @classmethod
    def _rat(cls, v: Any) -> Any:
        return _coerce_str(v) or ""

    @field_validator("dimension_score", mode="before")
    @classmethod
    def _score(cls, v: Any) -> Any:
        if v is None:
            return 50
        if isinstance(v, str):
            digits = "".join(ch for ch in v if ch.isdigit())
            return int(digits) if digits else 50
        return int(v)

    @field_validator("confidence", mode="before")
    @classmethod
    def _conf(cls, v: Any) -> Any:
        if v is None:
            return 0.5
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return 0.5
        return float(v)


class ResultSynthesis(BaseModel):
    """Gemini output for final report narrative.

    No scores or pathway here — those are deterministic. Gemini only writes
    human-readable narrative grounded in the supplied evidence.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    overall_summary: str = Field(validation_alias=AliasChoices("overall_summary", "summary"))
    dimension_summaries: dict[str, str] = Field(default_factory=dict)
    recommendation_rationale: str = Field(
        validation_alias=AliasChoices("recommendation_rationale", "rationale")
    )
    next_action: str = Field(validation_alias=AliasChoices("next_action", "next_step"))
    learning_priorities: list[str] = Field(default_factory=list)

    @field_validator("dimension_summaries", mode="before")
    @classmethod
    def _dim_summaries(cls, v: Any) -> Any:
        if v is None:
            return {}
        if isinstance(v, list):
            return {
                item.get("dimension", ""): item.get("summary", "")
                for item in v
                if isinstance(item, dict)
            }
        return v

    @field_validator("learning_priorities", mode="before")
    @classmethod
    def _coerce_priorities(cls, v: Any) -> Any:
        return _coerce_str_list(v)
