"""Database access layer using parameterized queries."""

from __future__ import annotations

import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "file::memory:?cache=shared")


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DATABASE_URL, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def initialize_schema() -> None:
    """Create tables if they don't exist. Called once at app startup."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def list_users(limit: int = 50) -> list[dict[str, Any]]:
    """List users, parameterized to prevent SQL injection."""
    # Clamp limit defensively — also validated at the API layer.
    limit = max(1, min(100, int(limit)))

    with _connect() as conn:
        cursor = conn.execute(
            "SELECT id, username, email, created_at FROM users "
            "ORDER BY id LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    """Fetch a single user by ID using parameterized query."""
    with _connect() as conn:
        cursor = conn.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
