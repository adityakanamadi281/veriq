# Deploying veriq

Two services:

| Part      | Host       | Config file   |
|-----------|------------|---------------|
| Backend   | Render     | `render.yaml` |
| Frontend  | Vercel     | `vercel.json` |

The backend reads its config from environment variables (`backend/app/core/config.py`).
The frontend reads browser-safe env vars at build time (`frontend/src/lib/env.ts`).
**No secrets are committed.** You set them in the Render / Vercel dashboards.

> Prerequisite: the Supabase project must exist and its schema applied first (Step 0),
> because both the backend and frontend depend on Supabase for auth + persistence.

---

## Step 0 — Supabase (one-time)

1. Create a project at https://supabase.com (free tier is fine).
2. Open **SQL Editor → New query**, paste the contents of
   `supabase/migrations/0001_init.sql`, and run it. This creates the tables,
   RLS policies, and the private `candidate-resumes` storage bucket.
3. Collect these values from **Project Settings → API**:
   - `Project URL` → `SUPABASE_URL` (backend) / `VITE_SUPABASE_URL` (frontend)
   - `anon` / `public` key → `SUPABASE_ANON_KEY` (backend) / `VITE_SUPABASE_ANON_KEY` (frontend)
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY` (**backend only — never in the browser**)
4. (Optional) From **Project Settings → Database → Connection string → URI**
   copy the Postgres URL → `DATABASE_URL` (backend). Not required for the app
   to run (the server uses the Supabase client), but handy to have.
5. In **Authentication → Providers**, enable **Email** and confirm
   "Confirm email" is off for a quick hackathon demo (or leave on and verify).

---

## Step 1 — Backend on Render

1. Push this repo to GitHub (the `.env` file is gitignored — confirm it is **not** committed).
2. In the Render dashboard: **New → Blueprint**, pick this repo.
   Render reads `render.yaml` and creates a web service named `veriq-backend`.
3. Fill in the env vars marked `sync: false` in the dashboard (**Environment** tab):

   | Key                        | Value                                                            |
   |----------------------------|------------------------------------------------------------------|
   | `GEMINI_API_KEY`           | Your Google AI Studio Gemini key                                 |
   | `GEMINI_MODEL`             | `gemini-2.5-flash` (already set as default, override if needed)  |
   | `SUPABASE_URL`             | from Step 0                                                      |
   | `SUPABASE_ANON_KEY`        | from Step 0                                                      |
   | `SUPABASE_SERVICE_ROLE_KEY`| from Step 0                                                      |
   | `DATABASE_URL`             | (optional) from Step 0                                           |
   | `BACKEND_URL`              | `https://veriq-backend.onrender.com` (this service's Render URL) |
   | `FRONTEND_URL`             | your Vercel URL from Step 2 (set/finish Step 2 first, then come back) |

   Already preset by the blueprint: `PYTHON_VERSION=3.12`, `APP_ENV=production`.
4. **Apply** / **Create**. Render builds (`pip install -r requirements.txt`) and starts:
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Visit `https://veriq-backend.onrender.com/health` — you should get JSON with
   `"status":"ok"` and `gemini_configured` / `supabase_configured` both `true`.

Notes:
- The service reads `FRONTEND_URL` to build its CORS allow-list (comma-separated).
  Add Vercel preview URLs there too if you want preview deploys to call the API:
  `https://veriq.vercel.app,https://veriq-git-main-<user>.vercel.app`.
- Render free web services spin down after idle; the first request after idle
  may take ~30 s to wake. The `/health` check keeps it warm during active use.

---

## Step 2 — Frontend on Vercel

1. In the Vercel dashboard: **Add New → Project → Import** this GitHub repo.
2. `vercel.json` (at repo root) already configures the build for you:
   - `installCommand`: `cd frontend && npm install`
   - `buildCommand`:   `cd frontend && npm run build`
   - `outputDirectory`: `frontend/dist`
   - SPA rewrite so React Router routes resolve to `index.html`
   - **You do not need to set a Root Directory** — leave it as the repo root.
3. Before clicking **Deploy**, open **Settings → Environment Variables** and add
   (these are baked into the build, so set them **before** the first build):

   | Key                     | Value                                                 |
   |-------------------------|-------------------------------------------------------|
   | `VITE_API_URL`          | `https://veriq-backend.onrender.com/api/v1`           |
   | `VITE_SUPABASE_URL`     | from Step 0                                           |
   | `VITE_SUPABASE_ANON_KEY`| from Step 0 (anon/public key — browser-safe)          |

   Mark them for the **Production** environment (and **Preview** if you want
   preview deploys to work). Redeploy after changing them.
4. Click **Deploy**. When it finishes, open the Vercel URL.
5. Copy the Vercel URL (e.g. `https://veriq.vercel.app`) back into the Render
   service's `FRONTEND_URL` env var (Step 1.3) and redeploy the backend so CORS
   allows it.

---

## Step 3 — Verify end-to-end

1. Open the Vercel URL → the landing page loads.
2. Sign up / sign in (Supabase email auth).
3. Complete profile → upload resume → start assessment → submit answers →
   view results/report.
4. If something fails, check:
   - Backend health: `https://veriq-backend.onrender.com/health`
     (`gemini_configured` and `supabase_configured` must both be `true`).
   - Browser devtools Network tab: are calls going to
     `https://veriq-backend.onrender.com/api/v1/...`? A CORS error means
     `FRONTEND_URL` on the backend doesn't include your Vercel origin.
   - Vercel build logs if `VITE_*` vars were missing (rebuild after adding).

---

## Local dev (unchanged)

```bash
# backend
uv sync
uv run uvicorn app.main:app --reload --app-dir backend

# frontend (separate terminal)
cd frontend
npm install
npm run dev
```

`.env` (backend) and `frontend/.env` hold local secrets; both are gitignored.

---

## What each config file does

- **`render.yaml`** — Render Blueprint. Declares the `veriq-backend` Python web
  service: build/start commands, Python 3.12, health check, and the full env-var
  list. Secrets are `sync: false` so you enter them in the dashboard.
- **`backend/requirements.txt`** — pinned, hashed deps exported from `uv.lock`.
  Lets Render's standard `pip` runtime install without needing `uv`.
- **`vercel.json`** — points Vercel's build into `frontend/`, outputs
  `frontend/dist`, and adds the SPA fallback rewrite for client-side routing.
- **`frontend/.env.example`** — documents the browser-safe env vars only.
