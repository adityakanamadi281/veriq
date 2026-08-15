"""API tests: the candidate journey over HTTP with mocked Gemini + memory store."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.app.core.deps import get_current_user, get_datastore
from backend.app.core.security import AuthUser
from backend.app.main import app
from backend.tests.fake_store import FakeStore


@pytest.fixture
def client():
    store = FakeStore()
    user = AuthUser(id="api-user", email="api@local.dev")

    async def _user():
        return user

    def _store():
        return store

    app.dependency_overrides[get_current_user] = _user
    app.dependency_overrides[get_datastore] = _store
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_full_journey(client):
    # Profile
    r = client.put(
        "/api/v1/profile",
        json={"name": "Ada", "target_role": "AI Engineer", "background": "I build APIs."},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Ada"

    # Start
    r = client.post("/api/v1/assessments", json={"introduction": "hi"})
    assert r.status_code == 200
    state = r.json()
    assert state["status"] == "in_progress"
    assert state["current_question"] is not None
    aid = state["id"]

    # Answer until complete
    for _ in range(10):
        q = state["current_question"]
        if q is None:
            break
        r = client.post(
            f"/api/v1/assessments/{aid}/responses",
            json={
                "question_id": q["id"],
                "text": "I validate inputs, parameterize queries, add retries with backoff, and verify with tests.",
                "submission_key": str(uuid.uuid4()),
            },
        )
        assert r.status_code == 200
        state = r.json()
        if state["status"] == "completed":
            break

    assert state["status"] == "completed"

    # Idempotency over HTTP: replay the last submission key (use a fresh one we track)
    r2 = client.post(
        f"/api/v1/assessments/{aid}/responses",
        json={"question_id": "x", "text": "dup", "submission_key": "replay-key"},
    )
    # Completed assessment with a brand-new key must reject, not crash.
    assert r2.status_code == 409

    # Result
    r = client.get(f"/api/v1/assessments/{aid}/result")
    assert r.status_code == 200
    result = r.json()
    assert 0 <= result["overall_score"] <= 100
    assert len(result["dimension_results"]) == 6

    # Report
    r = client.get(f"/api/v1/assessments/{aid}/report")
    assert r.status_code == 200
    assert r.json()["assessment_id"] == aid

    # History
    r = client.get("/api/v1/assessments")
    assert r.status_code == 200
    assert any(a["id"] == aid for a in r.json())


def test_resume_validation_rejects_non_pdf(client):
    import io

    r = client.post(
        "/api/v1/resume",
        files={"file": ("resume.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert r.status_code == 422
