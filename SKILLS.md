# SKILLS.md - AI Agent Memory Document

> Persistent context for Windsurf Cascade to remember project state
> **Updated: January 19, 2026**

---

## Project Identity

| Key | Value |
|-----|-------|
| **Project** | CreditX Ecosystem |
| **Domain** | creditx.credit |
| **Platform** | Spaceship Hyperlift (Medium plan) |
| **GitHub** | stackconsult/creditX-Ecosystem |
| **Branch** | main |

---

## Architecture

**Design**: Microservices in Single Container

```
Hyperlift Container (PORT)
├── nginx (entry point, routes externally)
├── supervisor (manages all processes)
├── Frontend (Next.js :3000)
├── API Gateway (Express :4000)
├── Agent Orchestrator (Python :8010)
├── CreditX Service (Python :8000)
├── Threat Service (Python :8001)
└── Guardian Service (Python :8002)
```

---

## Production Credentials

### API Keys (from .env file - DO NOT COMMIT ACTUAL KEYS)

| Variable | Location |
|----------|----------|
| `OPENAI_API_KEY` | See `.env` file (line 147) |
| `NEXT_PUBLIC_COPILOTKIT_API_KEY` | See `.env` file (line 148) |

> **Note**: Actual keys are in local `.env` file and Hyperlift Dashboard.

### Infrastructure (Spaceship Managed)

| Variable | Value |
|----------|-------|
| `CACHE_HOST` | `dragonfly-cache.internal` |
| `DATABASE_URL` | `postgresql://ecosystem:CHANGE_ME@postgres.internal:5432/ecosystem` |

---

## Tech Stack

### Frontend (`apps/frontend`)
- Next.js 14 (App Router, standalone output)
- CopilotKit with OpenAI Adapter
- TailwindCSS, shadcn/ui, Lucide icons
- Multi-face: Consumer `/`, Partner `/partner`, Internal `/internal`

### API Gateway (`apps/api`)
- Express.js, TypeScript
- JWT authentication middleware
- Routes to backend services

### Agent Orchestrator (`apps/agent`)
- FastAPI, Python 3.12
- LangGraph, LangChain
- OpenAI GPT-4 Turbo (NOT Anthropic)

### Backend Services
| Service | Port | Purpose |
|---------|------|---------|
| creditx-service | 8000 | Compliance, credit scoring |
| threat-service | 8001 | AI threat detection |
| guardian-service | 8002 | Device security |

---

## Key Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Unified build, all services |
| `docker/nginx.conf` | Routes PORT to internal services |
| `docker/supervisord.conf` | Process management |
| `docker/start.sh` | Startup script |
| `hyperlift.yaml` | Hyperlift configuration |
| `.env` | Environment variables (has real keys) |
| `AGENTS.md` | AI agent instructions |

---

## Deployment Status

- [x] Hyperlift Medium plan connected
- [x] GitHub repo connected
- [x] Domain creditx.credit connected
- [x] Unified Dockerfile created
- [x] nginx/supervisor configs created
- [ ] Environment variables set in Hyperlift dashboard
- [ ] First production deploy

---

## Important Notes

1. **LLM Provider**: OpenAI GPT-4 Turbo at runtime (NOT Anthropic)
2. **Build Tool**: Claude via Windsurf Cascade (development only)
3. **Multi-tenancy**: x-tenant-id, x-face, x-request-id headers
4. **Three faces**: Consumer, Partner, Internal (same backend)

---

*This file exists for AI agent memory persistence. Update when project state changes.*
