# ============================================================================
# creditX Ecosystem - Primary Production Container
# Multi-stage build for the main application service
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

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpcap0.8 \
    libpq5 \
    curl \
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

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
