"""Assessment result, report, and recommendation models.

The final synthesis is grounded in persisted evaluations — it may not invent
facts absent from the evidence.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .assessment import EvidenceItem
from .enums import Dimension, Pathway, ReadinessClassification


def _utcnow() -> datetime:
    return datetime.now(UTC)


class DimensionResult(BaseModel):
    dimension: Dimension
    score: int = Field(ge=0, le=100)
    classification: ReadinessClassification
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    summary: str = ""


class Recommendation(BaseModel):
    pathway: Pathway
    rationale: str
    capability_areas: list[str] = Field(default_factory=list)
    next_action: str
    learning_priorities: list[str] = Field(default_factory=list)


class ReadinessResult(BaseModel):
    """The structured readiness result returned by the engine."""

    overall_score: int = Field(ge=0, le=100)
    classification: ReadinessClassification
    dimension_results: list[DimensionResult] = Field(default_factory=list)
    key_strengths: list[str] = Field(default_factory=list)
    capability_gaps: list[str] = Field(default_factory=list)
    summary: str
    recommendation: Recommendation
    evidence: list[EvidenceItem] = Field(default_factory=list)
    completed_at: datetime = Field(default_factory=_utcnow)


class AssessmentReport(BaseModel):
    """Document-like report rendered in the frontend like a clean Notion page."""

    assessment_id: str
    title: str
    summary: str
    readiness: dict[str, Any]
    strengths: list[str]
    development_areas: list[str]
    evidence: list[EvidenceItem]
    recommended_pathway: Recommendation
    learning_priorities: list[str]
    created_at: datetime = Field(default_factory=_utcnow)
