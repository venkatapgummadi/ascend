"""Authentication middleware using HS256 JWT with strict expiry validation."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable

import jwt
from flask import g, jsonify, request

logger = logging.getLogger(__name__)


def _get_secret() -> str:
    """Fetch signing secret from the environment (never hardcode)."""
    secret = os.environ.get("JWT_SIGNING_SECRET")
    if not secret:
        raise RuntimeError(
            "JWT_SIGNING_SECRET environment variable is not set. "
            "Configure a high-entropy secret via your secrets manager."
        )
    return secret


def authenticate_request() -> dict[str, Any] | None:
    """
    Validate the Authorization header and return decoded claims on success.
    Returns None if authentication fails.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[len("Bearer "):].strip()
    if not token:
        return None

    try:
        claims = jwt.decode(
            token,
            _get_secret(),
            algorithms=["HS256"],
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        logger.info("Rejected expired token")
        return None
    except jwt.InvalidTokenError as exc:
        logger.info("Rejected invalid token: %s", exc)
        return None

    # Additional defense in depth — check expiry again explicitly.
    exp = claims.get("exp")
    if exp is None or datetime.now(tz=timezone.utc).timestamp() >= exp:
        return None

    return claims


def require_auth(fn: Callable) -> Callable:
    """Decorator that enforces authentication on a route."""

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        claims = authenticate_request()
        if claims is None:
            return jsonify({"error": "unauthorized"}), 401
        g.user = claims.get("sub")
        return fn(*args, **kwargs)

    return wrapper
