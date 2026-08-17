# VERIQ — System Plan & Guide

> Everything you need to understand the system, how the intelligence works, and
> exactly what to create in Supabase.

---

## 1. What is this system?

**VERIQ** (product name **veriq — AI Readiness Assessment**) is a premium,
candidate-facing application that measures how ready a person is for an
**AI-first engineering role**.

It does NOT give a generic personality or career score. Instead it runs a
**real, adaptive AI interview** powered by Google **Gemini**, collects
**evidence** of what the candidate actually knows and can do, and produces an
**evidence-based readiness result** with:

- an overall readiness score (0–100)
- a readiness classification (Ready / Developing / Emerging / Foundational)
- scores across 6 capability dimensions
- key strengths and capability gaps (each tied to real evidence)
- a personalized report (document-style, like a clean Notion page)
- a recommended next-step pathway

The candidate journey is:

```
Sign up → Build profile → Upload CV → Introduce yourself →
Answer adaptive questions (one at a time) → Complete →
Readiness result → Personalized report → Recommended pathway
```

---

## 2. How it works (architecture)

```
React  →  Supabase Auth  →  JWT  →  FastAPI  →  Supabase Postgres/Storage  →  Gemini SDK  →  Assessment Engine  →  FastAPI  →  React
```

### The four layers and their responsibilities

| Layer | Technology | Owns |
|---|---|---|
| **Candidate experience** | React + TypeScript + Tailwind (shadcn-style UI) | Screens, forms, input capture, session state, calm UX |
| **Auth + persistence + storage** | Supabase | Email/password auth, PostgreSQL data, private resume files, RLS ownership |
| **Business logic + security** | FastAPI (Python) | JWT verification, profile/resume/assessment APIs, assessment state, deterministic scoring, idempotency, authorization |
| **AI reasoning** | Google Gemini (`google-genai` Interactions API) | Resume understanding, question generation, response evaluation, report narrative |

### Hard rules that are enforced

- **React never calls Gemini.** All AI calls go through FastAPI.
- **React never sees secrets.** Only the Supabase **anon (publishable) key** is in the browser. `GEMINI_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, and `DATABASE_URL` are server-side only.
- **Postgres is the source of truth.** Profile, assessment, questions, responses, evaluations, results, and reports all persist in Supabase. A browser refresh never loses an assessment.
- **No local/deterministic fallbacks.** Real Gemini and real Supabase are required. (Unit tests mock both — see section 5.)

### Request flow example (submitting an answer)

```
React captures the answer
   ↓
React gets the Supabase session access token
   ↓
POST /api/v1/assessments/{id}/responses   (Authorization: Bearer <SUPABASE_JWT>)
   ↓
FastAPI verifies the JWT with Supabase → gets user_id
   ↓
FastAPI verifies the assessment belongs to this user_id
   ↓
FastAPI persists the raw response to Supabase (assessment_responses)
   ↓
FastAPI sends the question + response to Gemini for evaluation
   ↓
Gemini returns structured JSON (evidence, strengths, gaps, score, confidence)
   ↓
FastAPI validates it with Pydantic, persists to response_evaluations
   ↓
FastAPI (deterministic code) updates dimension evidence + decides stop/continue
   ↓
If continue: Gemini generates the next adaptive question → persist → return to React
If stop: build result + report → persist → return "completed"
```

---

## 3. How the intelligence works

This is the core. The intelligence is **Gemini**, used through the
**Interactions API** exactly like this:

```python
from google import genai

client = genai.Client(api_key=settings.gemini_api_key)
interaction = client.interactions.create(
    model=settings.gemini_model,   # gemini-2.5-flash
    input=prompt,
)
text = interaction.output_text
```

### What Gemini does vs. what normal code does

| Gemini (language/reasoning) | Deterministic code (reliable logic) |
|---|---|
| Resume extraction | Validation |
| Adaptive question generation | Scoring (weighted average) |
| Evidence extraction from responses | Readiness classification (thresholds) |
| Qualitative response evaluation | Pathway selection (thresholds) |
| Report narrative writing | Stopping rules |
| Classification rationale | State transitions, persistence, idempotency, auth |

**Gemini never mutates assessment state directly.** Gemini returns structured
JSON; FastAPI validates it with Pydantic and then deterministic code decides
what to do with it. This keeps the AI from arbitrarily changing state or
inventing facts.

### The six capability dimensions

1. Engineering Fundamentals
2. Problem Solving
3. AI Fluency
4. Agentic Engineering
5. Practical Reasoning
6. Communication

### The adaptive loop (evidence-led, not a fixed quiz)

```
1. Understand candidate context (profile + CV + self-introduction)
2. Gemini picks the single highest-value MISSING evidence target
   (which dimension has the biggest gap, given what we already know)
3. Ask ONE question
4. Candidate answers
5. Gemini evaluates the answer against explicit criteria:
   - extracts concrete evidence statements
   - identifies strengths
   - identifies gaps
   - gives a 0–100 capability signal for that dimension
   - gives a 0–1 confidence
   - says whether more evidence is needed
6. FastAPI validates + persists the evaluation
7. FastAPI updates the dimension evidence
8. Deterministic stopping rule decides: ask another question, or finish
9. On finish: deterministic scoring → classification → pathway → Gemini writes the narrative
```

### Why it’s "intelligent, not deterministic"

- **Questions are generated fresh by Gemini** based on the candidate’s background,
  target role, and previous answers. Two candidates get different questions.
  The same candidate on a different day may get different questions.
- **Evaluations are qualitative AI judgments**, not keyword matching. Gemini
  reads the answer and reasons about depth, correctness, and real experience.
- **Adaptation:** the next question targets the dimension with the most
  uncertainty or the biggest gap, so the assessment spends its questions where
  they’re most informative.

### Deterministic scoring (code-owned, explainable, no fake precision)

- Each dimension score = a recency-weighted average of that dimension’s
  evaluation signals. Dimensions with no evidence get an honest baseline (35),
  not a fake score.
- Overall score = a weighted average across all 6 dimensions (Agentic
  Engineering and AI Fluency weighted slightly higher for an AI-first role).
- Classification + pathway are pure thresholds:

| Overall score | Classification | Pathway |
|---|---|---|
| ≥ 75 | Ready | Ready |
| ≥ 60 | Developing | Targeted Capability Development |
| ≥ 45 | Emerging | Structured Capability Development |
| < 45 | Foundational | Foundation Development |

### Stopping rules (deterministic, code-owned)

The assessment stops when **any** of these is true:
- the candidate has answered the maximum number of questions (8), OR
- they’ve answered at least the minimum (4) AND every dimension has coverage
  AND recent confidence is high enough AND no evaluation says "more evidence needed".

This means Gemini can’t keep the candidate forever, and can’t stop too early.
Code owns this, not the model.

### Robust AI contracts (why validation doesn’t reject good answers)

Gemini’s `output_text` is free text. The prompts ask for strict JSON, but the
model sometimes returns slightly different shapes (e.g. `education` as an array
of objects, `target_dimension` instead of `dimension`, `null` for an options
list). The Pydantic schemas **coerce** these realistic forms into the flat
domain types and accept common key aliases — so valid intelligence is accepted,
while malformed output is still rejected. Every Gemini call has:

- a clearly defined input (the prompt)
- a clearly defined output schema (Pydantic)
- validation
- safe fallback to an application-level error (never a crash, never a leaked key)

---

## 4. What to do in Supabase (everything)

Supabase is responsible for **authentication, PostgreSQL persistence, and
private resume storage.** Here is exactly what to create.

### 4.1 Create a Supabase project

1. Go to https://supabase.com → New Project.
2. Pick a name, set a strong database password, choose a region close to you.
3. Wait for it to provision.

### 4.2 Get your four credentials

In the Supabase dashboard:

- **Project URL**: `Project Settings → API → Project URL`
- **anon (publishable) key**: `Project Settings → API → Project API keys → anon public`
- **service_role key**: `Project Settings → API → Project API keys → service_role` (secret — server only)
- **Database URL**: `Project Settings → Database → Connection string → URI`
  (looks like `postgresql://postgres.<ref>:<password>@<host>:5432/postgres`)

Put these in your backend `.env` (see `.env.example`):

```env
GEMINI_API_KEY=...                     # from Google AI Studio
GEMINI_MODEL=gemini-2.5-flash

SUPABASE_URL=https://<your-ref>.supabase.co
SUPABASE_ANON_KEY=<anon public key>
SUPABASE_SERVICE_ROLE_KEY=<service_role key>   # server only, never in React
DATABASE_URL=postgresql://postgres.<ref>:<password>@<host>:5432/postgres

APP_ENV=development
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

And put the **browser-safe** ones in `frontend/.env` (never the service-role key or Gemini key here):

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://<your-ref>.supabase.co
VITE_SUPABASE_ANON_KEY=<anon public key>
```

### 4.3 Configure Auth (email/password)

In `Authentication → Providers → Email`:
- Enable **Email** provider.
- For a local hackathon demo, you can **disable "Confirm email"** so signup
  logs you in immediately without checking an inbox. (For anything real, keep
  email confirmation on.)
- Set a strong password policy if you like.

That’s all auth config needed. The React app uses Supabase Auth for
signup/signin/signout; FastAPI verifies the JWT Supabase issues.

### 4.4 Create the database tables, RLS, and storage bucket

**Easiest path: run the migration SQL.**

Open `SQL Editor` in the Supabase dashboard, paste the entire contents of
`supabase/migrations/0001_init.sql`, and click **Run**. This creates
everything below in one go.

If you prefer to do it manually or want to understand what’s created, here’s
the full list:

#### Tables created

**1. `profiles`** — candidate application info, linked 1:1 to `auth.users`.
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | = `auth.users.id` (the user) |
| full_name | text | |
| education | text | |
| graduation_year | int | |
| experience | text | |
| target_role | text | e.g. "AI Engineer" |
| github_url | text | |
| linkedin_url | text | |
| resume_path | text | private Storage object path |
| resume_parsed | boolean | true after a CV is parsed |
| details | jsonb | technical_skills, projects, ai_tools, professional_links, background |
| created_at / updated_at | timestamptz | |

> Email/password are NOT stored here — they stay in Supabase Auth.

**2. `assessments`** — one per assessment run.
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| user_id | uuid, FK → auth.users | ownership |
| target_role | text | snapshot |
| status | text | created / in_progress / completing / completed / failed |
| current_question_id | uuid, nullable | the active question |
| introduction | text | candidate self-intro |
| profile_snapshot | jsonb | context captured at start |
| created_at / updated_at / completed_at | timestamptz | |

**3. `assessment_questions`** — the Gemini-generated questions.
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| assessment_id | uuid, FK → assessments | |
| question_number | int | sequence |
| dimension | text | one of the 6 dimensions |
| question | text | the prompt shown to the candidate |
| question_type | text | written / scenario / multiple_choice / code_review / debugging / practical_reasoning / agent_instruction |
| objective | text | internal assessment objective |
| evaluation_criteria | jsonb | array of strings |
| context | text | optional code/scenario block |
| options | jsonb | array of {id, text} for multiple choice |

**4. `assessment_responses`** — the candidate’s raw answers (persisted verbatim).
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | = question_id (one response per question) |
| assessment_id | uuid, FK → assessments | |
| question_id | uuid | |
| response_text | text | the answer |
| response_type | text | |
| selected_option_id | text | for multiple choice |
| duration_seconds | float | |
| submission_key | text | idempotency key (prevents duplicate submissions) |
| submitted_at | timestamptz | |

**5. `response_evaluations`** — Gemini’s normalized evaluation of each response.
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | = response_id |
| response_id | uuid | |
| assessment_id | uuid, FK → assessments | |
| dimension | text | |
| evidence | jsonb | array of {statement, supports} |
| strengths | jsonb | array of strings |
| gaps | jsonb | array of strings |
| capability_score | int | 0–100 signal for this dimension |
| confidence | float | 0–1 |
| needs_more_evidence | boolean | |
| rationale | text | |
| created_at | timestamptz | |

> Raw responses and normalized evaluations are kept **separate**, as required.

**6. `assessment_results`** — the final readiness result.
| Column | Type | Notes |
|---|---|---|
| id | uuid, PK | |
| assessment_id | uuid, FK → assessments, unique | |
| overall_score | int | 0–100 |
| readiness_classification | text | Ready / Developing / Emerging / Foundational |
| dimension_results | jsonb | per-dimension scores/strengths/gaps |
| strengths | jsonb | key strengths |
| capability_gaps | jsonb | capability gaps |
| personalized_summary | text | Gemini-written narrative |
| recommended_pathway | text | one of the 4 pathways |
| recommendation_reason | text | Gemini-written rationale |
| recommendation | jsonb | full recommendation object |
| evidence | jsonb | supporting evidence |
| created_at | timestamptz | |

**7. `assessment_reports`** — the document-like report.
| Column | Type | Notes |
|---|---|---|
| assessment_id | uuid, PK, FK → assessments | |
| report | jsonb | full report object |
| created_at | timestamptz | |

**8. `audit_events`** — lightweight traceability (optional).
| Column | Type |
|---|---|
| id | uuid, PK |
| user_id | uuid |
| assessment_id | uuid |
| event | text |
| metadata | jsonb |
| created_at | timestamptz |

#### Row Level Security (RLS) — ownership

RLS is **enabled on every table**. The rule is simple and consistent:
**a candidate can only ever touch rows where `user_id = auth.uid()`** (the
logged-in Supabase user).

- `profiles`: owned by `id = auth.uid()`.
- `assessments`: owned by `user_id = auth.uid()`.
- `assessment_questions / _responses / response_evaluations / assessment_results / assessment_reports`: owned through their parent assessment (policies use an `EXISTS` subquery checking `assessments.user_id = auth.uid()`).
- `audit_events`: owned by `user_id = auth.uid()`.

This means even if someone uses the anon key directly from the browser, they
can never read or write another candidate’s data. The FastAPI service-role
client bypasses RLS for trusted server-side operations.

#### Storage bucket — `candidate-resumes`

- A **private** bucket named `candidate-resumes` is created (`public = false`).
- Resumes are stored under `candidate-resumes/<user_id>/<resume_id>/<filename>.pdf`.
- Storage policies ensure a user can only read/write/delete objects under
  **their own** `<user_id>/` prefix.
- The database stores the **object path**, never a public URL. Resumes are never public.

#### Verification checklist (Phase 23)

- [x] Service-role key never appears in React
- [x] Gemini key never appears in React
- [x] Database password never appears in React
- [x] `.env` and `frontend/.env` are gitignored
- [x] RLS enabled on every table
- [x] Profile / assessment / response / result ownership enforced
- [x] Resume Storage is private + per-user
- [x] Backend verifies the Supabase JWT
- [x] Backend never trusts a frontend-supplied user_id
- [x] API errors don’t leak credentials
- [x] Logs don’t print API keys

---

## 5. Testing

Unit tests mock Gemini and the store (the repo rule is "Mock Gemini in unit
tests"), so they run with no API key and no database:

```bash
uv run pytest      # 13 tests
uv run ruff check backend
```

The mocks (`backend/tests/fake_gemini.py`, `backend/tests/fake_store.py`) are
**test-only** — production has zero fallbacks.

A real end-to-end test is done in the browser: sign up, upload a CV, run an
assessment. Each Gemini Interactions call takes ~60–90s, so a full assessment
is roughly 15–25 minutes.

---

## 6. Run the whole thing locally

```bash
# 1. one-time: create the Supabase schema
psql "$DATABASE_URL" -f supabase/migrations/0001_init.sql
# (or paste supabase/migrations/0001_init.sql into the Supabase SQL Editor and Run)

# 2. backend (real Gemini + real Supabase)
uv run uvicorn backend.app.main:app --reload --port 8000

# 3. frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 → sign up → profile → upload CV → start assessment.

`GET http://localhost:8000/health` should show:
`{"status":"ok","gemini_configured":true,"supabase_configured":true}`

---

## 7. File map (what was built)

**Backend (`backend/app/`)**
- `core/config.py` — Pydantic Settings (your exact env shape)
- `core/supabase.py` — one centralized server-side Supabase client (service-role)
- `core/security.py` — Supabase JWT verification, `get_current_user()`
- `core/errors.py` — predictable application errors (no secret leakage)
- `services/gemini_service.py` — **real Gemini Interactions API**, Pydantic-validated, no mock
- `services/prompts.py` — one prompt per use case (resume, question, evaluation, synthesis)
- `services/ai_contracts.py` — Pydantic output schemas with coercion/aliases
- `services/resume_parser.py` — validate → pypdf → Supabase Storage → Gemini → validate
- `services/assessment_engine.py` — adaptive loop + deterministic scoring/stopping
- `services/evaluator.py` — maps Gemini evaluation → validated Evaluation
- `services/report_service.py` — builds result + grounded report
- `services/assessment_service.py` — orchestration, idempotency, state transitions
- `repositories/supabase_store.py` — maps domain objects ↔ normalized Supabase tables
- `api/v1/` — profile, resumes, assessments, reports routes (all JWT-protected)

**Frontend (`frontend/src/`)**
- `context/AuthContext.tsx` — Supabase auth (signup/signin/signout, session restore)
- `lib/api.ts` — centralized API client (attaches Supabase JWT, handles 401/403/422/500)
- `lib/supabase.ts` — browser Supabase client (anon key only)
- `features/` — landing, auth, home, profile (+CV upload), assessment runner, results, report
- `components/ui/` — shadcn-style primitives (button, input, card, badge, progress, tabs, dialog, toasts, …)

**Data**
- `supabase/migrations/0001_init.sql` — all tables + RLS + private storage bucket

---

## 8. Known limitations

- A full assessment takes ~15–25 min because each Gemini Interactions call is ~60–90s.
- The normalized Supabase store is carefully mapped but should get one live
  round-trip validation against your real Supabase project (sign up in the
  browser and run one assessment).
- Voice input uses the browser Web Speech API and falls back to typing where unavailable.
- No real customer data is used; this is a hackathon reference implementation.
