"""Result & report API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from ..models.assessment import EvidenceItem
from ..models.enums import Dimension, Pathway, ReadinessClassification


class DimensionResultOut(BaseModel):
    dimension: Dimension
    score: int
    classification: ReadinessClassification
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    summary: str = ""


class RecommendationOut(BaseModel):
    pathway: Pathway
    rationale: str
    capability_areas: list[str] = Field(default_factory=list)
    next_action: str
    learning_priorities: list[str] = Field(default_factory=list)


class ResultOut(BaseModel):
    overall_score: int
    classification: ReadinessClassification
    dimension_results: list[DimensionResultOut] = Field(default_factory=list)
    key_strengths: list[str] = Field(default_factory=list)
    capability_gaps: list[str] = Field(default_factory=list)
    summary: str
    recommendation: RecommendationOut
    evidence: list[EvidenceItem] = Field(default_factory=list)
    completed_at: datetime


class ReportOut(BaseModel):
    assessment_id: str
    title: str
    summary: str
    readiness: dict
    strengths: list[str] = Field(default_factory=list)
    development_areas: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    recommended_pathway: RecommendationOut
    learning_priorities: list[str] = Field(default_factory=list)
    created_at: datetime
