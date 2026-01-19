# CreditX Ecosystem - Hyperlift Deployment Plan

> Complete stepwise deployment guide for Spaceship Hyperlift
> Last Updated: January 19, 2026

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Service Architecture](#service-architecture)
3. [Hyperlift App Setup Procedures](#hyperlift-app-setup-procedures)
4. [Environment Variables Configuration](#environment-variables-configuration)
5. [Domain & SSL Setup](#domain--ssl-setup)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Rollback Procedures](#rollback-procedures)

---

## Pre-Deployment Checklist

### ✅ Completed Items

| Item | Status | Notes |
|------|--------|-------|
| Dockerfiles created | ✅ | 4 service-specific Dockerfiles |
| .dockerignore | ✅ | Excludes node_modules, .git, .env |
| PORT env var support | ✅ | All services use `${PORT}` |
| dumb-init for SIGTERM | ✅ | All Dockerfiles |
| Non-root users | ✅ | Security best practice |
| Health endpoints | ✅ | `/health/live`, `/health/ready` |
| Multi-stage builds | ✅ | Smaller images |
| Next.js standalone | ✅ | `output: "standalone"` in next.config.js |
| hyperlift.yaml | ✅ | Configuration file |
| CI/CD workflow | ✅ | GitHub Actions |

### ⏳ Pending Items (Pre-Deploy)

| Item | Priority | Action Required |
|------|----------|-----------------|
| Create GitHub `production` environment | 🔴 High | GitHub Settings → Environments |
| Configure secrets in GitHub | 🔴 High | OPENAI_API_KEY, DATABASE_URL |
| Create Hyperlift apps | 🔴 High | 4 apps in Hyperlift Dashboard |
| Configure Hyperlift env vars | 🔴 High | Per-app secrets |
| Connect domains | 🟡 Medium | DNS CNAME records |

---

## Service Architecture

### Deployment Topology

```
                    ┌─────────────────────────────────────┐
                    │         Hyperlift Load Balancer     │
                    │         (SSL Termination)           │
                    └─────────────────┬───────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│   Frontend    │           │  API Gateway  │           │    Agent      │
│   (Next.js)   │           │  (Express)    │           │ Orchestrator  │
│   Port: 3000  │           │   Port: 4000  │           │  Port: 8010   │
└───────────────┘           └───────┬───────┘           └───────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │ CreditX   │   │  Threat   │   │ Guardian  │
            │ Service   │   │  Service  │   │ Service   │
            │ Port:8000 │   │ Port:8001 │   │ Port:8002 │
            └───────────┘   └───────────┘   └───────────┘
                    │               │               │
                    └───────────────┴───────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
            ┌───────────────┐           ┌───────────────┐
            │   PostgreSQL  │           │   Dragonfly   │
            │   (Database)  │           │   (Cache)     │
            └───────────────┘           └───────────────┘
```

### Hyperlift Apps to Create

| App Name | Dockerfile Path | Port | Domain |
|----------|-----------------|------|--------|
| `creditx-frontend` | `apps/frontend/Dockerfile` | 3000 | ecosystem.ai |
| `creditx-api` | `apps/api/Dockerfile` | 4000 | api.ecosystem.ai |
| `creditx-agent` | `apps/agent/Dockerfile` | 8010 | agent.ecosystem.ai |
| `creditx-service` | `Dockerfile` (root) | 8000 | service.ecosystem.ai |

---

## Hyperlift App Setup Procedures

### Step 1: Create Frontend App

```
1. Go to Hyperlift Dashboard → Create New App
2. Connect GitHub repository: stackconsult/creditX-Ecosystem
3. Configure build settings:
   - Dockerfile: apps/frontend/Dockerfile
   - Build context: apps/frontend
   - Branch: main
4. Set runtime settings:
   - Plan: Small (1 vCPU, 1 GB RAM) recommended
   - Instances: 2 (for HA)
5. Add environment variables:
   - PORT=3000
   - NODE_ENV=production
   - NEXT_PUBLIC_API_URL=https://api.ecosystem.ai
   - NEXT_PUBLIC_COPILOTKIT_API_KEY=(secret)
6. Configure health check:
   - Path: /api/health (or /)
   - Interval: 30s
   - Timeout: 5s
7. Save and deploy
```

### Step 2: Create API Gateway App

```
1. Go to Hyperlift Dashboard → Create New App
2. Connect GitHub repository: stackconsult/creditX-Ecosystem
3. Configure build settings:
   - Dockerfile: apps/api/Dockerfile
   - Build context: apps/api
   - Branch: main
4. Set runtime settings:
   - Plan: Small (1 vCPU, 1 GB RAM)
   - Instances: 2
5. Add environment variables:
   - PORT=4000
   - NODE_ENV=production
   - CREDITX_SERVICE_URL=https://service.ecosystem.ai
   - THREAT_SERVICE_URL=https://threat.ecosystem.ai
   - AGENT_SERVICE_URL=https://agent.ecosystem.ai
   - DRAGONFLY_HOST=(Spaceship managed)
   - DRAGONFLY_PORT=6379
6. Configure health check:
   - Path: /health/live
   - Interval: 30s
   - Timeout: 5s
7. Save and deploy
```

### Step 3: Create Agent Orchestrator App

```
1. Go to Hyperlift Dashboard → Create New App
2. Connect GitHub repository: stackconsult/creditX-Ecosystem
3. Configure build settings:
   - Dockerfile: apps/agent/Dockerfile
   - Build context: apps/agent
   - Branch: main
4. Set runtime settings:
   - Plan: Medium (2 vCPU, 2 GB RAM) - LLM workloads
   - Instances: 2
5. Add environment variables:
   - PORT=8010
   - ENVIRONMENT=production
   - OPENAI_API_KEY=(secret)
   - DRAGONFLY_HOST=(Spaceship managed)
   - DATABASE_URL=(Spaceship managed)
6. Configure health check:
   - Path: /health
   - Interval: 30s
   - Timeout: 5s
7. Save and deploy
```

### Step 4: Create CreditX Service App

```
1. Go to Hyperlift Dashboard → Create New App
2. Connect GitHub repository: stackconsult/creditX-Ecosystem
3. Configure build settings:
   - Dockerfile: Dockerfile (root)
   - Build context: . (root)
   - Branch: main
4. Set runtime settings:
   - Plan: Small (1 vCPU, 1 GB RAM)
   - Instances: 2
5. Add environment variables:
   - PORT=8000
   - ENVIRONMENT=production
   - DATABASE_URL=(Spaceship managed)
   - DRAGONFLY_HOST=(Spaceship managed)
   - OPENAI_API_KEY=(secret)
6. Configure health check:
   - Path: /health/live
   - Interval: 30s
   - Timeout: 5s
7. Save and deploy
```

---

## Environment Variables Configuration

### Required Secrets (Set in Hyperlift Dashboard)

| Variable | Apps | Source |
|----------|------|--------|
| `OPENAI_API_KEY` | agent, creditx-service | platform.openai.com |
| `COPILOTKIT_API_KEY` | frontend | cloud.copilotkit.ai |
| `DATABASE_URL` | agent, creditx-service | Spaceship Managed DB |
| `DRAGONFLY_HOST` | api, agent, creditx-service | Spaceship Managed Cache |

### Per-App Environment Variables

#### Frontend (`creditx-frontend`)
```yaml
PORT: 3000
NODE_ENV: production
NEXT_PUBLIC_API_URL: https://api.ecosystem.ai
NEXT_PUBLIC_AGENT_URL: https://agent.ecosystem.ai
NEXT_PUBLIC_COPILOTKIT_API_KEY: (secret)
```

#### API Gateway (`creditx-api`)
```yaml
PORT: 4000
NODE_ENV: production
CORS_ORIGINS: https://ecosystem.ai
CREDITX_SERVICE_URL: https://service.ecosystem.ai
THREAT_SERVICE_URL: https://threat.ecosystem.ai
GUARDIAN_SERVICE_URL: https://guardian.ecosystem.ai
AGENT_SERVICE_URL: https://agent.ecosystem.ai
DRAGONFLY_HOST: (managed)
DRAGONFLY_PORT: 6379
```

#### Agent Orchestrator (`creditx-agent`)
```yaml
PORT: 8010
ENVIRONMENT: production
OPENAI_API_KEY: (secret)
LLM_PROVIDER: openai
LLM_MODEL: gpt-4-turbo-preview
DRAGONFLY_HOST: (managed)
DATABASE_URL: (managed)
```

#### CreditX Service (`creditx-service`)
```yaml
PORT: 8000
ENVIRONMENT: production
DATABASE_URL: (managed)
DRAGONFLY_HOST: (managed)
OPENAI_API_KEY: (secret)
```

---

## Domain & SSL Setup

### Option A: Spaceship-Managed Domains (Recommended for Start)

```
Each app gets automatic subdomain:
- creditx-frontend.spaceship.dev
- creditx-api.spaceship.dev
- creditx-agent.spaceship.dev
- creditx-service.spaceship.dev

SSL: Automatic via Let's Encrypt
DNS: No configuration needed
```

### Option B: Custom Domains

```
Step 1: Add domain in Hyperlift Dashboard
  [App Settings] → [Domains] → [Add Custom Domain]
  Enter: ecosystem.ai

Step 2: Configure DNS at registrar
  Type: CNAME
  Name: @ (or www)
  Value: hyperlift-lb-xxx.spaceship.cloud (provided by Hyperlift)
  TTL: 3600

Step 3: Wait for propagation (5-30 minutes)
  Verify: nslookup ecosystem.ai

Step 4: SSL auto-provisioned by Hyperlift
  Certificate issued within 5-10 minutes
```

### Subdomain Mapping

| Subdomain | Hyperlift App |
|-----------|---------------|
| ecosystem.ai | creditx-frontend |
| api.ecosystem.ai | creditx-api |
| agent.ecosystem.ai | creditx-agent |
| service.ecosystem.ai | creditx-service |

---

## Post-Deployment Verification

### Health Check Verification

```bash
# Frontend
curl -f https://ecosystem.ai/api/health

# API Gateway
curl -f https://api.ecosystem.ai/health/live
curl -f https://api.ecosystem.ai/health/ready

# Agent Orchestrator
curl -f https://agent.ecosystem.ai/health

# CreditX Service
curl -f https://service.ecosystem.ai/health/live
curl -f https://service.ecosystem.ai/health/ready
```

### Smoke Tests

```bash
# Test frontend loads
curl -I https://ecosystem.ai

# Test API responds
curl https://api.ecosystem.ai/health/ready | jq

# Test agent endpoint
curl -X POST https://agent.ecosystem.ai/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Test creditx service
curl https://service.ecosystem.ai/health/ready | jq
```

### Monitoring Checklist

- [ ] All health checks passing in Hyperlift Dashboard
- [ ] CPU usage < 70% baseline
- [ ] Memory usage < 80% baseline
- [ ] Response times < 500ms (p95)
- [ ] Error rate < 1%

---

## Rollback Procedures

### Automatic Rollback

Hyperlift automatically rolls back if:
- Health checks fail for 60 seconds
- Container crashes repeatedly

### Manual Rollback

```
1. Go to Hyperlift Dashboard → [Your App] → Deployment History
2. Find the last stable deployment
3. Click "Rollback to this version"
4. Confirm and wait for container restart (~2-3 minutes)
```

### Emergency Procedures

```
If deployment is broken:
1. Immediate: Rollback via dashboard
2. If rollback fails: Scale instances to 0
3. Fix code locally
4. Push fix to GitHub
5. Manually trigger new deployment
```

---

## Build Gaps Identified & Remediation

### Gap 1: Database Migrations
**Status**: ⏳ Pending  
**Risk**: High  
**Action**: Create migration scripts before production deploy

### Gap 2: Authentication Middleware
**Status**: ⏳ Pending  
**Risk**: High  
**Action**: Implement JWT/OAuth before production

### Gap 3: Threat/Guardian/Apps/Phones Services
**Status**: ✅ Implemented (basic)  
**Risk**: Medium  
**Action**: Verify health endpoints work, create Hyperlift apps if needed

### Gap 4: Rate Limiting
**Status**: ✅ Basic in API Gateway  
**Risk**: Low  
**Action**: Verify configuration in production

### Gap 5: Logging & Observability
**Status**: ✅ Structured logging exists  
**Risk**: Low  
**Action**: Configure log export to monitoring system

---

## Deployment Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1: Prep** | 1 hour | Create GitHub env, Hyperlift apps |
| **Phase 2: Deploy** | 30 min | Deploy all 4 apps |
| **Phase 3: Verify** | 30 min | Health checks, smoke tests |
| **Phase 4: DNS** | 1-2 hours | Custom domain setup (if needed) |
| **Phase 5: Monitor** | Ongoing | Watch metrics, logs |

---

*Document created: January 19, 2026*  
*For: Spaceship Hyperlift Deployment*
