"""Response evaluator — turns a Gemini evaluation into a validated Evaluation.

Gemini produces the qualitative read; this layer maps it onto the domain model
and guards the value ranges. It never mutates assessment state.
"""

from __future__ import annotations

from ..models.assessment import Evaluation, EvidenceItem, Question, Response
from ..models.profile import CandidateProfile
from .gemini_service import gemini_service


class Evaluator:
    async def evaluate(
        self,
        question: Question,
        response: Response,
        profile: CandidateProfile,
    ) -> Evaluation:
        context = profile.context_for_assessment()
        output = await gemini_service.evaluate_response(
            question_prompt_text=question.prompt,
            dimension=question.dimension.value,
            criteria=question.evaluation_criteria,
            candidate_context=context,
            response_text=response.text,
        )
        return Evaluation(
            question_id=question.id,
            dimension=question.dimension,
            evidence=[EvidenceItem(**e.model_dump()) for e in output.evidence],
            strengths=output.strengths,
            gaps=output.gaps,
            dimension_score=output.dimension_score,
            confidence=output.confidence,
            rationale=output.rationale,
            more_evidence_needed=output.more_evidence_needed,
        )


evaluator = Evaluator()
