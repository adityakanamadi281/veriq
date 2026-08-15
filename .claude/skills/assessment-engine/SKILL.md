---
name: assessment-engine
description: Build and maintain AURA's adaptive AI assessment engine, including candidate context, question selection, evidence evaluation, scoring, completion, results, and recommendations.
---

# Assessment Engine Skill

## Purpose

Implement an evidence-led adaptive assessment rather than a static quiz.

## Core state

An assessment should have an explicit lifecycle such as:

`created → in_progress → completing → completed | failed`

Persist all state needed to resume.

## Candidate context

Candidate context can include:
- education
- experience
- target role
- technical skills
- projects
- AI/coding tools
- CV/background
- professional links

## Evidence model

For every evaluated response capture:
- dimension
- evidence statements
- capability signals
- strengths
- gaps
- confidence
- evaluation rationale
- question relevance
- whether more evidence is needed

Keep raw candidate responses separate from normalized evaluations.

## Adaptive selection

Select the next question using:
- target role relevance
- dimension coverage
- evidence uncertainty
- missing evidence
- prior responses
- candidate background
- redundancy avoidance

Prefer high-information questions that test concrete behavior, implementation decisions, debugging, reasoning, or applied AI work.

## Question formats

Support:
- written response
- voice response where implemented
- multiple choice
- scenario
- code review
- debugging
- practical reasoning
- agent instruction improvement

## Evaluation dimensions

1. Engineering Fundamentals
2. Problem Solving
3. AI Fluency
4. Agentic Engineering
5. Practical Reasoning
6. Communication

## Stopping

Do not let Gemini arbitrarily mutate application state.

The backend should decide whether sufficient evidence exists using deterministic thresholds/configuration over validated evaluation outputs.

## Final result

Generate:
- overall readiness score
- dimension results
- strengths
- capability gaps
- readiness classification
- personalized summary
- recommended pathway
- evidence

Pathways:
- Ready
- Targeted Capability Development
- Structured Capability Development
- Foundation Development

## Quality rules

Do not:
- fabricate candidate facts;
- reward verbosity alone;
- score based on protected or irrelevant personal characteristics;
- use generic career advice;
- expose hidden prompts;
- expose internal assessment logic to candidates.

Every important finding should be traceable to assessment evidence.
