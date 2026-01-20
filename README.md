# CreditX Ecosystem

Enterprise-grade financial compliance and automation platform with multi-tenant SaaS capabilities.

## Architecture

- **Frontend:** Next.js 14 (Netlify) - Multi-face UI (Consumer/Partner/Internal)
- **API Gateway:** Node.js/Express (Port 4000)
- **Agent Orchestrator:** Python 3.12/FastAPI + LangGraph (Port 8010)
- **Backend Services:** 6 microservices (Python/Node.js)
- **Cache:** Dragonfly (Redis-compatible)
- **Database:** PostgreSQL 16
- **Deployment:** Netlify (Frontend) + Spaceship Hyperlift (Backend)

## Services

| Service | Stack | Port | Description |
|---------|-------|------|-------------|
| Frontend | Next.js 14 | 3000 | Multi-face UI (Consumer/Partner/Internal) |
| API Gateway | Node.js/Express | 4000 | BFF layer, auth, routing |
| Agent Orchestrator | Python/FastAPI | 8010 | LangGraph workflows, AI agents |
| creditx-service | Python/FastAPI | 8000 | Compliance, credit scoring |
| threat-service | Python/FastAPI | 8001 | AI threat detection |
| guardian-service | Python/FastAPI | 8002 | Device security |
| apps-service | Node.js/Express | 8003 | 91-Apps automation |
| phones-service | Node.js/Express | 8004 | Stolen phone tracking |

## Quick Start

### Prerequisites

- Docker >= 24.0.0
- Node.js >= 20.0.0
- Python >= 3.12.0
- Git >= 2.40.0

### Local Development

```bash
# Clone repository
git clone https://github.com/stackconsult/creditX-Ecosystem.git
cd creditX-Ecosystem

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Frontend (Terminal 1)
cd apps/frontend
npm install
npm run dev
# Visit: http://localhost:3000

# Backend (Terminal 2)
cd ../api
npm install
npm run dev
# Visit: http://localhost:4000/health

# Agent Orchestrator (Terminal 3)
cd ../agent
pip install -r requirements.txt
python -m app.main
# Visit: http://localhost:8010/health
```

### Production Deployment

**Frontend (Netlify)**
- Auto-deploys from `main` branch
- Base directory: `apps/frontend`
- Build command: `npm run build`
- URL: https://creditx-frontend.netlify.app

**Backend (Hyperlift)**
```bash
docker build -t creditx-ecosystem:latest .
# Push to registry and deploy via Hyperlift dashboard
```

## Project Structure

```
creditX-Ecosystem/
├── apps/
│   ├── frontend/             # Next.js 14 UI (Netlify)
│   ├── api/                  # Express API Gateway
│   └── agent/                # Python Agent Orchestrator
├── services/                 # Backend Microservices
│   ├── shared/               # Shared libraries
│   │   ├── python/           # Python utilities
│   │   └── node/             # Node.js utilities
│   ├── creditx-service/      # Compliance, credit scoring
│   ├── threat-service/       # AI threat detection
│   ├── guardian-service/     # Device security
│   ├── apps-service/         # 91-Apps automation
│   └── phones-service/       # Phone tracking
├── packages/                 # TypeScript shared types
├── docker/                   # Container configs
├── docs/                     # Documentation
├── infrastructure/           # IaC configs
├── netlify.toml             # Netlify config (repo root)
├── hyperlift.yaml           # Hyperlift deployment
└── SKILLS.md                 # AI agent memory
```

## Deployment (Spaceship Hyperlift)

### Deployment Configuration

**Netlify**
- Site: moonlit-yeot-c72ff2.netlify.app
- Base: `apps/frontend`
- Node: 20

**Hyperlift**
- Application: creditX Ecosystem
- Repository: github.com/stackconsult/creditX-Ecosystem
- Branch: main
- Dockerfile: Dockerfile (root)

### Environment Variables

See `.env.example` for all required variables.
Key variables:
- `OPENAI_API_KEY` - OpenAI GPT-4 Turbo
- `DATABASE_URL` - PostgreSQL connection
- `CACHE_HOST` - Dragonfly cache
- `NEXT_PUBLIC_API_URL` - Backend URL

## License

Proprietary - All Rights Reserved
