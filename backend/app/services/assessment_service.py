"""Assessment orchestration: ties engine, store, and report service together.

Routes stay thin; this layer owns the request-level workflow, idempotency,
state transitions, and persistence ordering (state is saved before the next
question is returned).
"""

from __future__ import annotations

import logging
from datetime import UTC

from ..core.config import Settings, get_settings
from ..core.errors import (
    AssessmentStateError,
    NotFoundError,
    ValidationError,
)
from ..models.assessment import AssessmentState, Response
from ..models.enums import AssessmentStatus
from ..models.profile import CandidateProfile
from ..repositories.base import Store
from .assessment_engine import assessment_engine
from .report_service import report_service

logger = logging.getLogger("aura.assessment")


class AssessmentService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    # --- Profile ---
    def get_profile(self, store: Store, user_id: str) -> CandidateProfile:
        return store.get_profile(user_id) or CandidateProfile(user_id=user_id)

    def upsert_profile(self, store: Store, user_id: str, updates: dict) -> CandidateProfile:
        profile = self.get_profile(store, user_id)
        profile = profile.model_copy(
            update={k: v for k, v in updates.items() if k in CandidateProfile.model_fields}
        )
        from datetime import datetime

        profile.updated_at = datetime.now(UTC)
        return store.upsert_profile(profile)

    # --- Assessment lifecycle ---
    async def start_assessment(
        self,
        store: Store,
        user_id: str,
        introduction: str | None,
    ) -> AssessmentState:
        profile = self.get_profile(store, user_id)
        if not (profile.target_role or profile.background or profile.resume_parsed):
            # Allow starting but warn softly — context improves adaptation.
            logger.info("Starting assessment with minimal candidate context for %s", user_id)

        state = AssessmentState(
            user_id=user_id,
            profile_snapshot=profile.context_for_assessment(),
            status=AssessmentStatus.IN_PROGRESS,
            introduction=introduction,
        )
        state.ensure_dimension_evidence_populated()

        question = await assessment_engine.first_question(profile)
        state.questions.append(question)
        state.current_question_id = question.id
        state.touch()

        return store.create_assessment(state)

    async def submit_response(
        self,
        store: Store,
        user_id: str,
        assessment_id: str,
        *,
        question_id: str | None,
        text: str,
        selected_option_id: str | None = None,
        submission_key: str | None = None,
        duration_seconds: float | None = None,
    ) -> AssessmentState:
        state = store.get_assessment(assessment_id, user_id)
        if state is None:
            raise NotFoundError("Assessment not found.")

        # Idempotency first: a repeated submission returns the persisted state,
        # even if the assessment has since completed. This must never create a
        # second assessment turn for one logical submission.
        if submission_key:
            for r in state.responses:
                if r.submission_key == submission_key:
                    return state

        if state.status in (AssessmentStatus.COMPLETED, AssessmentStatus.FAILED):
            raise AssessmentStateError("This assessment is already complete.")
        if state.current_question_id is None:
            raise AssessmentStateError("There is no active question to answer.")

        expected_qid = question_id or state.current_question_id
        if expected_qid != state.current_question_id:
            raise AssessmentStateError("The response does not match the current question.")

        question = next((q for q in state.questions if q.id == state.current_question_id), None)
        if question is None:
            raise AssessmentStateError("The current question could not be found.")

        if not text.strip() and not selected_option_id:
            raise ValidationError("Please provide a response before continuing.")

        response = Response(
            question_id=question.id,
            text=text.strip(),
            selected_option_id=selected_option_id,
            duration_seconds=duration_seconds,
            submission_key=submission_key,
        )

        # Evaluate + update evidence (engine mutates the in-memory state).
        state = await assessment_engine.record_response(state, question, response)

        # Decide next step using deterministic stopping rules.
        next_question = await assessment_engine.next_question(state)

        if next_question is None:
            state.status = AssessmentStatus.COMPLETING
            state.current_question_id = None
            state.touch()
            store.save_assessment(state)
            # Build deterministic result + grounded report.
            result = await report_service.build_result(state)
            store.save_result(state.id, result)
            report = await report_service.build_report(state, result)
            store.save_report(state.id, report)
            from datetime import datetime

            state.completed_at = datetime.now(UTC)
            state.status = AssessmentStatus.COMPLETED
            state.touch()
            store.save_assessment(state)
        else:
            state.questions.append(next_question)
            state.current_question_id = next_question.id
            state.status = AssessmentStatus.IN_PROGRESS
            state.touch()
            store.save_assessment(state)

        return state

    def get_state(self, store: Store, user_id: str, assessment_id: str) -> AssessmentState:
        state = store.get_assessment(assessment_id, user_id)
        if state is None:
            raise NotFoundError("Assessment not found.")
        return state

    def list_assessments(self, store: Store, user_id: str) -> list[AssessmentState]:
        return store.list_assessments(user_id)

    def get_result(self, store: Store, user_id: str, assessment_id: str):
        state = self.get_state(store, user_id, assessment_id)
        if state.status != AssessmentStatus.COMPLETED:
            raise AssessmentStateError("This assessment has not completed yet.")
        result = store.get_result(assessment_id, user_id)
        if result is None:
            raise NotFoundError("Result not found.")
        return result

    def get_report(self, store: Store, user_id: str, assessment_id: str):
        state = self.get_state(store, user_id, assessment_id)
        if state.status != AssessmentStatus.COMPLETED:
            raise AssessmentStateError("This assessment has not completed yet.")
        report = store.get_report(assessment_id, user_id)
        if report is None:
            raise NotFoundError("Report not found.")
        return report


assessment_service = AssessmentService()
