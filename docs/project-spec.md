# HACKATHON-ADITYA — AI Assessment Framework

## Product name
**AURA — AI Readiness Assessment**

Repository: `veriq` 

AURA is a premium candidate-facing AI assessment product inspired by the workflow of modern AI-native hiring assessments. It is not a clone of any proprietary product. Its core workflow is:

**Sign up → Profile → Resume parsing → Assessment → Adaptive questions → Evidence evaluation → Readiness score → Report → Recommended pathway → History**

## Source-of-truth requirements
The four supplied hackathon PDFs are authoritative for product scope, terminology, assessment dimensions, UX direction, architecture constraints, and engineering principles. Do not silently replace their requirements with unrelated architecture.

## Core architecture

React → FastAPI → Supabase Auth/Storage/Postgres → Gemini assessment engine → FastAPI → React

The browser must never call Gemini directly. Gemini prompts and API credentials stay server-side. Persistent assessment state, candidate profile, responses, evaluations, scores, and final results live in Supabase/Postgres.

## Assessment dimensions

- Engineering Fundamentals
- Problem Solving
- AI Fluency
- Agentic Engineering
- Practical Reasoning
- Communication

The engine should collect evidence rather than merely produce a generic personality or career score.

## Adaptive loop

1. Understand candidate context.
2. Select the highest-value next capability/evidence target.
3. Ask one question.
4. Capture text, and optionally voice where implemented.
5. Evaluate the response against explicit criteria.
6. Store evidence and evaluation.
7. Update dimension evidence.
8. Decide whether another question is required.
9. Continue until sufficient evidence exists.
10. Produce a structured readiness result.

Deterministic application code owns state transitions, validation, persistence, arithmetic, permissions, and stopping-rule mechanics. Gemini owns language understanding, evidence extraction, question generation, qualitative evaluation, classification rationale, and report generation.

## Candidate resume parsing

Upload CV/PDF to Supabase Storage. The backend:
- validates file type/size;
- extracts text with `pypdf`;
- sends the extracted resume text to Gemini;
- requests strict structured JSON;
- validates the result with Pydantic;
- stores normalized candidate context;
- lets the candidate review/edit extracted fields before assessment.

Extract, where available:
- name
- education
- graduation year
- experience
- target role
- technical skills
- projects
- AI/coding tools
- GitHub
- LinkedIn
- professional links
- concise professional background

Never invent missing resume facts. Use null/empty values for absent information.

## Results

Return:
- overall readiness score
- dimension-level scores/findings
- key strengths
- capability gaps
- readiness classification
- personalized assessment summary
- recommended pathway
- evidence supporting important findings

Pathways:
- Ready
- Targeted Capability Development
- Structured Capability Development
- Foundation Development

## UX direction

Premium, minimal, calm, professional, intelligent:
- warm white/off-white background
- near-black text
- one restrained dark accent
- modern sans-serif
- generous whitespace
- subtle borders
- restrained cards
- responsive layout
- one obvious primary action per screen
- one assessment question at a time
- clear processing states such as “Evaluating response” and “Preparing next question”

Avoid gradients, gamification, excessive color, cartoon AI imagery, oversized shadows, clutter, and unnecessary dashboards.

## Authentication

Use Supabase Auth with email/password:
- Sign up
- Sign in
- Sign out
- protected candidate routes
- backend JWT verification
- profile ownership enforced by authenticated user ID

## Supabase storage

Suggested buckets:
- `candidate-resumes`
- `assessment-exports` (optional)

Keep resume objects private. Store only object paths in Postgres, not public URLs.

## Suggested database tables

- profiles
- resumes
- assessments
- assessment_questions
- assessment_responses
- response_evaluations
- assessment_results
- assessment_history (or derive from assessments)
- audit_events

Use `user_id` as the ownership boundary. Add timestamps and foreign keys. Enable Row Level Security in Supabase.

## API surface

Auth is handled by Supabase client/Auth. FastAPI owns application logic.

Candidate:
- `GET /api/v1/profile`
- `PUT /api/v1/profile`
- `POST /api/v1/resume`
- `POST /api/v1/resume/parse`
- `GET /api/v1/assessments`
- `POST /api/v1/assessments`
- `GET /api/v1/assessments/{assessment_id}`
- `POST /api/v1/assessments/{assessment_id}/responses`
- `GET /api/v1/assessments/{assessment_id}/result`
- `GET /api/v1/assessments/{assessment_id}/report`

Health:
- `GET /health`

## Python environment

Use `uv` and `pyproject.toml`. Do not introduce LangChain, Pinecone, ChromaDB, AWS, Kubernetes, microservices, queues, or multiple databases unless a later requirement genuinely requires them.

Suggested Python packages:
- fastapi
- uvicorn[standard]
- pydantic
- pydantic-settings
- supabase
- google-genai
- python-multipart
- pypdf
- httpx
- pytest

## Gemini SDK

Use the Google GenAI Python SDK and the Interactions API. The requested pattern is:

```python
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-2.5-flash",
    input="Explain how AI works in a few words",
)

print(interaction.output_text)
```

Keep model names configurable through environment variables. Do not hardcode API keys.

## Error handling

Explicitly handle:
- missing candidate information
- invalid input
- unsupported/oversized resume
- Gemini failures
- Supabase failures
- interrupted assessment state
- duplicate submissions
- loading states
- retryable failures

## Demonstration

The ideal demo is:
Candidate enters → Candidate is understood → Assessment adapts → Responses are evaluated → Readiness is determined → Result and recommendation are presented.

The product should work end-to-end without developer intervention or manual database changes.
