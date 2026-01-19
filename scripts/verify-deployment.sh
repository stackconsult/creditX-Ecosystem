#!/bin/bash
# CreditX Ecosystem - Post-Deployment Verification Script
# Run after Hyperlift deployment to verify all endpoints

set -e

DOMAIN="${1:-https://creditx.credit}"
TIMEOUT=10

echo "=============================================="
echo "CreditX Deployment Verification"
echo "Domain: $DOMAIN"
echo "Time: $(date)"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

passed=0
failed=0

check_endpoint() {
    local name="$1"
    local endpoint="$2"
    local expected_status="${3:-200}"
    
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$DOMAIN$endpoint" 2>/dev/null || echo "000")
    
    if [ "$status" == "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} $name ($endpoint) - $status"
        ((passed++))
    else
        echo -e "${RED}✗${NC} $name ($endpoint) - Expected $expected_status, got $status"
        ((failed++))
    fi
}

check_json_endpoint() {
    local name="$1"
    local endpoint="$2"
    local key="$3"
    
    response=$(curl -s --max-time $TIMEOUT "$DOMAIN$endpoint" 2>/dev/null || echo "{}")
    status=$(echo "$response" | grep -o "\"$key\"" | head -1)
    
    if [ -n "$status" ]; then
        echo -e "${GREEN}✓${NC} $name ($endpoint) - JSON valid with '$key'"
        ((passed++))
    else
        echo -e "${RED}✗${NC} $name ($endpoint) - Missing '$key' in response"
        ((failed++))
    fi
}

echo ""
echo "--- Health Checks ---"
check_endpoint "Main Health" "/health" 200
check_json_endpoint "Health JSON" "/health" "status"

echo ""
echo "--- Frontend Routes ---"
check_endpoint "Homepage" "/" 200
check_endpoint "Partner Portal" "/partner" 200
check_endpoint "Internal Portal" "/internal" 200

echo ""
echo "--- API Gateway ---"
check_endpoint "API Health Live" "/api/v1/health/live" 200
check_endpoint "API Health Ready" "/api/v1/health/ready" 200

echo ""
echo "--- API Endpoints (Auth Required) ---"
check_endpoint "Consumer API" "/api/v1/consumer/dashboard" 401
check_endpoint "Partner API" "/api/v1/partner/dashboard" 401
check_endpoint "Internal API" "/api/v1/internal/dashboard" 401
check_endpoint "Auth Login" "/api/v1/auth/login" 405

echo ""
echo "--- Agent Orchestrator ---"
check_endpoint "Agent Health" "/agent/health" 200

echo ""
echo "=============================================="
echo "Results: ${GREEN}$passed passed${NC}, ${RED}$failed failed${NC}"
echo "=============================================="

if [ $failed -gt 0 ]; then
    echo -e "${RED}Deployment verification FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}Deployment verification PASSED${NC}"
    exit 0
fi
