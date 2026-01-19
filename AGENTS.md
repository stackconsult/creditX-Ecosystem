# AGENTS.md - CreditX Ecosystem

> AI Agent Instructions for Windsurf Cascade and other coding assistants

## Project Overview

**CreditX Ecosystem** is an enterprise-grade financial compliance and automation platform. It provides credit intelligence, dispute resolution, threat detection, and multi-tenant SaaS capabilities.

## Development Environment

| Context | Tool | LLM |
|---------|------|-----|
| **Build Time** | Windsurf Cascade | Claude Opus 4 |
| **App Runtime** | CreditX Services | OpenAI GPT-4 Turbo |

> **Important**: We use Claude (via Windsurf Cascade) to BUILD this project, but the app itself uses OpenAI API at runtime. Do NOT configure Anthropic API keys for the app.

## Tech Stack

### Frontend (`apps/frontend`)
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI**: TailwindCSS, shadcn/ui, Lucide icons
- **AI Chat**: CopilotKit with OpenAI Adapter
- **Multi-face routing**: Consumer (`/`), Partner (`/partner`), Internal (`/internal`)

### API Gateway (`apps/api`)
- **Runtime**: Node.js 20 / Express.js
- **Language**: TypeScript
- **Purpose**: BFF layer, request forwarding, middleware

### Agent Orchestrator (`apps/agent`)
- **Runtime**: Python 3.12 / FastAPI
- **AI Framework**: LangGraph, LangChain
- **LLM Provider**: OpenAI (primary), Local models (optional)
- **Cache**: Dragonfly (Redis-compatible)

### Backend Services (`services/`)
| Service | Port | Stack | Purpose |
|---------|------|-------|---------|
| creditx-service | 8000 | Python/FastAPI | Compliance, credit scoring |
| threat-service | 8001 | Python/FastAPI | AI threat detection |
| guardian-service | 8002 | Python/FastAPI | Device security |
| apps-service | 8003 | Node.js/Express | 91-Apps automation |
| phones-service | 8004 | Node.js/Express | Stolen phone tracking |

### Shared Libraries
- `packages/shared` - TypeScript types, schemas, constants
- `services/shared/node` - Node.js utilities (logger, cache, http-client)
- `services/shared/python` - Python utilities (core_ai, resilience, cache)

## Required API Keys

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | ✅ Yes | App runtime LLM (GPT-4 Turbo) |
| `COPILOTKIT_API_KEY` | ✅ Yes | Frontend AI chat sidebar |
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection |
| `CACHE_HOST` | ✅ Yes | Dragonfly/Redis cache |
| `ANTHROPIC_API_KEY` | ❌ No | Not used in app runtime |

## Development Commands

```bash
# Frontend
cd apps/frontend && npm run dev

# API Gateway  
cd apps/api && npm run dev

# Agent Orchestrator
cd apps/agent && python -m app.main

# Python services
cd services/<service-name> && python -m app.main
```

## Code Conventions

### TypeScript/JavaScript
- Use ESLint with recommended config
- Prefer `async/await` over callbacks
- Use Zod for runtime validation
- Export types from `packages/shared`

### Python
- Use Pydantic for data validation
- Use structlog for logging
- Async-first with FastAPI
- Use pybreaker for circuit breakers

### File Structure
- Group by feature, not by type
- Keep API routes thin, logic in services
- Use dependency injection patterns

## Multi-Tenancy

All requests carry tenant context via headers:
- `x-tenant-id`: Tenant identifier
- `x-face`: consumer | partner | internal
- `x-request-id`: Correlation ID

Propagate these headers through all service calls.

## Deployment

- **Platform**: Spaceship Hyperlift
- **Manifests**: `infrastructure/spaceship/*.yaml`
- **CI/CD**: GitHub Actions (`.github/workflows/`)

## Known Issues & Tech Debt

1. TypeScript lint errors deferred for missing typings
2. Some Python services need full implementation
3. Database migrations not yet created
4. Authentication middleware placeholder only

## Build Status

See `docs/BUILD_STATUS.md` for current progress tracking.

---

*Last updated: January 2026*
*Built with Windsurf Cascade + Claude Opus 4*
