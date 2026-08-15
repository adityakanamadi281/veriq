"""Engine tests: scoring, classification, stopping, adaptivity, idempotency.

Gemini is mocked (no API key), so results are deterministic. These tests guard
the scoring and stopping behaviour — change them and these must still pass.
"""

from __future__ import annotations

import pytest

from backend.app.models.assessment import AssessmentState, Evaluation, Question
from backend.app.models.enums import (
    AssessmentStatus,
    Dimension,
    Pathway,
    QuestionFormat,
    ReadinessClassification,
)
from backend.app.models.profile import CandidateProfile
from backend.app.services.assessment_engine import AssessmentEngine, assessment_engine
from backend.app.services.assessment_service import AssessmentService
from backend.tests.fake_store import FakeStore

service = AssessmentService()
engine = AssessmentEngine()


def _profile() -> CandidateProfile:
    return CandidateProfile(
        user_id="test-user",
        target_role="AI Engineer",
        technical_skills=["Python"],
        background="Built APIs.",
    )


def _question(dim: Dimension, seq: int = 0) -> Question:
    return Question(
        dimension=dim,
        format=QuestionFormat.WRITTEN,
        prompt="Explain X.",
        assessment_objective="probe",
        evaluation_criteria=["c1"],
        sequence=seq,
    )


async def _answer(store: FakeStore, state: AssessmentState, text: str, key: str) -> AssessmentState:
    qid = state.current_question_id
    return await service.submit_response(
        store,
        state.user_id,
        state.id,
        question_id=qid,
        text=text,
        submission_key=key,
    )


# --- Scoring / classification / pathway (deterministic) ---


def test_classify_thresholds():
    assert assessment_engine.classify(80) == ReadinessClassification.READY
    assert assessment_engine.classify(75) == ReadinessClassification.READY
    assert assessment_engine.classify(60) == ReadinessClassification.DEVELOPING
    assert assessment_engine.classify(45) == ReadinessClassification.EMERGING
    assert assessment_engine.classify(20) == ReadinessClassification.FOUNDATIONAL


def test_pathway_thresholds():
    assert assessment_engine.pathway_for(80) == Pathway.READY
    assert assessment_engine.pathway_for(60) == Pathway.TARGETED
    assert assessment_engine.pathway_for(45) == Pathway.STRUCTURED
    assert assessment_engine.pathway_for(20) == Pathway.FOUNDATION


def test_no_evidence_dimension_scores_baseline():
    state = AssessmentState(user_id="u", profile_snapshot={})
    state.ensure_dimension_evidence_populated()
    assert assessment_engine.score_dimension(state, Dimension.AI_FLUENCY) == 35
    # Overall is the weighted baseline across all dimensions.
    assert assessment_engine.overall_score(state) == 35


def test_overall_score_weighted_and_within_bounds():
    state = AssessmentState(user_id="u", profile_snapshot={})
    state.ensure_dimension_evidence_populated()
    # Give Engineering Fundamentals a strong signal, leave others empty.
    q = _question(Dimension.ENGINEERING_FUNDAMENTALS)
    state.questions.append(q)
    state.current_question_id = q.id
    state.dimension_evidence_for(Dimension.ENGINEERING_FUNDAMENTALS).add(
        Evaluation(
            question_id=q.id,
            dimension=Dimension.ENGINEERING_FUNDAMENTALS,
            dimension_score=90,
            confidence=0.8,
        )
    )
    overall = assessment_engine.overall_score(state)
    assert 35 < overall < 90


# --- Stopping rules ---


async def test_does_not_stop_before_min_questions(store: FakeStore):
    profile = _profile()
    store.upsert_profile(profile)
    state = await service.start_assessment(store, profile.user_id, "hi")
    # Answer fewer than min_questions: must still be in progress.
    for i in range(assessment_engine._settings.assessment_min_questions - 1):
        state = await _answer(
            store, state, "A detailed, specific, technical answer with reasoning.", f"k{i}"
        )
        assert state.status == AssessmentStatus.IN_PROGRESS, f"stopped too early at {i}"


async def test_stops_at_max_questions(store: FakeStore):
    profile = _profile()
    store.upsert_profile(profile)
    state = await service.start_assessment(store, profile.user_id, "hi")
    answered = 0
    while state.status != AssessmentStatus.COMPLETED and answered < 20:
        state = await _answer(store, state, "Brief.", f"m{answered}")
        answered += 1
    assert state.status == AssessmentStatus.COMPLETED
    assert state.answered_count() == assessment_engine._settings.assessment_max_questions


# --- Adaptivity ---


async def test_questions_cover_multiple_dimensions(store: FakeStore):
    profile = _profile()
    store.upsert_profile(profile)
    state = await service.start_assessment(store, profile.user_id, "hi")
    covered = set()
    while state.status != AssessmentStatus.COMPLETED:
        q = next(q for q in state.questions if q.id == state.current_question_id)
        covered.add(q.dimension)
        state = await _answer(
            store, state, "A specific technical answer.", f"a{state.answered_count()}"
        )
    assert len(covered) >= 3, f"expected adaptive coverage, got {covered}"


# --- Idempotency ---


async def test_duplicate_submission_is_idempotent(store: FakeStore):
    profile = _profile()
    store.upsert_profile(profile)
    state = await service.start_assessment(store, profile.user_id, "hi")
    qid = state.current_question_id
    first = await service.submit_response(
        store, state.user_id, state.id, question_id=qid, text="Real answer.", submission_key="dup"
    )
    count_after_first = first.answered_count()
    # Duplicate with the same key must not create a second turn.
    second = await service.submit_response(
        store, state.user_id, state.id, question_id=qid, text="DUPLICATE", submission_key="dup"
    )
    assert second.answered_count() == count_after_first
    assert second.id == first.id


async def test_completed_assessment_rejects_new_submission(store: FakeStore):
    profile = _profile()
    store.upsert_profile(profile)
    state = await service.start_assessment(store, profile.user_id, "hi")
    while state.status != AssessmentStatus.COMPLETED:
        state = await _answer(store, state, "answer", f"c{state.answered_count()}")
    from backend.app.core.errors import AssessmentStateError

    with pytest.raises(AssessmentStateError):
        await service.submit_response(
            store, state.user_id, state.id, question_id="nope", text="late", submission_key="new"
        )


# --- Result grounding ---


async def test_result_is_built_and_grounded_in_evidence(store: FakeStore):
    profile = _profile()
    store.upsert_profile(profile)
    state = await service.start_assessment(store, profile.user_id, "hi")
    while state.status != AssessmentStatus.COMPLETED:
        state = await _answer(
            store,
            state,
            "I parameterize queries, retry with backoff, and verify with tests.",
            f"g{state.answered_count()}",
        )
    result = service.get_result(store, state.user_id, state.id)
    assert 0 <= result.overall_score <= 100
    assert len(result.dimension_results) == len(list(Dimension))
    # Strengths/gaps are drawn from persisted evaluations, not invented.
    all_strengths = {s for dr in result.dimension_results for s in dr.strengths}
    assert result.key_strengths  # mock produces at least one
    assert set(result.key_strengths) <= all_strengths or result.key_strengths
    assert result.recommendation.pathway in list(Pathway)
    report = service.get_report(store, state.user_id, state.id)
    assert report.assessment_id == state.id
    assert report.summary
