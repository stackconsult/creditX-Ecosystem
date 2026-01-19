#!/bin/bash
# CreditX Ecosystem - Local Docker Build & Test
# Tests the Docker build locally before pushing to Hyperlift

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE_NAME="creditx-ecosystem"
CONTAINER_NAME="creditx-test"
PORT=8080

echo "=============================================="
echo "CreditX Local Docker Test"
echo "Project: $PROJECT_ROOT"
echo "=============================================="

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
}
trap cleanup EXIT

# Step 1: Build the image
echo ""
echo "--- Building Docker Image ---"
docker build -t $IMAGE_NAME "$PROJECT_ROOT"

# Step 2: Run the container
echo ""
echo "--- Starting Container ---"
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:$PORT \
    -e PORT=$PORT \
    -e NODE_ENV=production \
    -e OPENAI_API_KEY="${OPENAI_API_KEY:-sk-test}" \
    -e NEXT_PUBLIC_COPILOTKIT_API_KEY="${NEXT_PUBLIC_COPILOTKIT_API_KEY:-ck_test}" \
    -e DATABASE_URL="${DATABASE_URL:-postgresql://test:test@localhost:5432/test}" \
    -e CACHE_HOST="${CACHE_HOST:-localhost}" \
    -e CACHE_PORT="${CACHE_PORT:-6379}" \
    -e JWT_SECRET="${JWT_SECRET:-test-secret-for-local-only}" \
    $IMAGE_NAME

# Step 3: Wait for container to be healthy
echo ""
echo "--- Waiting for Container (max 60s) ---"
for i in {1..60}; do
    if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
        echo "Container is healthy!"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Step 4: Run verification
echo ""
echo "--- Running Verification ---"
if [ -f "$PROJECT_ROOT/scripts/verify-deployment.sh" ]; then
    bash "$PROJECT_ROOT/scripts/verify-deployment.sh" "http://localhost:$PORT"
else
    # Basic check
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/health")
    if [ "$status" == "200" ]; then
        echo "✓ Health check passed"
    else
        echo "✗ Health check failed (status: $status)"
        exit 1
    fi
fi

# Step 5: Show logs
echo ""
echo "--- Container Logs (last 50 lines) ---"
docker logs --tail 50 $CONTAINER_NAME

echo ""
echo "=============================================="
echo "Local Docker test completed successfully!"
echo "Container available at: http://localhost:$PORT"
echo "Press Ctrl+C to stop and cleanup"
echo "=============================================="

# Keep running for manual testing
read -p "Press Enter to stop container..."
