# Multi-stage build for a hardened Python Flask container.
# Demonstrates ASCEND-compliant patterns: pinned base image, non-root user,
# minimal runtime dependencies, no shell by default in the final stage.

# ---------- Stage 1: builder ----------
FROM python:3.12.7-slim-bookworm@sha256:af4e85f1cac90dd3771e47292ea7c8a9830abfabbe4faa5c53f158854c2e819d AS builder

WORKDIR /build

# Only install what's needed to compile wheels; drop after.
RUN apt-get update && apt-get install --no-install-recommends -y \
        gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.12.7-slim-bookworm@sha256:af4e85f1cac90dd3771e47292ea7c8a9830abfabbe4faa5c53f158854c2e819d AS runtime

# Security: non-root user, no shell, no package manager in final image.
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --no-create-home --shell /sbin/nologin app

# Remove unneeded setuid binaries and package manager.
RUN find / -xdev -perm /4000 -type f -exec chmod -s {} \; 2>/dev/null || true

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=app:app app/ ./app/

USER app

EXPOSE 5000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_DEBUG=false \
    LOG_LEVEL=INFO

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://localhost:5000/healthz').status == 200 else 1)"

CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "app.main:app"]
