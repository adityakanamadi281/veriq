"""Supabase/Postgres-backed store using the normalized schema.

The engine works with an in-memory ``AssessmentState``; this store maps that
object to/from the normalized tables (assessments, assessment_questions,
assessment_responses, response_evaluations, assessment_results,
assessment_reports). Postgres is the source of truth and the only persistence
backend in production. Ownership is enforced by ``user_id`` and RLS.
"""

from __future__ import annotations

from typing import Any

from ..core.errors import AppError
from ..core.supabase import get_supabase_admin
from ..models.assessment import (
    AssessmentState,
    Evaluation,
    EvidenceItem,
    Question,
    QuestionOption,
    Response,
)
from ..models.enums import AssessmentStatus, Dimension, QuestionFormat
from ..models.profile import CandidateProfile, Project
from ..models.result import AssessmentReport, ReadinessResult


def _err(context: str, exc: Exception) -> AppError:
    err = AppError(
        f"Could not {context} right now. Please try again.",
        code="persistence_error",
        status_code=503,
    )
    err.__cause__ = exc
    return err


class SupabaseStore:
    def _client(self) -> Any:
        return get_supabase_admin()

    # ---------------- Profiles ----------------
    def get_profile(self, user_id: str) -> CandidateProfile | None:
        try:
            res = (
                self._client()
                .table("profiles")
                .select("*")
                .eq("id", user_id)
                .maybe_single()
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            raise _err("load your profile", exc)
        if not res or not res.data:
            return None
        return _profile_from_row(res.data)

    def upsert_profile(self, profile: CandidateProfile) -> CandidateProfile:
        try:
            self._client().table("profiles").upsert(_profile_to_row(profile)).execute()
        except Exception as exc:  # noqa: BLE001
            raise _err("save your profile", exc)
        return profile

    # ---------------- Assessments ----------------
    def create_assessment(self, state: AssessmentState) -> AssessmentState:
        return self._save_assessment(state)

    def save_assessment(self, state: AssessmentState) -> AssessmentState:
        return self._save_assessment(state)

    def _save_assessment(self, state: AssessmentState) -> AssessmentState:
        client = self._client()
        try:
            client.table("assessments").upsert(_assessment_to_row(state)).execute()

            if state.questions:
                client.table("assessment_questions").upsert(
                    [_question_to_row(state.id, q) for q in state.questions]
                ).execute()

            if state.responses:
                client.table("assessment_responses").upsert(
                    [_response_to_row(state.id, r) for r in state.responses]
                ).execute()

            if state.evaluations:
                client.table("response_evaluations").upsert(
                    [_evaluation_to_row(state.id, e) for e in state.evaluations]
                ).execute()
        except Exception as exc:  # noqa: BLE001
            raise _err("save assessment progress", exc)
        return state

    def get_assessment(self, assessment_id: str, user_id: str) -> AssessmentState | None:
        client = self._client()
        try:
            res = (
                client.table("assessments")
                .select("*")
                .eq("id", assessment_id)
                .eq("user_id", user_id)
                .maybe_single()
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            raise _err("load assessment", exc)
        if not res or not res.data:
            return None

        state = _assessment_from_row(res.data)
        try:
            qres = (
                client.table("assessment_questions")
                .select("*")
                .eq("assessment_id", assessment_id)
                .order("question_number")
                .execute()
            )
            rres = (
                client.table("assessment_responses")
                .select("*")
                .eq("assessment_id", assessment_id)
                .order("submitted_at")
                .execute()
            )
            eres = (
                client.table("response_evaluations")
                .select("*")
                .eq("assessment_id", assessment_id)
                .order("created_at")
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            raise _err("load assessment detail", exc)

        state.questions = [_question_from_row(r) for r in (qres.data or [])]
        state.responses = [_response_from_row(r) for r in (rres.data or [])]
        state.evaluations = [_evaluation_from_row(r) for r in (eres.data or [])]
        # Rebuild dimension evidence deterministically from persisted evaluations.
        state.dimension_evidence = {}
        for ev in state.evaluations:
            state.dimension_evidence_for(ev.dimension).add(ev)
        state.ensure_dimension_evidence_populated()
        return state

    def list_assessments(self, user_id: str) -> list[AssessmentState]:
        try:
            res = (
                self._client()
                .table("assessments")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            raise _err("load assessment history", exc)
        # Minimal states (no children) — enough for history summaries.
        return [_assessment_from_row(r, minimal=True) for r in (res.data or [])]

    # ---------------- Results & reports ----------------
    def save_result(self, assessment_id: str, result: ReadinessResult) -> ReadinessResult:
        try:
            self._client().table("assessment_results").upsert(
                _result_to_row(assessment_id, result)
            ).execute()
        except Exception as exc:  # noqa: BLE001
            raise _err("save result", exc)
        return result

    def get_result(self, assessment_id: str, user_id: str) -> ReadinessResult | None:
        try:
            res = (
                self._client()
                .table("assessment_results")
                .select("*, assessments!inner(user_id)")
                .eq("assessment_id", assessment_id)
                .maybe_single()
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            raise _err("load result", exc)
        if not res or not res.data:
            return None
        owner = res.data.get("assessments")
        if isinstance(owner, dict) and owner.get("user_id") != user_id:
            return None
        return _result_from_row(res.data)

    def list_results(self, user_id: str) -> list[ReadinessResult]:
        try:
            res = (
                self._client()
                .table("assessment_results")
                .select("*, assessments!inner(user_id)")
                .eq("assessments.user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            raise _err("load results history", exc)
        return [_result_from_row(r) for r in (res.data or [])]

    def save_report(self, assessment_id: str, report: AssessmentReport) -> AssessmentReport:
        try:
            self._client().table("assessment_reports").upsert(
                {"assessment_id": assessment_id, "report": report.model_dump(mode="json")}
            ).execute()
        except Exception as exc:  # noqa: BLE001
            raise _err("save report", exc)
        return report

    def get_report(self, assessment_id: str, user_id: str) -> AssessmentReport | None:
        try:
            res = (
                self._client()
                .table("assessment_reports")
                .select("report, assessments!inner(user_id)")
                .eq("assessment_id", assessment_id)
                .maybe_single()
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            raise _err("load report", exc)
        if not res or not res.data:
            return None
        owner = res.data.get("assessments")
        if isinstance(owner, dict) and owner.get("user_id") != user_id:
            return None
        return AssessmentReport.model_validate(res.data["report"])


# --------------------------- mappers ---------------------------


def _profile_to_row(p: CandidateProfile) -> dict[str, Any]:
    return {
        "id": p.user_id,
        "full_name": p.name,
        "education": p.education,
        "graduation_year": p.graduation_year,
        "experience": p.experience,
        "target_role": p.target_role,
        "github_url": p.github,
        "linkedin_url": p.linkedin,
        "resume_path": p.resume_path,
        "resume_parsed": p.resume_parsed,
        "details": {
            "technical_skills": p.technical_skills,
            "projects": [pr.model_dump(mode="json") for pr in p.projects],
            "ai_tools": p.ai_tools,
            "professional_links": p.professional_links,
            "background": p.background,
        },
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


def _profile_from_row(row: dict[str, Any]) -> CandidateProfile:
    details = row.get("details") or {}
    return CandidateProfile(
        user_id=row["id"],
        name=row.get("full_name"),
        education=row.get("education"),
        graduation_year=row.get("graduation_year"),
        experience=row.get("experience"),
        target_role=row.get("target_role"),
        technical_skills=details.get("technical_skills", []),
        projects=[Project(**p) for p in details.get("projects", [])],
        ai_tools=details.get("ai_tools", []),
        github=row.get("github_url"),
        linkedin=row.get("linkedin_url"),
        professional_links=details.get("professional_links", []),
        background=details.get("background"),
        resume_path=row.get("resume_path"),
        resume_parsed=row.get("resume_parsed", False),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )


def _assessment_to_row(s: AssessmentState) -> dict[str, Any]:
    target_role = (s.profile_snapshot or {}).get("target_role")
    return {
        "id": s.id,
        "user_id": s.user_id,
        "target_role": target_role,
        "status": s.status.value,
        "current_question_id": s.current_question_id,
        "introduction": s.introduction,
        "profile_snapshot": s.profile_snapshot or {},
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        "completed_at": s.completed_at.isoformat() if s.completed_at else None,
    }


def _assessment_from_row(row: dict[str, Any], *, minimal: bool = False) -> AssessmentState:
    state = AssessmentState(
        id=row["id"],
        user_id=row["user_id"],
        profile_snapshot=row.get("profile_snapshot") or {},
        status=AssessmentStatus(row.get("status", "created")),
        current_question_id=row.get("current_question_id"),
        introduction=row.get("introduction"),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
        completed_at=row.get("completed_at"),
    )
    if not minimal:
        state.ensure_dimension_evidence_populated()
    return state


def _question_to_row(assessment_id: str, q: Question) -> dict[str, Any]:
    return {
        "id": q.id,
        "assessment_id": assessment_id,
        "question_number": q.sequence,
        "dimension": q.dimension.value,
        "question": q.prompt,
        "question_type": q.format.value,
        "objective": q.assessment_objective,
        "evaluation_criteria": q.evaluation_criteria,
        "context": q.context,
        "options": [o.model_dump() for o in q.options],
    }


def _question_from_row(row: dict[str, Any]) -> Question:
    return Question(
        id=row["id"],
        dimension=Dimension(row["dimension"]),
        format=QuestionFormat(row.get("question_type", "written")),
        prompt=row["question"],
        context=row.get("context"),
        options=[QuestionOption(**o) for o in (row.get("options") or [])],
        assessment_objective=row.get("objective") or "",
        evaluation_criteria=row.get("evaluation_criteria") or [],
        sequence=row.get("question_number", 0),
    )


def _response_to_row(assessment_id: str, r: Response) -> dict[str, Any]:
    return {
        "id": r.question_id,  # one response per question -> stable id
        "assessment_id": assessment_id,
        "question_id": r.question_id,
        "response_text": r.text,
        "response_type": "written",
        "selected_option_id": r.selected_option_id,
        "duration_seconds": r.duration_seconds,
        "submission_key": r.submission_key,
        "submitted_at": r.created_at.isoformat() if r.created_at else None,
    }


def _response_from_row(row: dict[str, Any]) -> Response:
    return Response(
        question_id=row["question_id"],
        text=row.get("response_text", ""),
        selected_option_id=row.get("selected_option_id"),
        duration_seconds=row.get("duration_seconds"),
        created_at=row.get("submitted_at"),
        submission_key=row.get("submission_key"),
    )


def _evaluation_to_row(assessment_id: str, e: Evaluation) -> dict[str, Any]:
    return {
        "id": e.question_id,  # one evaluation per response -> stable id
        "response_id": e.question_id,
        "assessment_id": assessment_id,
        "dimension": e.dimension.value,
        "evidence": [ev.model_dump(mode="json") for ev in e.evidence],
        "strengths": e.strengths,
        "gaps": e.gaps,
        "capability_score": e.dimension_score,
        "confidence": e.confidence,
        "needs_more_evidence": e.more_evidence_needed,
        "rationale": e.rationale,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


def _evaluation_from_row(row: dict[str, Any]) -> Evaluation:
    return Evaluation(
        question_id=row["response_id"],
        dimension=Dimension(row["dimension"]),
        evidence=[EvidenceItem(**e) for e in (row.get("evidence") or [])],
        strengths=row.get("strengths") or [],
        gaps=row.get("gaps") or [],
        dimension_score=row.get("capability_score", 50),
        confidence=row.get("confidence", 0.5),
        rationale=row.get("rationale", ""),
        more_evidence_needed=row.get("needs_more_evidence", True),
        created_at=row.get("created_at"),
    )


def _result_to_row(assessment_id: str, r: ReadinessResult) -> dict[str, Any]:
    return {
        "assessment_id": assessment_id,
        "overall_score": r.overall_score,
        "readiness_classification": r.classification.value,
        "dimension_results": [dr.model_dump(mode="json") for dr in r.dimension_results],
        "strengths": r.key_strengths,
        "capability_gaps": r.capability_gaps,
        "personalized_summary": r.summary,
        "recommended_pathway": r.recommendation.pathway.value,
        "recommendation_reason": r.recommendation.rationale,
        "recommendation": r.recommendation.model_dump(mode="json"),
        "evidence": [e.model_dump(mode="json") for e in r.evidence],
        "created_at": r.completed_at.isoformat() if r.completed_at else None,
    }


def _result_from_row(row: dict[str, Any]) -> ReadinessResult:
    from ..models.result import DimensionResult, Recommendation

    rec_data = row.get("recommendation") or {}
    if not rec_data and row.get("recommended_pathway"):
        rec_data = {
            "pathway": row["recommended_pathway"],
            "rationale": row.get("recommendation_reason", ""),
            "capability_areas": [],
            "next_action": "",
            "learning_priorities": [],
        }
    return ReadinessResult(
        overall_score=row["overall_score"],
        classification=row["readiness_classification"],
        dimension_results=[DimensionResult(**d) for d in (row.get("dimension_results") or [])],
        key_strengths=row.get("strengths") or [],
        capability_gaps=row.get("capability_gaps") or [],
        summary=row.get("personalized_summary", ""),
        recommendation=Recommendation.model_validate(rec_data),
        evidence=[EvidenceItem(**e) for e in (row.get("evidence") or [])],
        completed_at=row.get("created_at"),
    )
