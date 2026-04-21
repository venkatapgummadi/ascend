"""Tests for the Flask API endpoints."""

from __future__ import annotations

import pytest

from app.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_healthz_returns_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_readyz_returns_ready(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json == {"status": "ready"}


def test_users_requires_auth(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 401
    assert response.json == {"error": "unauthorized"}


def test_user_by_id_requires_auth(client):
    response = client.get("/api/v1/users/1")
    assert response.status_code == 401
