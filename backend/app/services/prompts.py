"""Prompt templates for each Gemini use case.

Kept separate from the service so the contracts and wording are reviewable.
Prompts instruct the model to preserve facts, avoid fabrication, and stay
within the supplied evidence. No candidate secrets beyond what is needed for
the task are included.
"""

from __future__ import annotations

import json
from typing import Any

SYSTEM = (
    "You are AURA, an expert engineering assessor. You are precise, fair, and "
    "evidence-led. You never fabricate facts. You never reward verbosity alone. "
    "You never score based on personal characteristics. You return strictly "
    "valid JSON matching the requested schema."
)

RESUME_INSTRUCTION = """\
Extract structured candidate facts from the resume text below.

Rules:
- Preserve facts only. Do not infer experience or skills that are not stated.
- Use null for any field that is not present. Use empty arrays for missing lists.
- Normalize skill names conservatively (e.g. "React.js" -> "React").
- "background" is a concise 2-3 sentence professional summary in your own words.
- Never invent GitHub/LinkedIn URLs.

Return STRICT JSON with EXACTLY these keys and types (no other keys):
{{
  "name": string | null,
  "education": string | null,
  "graduation_year": integer | null,
  "experience": string | null,
  "target_role": string | null,
  "technical_skills": array of strings,
  "projects": array of {{"name": string, "description": string, "technologies": array of strings, "url": string|null}},
  "ai_tools": array of strings,
  "github": string | null,
  "linkedin": string | null,
  "professional_links": array of strings,
  "background": string | null
}}

Example: {{"name":"Jane Doe","education":"B.Tech, CS, IIT Bombay, 2024","graduation_year":2024,"experience":"2 years as a backend engineer","target_role":"AI Engineer","technical_skills":["Python","FastAPI","PostgreSQL"],"projects":[{{"name":"VeriQ","description":"AI assessment platform","technologies":["React","FastAPI"],"url":null}}],"ai_tools":["Copilot","Cursor"],"github":"https://github.com/jane","linkedin":"https://linkedin.com/in/jane","professional_links":[],"background":"Jane is a backend engineer targeting AI-first roles."}}

Resume text:
<<<
{resume_text}
>>>
"""

QUESTION_INSTRUCTION = """\
Generate ONE high-information assessment question for the candidate.
Selection priority: target the single highest-value evidence gap given the
candidate context, dimensions already covered, evidence collected, and prior
questions. Prefer questions that test concrete behaviour, implementation
decisions, debugging, reasoning, or applied AI work. Avoid questions redundant
with evidence already collected.

Candidate context (JSON):
{candidate_context}

Dimensions (pick exactly one as the target):
{dimensions}

Question format must be one of: written, scenario, multiple_choice, code_review,
debugging, practical_reasoning, agent_instruction. Use multiple_choice only when
a discrete decision is the natural probe; include 3-4 options with stable ids.
For code_review/debugging, put any code or scenario in "context".

Evidence already collected per dimension (JSON):
{evidence_summary}

Prior questions asked (JSON):
{prior_questions}

Return STRICT JSON with EXACTLY these keys (no other keys):
{{
  "dimension": one of the dimensions listed above,
  "format": "written" | "scenario" | "multiple_choice" | "code_review" | "debugging" | "practical_reasoning" | "agent_instruction",
  "prompt": string (the question to ask),
  "context": string | null,
  "options": array of {{"id": string, "text": string}} (empty array unless format is multiple_choice),
  "assessment_objective": string (one line),
  "evaluation_criteria": array of 2-4 strings,
  "more_evidence_needed_hint": boolean
}}
"""

EVALUATION_INSTRUCTION = """\
Evaluate the candidate's response against the question's explicit criteria.
Be evidence-led and specific. Do not reward length alone.

Question:
{question_prompt}

Target dimension: {dimension}
Evaluation criteria (JSON): {criteria}

Candidate context (JSON): {candidate_context}

Candidate response:
<<<
{response_text}
>>>

Return STRICT JSON with EXACTLY these keys (no other keys):
{{
  "evidence": array of {{"statement": string, "supports": string}},
  "strengths": array of strings,
  "gaps": array of strings,
  "dimension_score": integer 0-100,
  "confidence": number 0-1,
  "rationale": string,
  "more_evidence_needed": boolean
}}
"""

SYNTHESIS_INSTRUCTION = """\
Write the narrative for the candidate's readiness report. You are GIVEN the
deterministic scores, classification, pathway, and the evidence. Do NOT invent
scores, new evidence, or facts not present below. Write in second person,
calm and professional. Be specific and tie every claim to the evidence.

Overall readiness score: {overall_score}/100
Classification: {classification}
Recommended pathway: {pathway}

Dimension results (JSON):
{dimension_results}

Key strengths (JSON): {key_strengths}
Capability gaps (JSON): {capability_gaps}

Return STRICT JSON with EXACTLY these keys (no other keys):
{{
  "overall_summary": string (2-3 sentences),
  "dimension_summaries": object mapping each dimension name to one sentence,
  "recommendation_rationale": string,
  "next_action": string (a concrete next step),
  "learning_priorities": array of 3-5 strings
}}
"""


def _compact(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)


def resume_prompt(resume_text: str) -> str:
    return RESUME_INSTRUCTION.format(resume_text=resume_text[:12000])


def question_prompt(
    candidate_context: dict[str, Any],
    evidence_summary: dict[str, Any],
    prior_questions: list[dict[str, Any]],
    dimensions: list[str],
) -> str:
    return QUESTION_INSTRUCTION.format(
        candidate_context=_compact(candidate_context),
        dimensions=", ".join(dimensions),
        evidence_summary=_compact(evidence_summary),
        prior_questions=_compact(prior_questions),
    )


def evaluation_prompt(
    question_prompt_text: str,
    dimension: str,
    criteria: list[str],
    candidate_context: dict[str, Any],
    response_text: str,
) -> str:
    return EVALUATION_INSTRUCTION.format(
        question_prompt=question_prompt_text,
        dimension=dimension,
        criteria=_compact(criteria),
        candidate_context=_compact(candidate_context),
        response_text=response_text[:8000],
    )


def synthesis_prompt(
    overall_score: int,
    classification: str,
    pathway: str,
    dimension_results: list[dict[str, Any]],
    key_strengths: list[str],
    capability_gaps: list[str],
) -> str:
    return SYNTHESIS_INSTRUCTION.format(
        overall_score=overall_score,
        classification=classification,
        pathway=pathway,
        dimension_results=_compact(dimension_results),
        key_strengths=_compact(key_strengths),
        capability_gaps=_compact(capability_gaps),
    )
