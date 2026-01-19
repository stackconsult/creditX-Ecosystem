#!/bin/bash
# CreditX Ecosystem - Container Startup Script
# Single entry point for Hyperlift deployment

set -e

echo "=============================================="
echo "CreditX Ecosystem - Starting Services"
echo "=============================================="
echo "PORT: ${PORT:-3000}"
echo "Environment: ${ENVIRONMENT:-production}"
echo "=============================================="

# Create logs directory
mkdir -p /app/logs
chmod 755 /app/logs

# Substitute PORT in nginx config
export PORT=${PORT:-3000}
envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Validate environment variables
echo "Validating environment..."

if [ -z "$OPENAI_API_KEY" ]; then
    echo "WARNING: OPENAI_API_KEY not set - AI features may not work"
fi

if [ -z "$DATABASE_URL" ]; then
    echo "WARNING: DATABASE_URL not set - using default connection"
fi

if [ -z "$CACHE_HOST" ]; then
    echo "WARNING: CACHE_HOST not set - cache features may not work"
fi

# Set Python path for shared modules
export PYTHONPATH="/app/services/shared/python:${PYTHONPATH}"

# Run database migrations if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    cd /app/packages/database
    python migrate.py upgrade || echo "Migration warning: ${?}"
    cd /app
fi

echo "Starting supervisor..."
echo "=============================================="

# Start all services via supervisor
exec /usr/local/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
