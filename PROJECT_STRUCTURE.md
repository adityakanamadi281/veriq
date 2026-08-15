# AURA / hackathon-aditya structure

veriq/
├── CLAUDE.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── README.md
├── .claude/
│   ├── instructions.md
│   ├── settings.json.example
│   ├── rules/
│   │   └── repository.md
│   └── skills/
│       ├── assessment-engine/
│       │   └── SKILL.md
│       └── gemini-sdk/
│           └── SKILL.md
├── backend/
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── config.py
│       │   ├── security.py
│       │   └── errors.py
│       ├── api/
│       │   └── v1/
│       │       ├── profile.py
│       │       ├── resumes.py
│       │       ├── assessments.py
│       │       └── reports.py
│       ├── models/
│       │   ├── profile.py
│       │   ├── assessment.py
│       │   └── result.py
│       ├── schemas/
│       │   ├── profile.py
│       │   ├── resume.py
│       │   ├── assessment.py
│       │   └── result.py
│       ├── services/
│       │   ├── gemini_service.py
│       │   ├── resume_parser.py
│       │   ├── assessment_engine.py
│       │   ├── evaluator.py
│       │   └── report_service.py
│       └── repositories/
│           ├── profiles.py
│           ├── assessments.py
│           └── results.py
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── profile/
│   │   │   ├── assessment/
│   │   │   └── results/
│   │   ├── lib/
│   │   │   ├── supabase.ts
│   │   │   └── api.ts
│   │   └── types/
│   └── public/
├── supabase/
│   ├── migrations/
│   └── seed.sql
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
    ├── project-spec.md
    └── source-material-extracted.md
