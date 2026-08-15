"""Test configuration.

Production uses real Gemini + Supabase only (no fallbacks). Tests mock both:
- Gemini is replaced by ``FakeGemini`` injected via ``gemini_service._generate_fn``.
- The store is replaced by ``FakeStore`` (in-memory).

This keeps unit tests fast and independent of a real API key or database, per
the repository rule "Mock Gemini in unit tests."
"""

from __future__ import annotations

import os

import pytest

# Provide empty values so Settings() loads without real credentials.
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("SUPABASE_URL", "")
os.environ.setdefault("SUPABASE_ANON_KEY", "")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "")
os.environ.setdefault("DATABASE_URL", "")

from backend.app.core.security import AuthUser
from backend.app.services.gemini_service import gemini_service
from backend.tests.fake_gemini import FakeGemini
from backend.tests.fake_store import FakeStore


@pytest.fixture
def store() -> FakeStore:
    return FakeStore()


@pytest.fixture
def auth_user() -> AuthUser:
    return AuthUser(id="test-user", email="test@local.dev")


@pytest.fixture(autouse=True)
def fake_gemini():
    """Inject the fake Gemini for every test, restore afterward."""
    fake = FakeGemini()
    previous = gemini_service._generate_fn
    gemini_service._generate_fn = fake
    yield fake
    gemini_service._generate_fn = previous
