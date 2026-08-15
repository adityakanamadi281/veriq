"""The adaptive assessment engine.

Owns the loop lifecycle and the deterministic decisions: state transitions,
stopping rules, scoring, classification, and pathway selection. Gemini is used
only for question generation and (via the evaluator) response evaluation. The
model never mutates assessment state directly.
"""

from __future__ import annotations

import logging
from typing import Any

from ..core.config import Settings, get_settings
from ..core.errors import AssessmentStateError
from ..models.assessment import AssessmentState, Question, QuestionOption, Response
from ..models.enums import AssessmentStatus, Dimension, Pathway, ReadinessClassification
from ..models.profile import CandidateProfile
from .evaluator import evaluator
from .gemini_service import gemini_service

logger = logging.getLogger("aura.engine")

# Dimensions most relevant to an AI-first engineering role get extra weight.
_DIMENSION_WEIGHTS: dict[Dimension, float] = {
    Dimension.ENGINEERING_FUNDAMENTALS: 1.0,
    Dimension.PROBLEM_SOLVING: 1.0,
    Dimension.AI_FLUENCY: 1.2,
    Dimension.AGENTIC_ENGINEERING: 1.3,
    Dimension.PRACTICAL_REASONING: 1.0,
    Dimension.COMMUNICATION: 0.8,
}

# Score assigned to a dimension with no collected evidence (honest baseline).
_NO_EVIDENCE_SCORE = 35


class AssessmentEngine:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    # --- Lifecycle ---
    async def start(self, profile: CandidateProfile) -> Question:
        """Create an assessment and return the first question (caller persists)."""
        # Implemented in the service layer that owns the store; this helper is
        # kept for clarity. The orchestration lives in `start_assessment`.
        raise NotImplementedError

    async def first_question(self, profile: CandidateProfile) -> Question:
        context = profile.context_for_assessment()
        question = await self._generate_question(context, [], [])
        question.sequence = 0
        return question

    async def next_question(self, state: AssessmentState) -> Question | None:
        """Return the next question, or None if the assessment should complete."""
        if self._should_stop(state):
            return None
        context = state.profile_snapshot or {}
        prior = [self._question_summary(q) for q in state.questions]
        evidence_summary = self._evidence_summary(state)
        question = await self._generate_question(context, evidence_summary, prior)
        question.sequence = state.answered_count()
        return question

    # --- Response handling ---
    async def record_response(
        self, state: AssessmentState, question: Question, response: Response
    ) -> AssessmentState:
        if state.status not in (AssessmentStatus.CREATED, AssessmentStatus.IN_PROGRESS):
            raise AssessmentStateError("This assessment is not in progress.")
        if state.current_question_id != question.id:
            raise AssessmentStateError("The response does not match the current question.")

        evaluation = await evaluator.evaluate(question, response, _profile_from_snapshot(state))

        # Persist raw response + normalized evaluation separately. The question
        # is retained in history (used for adaptive selection and the report);
        # only the active pointer is cleared.
        state.responses.append(response)
        state.evaluations.append(evaluation)
        state.dimension_evidence_for(question.dimension).add(evaluation)
        state.current_question_id = None
        state.ensure_dimension_evidence_populated()
        state.touch()
        return state

    # --- Stopping / scoring (deterministic, code-owned) ---
    def _should_stop(self, state: AssessmentState) -> bool:
        settings = self._settings
        answered = state.answered_count()
        if answered >= settings.assessment_max_questions:
            return True
        if answered < settings.assessment_min_questions:
            return False
        # All dimensions covered with adequate confidence and no open requests.
        all_covered = all(
            state.dimension_evidence_for(d).coverage
            >= settings.assessment_evidence_target_per_dimension
            for d in Dimension
        )
        if not all_covered:
            return False
        recent = state.evaluations[-3:]
        avg_conf = sum(e.confidence for e in recent) / len(recent) if recent else 0.0
        any_more_needed = any(e.more_evidence_needed for e in recent)
        return avg_conf >= settings.min_confidence_to_stop and not any_more_needed

    def score_dimension(self, state: AssessmentState, dimension: Dimension) -> int:
        de = state.dimension_evidence_for(dimension)
        if de.coverage == 0:
            return _NO_EVIDENCE_SCORE
        return de.aggregate_score()

    def overall_score(self, state: AssessmentState) -> int:
        total_w = 0.0
        total_s = 0.0
        for d in Dimension:
            w = _DIMENSION_WEIGHTS[d]
            total_w += w
            total_s += self.score_dimension(state, d) * w
        return round(total_s / total_w) if total_w else 0

    def classify(self, score: int) -> ReadinessClassification:
        s = self._settings
        if score >= s.threshold_ready:
            return ReadinessClassification.READY
        if score >= s.threshold_targeted:
            return ReadinessClassification.DEVELOPING
        if score >= s.threshold_structured:
            return ReadinessClassification.EMERGING
        return ReadinessClassification.FOUNDATIONAL

    def pathway_for(self, score: int) -> Pathway:
        s = self._settings
        if score >= s.threshold_ready:
            return Pathway.READY
        if score >= s.threshold_targeted:
            return Pathway.TARGETED
        if score >= s.threshold_structured:
            return Pathway.STRUCTURED
        return Pathway.FOUNDATION

    # --- Internal helpers ---
    async def _generate_question(
        self,
        candidate_context: dict[str, Any],
        evidence_summary: dict[str, Any],
        prior_questions: list[dict[str, Any]],
    ) -> Question:
        dimensions = [d.value for d in Dimension]
        # Real Gemini only — no deterministic fallback. Errors propagate to the
        # caller as an application-level GeminiError.
        generated = await gemini_service.generate_question(
            candidate_context, evidence_summary, prior_questions, dimensions
        )

        return Question(
            dimension=generated.dimension,
            format=generated.format,
            prompt=generated.prompt,
            context=generated.context,
            options=[QuestionOption(id=o.id, text=o.text) for o in generated.options],
            assessment_objective=generated.assessment_objective,
            evaluation_criteria=generated.evaluation_criteria,
        )

    def _question_summary(self, q: Question) -> dict[str, Any]:
        return {
            "dimension": q.dimension.value,
            "format": q.format.value,
            "prompt": q.prompt,
        }

    def _evidence_summary(self, state: AssessmentState) -> dict[str, Any]:
        return {
            d.value: {
                "coverage": state.dimension_evidence_for(d).coverage,
                "score": self.score_dimension(state, d),
                "strengths": state.dimension_evidence_for(d).top_strengths(2),
                "gaps": state.dimension_evidence_for(d).top_gaps(2),
            }
            for d in Dimension
        }


def _profile_from_snapshot(state: AssessmentState) -> CandidateProfile:
    snap = state.profile_snapshot or {}
    # Minimal profile for evaluation context; full object not required.
    return CandidateProfile(
        user_id=state.user_id,
        **{k: v for k, v in snap.items() if k in CandidateProfile.model_fields and k != "user_id"},
    )


assessment_engine = AssessmentEngine()
