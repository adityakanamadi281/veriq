"""Report service — assembles the readiness result and the report.

Scoring, classification, and pathway are deterministic (computed by the
engine). Gemini is asked only for the human-readable narrative, which is
grounded in the supplied evidence and may not invent facts or scores.
"""

from __future__ import annotations

import logging

from ..models.assessment import AssessmentState
from ..models.enums import Dimension
from ..models.result import (
    AssessmentReport,
    DimensionResult,
    ReadinessResult,
    Recommendation,
)
from .assessment_engine import assessment_engine
from .gemini_service import gemini_service

logger = logging.getLogger("aura.report")


class ReportService:
    async def build_result(self, state: AssessmentState) -> ReadinessResult:
        overall = assessment_engine.overall_score(state)
        classification = assessment_engine.classify(overall)
        pathway = assessment_engine.pathway_for(overall)

        dimension_results: list[DimensionResult] = []
        for d in Dimension:
            de = state.dimension_evidence_for(d)
            score = assessment_engine.score_dimension(state, d)
            dimension_results.append(
                DimensionResult(
                    dimension=d,
                    score=score,
                    classification=assessment_engine.classify(score),
                    strengths=de.top_strengths(3),
                    gaps=de.top_gaps(3),
                    evidence=de.evidence,
                    summary="",
                )
            )

        key_strengths = self._top_findings(dimension_results, attr="strengths", k=4)
        capability_gaps = self._top_findings(dimension_results, attr="gaps", k=4)

        # Narrative from Gemini, grounded in the deterministic values above.
        try:
            synthesis = await gemini_service.synthesize_result(
                overall_score=overall,
                classification=classification.value,
                pathway=pathway.value,
                dimension_results=[dr.model_dump(mode="json") for dr in dimension_results],
                key_strengths=key_strengths,
                capability_gaps=capability_gaps,
            )
        except Exception:  # noqa: BLE001
            logger.warning("Synthesis failed; using deterministic narrative.")
            synthesis = None

        for dr in dimension_results:
            dr.summary = (
                synthesis.dimension_summaries.get(dr.dimension.value) if synthesis else ""
            ) or (f"Scored {dr.score}/100 in {dr.dimension.value}.")

        capability_areas = [dr.dimension.value for dr in dimension_results if dr.gaps]
        recommendation = Recommendation(
            pathway=pathway,
            rationale=(
                synthesis.recommendation_rationale
                if synthesis
                else f"Selected based on an overall readiness of {overall}/100."
            ),
            capability_areas=capability_areas,
            next_action=(
                synthesis.next_action
                if synthesis
                else "Focus on the highest-priority capability gap."
            ),
            learning_priorities=(synthesis.learning_priorities if synthesis else capability_gaps),
        )

        all_evidence = [e for dr in dimension_results for e in dr.evidence]

        return ReadinessResult(
            overall_score=overall,
            classification=classification,
            dimension_results=dimension_results,
            key_strengths=key_strengths,
            capability_gaps=capability_gaps,
            summary=(
                synthesis.overall_summary
                if synthesis
                else f"You are at {overall}/100 readiness ({classification.value})."
            ),
            recommendation=recommendation,
            evidence=all_evidence,
        )

    async def build_report(
        self, state: AssessmentState, result: ReadinessResult
    ) -> AssessmentReport:
        return AssessmentReport(
            assessment_id=state.id,
            title="Your AURA Readiness Assessment",
            summary=result.summary,
            readiness={
                "overall_score": result.overall_score,
                "classification": result.classification.value,
                "dimensions": [dr.model_dump(mode="json") for dr in result.dimension_results],
            },
            strengths=result.key_strengths,
            development_areas=result.capability_gaps,
            evidence=result.evidence,
            recommended_pathway=result.recommendation,
            learning_priorities=result.recommendation.learning_priorities,
        )

    def _top_findings(
        self, dimension_results: list[DimensionResult], *, attr: str, k: int
    ) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        # Rank dimensions by gap size for gaps, by score for strengths.
        if attr == "strengths":
            ordered = sorted(dimension_results, key=lambda d: d.score, reverse=True)
        else:
            ordered = sorted(dimension_results, key=lambda d: d.score)
        for dr in ordered:
            for item in getattr(dr, attr):
                if item and item not in seen:
                    seen.add(item)
                    out.append(item)
                if len(out) >= k:
                    return out
        return out


report_service = ReportService()
