"""Assessment domain models: questions, responses, evaluations, evidence, state.

Raw candidate responses are kept separate from normalized evaluations. The
engine stores enough to resume an assessment after a browser refresh.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .enums import AssessmentStatus, Dimension, QuestionFormat


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _gen_id() -> str:
    return str(uuid4())


class QuestionOption(BaseModel):
    id: str
    text: str


class Question(BaseModel):
    """A single adaptive question produced by the engine."""

    id: str = Field(default_factory=_gen_id)
    dimension: Dimension
    format: QuestionFormat
    prompt: str
    context: str | None = None  # optional framing, e.g. a code snippet / scenario
    options: list[QuestionOption] = Field(default_factory=list)  # for multiple choice
    assessment_objective: str
    evaluation_criteria: list[str] = Field(default_factory=list)
    sequence: int = 0


class Response(BaseModel):
    """The candidate's raw answer to a question. Stored verbatim."""

    question_id: str
    text: str
    selected_option_id: str | None = None
    duration_seconds: float | None = None
    created_at: datetime = Field(default_factory=_utcnow)
    # Idempotency key supplied by the client to dedupe double-submits.
    submission_key: str | None = None


class EvidenceItem(BaseModel):
    """A concrete, traceable observation drawn from a response."""

    statement: str
    supports: str  # what capability this speaks to


class Evaluation(BaseModel):
    """Normalized evaluation of a single response, produced by Gemini.

    The engine treats this as validated input to deterministic logic. Gemini
    never mutates assessment state directly.
    """

    question_id: str
    dimension: Dimension
    evidence: list[EvidenceItem] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    # 0-100 capability signal for this dimension contribution.
    dimension_score: int = Field(ge=0, le=100, default=50)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    rationale: str = ""
    more_evidence_needed: bool = True
    created_at: datetime = Field(default_factory=_utcnow)


class DimensionEvidence(BaseModel):
    """Accumulated evidence for one dimension across the assessment."""

    dimension: Dimension
    scores: list[int] = Field(default_factory=list)  # per-evaluation signals
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    coverage: int = 0  # number of questions touching this dimension

    def add(self, evaluation: Evaluation) -> None:
        self.scores.append(evaluation.dimension_score)
        self.strengths.extend(evaluation.strengths)
        self.gaps.extend(evaluation.gaps)
        self.evidence.extend(evaluation.evidence)
        self.coverage += 1

    def aggregate_score(self) -> int:
        if not self.scores:
            return 0
        # Weighted toward recent evidence (recency reflects adaptation).
        weights = [1.0 + 0.1 * i for i in range(len(self.scores))]
        weighted = sum(s * w for s, w in zip(self.scores, weights, strict=True))
        return round(weighted / sum(weights))

    def top_strengths(self, k: int = 3) -> list[str]:
        # Preserve order of first appearance, dedupe.
        seen: set[str] = set()
        out: list[str] = []
        for s in self.strengths:
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out[:k]

    def top_gaps(self, k: int = 3) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for g in self.gaps:
            if g not in seen:
                seen.add(g)
                out.append(g)
        return out[:k]


class AssessmentState(BaseModel):
    """The durable, resumable state of one assessment."""

    id: str = Field(default_factory=_gen_id)
    user_id: str
    profile_snapshot: dict[str, Any] = Field(default_factory=dict)
    status: AssessmentStatus = AssessmentStatus.CREATED
    questions: list[Question] = Field(default_factory=list)
    responses: list[Response] = Field(default_factory=list)
    evaluations: list[Evaluation] = Field(default_factory=list)
    dimension_evidence: dict[str, DimensionEvidence] = Field(default_factory=dict)
    current_question_id: str | None = None
    introduction: str | None = None  # candidate's self-introduction
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    completed_at: datetime | None = None

    def dimension_evidence_for(self, dimension: Dimension) -> DimensionEvidence:
        key = dimension.value
        if key not in self.dimension_evidence:
            self.dimension_evidence[key] = DimensionEvidence(dimension=dimension)
        return self.dimension_evidence[key]

    def answered_count(self) -> int:
        return len(self.responses)

    def touch(self) -> None:
        self.updated_at = _utcnow()

    def ensure_dimension_evidence_populated(self) -> None:
        for d in Dimension:
            self.dimension_evidence_for(d)
