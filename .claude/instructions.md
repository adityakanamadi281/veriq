# VERIQ — Claude Code Instructions

You are the primary implementation agent for `veriq`, a candidate-facing AI readiness assessment system.

## 1. Authority

Use the supplied hackathon PDFs as the product source of truth:
- Sprint 1 Assessment Engine
- Sprint 2 Candidate Application & Integration
- Candidate Application UI & Experience Brief
- Hackathon Developer Setup Guide

The extracted source is in `docs/source-material-extracted.md`.

Preserve the source terminology and intent. Do not silently add architecture that conflicts with the briefs.

## 2. Product goal

Build AURA, a premium AI assessment experience that understands a candidate from profile/CV context, runs an adaptive assessment, evaluates evidence, produces a readiness result, and recommends the next capability pathway.

The experience should resemble the quality and interaction model of modern AI-native assessments, but must remain an original implementation.

## 3. Non-negotiable architecture

React frontend → FastAPI backend → Supabase Auth/Storage/Postgres → Gemini → FastAPI → React.

The frontend must never call Gemini directly.

The backend owns:
- assessment state
- question selection
- scoring
- readiness classification
- recommendation rules
- Gemini prompts
- secrets
- persistence
- deterministic calculations

Use Gemini for:
- language understanding
- reasoning
- resume extraction
- evidence extraction
- qualitative response evaluation
- adaptive question generation
- classification support
- report generation

Use normal code for:
- validation
- arithmetic
- persistence
- permissions
- state transitions
- stopping criteria
- idempotency

## 4. Resume parsing

When a candidate uploads a PDF:
1. Store the private object in Supabase Storage.
2. Extract text with `pypdf`.
3. Send the text to Gemini.
4. Request structured JSON matching Pydantic models.
5. Validate the response.
6. Persist normalized candidate context.
7. Show extracted fields to the candidate for confirmation/editing.
8. Never fabricate missing facts.

## 5. Assessment engine

The assessment must be adaptive.

Dimensions:
- Engineering Fundamentals
- Problem Solving
- AI Fluency
- Agentic Engineering
- Practical Reasoning
- Communication

For each response:
1. persist raw response;
2. evaluate against explicit criteria;
3. extract evidence;
4. update dimension evidence;
5. choose the next highest-value evidence target;
6. either ask the next question or finish.

Do not ask a fixed questionnaire if the existing evidence makes a question redundant.

Avoid fake precision. Scores should be explainable and tied to evidence.

## 6. Structured AI output

Prefer typed structured outputs validated by Pydantic. Every Gemini call used in core assessment logic must have:
- a clearly defined input contract;
- a clearly defined output schema;
- validation;
- safe fallback/error handling;
- logging without secrets or sensitive raw data where inappropriate.

## 7. Idempotency and reliability

Response submission must be safe against duplicate requests. Never create two assessment turns for one logical submission.

Persist state before returning the next question.

Refreshing the browser must not lose an assessment.

## 8. UX

One question per screen.

Professional processing labels:
- Evaluating response
- Preparing next question
- Preparing your assessment

Avoid:
- AI is thinking...
- gamification
- fake progress
- unnecessary dashboards
- decorative AI branding

Results should answer:
1. Where do I stand?
2. Why?
3. What should I do next?

## 9. Authentication/security

Use Supabase Auth email/password.

Never:
- commit API keys;
- hardcode credentials;
- expose service-role credentials in React;
- expose Gemini credentials in the browser;
- make the repository public;
- use real customer data.

Keep `.env` out of git.

## 10. Development discipline

Use `uv` for Python dependency management.

Prefer small, testable modules.

Do not introduce:
- LangChain
- Pinecone
- ChromaDB
- AWS
- Kubernetes
- microservices
- message queues
- another database

unless a concrete requirement appears that cannot reasonably be met with the current stack.

## 11. Implementation order

1. Scaffold monorepo.
2. Configure uv/pyproject.toml.
3. Configure Supabase Auth/DB/Storage.
4. Implement FastAPI health and auth middleware.
5. Implement profile CRUD.
6. Implement resume upload/text extraction/Gemini parsing.
7. Implement assessment schema and persistence.
8. Implement Gemini assessment service.
9. Implement adaptive assessment loop.
10. Implement results/report/recommendation.
11. Build React auth/profile/assessment/results screens.
12. Integrate frontend API service layer.
13. Add tests.
14. Run full end-to-end validation.
15. Update README.

Always get one complete vertical workflow working before polishing secondary features.

## 12. Definition of done

A new user can:
Sign up → Sign in → Upload CV → Review profile → Start assessment → Answer adaptive questions → Complete assessment → See readiness result → Read personalized report → See recommended pathway.

No manual database edits. No developer-only shortcuts. No frontend Gemini calls.

