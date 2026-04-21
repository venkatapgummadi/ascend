"""Tests for JWT authentication middleware."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.main import app


SECRET = "test-secret-do-not-use-in-production"


@pytest.fixture(autouse=True)
def set_secret(monkeypatch):
    monkeypatch.setenv("JWT_SIGNING_SECRET", SECRET)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _token(subject: str = "user-1", expires_in_seconds: int = 300) -> str:
    now = datetime.now(tz=timezone.utc)
    claims = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in_seconds),
    }
    return jwt.encode(claims, SECRET, algorithm="HS256")


def test_valid_token_permits_access(client):
    token = _token()
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    # 200 or 500 depending on DB state — what matters here is that it's NOT 401.
    assert response.status_code != 401


def test_expired_token_rejected(client):
    token = _token(expires_in_seconds=-1)  # already expired
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_missing_header_rejected(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 401


def test_wrong_scheme_rejected(client):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": "Basic something"},
    )
    assert response.status_code == 401


def test_garbage_token_rejected(client):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": "Bearer not-a-jwt"},
    )
    assert response.status_code == 401
