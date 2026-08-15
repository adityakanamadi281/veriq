# Repository Rules

- Keep product logic in FastAPI.
- Keep Gemini credentials server-side.
- Keep Supabase service-role credentials server-side.
- React may use only the Supabase anon/publishable client credential intended for browser use.
- Never commit `.env`.
- Prefer Pydantic models for AI contracts.
- Prefer async FastAPI handlers when calling async-capable dependencies.
- Keep assessment state in Postgres/Supabase.
- Use idempotency for response submission.
- Add tests before changing scoring/stopping behavior.
- Keep UI calm and evidence-oriented.
