#!/bin/bash
# CreditX Ecosystem - Container Startup Script
# Domain: creditx.credit
# Platform: Spaceship Hyperlift

set -e
set -x  # Debug output

echo "=============================================="
echo "CreditX Ecosystem - Starting Services"
echo "Domain: creditx.credit"
echo "=============================================="
echo "PORT: ${PORT:-3000}"
echo "Environment: ${ENVIRONMENT:-production}"
echo "=============================================="

# Create logs directory
mkdir -p /app/logs
chmod 755 /app/logs

# Environment variables are injected by Hyperlift Dashboard
# No need to load from file - Hyperlift injects them at container runtime

# Substitute PORT in nginx config (Hyperlift default is 8080)
export PORT=${PORT:-8080}
envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Validate critical environment variables
echo "Validating environment..."

if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY not set - AI features will not work"
else
    echo "✓ OPENAI_API_KEY configured"
fi

if [ -z "$COPILOTKIT_API_KEY" ] && [ -z "$NEXT_PUBLIC_COPILOTKIT_API_KEY" ]; then
    echo "WARNING: COPILOTKIT_API_KEY not set"
else
    echo "✓ COPILOTKIT_API_KEY configured"
fi

if [ -z "$DATABASE_URL" ]; then
    echo "WARNING: DATABASE_URL not set - using default"
else
    echo "✓ DATABASE_URL configured"
fi

if [ -z "$CACHE_HOST" ]; then
    echo "WARNING: CACHE_HOST not set"
else
    echo "✓ CACHE_HOST configured: $CACHE_HOST"
fi

# Set Python path for shared modules
export PYTHONPATH="/app/services/shared/python:${PYTHONPATH}"

# Run database migrations if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    cd /app/packages/database
    python migrate.py upgrade 2>/dev/null || echo "Migration skipped or warning"
    cd /app
fi

echo "=============================================="
echo "Starting supervisor with all services..."
echo "=============================================="

# Start all services via supervisor
exec /usr/local/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
