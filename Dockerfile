# ============================================================================
# CreditX Ecosystem - Unified Full-Stack Production Container
# Single-app deployment for Spaceship Hyperlift
# Contains: Next.js Frontend + Express API + Python Microservices
# ============================================================================
# Architecture: Microservices in single container
# - nginx (PORT) → routes to internal services
# - Next.js Frontend (:3000)
# - Express API Gateway (:4000)
# - Python Services (:8000, :8001, :8002, :8010)
# - supervisor manages all processes
# ============================================================================

# ==========================================================================
# Stage 1: Build Frontend (Next.js)
# ==========================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy package files first for layer caching
COPY apps/frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY apps/frontend .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ==========================================================================
# Stage 2: Build API Gateway (Express)
# ==========================================================================
FROM node:20-alpine AS api-builder
WORKDIR /app/api

COPY apps/api/package*.json ./
RUN npm ci

COPY apps/api .
RUN npm run build

# ==========================================================================
# Stage 3: Python Dependencies
# ==========================================================================
FROM python:3.12-slim AS python-deps
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy all Python requirements
COPY services/creditx-service/requirements.txt ./requirements-creditx.txt
COPY services/threat-service/requirements.txt ./requirements-threat.txt
COPY services/guardian-service/requirements.txt ./requirements-guardian.txt
COPY apps/agent/requirements.txt ./requirements-agent.txt

# Install all Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-creditx.txt && \
    pip install --no-cache-dir -r requirements-threat.txt && \
    pip install --no-cache-dir -r requirements-guardian.txt && \
    pip install --no-cache-dir -r requirements-agent.txt && \
    pip install --no-cache-dir supervisor uvicorn[standard] gunicorn

# ==========================================================================
# Stage 4: Final Runtime
# ==========================================================================
FROM python:3.12-slim AS runner
WORKDIR /app

# Install curl and dumb-init for health checks and signal handling
RUN apt-get update && apt-get install -y curl dumb-init && rm -rf /var/lib/apt/lists/* \
    libpq5 \
    nginx \
    gettext-base \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && mkdir -p /app/logs \
    && mkdir -p /etc/supervisor/conf.d

# Copy Python packages from deps stage
COPY --from=python-deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Copy Frontend (standalone build)
COPY --from=frontend-builder /app/frontend/.next/standalone ./frontend
COPY --from=frontend-builder /app/frontend/.next/static ./frontend/.next/static
COPY --from=frontend-builder /app/frontend/public ./frontend/public

# Copy API Gateway
COPY --from=api-builder /app/api/dist ./api/dist
COPY --from=api-builder /app/api/node_modules ./api/node_modules
COPY --from=api-builder /app/api/package.json ./api/

# Copy Python shared libraries
COPY services/shared/python ./services/shared/python

# Copy Python services
COPY services/creditx-service ./services/creditx-service
COPY services/threat-service ./services/threat-service
COPY services/guardian-service ./services/guardian-service
COPY apps/agent ./apps/agent

# Copy database migrations
COPY packages/database ./packages/database

# Copy nginx config (as template for PORT substitution)
COPY docker/nginx.conf /etc/nginx/nginx.conf.template

# Copy supervisor config
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy startup script
COPY docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set permissions
RUN chown -R root:root /app && \
    chmod -R 755 /app

# Environment variables
ENV PORT=3000
ENV NODE_ENV=production
ENV ENVIRONMENT=production
ENV PYTHONPATH=/app/services/shared/python
ENV PYTHONUNBUFFERED=1

# Expose default port (Hyperlift overrides via PORT)
EXPOSE 3000

# Health check using PORT env var
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Use dumb-init for proper signal handling (SIGTERM on deployment)
ENTRYPOINT ["dumb-init", "--"]
CMD ["/app/start.sh"]
