"""Flask API demonstrating ASCEND-compliant patterns."""

from __future__ import annotations

import logging
import os
from typing import Any

from flask import Flask, jsonify, request

from app.auth import authenticate_request, require_auth
from app.database import get_user_by_id, list_users

app = Flask(__name__)

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@app.route("/healthz", methods=["GET"])
def healthz() -> Any:
    """Kubernetes / load-balancer liveness probe."""
    return jsonify({"status": "ok"}), 200


@app.route("/readyz", methods=["GET"])
def readyz() -> Any:
    """Readiness probe — confirms dependencies are reachable."""
    # In a real app, check database / cache / downstream services.
    return jsonify({"status": "ready"}), 200


@app.route("/api/v1/users", methods=["GET"])
@require_auth
def list_users_endpoint() -> Any:
    """List users — requires authentication."""
    try:
        limit = int(request.args.get("limit", "50"))
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400

    limit = max(1, min(100, limit))  # clamp to [1, 100]
    users = list_users(limit=limit)
    return jsonify({"users": users}), 200


@app.route("/api/v1/users/<int:user_id>", methods=["GET"])
@require_auth
def get_user_endpoint(user_id: int) -> Any:
    """Get a single user by ID — requires authentication."""
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"user": user}), 200


@app.errorhandler(401)
def unauthorized(error) -> Any:
    return jsonify({"error": "unauthorized"}), 401


@app.errorhandler(500)
def server_error(error) -> Any:
    logger.error("Internal server error: %s", error)
    return jsonify({"error": "internal server error"}), 500


if __name__ == "__main__":
    # In production, use gunicorn or uwsgi — never Flask's dev server.
    # Debug must never be True in production.
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug)
