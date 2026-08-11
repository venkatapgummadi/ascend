# Multi-stage build for a hardened Node.js container.
# Demonstrates ASCEND-compliant patterns: pinned base image, non-root user,
# minimal runtime dependencies.

# ---------- Stage 1: builder ----------
FROM node:24.1.0-alpine3.20@sha256:8fe019e0d57dbdce5f5c27c0b63d2775cf34b00e3755a7dea969802d7e0c2b25 AS builder

WORKDIR /build

COPY package*.json ./
RUN npm ci --omit=dev --ignore-scripts \
 && npm cache clean --force

# ---------- Stage 2: runtime ----------
FROM node:24.1.0-alpine3.20@sha256:8fe019e0d57dbdce5f5c27c0b63d2775cf34b00e3755a7dea969802d7e0c2b25 AS runtime

# Non-root user
RUN addgroup -S -g 10001 app \
 && adduser -S -u 10001 -G app -s /sbin/nologin app

WORKDIR /app

COPY --from=builder --chown=app:app /build/node_modules ./node_modules
COPY --chown=app:app src/ ./src/
COPY --chown=app:app package.json ./

USER app

EXPOSE 3000

ENV NODE_ENV=production

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/healthz', r => process.exit(r.statusCode === 200 ? 0 : 1))"

CMD ["node", "src/index.js"]
