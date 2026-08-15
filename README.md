# VERIQ — AI Readiness Assessment

A premium, candidate-facing assessment that understands you from your profile, runs an
**adaptive, evidence-led** assessment powered by **Google Gemini**, evaluates your
responses, and produces an evidence-based readiness result with a personalized
report and a recommended capability pathway.

> Sign up → Build profile → Upload CV → Start assessment → Answer adaptive
> questions → Complete → Readiness result → Personalized report → Recommended
> pathway.

## Architecture

```
React → Supabase Auth → JWT → FastAPI → Supabase Postgres/Storage → Gemini SDK → Assessment Engine → FastAPI → React
```

- **React** — candidate experience. Uses only the Supabase **anon/publishable** key.
- **Supabase** — email/password auth, PostgreSQL persistence, private resume storage.
  RLS enforces the `auth.uid()` ownership boundary.
- **FastAPI** — business logic, assessment state, authorization, resume processing,
  deterministic scoring/state, report generation. Verifies the Supabase JWT.
- **Gemini** (`google-genai`, Interactions API) — resume understanding, structured
  extraction, adaptive question generation, evidence extraction, qualitative response
  evaluation, report narrative. Called **server-side only**.

The frontend **never** calls Gemini and **never** sees the service-role key or
`GEMINI_API_KEY`. There are **no local/deterministic fallbacks** in production:
real Gemini and real Supabase are required.

### Gemini vs. deterministic code

| Gemini (reasoning/language) | Deterministic code |
| --- | --- |
| resume extraction, question generation, response evaluation, report narrative | validation, scoring, classification, pathway selection, stopping rules, idempotency, state transitions, persistence, auth |

Gemini never mutates assessment state. Every Gemini response is parsed and
validated by Pydantic before it touches state. Every important finding is
traceable to persisted evidence.

## Project structure

```
veriq/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + lifespan + health
│   │   ├── core/                   # config, supabase client, security (JWT), errors, deps
│   │   ├── models/                 # domain models (Pydantic)
│   │   ├── schemas/                # API request/response DTOs
│   │   ├── services/               # gemini (Interactions API), resume_parser, engine, evaluator, report, orchestration
│   │   ├── repositories/           # Store protocol + SupabaseStore (normalized tables)
│   │   └── api/v1/                 # profile, resumes, assessments, reports routes
│   └── tests/                      # engine + API tests (mocked Gemini + fake store)
├── frontend/
│   ├── src/
│   │   ├── components/ui/          # shadcn-style primitives
│   │   ├── components/layout/      # app shell, page container
│   │   ├── features/               # landing, auth, home, profile, assessment, results, report
│   │   ├── context/                # Supabase auth context
│   │   ├── lib/                    # api client, env, supabase, utils, classification
│   │   └── types/                  # API types
│   └── package.json
├── supabase/migrations/0001_init.sql   # normalized tables + RLS + private storage bucket
└── pyproject.toml
```

## Requirements

- Python 3.12+ and [`uv`](https://docs.astral.sh/uv/)
- Node 20+ and npm
- A Supabase project (URL + anon key + service-role key)
- A Google Gemini API key

## Setup

### 1. Backend

```bash
uv sync
```

Create `.env` (see `.env.example`):

```env
GEMINI_API_KEY=...              # required — real Gemini, no fallback
GEMINI_MODEL=gemini-2.5-flash

SUPABASE_URL=...                # required
SUPABASE_ANON_KEY=...           # browser-safe
SUPABASE_SERVICE_ROLE_KEY=...   # server-only, never exposed to React

DATABASE_URL=...

APP_ENV=development
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

Run the API:

```bash
uv run uvicorn app.main:app --reload --port 8000 
```

Health: `GET http://localhost:8000/health` → reports `gemini_configured` and
`supabase_configured`.

### 2. Database

Run the migration against your Supabase Postgres:

```bash
psql "$DATABASE_URL" -f supabase/migrations/0001_init.sql
```

Creates `profiles`, `assessments`, `assessment_questions`,
`assessment_responses`, `response_evaluations`, `assessment_results`,
`assessment_reports`, `audit_events`, the private `candidate-resumes` storage
bucket, and RLS policies. The `candidate-resumes` bucket must exist for resume
uploads (the migration creates it).

### 3. Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env` (see `frontend/.env.example`) — **browser-safe values only**:

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=...           # same Supabase URL as backend
VITE_SUPABASE_ANON_KEY=...      # same anon key as backend (browser-safe)
```

Run:

```bash
npm run dev
```

Open http://localhost:5173

## Gemini integration

The service uses the Google GenAI **Interactions API** exactly as specified:

```python
from google import genai
client = genai.Client(api_key=settings.gemini_api_key)
interaction = client.interactions.create(model=settings.gemini_model, input=prompt)
text = interaction.output_text
```

Each use case (resume extraction, question generation, response evaluation,
report synthesis) has its own prompt and Pydantic schema. The model is asked to
return strict JSON; `output_text` is parsed and validated before use. The
schemas coerce the model's realistic structured forms (e.g. `education` as an
array, `target_dimension` instead of `dimension`) into the flat domain types, so
validation is robust without rejecting valid intelligence.

## Tests

```bash
uv run pytest
```

Unit tests mock Gemini (`FakeGemini` injected via `gemini_service._generate_fn`) and
use an in-memory `FakeStore`, per the rule "Mock Gemini in unit tests." They do
**not** require a real Gemini key or database. Covers scoring thresholds,
classification, pathway mapping, stopping rules, adaptive coverage, idempotency,
result grounding, and the full HTTP journey.

## API surface

All under `/api/v1`, Supabase-JWT authenticated (`Authorization: Bearer <token>`):

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | service health + config status |
| `GET`/`PUT` | `/profile` | retrieve / update candidate profile |
| `POST` | `/resume` | upload PDF → store in Supabase Storage → Gemini parse → review |
| `POST` | `/resume/parse` | re-parse a stored resume |
| `GET` | `/assessments` | list assessment history |
| `POST` | `/assessments` | start an assessment → first Gemini question |
| `GET` | `/assessments/{id}` | current state (resumable) |
| `POST` | `/assessments/{id}/responses` | submit a response (idempotent) → next question or completion |
| `GET` | `/assessments/{id}/result` | readiness result |
| `GET` | `/assessments/{id}/report` | document-like report |
| `GET` | `/reports/{id}` | report alias |

Response submission is idempotent (`submission_key`); state is saved before the
next question is returned, so a browser refresh never loses an assessment.
Ownership is always verified via the JWT-derived `user_id`, never the request body.

## Assessment design

Six capability dimensions: **Engineering Fundamentals, Problem Solving, AI Fluency,
Agentic Engineering, Practical Reasoning, Communication.**

The loop: understand candidate context → Gemini selects the highest-value
evidence target → ask one question → Gemini evaluates against explicit
criteria → extract evidence → update dimension evidence → deterministic code
decides whether enough evidence exists → repeat or complete.

Readiness classifications and pathways (deterministic, threshold-based):

| Score | Classification | Pathway |
| --- | --- | --- |
| ≥ 75 | Ready | Ready |
| ≥ 60 | Developing | Targeted Capability Development |
| ≥ 45 | Emerging | Structured Capability Development |
| < 45 | Foundational | Foundation Development |

## UX

One question per screen. Restrained progress (a count, not a fake percentage).
Professional processing labels — “Evaluating response”, “Preparing next
question”, “Preparing your assessment”. No gamification, gradients, or
decorative AI branding. Results answer **Where do I stand? · Why? · What should I
do next?** The report reads like a clean document, not a dashboard.

## Security

- `GEMINI_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `DATABASE_URL` are server-side
  only and never reach the browser (React uses only the Supabase anon key).
- `.env` and `frontend/.env` are gitignored. Keep the repository private.
- RLS enabled on every table; ownership enforced via `auth.uid()`.
- Resume Storage is private; one candidate cannot access another's resume.
- FastAPI verifies the Supabase JWT and never trusts a frontend-supplied `user_id`.
- API errors never leak credentials; logs never print API keys.

## Run locally

```bash
# 1. database
psql "$DATABASE_URL" -f supabase/migrations/0001_init.sql

# 2. backend
uv run uvicorn backend.app.main:app --reload --port 8000

# 3. frontend
cd frontend && npm install && npm run dev
```

Then open http://localhost:5173, sign up with a real email/password (Supabase
Auth), build your profile, upload a CV, and run the assessment. Gemini generates
adaptive questions and evaluates your responses in real time.
