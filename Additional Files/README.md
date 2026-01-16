# creditX Ecosystem

Enterprise-grade financial compliance and automation platform built on Spaceship Hyperlift infrastructure.

## Architecture

- **Frontend:** Next.js 14 (Node.js 20)
- **Agent:** Python 3.12 with LangGraph/FastAPI
- **API:** Node.js backend
- **Cache:** Dragonfly (Redis-compatible)
- **Database:** PostgreSQL 16
- **Deployment:** Spaceship Hyperlift

## Services

| Service | Stack | Port | Description |
|---------|-------|------|-------------|
| creditx-service | Python/FastAPI | 8000 | Compliance document management |
| threat-service | Python/FastAPI | 8001 | Global AI threat detection |
| guardian-service | Python/FastAPI | 8002 | Device security monitoring |
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

# Start services with Docker Compose
docker-compose up -d

# Verify health
curl http://localhost:8000/health/live
```

### Build Docker Image

```bash
docker build -t creditx-ecosystem:latest .
```

## Project Structure

```
creditX-Ecosystem/
├── Dockerfile                 # Primary production container
├── docker/                    # Service-specific Dockerfiles
├── services/
│   ├── shared/               # Shared libraries
│   │   ├── python/           # Python utilities
│   │   └── node/             # Node.js utilities
│   ├── creditx-service/      # Main compliance service
│   ├── threat-service/       # Threat detection
│   ├── guardian-service/     # Device guardian
│   ├── apps-service/         # Automation apps
│   └── phones-service/       # Phone tracking
├── config/
│   ├── hyperlift/            # Hyperlift deployment configs
│   └── monitoring/           # Prometheus/Grafana configs
├── apps/                     # Frontend applications
├── packages/                 # Shared packages
└── infrastructure/           # Terraform IaC
```

## Deployment (Spaceship Hyperlift)

### Hyperlift Configuration

- **Application Name:** creditX Ecosystem
- **Repository:** github.com/stackconsult/creditX-Ecosystem
- **Branch:** main
- **Dockerfile:** Dockerfile

### Environment Variables

See `.env.example` for required configuration.

## License

Proprietary - All Rights Reserved
