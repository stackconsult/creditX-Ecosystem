# SKILLS.md - AI Agent Memory Document

> Persistent context for Windsurf Cascade to remember project state  
> **Updated: January 19, 2026 @ 2:05 PM MST**

---

## 🚦 Current Status

**ALL CODE COMPLETE** - Waiting on Hyperlift technical team for:
- Dashboard access
- Managed PostgreSQL provisioning
- Managed Dragonfly provisioning
- GitHub secrets integration confirmation

---

## Project Identity

| Key | Value |
|-----|-------|
| **Project** | CreditX Ecosystem |
| **Domain** | creditx.credit |
| **Platform** | Spaceship Hyperlift (Medium plan) |
| **GitHub** | stackconsult/creditX-Ecosystem |
| **Branch** | main (auto-deploy enabled) |

---

## Architecture

**Design**: Microservices in Single Hyperlift Container

```
Hyperlift Container (PORT from environment)
│
├── nginx (entry point, routes to internal services)
│   ├── /health → 200 OK (Hyperlift health check)
│   ├── /api/* → API Gateway :4000
│   ├── /agent/* → Agent Orchestrator :8010
│   ├── /services/creditx/* → CreditX Service :8000
│   └── /* → Frontend :3000
│
└── supervisor (process manager)
    ├── frontend (Next.js :3000)
    ├── api-gateway (Express :4000)
    ├── agent-orchestrator (FastAPI :8010)
    ├── creditx-service (FastAPI :8000)
    ├── threat-service (FastAPI :8001)
    └── guardian-service (FastAPI :8002)
```

---

## Credentials Location

### API Keys (DO NOT COMMIT TO GIT)

| Variable | Location in `.env` |
|----------|-------------------|
| `OPENAI_API_KEY` | Line 147 (starts with `sk-proj-`) |
| `NEXT_PUBLIC_COPILOTKIT_API_KEY` | Line 148 (starts with `ck_pub_`) |

### Infrastructure (From Spaceship - WAITING)

| Variable | Status |
|----------|--------|
| `DATABASE_URL` | ⏳ Waiting on Hyperlift team |
| `CACHE_HOST` | ⏳ Waiting on Hyperlift team |

---

## Completed Components (41/41)

### Infrastructure (8/8)
- ✅ `Dockerfile` - Multi-stage, all 6 services
- ✅ `docker/nginx.conf` - Routes PORT → internal services
- ✅ `docker/supervisord.conf` - Process management
- ✅ `docker/start.sh` - Startup + env validation
- ✅ `hyperlift.yaml` - Domain, secrets, auto-deploy
- ✅ `.github/workflows/deploy.yml` - CI/CD pipeline
- ✅ `SKILLS.md` - AI agent memory
- ✅ `AGENTS.md` - AI agent instructions

### Frontend (6/6)
- ✅ Next.js 14 App Router (standalone output)
- ✅ CopilotKit with OpenAI Adapter
- ✅ Multi-face routing: `(consumer)/`, `(partner)/`, `(internal)/`
- ✅ API Client with tenant headers
- ✅ TailwindCSS, shadcn/ui, Lucide icons
- ✅ `next.config.js` with rewrites

### API Gateway (9/9)
- ✅ Express.js server (Port 4000)
- ✅ JWT auth middleware (`middleware/auth.ts`)
- ✅ API key authentication
- ✅ Role-based access (`requireRole()`, `requireFace()`)
- ✅ Health routes
- ✅ Consumer routes
- ✅ Partner routes
- ✅ Internal routes
- ✅ Agent proxy routes

### Agent Orchestrator (5/5)
- ✅ FastAPI server (Port 8010)
- ✅ LangGraph integration
- ✅ LangChain integration
- ✅ OpenAI GPT-4 Turbo config
- ✅ Health endpoints

### Backend Services (6/6)
- ✅ creditx-service (8000) - Compliance, credit scoring
- ✅ threat-service (8001) - AI threat detection
- ✅ guardian-service (8002) - Device security
- ✅ apps-service (8003) - 91-Apps automation
- ✅ phones-service (8004) - Stolen phone tracking
- ✅ local-ai (8005) - Local model inference

### Database (4/4)
- ✅ Migration runner (`migrate.py`)
- ✅ `001_initial_schema.sql` (18KB)
- ✅ `002_materialized_views.sql` (11KB)
- ✅ `003_module_tables.sql` (22KB)

### Shared Libraries (3/3)
- ✅ `packages/shared` - TypeScript types, Zod schemas
- ✅ `services/shared/node` - Logger, cache, http-client
- ✅ `services/shared/python` - core_ai, resilience, cache

---

## GitHub Secrets (Set When Hyperlift Ready)

| Secret Name | Source |
|-------------|--------|
| `OPENAI_API_KEY` | `.env` line 147 |
| `COPILOTKIT_API_KEY` | `.env` line 148 |
| `NEXT_PUBLIC_COPILOTKIT_API_KEY` | `.env` line 148 |
| `DATABASE_URL` | From Spaceship managed PostgreSQL |
| `CACHE_HOST` | From Spaceship managed Dragonfly |
| `CACHE_PORT` | `6379` |
| `JWT_SECRET` | Generate: `openssl rand -base64 32` |

---

## Key Technical Decisions

1. **LLM Provider**: OpenAI GPT-4 Turbo at runtime
   - Anthropic/Claude is NOT used in the app
   - Claude is only used for development via Windsurf Cascade

2. **Multi-tenancy**: Headers propagated through all services
   - `x-tenant-id` - Tenant identifier
   - `x-face` - consumer | partner | internal
   - `x-request-id` - Correlation ID

3. **Three Faces**: Same backend, different UI/permissions
   - Consumer: End users (`/`)
   - Partner: B2B clients (`/partner`)
   - Internal: CreditX staff (`/internal`)

4. **Single Container**: All services in one Hyperlift deployment
   - Simpler deployment, lower cost
   - Internal localhost communication (fast)
   - nginx routes externally, supervisor manages processes

---

## File Quick Reference

| File | Purpose |
|------|---------|
| `Dockerfile` | Unified build |
| `docker/nginx.conf` | Route PORT → services |
| `docker/supervisord.conf` | Process management |
| `docker/start.sh` | Container startup |
| `hyperlift.yaml` | Hyperlift config |
| `.env` | Real API keys (local only) |
| `AGENTS.md` | AI instructions |
| `SKILLS.md` | AI memory (this file) |
| `docs/BUILD_STATUS.md` | Full audit status |

---

## Next Steps (When Hyperlift Reports Back)

1. Get `DATABASE_URL` from managed PostgreSQL
2. Get `CACHE_HOST` from managed Dragonfly
3. Generate `JWT_SECRET`: `openssl rand -base64 32`
4. Set all 7 secrets in GitHub repository settings
5. Push to main → Hyperlift auto-deploys
6. Verify at https://creditx.credit

---

*This file exists for AI agent memory persistence.*  
*Update when project state changes.*  
*Last audit: January 19, 2026 @ 2:05 PM MST*
