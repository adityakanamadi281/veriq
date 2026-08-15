"""Map domain models to API response schemas."""

from __future__ import annotations

from ...core.config import Settings
from ...models.assessment import AssessmentState
from ...models.enums import AssessmentStatus, Dimension
from ...models.result import AssessmentReport, ReadinessResult
from ...schemas.assessment import (
    AssessmentStateOut,
    AssessmentSummaryOut,
    QuestionOptionOut,
    QuestionOut,
)
from ...schemas.result import DimensionResultOut, RecommendationOut, ReportOut, ResultOut


def to_question_out(question) -> QuestionOut:
    return QuestionOut(
        id=question.id,
        dimension=question.dimension,
        format=question.format,
        prompt=question.prompt,
        context=question.context,
        options=[QuestionOptionOut(id=o.id, text=o.text) for o in question.options],
        sequence=question.sequence,
    )


def to_state_out(
    state: AssessmentState, settings: Settings, processing_label: str | None = None
) -> AssessmentStateOut:
    current = None
    if state.current_question_id:
        q = next((q for q in state.questions if q.id == state.current_question_id), None)
        if q is not None:
            current = to_question_out(q)
    covered = [d.value for d in Dimension if state.dimension_evidence_for(d).coverage > 0]
    return AssessmentStateOut(
        id=state.id,
        status=state.status,
        answered_count=state.answered_count(),
        max_questions=settings.assessment_max_questions,
        current_question=current,
        dimensions_covered=covered,
        completed=state.status == AssessmentStatus.COMPLETED,
        completed_at=state.completed_at,
        processing_label=processing_label,
    )


def to_result_out(result: ReadinessResult) -> ResultOut:
    return ResultOut(
        overall_score=result.overall_score,
        classification=result.classification,
        dimension_results=[
            DimensionResultOut(
                dimension=dr.dimension,
                score=dr.score,
                classification=dr.classification,
                strengths=dr.strengths,
                gaps=dr.gaps,
                summary=dr.summary,
            )
            for dr in result.dimension_results
        ],
        key_strengths=result.key_strengths,
        capability_gaps=result.capability_gaps,
        summary=result.summary,
        recommendation=RecommendationOut(
            pathway=result.recommendation.pathway,
            rationale=result.recommendation.rationale,
            capability_areas=result.recommendation.capability_areas,
            next_action=result.recommendation.next_action,
            learning_priorities=result.recommendation.learning_priorities,
        ),
        evidence=result.evidence,
        completed_at=result.completed_at,
    )


def to_report_out(report: AssessmentReport) -> ReportOut:
    return ReportOut(
        assessment_id=report.assessment_id,
        title=report.title,
        summary=report.summary,
        readiness=report.readiness,
        strengths=report.strengths,
        development_areas=report.development_areas,
        evidence=report.evidence,
        recommended_pathway=RecommendationOut(
            pathway=report.recommended_pathway.pathway,
            rationale=report.recommended_pathway.rationale,
            capability_areas=report.recommended_pathway.capability_areas,
            next_action=report.recommended_pathway.next_action,
            learning_priorities=report.recommended_pathway.learning_priorities,
        ),
        learning_priorities=report.learning_priorities,
        created_at=report.created_at,
    )


def to_summary_out(state: AssessmentState, result=None) -> AssessmentSummaryOut:
    overall = getattr(result, "overall_score", None) if result else None
    classification = getattr(result, "classification", None) if result else None
    pathway = getattr(getattr(result, "recommendation", None), "pathway", None) if result else None
    return AssessmentSummaryOut(
        id=state.id,
        status=state.status,
        created_at=state.created_at,
        completed_at=state.completed_at,
        overall_score=overall,
        classification=classification.value if classification else None,
        pathway=pathway.value if pathway else None,
    )
