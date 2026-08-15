"""Store factory. Production uses Supabase/Postgres only.

There is no in-memory fallback in production. Tests inject a fake store
directly (see ``backend/tests``).
"""

from __future__ import annotations

from .base import Store
from .supabase_store import SupabaseStore


def get_store() -> Store:
    return SupabaseStore()
