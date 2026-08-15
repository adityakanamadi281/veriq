-- VERIQ — initial schema (Supabase/Postgres).
-- Normalized tables; Postgres is the source of truth. RLS enforces the
-- auth.uid() ownership boundary for any browser-side (anon-key) access; the
-- FastAPI service-role client bypasses RLS for trusted server-side operations.

create extension if not exists "pgcrypto";

-- ========== profiles ==========
-- Linked directly to auth.users. Email/password stay in Supabase Auth.
create table if not exists public.profiles (
  id              uuid primary key references auth.users (id) on delete cascade,
  full_name       text,
  education       text,
  graduation_year int,
  experience      text,
  target_role     text,
  github_url      text,
  linkedin_url    text,
  resume_path     text,
  resume_parsed   boolean not null default false,
  -- lists/structured fields: technical_skills, projects, ai_tools,
  -- professional_links, background
  details         jsonb not null default '{}'::jsonb,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);

-- ========== assessments ==========
create table if not exists public.assessments (
  id                 uuid primary key default gen_random_uuid(),
  user_id            uuid not null references auth.users (id) on delete cascade,
  target_role        text,
  status             text not null default 'created',
  current_question_id uuid,
  introduction       text,
  profile_snapshot   jsonb not null default '{}'::jsonb,
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now(),
  completed_at       timestamptz
);
create index if not exists assessments_user_created_idx
  on public.assessments (user_id, created_at desc);

-- ========== assessment_questions ==========
create table if not exists public.assessment_questions (
  id                  uuid primary key default gen_random_uuid(),
  assessment_id       uuid not null references public.assessments (id) on delete cascade,
  question_number     int not null,
  dimension           text not null,
  question            text not null,
  question_type       text not null default 'written',
  objective           text,
  evaluation_criteria jsonb not null default '[]'::jsonb,
  context             text,
  options             jsonb not null default '[]'::jsonb,
  created_at          timestamptz not null default now(),
  unique (assessment_id, question_number)
);
create index if not exists questions_assessment_idx on public.assessment_questions (assessment_id);

-- ========== assessment_responses ==========
-- id is the question_id (one response per question per assessment).
create table if not exists public.assessment_responses (
  id                  uuid primary key default gen_random_uuid(),
  assessment_id       uuid not null references public.assessments (id) on delete cascade,
  question_id         uuid not null,
  response_text       text not null default '',
  response_type       text not null default 'written',
  selected_option_id  text,
  duration_seconds    double precision,
  submission_key      text,
  submitted_at        timestamptz not null default now(),
  unique (assessment_id, question_id)
);
create index if not exists responses_assessment_idx on public.assessment_responses (assessment_id);
create index if not exists responses_submission_key_idx on public.assessment_responses (submission_key);

-- ========== response_evaluations ==========
-- id is the response id (one evaluation per response).
create table if not exists public.response_evaluations (
  id                    uuid primary key default gen_random_uuid(),
  response_id           uuid not null,
  assessment_id         uuid not null references public.assessments (id) on delete cascade,
  dimension             text not null,
  evidence              jsonb not null default '[]'::jsonb,
  strengths             jsonb not null default '[]'::jsonb,
  gaps                  jsonb not null default '[]'::jsonb,
  capability_score      int not null default 50,
  confidence            double precision not null default 0.5,
  needs_more_evidence   boolean not null default true,
  rationale             text not null default '',
  created_at            timestamptz not null default now(),
  unique (response_id)
);
create index if not exists evaluations_assessment_idx on public.response_evaluations (assessment_id);

-- ========== assessment_results ==========
create table if not exists public.assessment_results (
  id                         uuid primary key default gen_random_uuid(),
  assessment_id              uuid not null references public.assessments (id) on delete cascade,
  overall_score              int not null,
  readiness_classification   text not null,
  dimension_results          jsonb not null default '[]'::jsonb,
  strengths                  jsonb not null default '[]'::jsonb,
  capability_gaps            jsonb not null default '[]'::jsonb,
  personalized_summary       text not null default '',
  recommended_pathway        text not null,
  recommendation_reason      text not null default '',
  recommendation             jsonb not null default '{}'::jsonb,
  evidence                   jsonb not null default '[]'::jsonb,
  created_at                 timestamptz not null default now(),
  unique (assessment_id)
);

-- ========== assessment_reports ==========
create table if not exists public.assessment_reports (
  assessment_id uuid primary key references public.assessments (id) on delete cascade,
  report        jsonb not null,
  created_at    timestamptz not null default now()
);

-- ========== audit_events ==========
create table if not exists public.audit_events (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid references auth.users (id) on delete cascade,
  assessment_id uuid references public.assessments (id) on delete cascade,
  event         text not null,
  metadata      jsonb not null default '{}'::jsonb,
  created_at    timestamptz not null default now()
);
create index if not exists audit_user_idx on public.audit_events (user_id, created_at desc);

-- ========== Row Level Security ==========
alter table public.profiles              enable row level security;
alter table public.assessments           enable row level security;
alter table public.assessment_questions  enable row level security;
alter table public.assessment_responses  enable row level security;
alter table public.response_evaluations  enable row level security;
alter table public.assessment_results    enable row level security;
alter table public.assessment_reports    enable row level security;
alter table public.audit_events          enable row level security;

-- profiles: a user owns the row keyed by their id.
create policy "profiles self select" on public.profiles
  for select using (id = auth.uid());
create policy "profiles self insert" on public.profiles
  for insert with check (id = auth.uid());
create policy "profiles self update" on public.profiles
  for update using (id = auth.uid()) with check (id = auth.uid());

-- assessments: ownership via user_id.
create policy "assessments self select" on public.assessments
  for select using (user_id = auth.uid());
create policy "assessments self insert" on public.assessments
  for insert with check (user_id = auth.uid());
create policy "assessments self update" on public.assessments
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy "assessments self delete" on public.assessments
  for delete using (user_id = auth.uid());

-- child tables: ownership derived through the parent assessment.
create policy "questions self select" on public.assessment_questions
  for select using (
    exists (select 1 from public.assessments a where a.id = assessment_questions.assessment_id and a.user_id = auth.uid())
  );
create policy "questions self write" on public.assessment_questions
  for all using (
    exists (select 1 from public.assessments a where a.id = assessment_questions.assessment_id and a.user_id = auth.uid())
  ) with check (
    exists (select 1 from public.assessments a where a.id = assessment_questions.assessment_id and a.user_id = auth.uid())
  );

create policy "responses self select" on public.assessment_responses
  for select using (
    exists (select 1 from public.assessments a where a.id = assessment_responses.assessment_id and a.user_id = auth.uid())
  );
create policy "responses self write" on public.assessment_responses
  for all using (
    exists (select 1 from public.assessments a where a.id = assessment_responses.assessment_id and a.user_id = auth.uid())
  ) with check (
    exists (select 1 from public.assessments a where a.id = assessment_responses.assessment_id and a.user_id = auth.uid())
  );

create policy "evaluations self select" on public.response_evaluations
  for select using (
    exists (select 1 from public.assessments a where a.id = response_evaluations.assessment_id and a.user_id = auth.uid())
  );
create policy "evaluations self write" on public.response_evaluations
  for all using (
    exists (select 1 from public.assessments a where a.id = response_evaluations.assessment_id and a.user_id = auth.uid())
  ) with check (
    exists (select 1 from public.assessments a where a.id = response_evaluations.assessment_id and a.user_id = auth.uid())
  );

create policy "results self select" on public.assessment_results
  for select using (
    exists (select 1 from public.assessments a where a.id = assessment_results.assessment_id and a.user_id = auth.uid())
  );
create policy "results self write" on public.assessment_results
  for all using (
    exists (select 1 from public.assessments a where a.id = assessment_results.assessment_id and a.user_id = auth.uid())
  ) with check (
    exists (select 1 from public.assessments a where a.id = assessment_results.assessment_id and a.user_id = auth.uid())
  );

create policy "reports self select" on public.assessment_reports
  for select using (
    exists (select 1 from public.assessments a where a.id = assessment_reports.assessment_id and a.user_id = auth.uid())
  );
create policy "reports self write" on public.assessment_reports
  for all using (
    exists (select 1 from public.assessments a where a.id = assessment_reports.assessment_id and a.user_id = auth.uid())
  ) with check (
    exists (select 1 from public.assessments a where a.id = assessment_reports.assessment_id and a.user_id = auth.uid())
  );

create policy "audit self select" on public.audit_events
  for select using (user_id = auth.uid());
create policy "audit self insert" on public.audit_events
  for insert with check (user_id = auth.uid());

-- ========== Storage: private resume bucket ==========
insert into storage.buckets (id, name, public)
values ('candidate-resumes', 'candidate-resumes', false)
on conflict (id) do nothing;

-- Objects are private; only the owning user may read/write their prefix.
create policy "resumes self read" on storage.objects
  for select using (
    bucket_id = 'candidate-resumes'
    and (storage.foldername(name))[1] = auth.uid()::text
  );
create policy "resumes self write" on storage.objects
  for insert with check (
    bucket_id = 'candidate-resumes'
    and (storage.foldername(name))[1] = auth.uid()::text
  );
create policy "resumes self delete" on storage.objects
  for delete using (
    bucket_id = 'candidate-resumes'
    and (storage.foldername(name))[1] = auth.uid()::text
  );
