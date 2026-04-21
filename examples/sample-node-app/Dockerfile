# Multi-stage build for a hardened Node.js container.
# Demonstrates ASCEND-compliant patterns: pinned base image, non-root user,
# minimal runtime dependencies.

# ---------- Stage 1: builder ----------
FROM node:20.18.0-alpine3.20@sha256:2bff48f72ecb9b5d5b87c8f2b87e2e0928068ba9db78cd5fef5e6f9f6b5c3b6b AS builder

WORKDIR /build

COPY package*.json ./
RUN npm ci --omit=dev --ignore-scripts \
 && npm cache clean --force

# ---------- Stage 2: runtime ----------
FROM node:20.18.0-alpine3.20@sha256:2bff48f72ecb9b5d5b87c8f2b87e2e0928068ba9db78cd5fef5e6f9f6b5c3b6b AS runtime

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
