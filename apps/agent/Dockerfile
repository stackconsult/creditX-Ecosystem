# ============================================================================
# CreditX Agent Orchestrator - FastAPI/LangGraph Production Container
# For Spaceship Hyperlift deployment
# ============================================================================

FROM python:3.12-slim AS deps
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runner
WORKDIR /app

# Install runtime dependencies and dumb-init
RUN apt-get update && apt-get install -y \
    curl \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1001 agent && \
    chown -R agent:agent /app

# Copy Python packages
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=agent:agent app ./app

USER agent

# Default port (Hyperlift will override)
ENV PORT=8010
EXPOSE 8010

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Use dumb-init for graceful shutdown
ENTRYPOINT ["dumb-init", "--"]
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
