"""In-memory fake store used ONLY by unit tests.

Production uses Supabase/Postgres (no in-memory fallback). This test double
implements the same Store protocol so the engine and API can be exercised
without a database.
"""

from __future__ import annotations

from threading import Lock

from backend.app.core.errors import NotFoundError
from backend.app.models.assessment import AssessmentState
from backend.app.models.profile import CandidateProfile
from backend.app.models.result import AssessmentReport, ReadinessResult


class FakeStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._profiles: dict[str, CandidateProfile] = {}
        self._assessments: dict[str, AssessmentState] = {}
        self._results: dict[str, ReadinessResult] = {}
        self._reports: dict[str, AssessmentReport] = {}

    # --- Profiles ---
    def get_profile(self, user_id: str) -> CandidateProfile | None:
        return self._profiles.get(user_id)

    def upsert_profile(self, profile: CandidateProfile) -> CandidateProfile:
        with self._lock:
            self._profiles[profile.user_id] = profile
            return profile

    # --- Assessments ---
    def create_assessment(self, state: AssessmentState) -> AssessmentState:
        with self._lock:
            self._assessments[state.id] = state
            return state

    def save_assessment(self, state: AssessmentState) -> AssessmentState:
        with self._lock:
            if state.id not in self._assessments:
                raise NotFoundError("Assessment not found.")
            self._assessments[state.id] = state
            return state

    def get_assessment(self, assessment_id: str, user_id: str) -> AssessmentState | None:
        state = self._assessments.get(assessment_id)
        if state is None or state.user_id != user_id:
            return None
        return state

    def list_assessments(self, user_id: str) -> list[AssessmentState]:
        return [s for s in self._assessments.values() if s.user_id == user_id]

    # --- Results & reports ---
    def save_result(self, assessment_id: str, result: ReadinessResult) -> ReadinessResult:
        with self._lock:
            self._results[assessment_id] = result
            return result

    def get_result(self, assessment_id: str, user_id: str) -> ReadinessResult | None:
        state = self._assessments.get(assessment_id)
        if state is None or state.user_id != user_id:
            return None
        return self._results.get(assessment_id)

    def list_results(self, user_id: str) -> list[ReadinessResult]:
        ids = {s.id for s in self._assessments.values() if s.user_id == user_id}
        return [r for aid, r in self._results.items() if aid in ids]

    def save_report(self, assessment_id: str, report: AssessmentReport) -> AssessmentReport:
        with self._lock:
            self._reports[assessment_id] = report
            return report

    def get_report(self, assessment_id: str, user_id: str) -> AssessmentReport | None:
        state = self._assessments.get(assessment_id)
        if state is None or state.user_id != user_id:
            return None
        return self._reports.get(assessment_id)
