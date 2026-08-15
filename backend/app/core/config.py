"""Application configuration loaded from environment variables.

All secrets are read here and never re-exported to the frontend. VeriQ uses
real Gemini and real Supabase only — there are no local/deterministic
fallbacks in production. Set the credentials in .env.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Gemini ---
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # --- Supabase ---
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # --- Database ---
    database_url: str = ""

    # --- App ---
    app_env: str = "development"
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"

    # --- Assessment engine tuning (deterministic, code-owned) ---
    assessment_min_questions: int = 4
    assessment_max_questions: int = 8
    assessment_evidence_target_per_dimension: int = 1
    threshold_ready: int = 75
    threshold_targeted: int = 60
    threshold_structured: int = 45
    min_confidence_to_stop: float = 0.6

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Derived helpers ---
    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key)

    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.frontend_url.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


# Module-level instance for the import style used by the Gemini service.
settings = get_settings()
