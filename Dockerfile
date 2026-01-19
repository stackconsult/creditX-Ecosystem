# ============================================================================
# creditX Ecosystem - Primary Production Container
# Multi-stage build for Spaceship Hyperlift deployment
# Follows Hyperlift best practices: PORT env var, dumb-init, non-root user
# ============================================================================

FROM python:3.12-slim AS base

# Install system dependencies
FROM base AS deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpcap-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY services/creditx-service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim AS runner

# Install runtime dependencies and dumb-init for signal handling
RUN apt-get update && apt-get install -y \
    libpcap0.8 \
    libpq5 \
    curl \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1001 creditx && \
    chown -R creditx:creditx /app

# Copy dependencies
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy shared libraries
COPY --chown=creditx:creditx services/shared/python ./shared/python

# Copy application code
COPY --chown=creditx:creditx services/creditx-service/app ./app

USER creditx

# Default port (Hyperlift will override via PORT env var)
ENV PORT=8000

EXPOSE 8000

# Health check using PORT env var
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health/live || exit 1

# Use dumb-init for proper signal handling (SIGTERM on deployment)
ENTRYPOINT ["dumb-init", "--"]

# Run with uvicorn using PORT env var
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 4"]
