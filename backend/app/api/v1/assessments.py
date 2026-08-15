"""Assessment routes: list, start, state, submit, result, report."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ...core.deps import get_current_settings, get_current_user, get_datastore
from ...core.security import AuthUser
from ...repositories.base import Store
from ...schemas.assessment import (
    AssessmentStateOut,
    AssessmentSummaryOut,
    StartAssessmentRequest,
    SubmitResponseRequest,
)
from ...schemas.result import ResultOut
from .mappers import to_result_out, to_state_out, to_summary_out

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.get("", response_model=list[AssessmentSummaryOut])
async def list_assessments(
    user: AuthUser = Depends(get_current_user),
    store: Store = Depends(get_datastore),
):
    states = _list_states(store, user.id)
    out: list[AssessmentSummaryOut] = []
    for state in states:
        result = store.get_result(state.id, user.id) if state.status.value == "completed" else None
        out.append(to_summary_out(state, result))
    return out


@router.post("", response_model=AssessmentStateOut)
async def start_assessment(
    body: StartAssessmentRequest,
    user: AuthUser = Depends(get_current_user),
    store: Store = Depends(get_datastore),
    settings=Depends(get_current_settings),
):
    from ...services.assessment_service import assessment_service

    state = await assessment_service.start_assessment(store, user.id, body.introduction)
    return to_state_out(state, settings)


@router.get("/{assessment_id}", response_model=AssessmentStateOut)
async def get_assessment(
    assessment_id: str,
    user: AuthUser = Depends(get_current_user),
    store: Store = Depends(get_datastore),
    settings=Depends(get_current_settings),
):
    from ...services.assessment_service import assessment_service

    state = assessment_service.get_state(store, user.id, assessment_id)
    return to_state_out(state, settings)


@router.post("/{assessment_id}/responses", response_model=AssessmentStateOut)
async def submit_response(
    assessment_id: str,
    body: SubmitResponseRequest,
    user: AuthUser = Depends(get_current_user),
    store: Store = Depends(get_datastore),
    settings=Depends(get_current_settings),
):
    from ...services.assessment_service import assessment_service

    state = await assessment_service.submit_response(
        store,
        user.id,
        assessment_id,
        question_id=body.question_id,
        text=body.text,
        selected_option_id=body.selected_option_id,
        submission_key=body.submission_key,
        duration_seconds=body.duration_seconds,
    )
    label = None
    if state.status.value == "completed":
        label = "Preparing your assessment"
    elif state.status.value == "in_progress" and state.current_question_id:
        label = "Preparing next question"
    return to_state_out(state, settings, processing_label=label)


@router.get("/{assessment_id}/result", response_model=ResultOut)
async def get_result(
    assessment_id: str,
    user: AuthUser = Depends(get_current_user),
    store: Store = Depends(get_datastore),
):
    from ...services.assessment_service import assessment_service

    result = assessment_service.get_result(store, user.id, assessment_id)
    return to_result_out(result)


@router.get("/{assessment_id}/report")
async def get_report(
    assessment_id: str,
    user: AuthUser = Depends(get_current_user),
    store: Store = Depends(get_datastore),
):
    from ...services.assessment_service import assessment_service

    report = assessment_service.get_report(store, user.id, assessment_id)
    from .mappers import to_report_out

    return to_report_out(report)


def _list_states(store: Store, user_id: str):
    from ...services.assessment_service import assessment_service

    return assessment_service.list_assessments(store, user_id)
