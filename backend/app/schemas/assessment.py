"""Assessment API schemas.

The frontend never sees evaluation criteria or internal objectives — only what
the candidate needs to answer well: the dimension, format, prompt, optional
context, and (for multiple choice) the options.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from ..models.enums import AssessmentStatus, Dimension, QuestionFormat


class QuestionOptionOut(BaseModel):
    id: str
    text: str


class QuestionOut(BaseModel):
    id: str
    dimension: Dimension
    format: QuestionFormat
    prompt: str
    context: str | None = None
    options: list[QuestionOptionOut] = Field(default_factory=list)
    sequence: int = 0


class SubmitResponseRequest(BaseModel):
    question_id: str | None = None
    text: str = ""
    selected_option_id: str | None = None
    submission_key: str | None = None
    duration_seconds: float | None = None


class StartAssessmentRequest(BaseModel):
    introduction: str | None = None


class AssessmentStateOut(BaseModel):
    id: str
    status: AssessmentStatus
    answered_count: int
    max_questions: int
    current_question: QuestionOut | None = None
    dimensions_covered: list[str] = Field(default_factory=list)
    completed: bool = False
    completed_at: datetime | None = None
    # The professional processing label the UI should display while waiting.
    processing_label: str | None = None


class AssessmentSummaryOut(BaseModel):
    id: str
    status: AssessmentStatus
    created_at: datetime
    completed_at: datetime | None = None
    overall_score: int | None = None
    classification: str | None = None
    pathway: str | None = None
