"""Server-side Supabase client.

A single client is created lazily and reused. The service-role key is used for
trusted server-side operations (persistence, admin lookups, storage) and must
never reach the browser. Do not create Supabase clients inside route handlers.
"""

from __future__ import annotations

from threading import Lock
from typing import Any

from .config import Settings, get_settings
from .errors import AppError

_client: Any | None = None
_lock = Lock()


def _create_client(settings: Settings) -> Any:
    try:
        from supabase import create_client  # type: ignore[import-not-found]
    except Exception as exc:
        raise AppError(
            "Supabase dependency is not available.",
            code="supabase_unavailable",
            status_code=503,
        ) from exc
    # Prefer the service-role key for server-side trusted operations.
    key = settings.supabase_service_role_key or settings.supabase_anon_key
    return create_client(settings.supabase_url, key)


def get_supabase_admin() -> Any:
    """Return the shared server-side Supabase client (service-role)."""
    settings = get_settings()
    if not settings.supabase_configured:
        raise AppError(
            "Supabase is not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY in .env.",
            code="supabase_unconfigured",
            status_code=503,
        )
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = _create_client(settings)
    return _client


def reset_supabase_client() -> None:
    """Reset the cached client (used by tests)."""
    global _client
    with _lock:
        _client = None
