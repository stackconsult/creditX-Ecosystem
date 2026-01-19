# CreditX Ecosystem - Enterprise Code Map

> **Complete System Architecture Documentation**  
> Last Updated: January 19, 2026  
> Version: 2.0.0-dragonfly

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CREDITX ECOSYSTEM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Consumer   │    │   Partner    │    │   Internal   │   ← Multi-Face   │
│  │   OS (/)     │    │   OS (/p)    │    │   OS (/i)    │     Frontend     │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                   │
│         │                    │                   │                           │
│         └────────────────────┼───────────────────┘                           │
│                              ▼                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     Next.js 14 Frontend + CopilotKit                   │  │
│  │                        apps/frontend (Port 3000)                       │  │
│  └───────────────────────────────┬───────────────────────────────────────┘  │
│                                  ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    Express.js API Gateway (BFF)                        │  │
│  │                       apps/api (Port 4000)                             │  │
│  └───────────────────────────────┬───────────────────────────────────────┘  │
│                                  ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                  FastAPI Agent Orchestrator (LangGraph)                │  │
│  │                       apps/agent (Port 8010)                           │  │
│  └───────────────────────────────┬───────────────────────────────────────┘  │
│                                  ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        MICROSERVICES LAYER                              ││
│  │  ┌─────────────┬─────────────┬─────────────┬─────────────┬───────────┐ ││
│  │  │  CreditX    │   Threat    │  Guardian   │    Apps     │  Phones   │ ││
│  │  │  Service    │   Service   │  Service    │   Service   │  Service  │ ││
│  │  │  :8000      │   :8001     │   :8002     │    :8003    │  :8004    │ ││
│  │  └──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴─────┬─────┘ ││
│  └─────────┼─────────────┼─────────────┼─────────────┼────────────┼───────┘│
│            │             │             │             │            │         │
│            └─────────────┴─────────────┼─────────────┴────────────┘         │
│                                        ▼                                     │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      SHARED INFRASTRUCTURE                             │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐│  │
│  │  │  Dragonfly      │  │   PostgreSQL    │  │   Spaceship Services    ││  │
│  │  │  (Redis Cache)  │  │   (Database)    │  │   (Spacemail, CDN)      ││  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────┘│  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
creditX-Ecosystem/
├── apps/
│   ├── frontend/          # Next.js 14 Multi-Face UI
│   │   └── src/app/
│   │       ├── (consumer)/ # Consumer OS routes
│   │       ├── (partner)/  # Partner OS routes
│   │       ├── (internal)/ # Internal OS routes
│   │       └── api/copilotkit/ # CopilotKit integration
│   ├── api/               # Express.js API Gateway
│   │   └── src/
│   │       ├── routes/    # consumer, partner, internal, agents, auth
│   │       ├── middleware/ # auth, error-handler, request-logger
│   │       └── lib/       # logger, http-client
│   └── agent/             # FastAPI Agent Orchestrator
│       └── app/
│           ├── routes/    # agents, executions, chat, health
│           └── services/  # cache, llm
├── services/
│   ├── creditx-service/   # Compliance & Credit Intelligence (Port 8000)
│   ├── threat-service/    # Global AI Alert Network (Port 8001)
│   ├── guardian-service/  # AI Endpoint Security (Port 8002)
│   ├── apps-service/      # 91-Apps Workflow Automation (Port 8003)
│   ├── phones-service/    # Stolen Device Recovery (Port 8004)
│   ├── local-ai/          # Local LLM Service (Port 8080)
│   └── shared/
│       ├── python/        # Shared Python libraries
│       │   ├── core_ai.py      # Multi-provider AI router
│       │   ├── core_database.py # PostgreSQL client
│       │   ├── core_cache.py   # Dragonfly cache client
│       │   ├── core_events.py  # Redis Streams event bus
│       │   ├── core_agents.py  # Agent orchestration framework
│       │   ├── core_config.py  # Configuration management
│       │   ├── core_logging.py # Structured logging
│       │   ├── core_resilience.py # Circuit breakers & retry
│       │   └── core_spacemail.py # Email service client
│       └── node/          # Shared Node.js libraries
│           ├── logger.ts
│           ├── http-client.ts
│           └── cache.ts
├── packages/
│   ├── database/migrations/ # SQL migrations
│   └── shared/            # TypeScript types & schemas
├── config/
│   └── agents/            # Agent YAML configurations
├── infrastructure/
│   └── spaceship/         # Hyperlift deployment manifests
└── docker/
    └── docker-compose.yml # Local development
```

---

## 🔄 Execution Traces

### Trace 1: Compliance Document Creation Flow

**Path:** `Frontend → API Gateway → CreditX Service → PostgreSQL → Dragonfly`

```
Compliance Document Creation Flow
├── Next.js Frontend
│   └── POST /api/v1/consumer/documents
│       └── API Gateway (Express.js)
│           └── Forward to CreditX Service
│
└── CreditX Service (FastAPI)
    └── POST /api/v1/compliance/documents
        ├── routes_compliance.py:184 [create_document()]
        │   ├── Line 191: get_database() → Singleton PostgreSQL client
        │   │   └── core_database.py:319 [get_database()]
        │   │       └── Line 103: asyncpg.create_pool()
        │   │
        │   ├── Line 200: db.fetchrow() → Insert document
        │   │   └── core_database.py:231 [fetchrow()]
        │   │       └── Line 231: CircuitBreaker → asyncpg.fetchrow()
        │   │
        │   ├── Line 208: logger.info() → Structured audit log
        │   │   └── extra={"document_id", "tenant_id"}
        │   │
        │   └── Line 213: Return ComplianceDocument response
        │
        └── Response: {document_id, customer_id, status, created_at}
```

**Key Files:**
| Location | File | Line | Description |
|----------|------|------|-------------|
| 1a | `services/creditx-service/app/main.py` | 201 | Router registration |
| 1b | `services/creditx-service/app/routes_compliance.py` | 191 | Database client acquisition |
| 1c | `services/creditx-service/app/routes_compliance.py` | 200 | Document INSERT execution |
| 1d | `services/shared/python/core_database.py` | 231 | Circuit breaker protected query |
| 1e | `services/creditx-service/app/routes_compliance.py` | 208 | Audit logging |
| 1f | `services/creditx-service/app/routes_compliance.py` | 213 | Response construction |

---

### Trace 2: AI Agent Execution with HITL Approval Gate

**Path:** `API → Agent Orchestrator → BaseAgent → AI Router → Event Bus`

```
Agent Execution with HITL Flow
├── API Gateway
│   └── POST /api/v1/agents/execute
│       └── routes_agents.py:108 [execute_agent()]
│
└── Agent Orchestrator
    └── core_agents.py:440 [orchestrator.execute()]
        ├── Line 436: get_agent() → Lookup from registry
        ├── Line 472: Create AgentTask
        └── Line 482: agent.run(task)
            │
            └── BaseAgent.run() Workflow
                ├── Line 249: validate_input()
                │
                ├── Line 254: check_hitl() → HITL Gate
                │   └── Line 188: event_bus.publish("agent-hitl")
                │       └── core_events.py:160 [xadd() to Dragonfly]
                │
                ├── Line 260: execute() → Business Logic
                │   └── Line 282: ai_router.complete()
                │       └── core_ai.py:485 → OpenAI/Anthropic/Local
                │
                └── Line 262: finalize()
                    └── Line 222: event_bus.publish("agent-tasks")
                        └── EventType.AGENT_TASK_COMPLETED
```

**Key Files:**
| Location | File | Line | Description |
|----------|------|------|-------------|
| 2a | `services/creditx-service/app/routes_agents.py` | 121 | Orchestrator singleton |
| 2b | `services/creditx-service/app/routes_agents.py` | 123 | Agent execution request |
| 2c | `services/shared/python/core_agents.py` | 482 | Agent workflow invocation |
| 2d | `services/shared/python/core_agents.py` | 254 | HITL gate check |
| 2e | `services/shared/python/core_agents.py` | 188 | HITL notification event |
| 2f | `services/shared/python/core_agents.py` | 260 | Agent logic execution |
| 2g | `services/shared/python/core_agents.py` | 282 | AI model completion |
| 2h | `services/shared/python/core_agents.py` | 222 | Task completion event |

---

### Trace 3: Threat Detection and AI Analysis

**Path:** `Threat Service → AI Router → PostgreSQL → Event Bus`

```
Threat Detection and AI Analysis Flow
├── Threat Service (FastAPI)
│   └── POST /api/v1/analyze
│       ├── main.py:220: get_ai_router() → Singleton
│       │   └── core_ai.py:593 [get_ai_router()]
│       │
│       ├── main.py:236: ai_router.complete()
│       │   └── core_ai.py:485 [complete()]
│       │       ├── Line 526: _select_model(capability)
│       │       ├── Line 528: _get_client(provider)
│       │       │   └── OpenAI / Anthropic / Local
│       │       └── Line 531: client.complete()
│       │           └── Response with tokens, cost, latency
│       │
│       └── main.py:247: json.loads(result.content)
│           └── Return ThreatAnalysisResponse
│
└── Alert Creation Flow
    └── POST /api/v1/alerts
        ├── main.py:183: db.fetchrow() → Insert alert
        └── main.py:201: event_bus.publish("threats")
            └── EventType.THREAT_DETECTED
```

**Key Files:**
| Location | File | Line | Description |
|----------|------|------|-------------|
| 3a | `services/threat-service/app/main.py` | 220 | AI Router initialization |
| 3b | `services/threat-service/app/main.py` | 236 | AI threat analysis |
| 3c | `services/threat-service/app/main.py` | 247 | Parse AI response |
| 3d | `services/threat-service/app/main.py` | 174 | Event bus connection |
| 3e | `services/threat-service/app/main.py` | 183 | Alert database insert |
| 3f | `services/threat-service/app/main.py` | 201 | Threat event publication |
| 3g | `services/shared/python/core_events.py` | 161 | Stream write (XADD) |

---

### Trace 4: Infrastructure Initialization and Connection Pooling

**Path:** `FastAPI Lifespan → Cache → Database → Event Bus`

```
Application Startup Sequence
├── FastAPI Lifespan Context
│   └── main.py:42 [lifespan()]
│       │
│       ├── Cache Initialization
│       │   └── main.py:55: get_cache()
│       │       └── core_cache.py:304 [get_cache()]
│       │           └── DragonflyCache.connect()
│       │               ├── Line 114: ConnectionPool creation
│       │               ├── Line 126: client.ping() verify
│       │               └── Line 128: logger.info("connected")
│       │
│       ├── Database Initialization
│       │   └── main.py:61: get_database()
│       │       └── core_database.py:319 [get_database()]
│       │           └── DatabaseClient.connect()
│       │               ├── Line 103: asyncpg.create_pool()
│       │               ├── Line 81: CircuitBreaker setup
│       │               └── Line 115: logger.info("connected")
│       │
│       └── Event Bus Initialization
│           └── get_event_bus(service_name)
│               └── core_events.py:301 [get_event_bus()]
│                   ├── Line 120: ConnectionPool creation
│                   └── Line 127: client.ping() verify
│
└── yield (app runs) → shutdown cleanup
```

**Key Files:**
| Location | File | Line | Description |
|----------|------|------|-------------|
| 4a | `services/creditx-service/app/main.py` | 55 | Cache singleton init |
| 4b | `services/shared/python/core_cache.py` | 114 | Dragonfly connection pool |
| 4c | `services/shared/python/core_cache.py` | 126 | Cache health verification |
| 4d | `services/creditx-service/app/main.py` | 61 | Database client init |
| 4e | `services/shared/python/core_database.py` | 103 | PostgreSQL pool creation |
| 4f | `services/shared/python/core_database.py` | 81 | Circuit breaker setup |
| 4g | `services/shared/python/core_events.py` | 127 | Event bus connection |

---

### Trace 5: Workflow Automation Trigger

**Path:** `Apps Service → Database → Event Bus`

```
Workflow Automation Trigger Flow
├── POST /api/v1/workflows/{id}/trigger
│   └── main.py:197 [trigger_workflow()]
│       ├── Line 204: get_database()
│       ├── Line 205: get_event_bus("apps-service")
│       │
│       ├── Database Operations
│       │   ├── Line 207: fetchrow() → Lookup workflow
│       │   ├── Line 221: fetchrow() → Create execution
│       │   └── Line 231: execute() → Update counters
│       │
│       └── Event Publishing
│           └── Line 238: event_bus.publish("workflows")
│               └── Event(EventType.WORKFLOW_STARTED, payload)
│
└── Response: WorkflowExecution model
```

**Key Files:**
| Location | File | Line | Description |
|----------|------|------|-------------|
| 5a | `services/apps-service/app/main.py` | 204 | Database connection |
| 5b | `services/apps-service/app/main.py` | 207 | Workflow lookup |
| 5c | `services/apps-service/app/main.py` | 221 | Execution record creation |
| 5d | `services/apps-service/app/main.py` | 231 | Workflow counter update |
| 5e | `services/apps-service/app/main.py` | 205 | Event bus acquisition |
| 5f | `services/apps-service/app/main.py` | 238 | Workflow started event |

---

### Trace 6: Stolen Device Reporting with Email Notification

**Path:** `Phones Service → Database → Event Bus → Spacemail`

```
Stolen Device Reporting Flow
├── POST /api/v1/devices/{id}/report
│   └── main.py:210 [report_device()]
│       ├── Line 218: get_database()
│       ├── Line 219: get_event_bus("phones-service")
│       │
│       ├── Database Operations
│       │   ├── Line 230: db.fetchrow() → Insert report
│       │   │   └── Record: report_type, location, police_report_number
│       │   └── Line 251: db.execute() → Update device status
│       │       └── SET status = 'stolen'/'lost'/'recovered'
│       │
│       └── Event Publishing
│           └── Line 259: event_bus.publish("devices")
│               └── Event(EventType.NOTIFICATION_REQUESTED)
│
└── Email Notification (async handler)
    └── core_spacemail.py:161 [SpacemailClient.send()]
        ├── Line 176: client.post("/messages")
        └── Line 188: logger.info() → message_id, recipients
```

**Key Files:**
| Location | File | Line | Description |
|----------|------|------|-------------|
| 6a | `services/phones-service/app/main.py` | 218 | Database client |
| 6b | `services/phones-service/app/main.py` | 230 | Report insert |
| 6c | `services/phones-service/app/main.py` | 251 | Device status update |
| 6d | `services/phones-service/app/main.py` | 219 | Event bus connection |
| 6e | `services/phones-service/app/main.py` | 259 | Notification event |
| 6f | `services/shared/python/core_spacemail.py` | 176 | Spacemail API call |
| 6g | `services/shared/python/core_spacemail.py` | 188 | Email delivery log |

---

### Trace 7: AI Model Selection and Multi-Provider Routing

**Path:** `AIRouter → Model Selection → Provider Client → Cache`

```
AI Model Selection and Execution Flow
├── core_ai.py:485 [AIRouter.complete()]
│   │
│   ├── Model Selection Phase
│   │   ├── Line 521: Check if specific model requested
│   │   └── Line 526: _select_model(capability, prefer_local, prefer_cheap)
│   │       └── Line 454: Filter by capability
│   │           └── AVAILABLE_MODELS filtering
│   │
│   ├── Cache-Aside Pattern
│   │   ├── Line 514: cache.get(f"ai:{cache_key}")
│   │   │   └── Return cached if hit
│   │   └── Line 543: cache.set() → Store result
│   │
│   ├── Provider Client Selection
│   │   └── Line 528: _get_client(provider)
│   │       ├── OPENAI → OpenAIClient.complete()
│   │       │   └── Line 249: client.chat.completions.create()
│   │       ├── ANTHROPIC → AnthropicClient.complete()
│   │       │   └── Line 324: client.messages.create()
│   │       └── LOCAL → LocalModelClient.complete()
│   │           └── Line 395: client.post("/v1/chat/completions")
│   │
│   └── Metrics & Failover
│       ├── Line 539: metrics.record(result)
│       └── Line 551-573: Automatic failover on error
```

**Available Models:**
| Model ID | Provider | Capabilities | Cost/1K (in/out) |
|----------|----------|--------------|------------------|
| gpt-4-turbo | OpenAI | reasoning, code, vision | $0.01 / $0.03 |
| gpt-4o-mini | OpenAI | fast_inference, code | $0.00015 / $0.0006 |
| claude-3-5-sonnet | Anthropic | reasoning, code, long_context | $0.003 / $0.015 |
| claude-3-haiku | Anthropic | fast_inference | $0.00025 / $0.00125 |
| qwen-2.5-7b | Local | fast_inference, code | $0.00 / $0.00 |

**Key Files:**
| Location | File | Line | Description |
|----------|------|------|-------------|
| 7a | `services/shared/python/core_ai.py` | 526 | Model selection logic |
| 7b | `services/shared/python/core_ai.py` | 454 | Capability filtering |
| 7c | `services/shared/python/core_ai.py` | 514 | Cache lookup |
| 7d | `services/shared/python/core_ai.py` | 528 | Provider client selection |
| 7e | `services/shared/python/core_ai.py` | 324 | Anthropic API call |
| 7f | `services/shared/python/core_ai.py` | 539 | Usage metrics tracking |
| 7g | `services/shared/python/core_ai.py` | 543 | Cache write |

---

### Trace 8: Service Health Check and Readiness Probes

**Path:** `Health Endpoint → Cache Check → Database Check → Circuit Breaker Status`

```
Service Health Check Flow
├── GET /health/ready
│   └── main.py:132 [readiness()]
│       │
│       ├── Cache Health Check
│       │   └── main.py:138: get_cache()
│       │       └── cache.health_check()
│       │           └── core_cache.py:145 [health_check()]
│       │               ├── Line 149: client.ping()
│       │               └── Line 150: Measure latency
│       │
│       ├── Database Health Check
│       │   └── main.py:145: get_database()
│       │       └── db.health_check()
│       │           └── core_database.py:127 [health_check()]
│       │               ├── Line 131: pool.acquire()
│       │               └── Line 132: SELECT 1
│       │
│       └── Aggregation
│           ├── Line 151: all(v == "healthy")
│           └── Return 200 or 503
│
└── GET /status (Detailed)
    └── main.py:171 [status()]
        ├── Line 195: circuit_breaker_status()
        ├── Line 181: cache_metrics.to_dict()
        └── Line 187: database_metrics.to_dict()
```

**Key Files:**
| Location | File | Line | Description |
|----------|------|------|-------------|
| 8a | `services/creditx-service/app/main.py` | 138 | Cache client retrieval |
| 8b | `services/creditx-service/app/main.py` | 139 | Cache health probe |
| 8c | `services/shared/python/core_cache.py` | 149 | Dragonfly ping |
| 8d | `services/creditx-service/app/main.py` | 145 | Database client retrieval |
| 8e | `services/shared/python/core_database.py` | 132 | Database query test |
| 8f | `services/creditx-service/app/main.py` | 151 | Health aggregation |
| 8g | `services/creditx-service/app/main.py` | 195 | Circuit breaker status |

---

### Trace 9: CopilotKit Integration Flow

**Path:** `Frontend → CopilotKit Route → Agent Execution → Response`

```
CopilotKit Integration Flow
├── Next.js Frontend
│   └── CopilotKit Chat Component
│       └── POST /api/copilotkit
│
└── apps/frontend/src/app/api/copilotkit/route.ts
    ├── Line 4: CopilotRuntime initialization
    │   └── Actions: executeAgent, listAgents
    │
    ├── Line 33: OpenAIAdapter configuration
    │   └── model: "gpt-4-turbo-preview"
    │
    └── Line 37: POST handler
        └── runtime.handleRequest(req, adapter)
            │
            └── Action: executeAgent
                └── fetch("/api/v1/agents/execute")
                    └── Backend agent execution
```

**Key Files:**
| Location | File | Line | Description |
|----------|------|------|-------------|
| 9a | `apps/frontend/src/app/api/copilotkit/route.ts` | 4 | Runtime initialization |
| 9b | `apps/frontend/src/app/api/copilotkit/route.ts` | 13 | executeAgent handler |
| 9c | `apps/frontend/src/app/api/copilotkit/route.ts` | 33 | OpenAI adapter |
| 9d | `apps/frontend/src/app/api/copilotkit/route.ts` | 37 | POST request handler |

---

## 🏗️ Service Details

### CreditX Service (Port 8000)

**Purpose:** Compliance automation, credit intelligence, document processing

**Entry Point:** `services/creditx-service/app/main.py`

**Routes:**
| Path | Method | Handler | Description |
|------|--------|---------|-------------|
| `/api/v1/compliance/documents` | GET | `list_documents` | List documents with pagination |
| `/api/v1/compliance/documents` | POST | `create_document` | Create compliance document |
| `/api/v1/compliance/documents/{id}` | GET | `get_document` | Get document (cache-aside) |
| `/api/v1/compliance/documents/{id}` | PATCH | `update_document` | Update document status |
| `/api/v1/compliance/sanctions/check` | POST | `check_sanctions` | Sanctions screening |
| `/api/v1/agents` | GET | `list_agents` | List available agents |
| `/api/v1/agents/execute` | POST | `execute_agent` | Execute agent task |
| `/api/v1/agents/hitl/approve` | POST | `approve_hitl` | HITL approval |
| `/api/v1/copilotkit` | POST | `copilotkit_handler` | CopilotKit integration |
| `/health/live` | GET | `liveness` | Kubernetes liveness |
| `/health/ready` | GET | `readiness` | Kubernetes readiness |
| `/metrics` | GET | `metrics` | Prometheus metrics |

---

### Threat Service (Port 8001)

**Purpose:** Global AI Alert Network, threat detection, security alerting

**Entry Point:** `services/threat-service/app/main.py`

**Routes:**
| Path | Method | Handler | Description |
|------|--------|---------|-------------|
| `/api/v1/alerts` | GET | `list_alerts` | List threat alerts |
| `/api/v1/alerts` | POST | `create_alert` | Create threat alert |
| `/api/v1/analyze` | POST | `analyze_threat` | AI-powered threat analysis |
| `/api/v1/packets/ingest` | POST | `ingest_packet` | Ingest network packet |
| `/api/v1/threats/active` | GET | `get_active_threats` | Get active threats |
| `/api/v1/threats/{id}` | GET | `get_threat_details` | Threat details |
| `/api/v1/threats/{id}/investigate` | POST | `investigate_threat` | Start investigation |
| `/api/v1/threats/{id}/resolve` | PATCH | `resolve_threat` | Resolve threat |
| `/api/v1/dashboard/real-time` | GET | `get_realtime_dashboard` | Real-time dashboard |

---

### Guardian Service (Port 8002)

**Purpose:** AI Endpoint Security, device management, incident response

**Entry Point:** `services/guardian-service/app/main.py`

**Routes:**
| Path | Method | Handler | Description |
|------|--------|---------|-------------|
| `/api/v1/telemetry/ingest` | POST | `ingest_telemetry` | Ingest endpoint telemetry |
| `/api/v1/endpoints/{tenant}` | GET | `get_endpoints` | List endpoints |
| `/api/v1/endpoints/{id}/details` | GET | `get_endpoint_details` | Endpoint details |
| `/api/v1/endpoints/{id}/isolate` | POST | `isolate_endpoint` | Isolate endpoint |
| `/api/v1/endpoints/{id}/restore` | POST | `restore_endpoint` | Restore endpoint |
| `/api/v1/incidents/active` | GET | `get_active_incidents` | Active incidents |
| `/api/v1/incidents/{id}` | GET | `get_incident_details` | Incident details |
| `/api/v1/incidents/{id}/resolve` | PATCH | `resolve_incident` | Resolve incident |
| `/api/v1/baselines/{id}/establish` | POST | `establish_baseline` | Establish baseline |
| `/api/v1/policies` | GET | `get_policies` | Security policies |
| `/api/v1/dashboard` | GET | `get_dashboard` | Guardian dashboard |

---

### Apps Service (Port 8003)

**Purpose:** 91-Apps Business Automation, workflow management

**Entry Point:** `services/apps-service/app/main.py`

**Routes:**
| Path | Method | Handler | Description |
|------|--------|---------|-------------|
| `/api/v1/workflows` | GET | `list_workflows` | List workflows |
| `/api/v1/workflows` | POST | `create_workflow` | Create workflow |
| `/api/v1/workflows/{id}/trigger` | POST | `trigger_workflow` | Trigger execution |
| `/api/v1/leads/score` | POST | `score_lead` | ML lead scoring |
| `/api/v1/leads` | GET | `get_leads` | List leads |
| `/api/v1/leads/{id}` | PATCH | `update_lead` | Update lead |
| `/api/v1/purchase-orders` | POST | `create_po` | Create PO |
| `/api/v1/emails/send` | POST | `send_email` | Send email |

---

### Phones Service (Port 8004)

**Purpose:** Stolen/Lost Device Recovery, tracking, chain-of-custody

**Entry Point:** `services/phones-service/app/main.py`

**Routes:**
| Path | Method | Handler | Description |
|------|--------|---------|-------------|
| `/api/v1/devices` | GET | `list_devices` | List tracked devices |
| `/api/v1/devices` | POST | `register_device` | Register device |
| `/api/v1/devices/{id}/report` | POST | `report_device` | Report lost/stolen |
| `/api/v1/devices/{id}/report-stolen` | POST | `report_stolen` | Report stolen |
| `/api/v1/devices/{id}/location/update` | POST | `update_location` | Update location |
| `/api/v1/devices/{id}/location/history` | GET | `get_location_history` | Location history |
| `/api/v1/devices/{id}/location/current` | GET | `get_current_location` | Current location |
| `/api/v1/devices/{id}/lock` | POST | `lock_device` | Remote lock |
| `/api/v1/devices/{id}/wipe` | POST | `wipe_device` | Remote wipe |
| `/api/v1/insurance/claim` | POST | `file_claim` | File insurance claim |
| `/api/v1/workflows/{id}` | GET | `get_recovery_workflow` | Recovery workflow |

---

## 🔧 Shared Libraries

### core_ai.py - Multi-Provider AI Router

```python
# Key Classes
AIProvider(Enum)           # openai, anthropic, local, auto
ModelCapability(Enum)      # reasoning, fast_inference, embedding, vision, code
ModelConfig                # Model configuration dataclass
Message                    # Chat message structure
CompletionResult           # AI completion result with tokens/cost/latency
UsageMetrics               # Track usage for cost management
OpenAIClient               # OpenAI provider implementation
AnthropicClient            # Anthropic provider implementation
LocalModelClient           # Local model (Qwen) implementation
AIRouter                   # Main router with automatic selection/failover

# Key Functions
get_ai_router()            # Get singleton router
quick_complete()           # Simple completion helper
```

### core_database.py - PostgreSQL Client

```python
# Key Classes
DatabaseMetrics            # Query count, errors, latency
DatabaseClient             # Main async client with circuit breaker

# Key Methods
connect()                  # Initialize connection pool
health_check()             # Readiness probe
acquire(tenant_id)         # Get connection with tenant schema
transaction(tenant_id)     # Transaction context manager
execute()                  # INSERT/UPDATE/DELETE
fetch()                    # SELECT multiple rows
fetchrow()                 # SELECT single row
fetchval()                 # SELECT single value
create_tenant_schema()     # Multi-tenant isolation
run_migrations()           # Apply SQL migrations

# Key Functions
get_database()             # Get singleton instance
```

### core_cache.py - Dragonfly Cache Client

```python
# Key Classes
CacheMetrics               # Hits, misses, latency
DragonflyCache             # Main async client with circuit breaker

# Key Methods
connect()                  # Initialize connection pool
health_check()             # Readiness probe
get(key)                   # Get with JSON decode
set(key, value, ttl)       # Set with JSON encode
delete(key)                # Delete key
delete_pattern(pattern)    # Delete by pattern
cache_aside(key, fetch_fn) # Cache-aside with stampede protection
publish(channel, message)  # Pub/sub publish
xadd(stream, data)         # Redis Streams add

# Key Functions
get_cache()                # Get singleton instance
```

### core_events.py - Event Bus (Redis Streams)

```python
# Key Classes
EventType(Enum)            # Standard event types
Event                      # Event structure with serialization
EventBus                   # Main async event bus client

# Key Methods
connect()                  # Initialize connection
publish(stream, event)     # Publish event to stream
subscribe(stream, handler) # Subscribe with consumer group
get_pending()              # Get unacked messages
claim_stale()              # Claim dead consumer messages
replay()                   # Replay events from stream

# Key Functions
get_event_bus(service_name) # Get singleton instance
```

### core_agents.py - Agent Orchestration Framework

```python
# Key Enums
AgentType                  # assistant, operator, ambassador
RiskLevel                  # low, medium, high, critical
Face                       # consumer, partner, internal
Engine                     # outcome, rights_trust, risk_security, market_capital, cross
AgentStatus                # idle, validating, executing, waiting_hitl, completed, failed

# Key Classes
AgentConfig                # Agent configuration from registry
AgentState(TypedDict)      # State passed through workflow
AgentTask                  # Represents execution task
BaseAgent(ABC)             # Abstract base for all agents
ExplainerAgent             # Cross-cutting explainer
NotificationAgent          # Cross-cutting notification
AgentOrchestrator          # Central orchestrator

# Key Methods (BaseAgent)
validate_input()           # Abstract - validate input
execute()                  # Abstract - business logic
check_hitl()               # Check HITL approval required
finalize()                 # Finalize execution
run()                      # Full workflow execution
complete_with_ai()         # Helper for AI completion

# Key Methods (AgentOrchestrator)
initialize()               # Load configs from database
get_available_agents(face) # Get face-visible agents
execute()                  # Execute agent task
approve_hitl()             # HITL approval

# Key Functions
get_orchestrator()         # Get singleton instance
```

### core_spacemail.py - Email Service Client

```python
# Key Classes
EmailPriority(Enum)        # low, normal, high, urgent
EmailStatus(Enum)          # queued, sent, delivered, opened, etc.
EmailRecipient             # Recipient with metadata
EmailMessage               # Full email message structure
SendResult                 # Send operation result
SpacemailClient            # Spacemail API client
NotificationTemplates      # Standard template IDs

# Key Methods
send(message)              # Send email with retry
send_template()            # Send using template
get_status(message_id)     # Get delivery status
health_check()             # Service health

# Key Functions
get_spacemail()            # Get singleton instance
```

---

## 🌐 API Gateway (apps/api)

**Entry Point:** `apps/api/src/index.ts`

**Middleware Stack:**
1. `helmet` - Security headers
2. `cors` - CORS configuration
3. `compression` - Response compression
4. `express.json` - JSON body parsing
5. `rateLimit` - Rate limiting (1000/15min)
6. `requestLogger` - Request logging
7. `authMiddleware` - JWT authentication

**Route Groups:**
| Path | Auth | Router | Description |
|------|------|--------|-------------|
| `/health` | No | `healthRoutes` | Health checks |
| `/api/v1/auth` | No | `authRoutes` | Authentication |
| `/api/v1/consumer` | Yes | `consumerRoutes` | Consumer OS routes |
| `/api/v1/partner` | Yes | `partnerRoutes` | Partner OS routes |
| `/api/v1/internal` | Yes | `internalRoutes` | Internal OS routes |
| `/api/v1/agents` | Yes | `agentRoutes` | Agent routes |

---

## 🎨 Frontend (apps/frontend)

**Framework:** Next.js 14 (App Router)

**Multi-Face Routing:**
```
src/app/
├── (consumer)/          # Consumer OS - Credit repair clients
│   ├── dashboard/
│   ├── disputes/
│   ├── documents/
│   └── settings/
├── (partner)/           # Partner OS - Partners & affiliates
│   ├── dashboard/
│   ├── clients/
│   ├── reports/
│   └── settings/
├── (internal)/          # Internal OS - Staff & admins
│   ├── dashboard/
│   ├── compliance/
│   ├── agents/
│   ├── users/
│   └── settings/
└── api/copilotkit/      # CopilotKit integration
```

**CopilotKit Integration:**
- Uses `OpenAIAdapter` with `gpt-4-turbo-preview`
- Actions: `executeAgent`, `listAgents`
- Connects to backend agent execution API

---

## 🤖 Agent Orchestrator (apps/agent)

**Framework:** FastAPI + LangGraph

**Entry Point:** `apps/agent/app/main.py`

**Configuration:** `apps/agent/app/config.py`
- LLM Provider: OpenAI (gpt-4-turbo-preview)
- Cache: Dragonfly
- Service URLs for all microservices

**Route Groups:**
| Prefix | Router | Description |
|--------|--------|-------------|
| `/health` | `health.router` | Health checks |
| `/api/v1/agents` | `agents.router` | Agent management |
| `/api/v1/executions` | `executions.router` | Execution tracking |
| `/api/v1/chat` | `chat.router` | Chat interface |

**Agent Registry:**
| Agent ID | Name | Engine | Capabilities |
|----------|------|--------|--------------|
| outcome_optimizer | Outcome Optimizer | outcome | credit_analysis, plan_generation |
| dispute_resolution | Dispute Resolution | rights_trust | dispute_filing, evidence_analysis |
| risk_assessor | Risk Assessment | risk_security | risk_scoring, fraud_detection |
| underwriting_agent | Underwriting | market_capital | application_review, decision_making |
| compliance_monitor | Compliance Monitor | rights_trust | audit_logging, policy_enforcement |

---

## 📊 Event Types

```python
class EventType(str, Enum):
    # Document Events
    DOCUMENT_CREATED = "document.created"
    DOCUMENT_UPDATED = "document.updated"
    DOCUMENT_APPROVED = "document.approved"
    DOCUMENT_REJECTED = "document.rejected"
    
    # Threat Events
    THREAT_DETECTED = "threat.detected"
    THREAT_RESOLVED = "threat.resolved"
    THREAT_ESCALATED = "threat.escalated"
    
    # Agent Events
    AGENT_TASK_STARTED = "agent.task.started"
    AGENT_TASK_COMPLETED = "agent.task.completed"
    AGENT_TASK_FAILED = "agent.task.failed"
    
    # Notification Events
    NOTIFICATION_REQUESTED = "notification.requested"
    NOTIFICATION_SENT = "notification.sent"
    
    # Workflow Events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
```

---

## 🔐 Multi-Tenancy

All requests carry tenant context via headers:
- `x-tenant-id` - Tenant identifier
- `x-face` - consumer | partner | internal
- `x-request-id` - Correlation ID
- `x-user-id` - User identifier

**Database Isolation:**
- Schema-per-tenant: `tenant_{tenant_id}`
- Automatic `SET search_path` on connection

---

## 📈 Observability

**Prometheus Metrics:**
- `creditx_requests_total` - HTTP request counter
- `creditx_request_latency_seconds` - Request latency histogram
- `apps_workflows_created_total` - Workflow counter
- `threat_alerts_created_total` - Alert counter by severity
- `guardian_endpoints_registered_total` - Endpoint counter
- `phones_devices_reported_total` - Device report counter

**Health Endpoints:**
- `/health/live` - Kubernetes liveness (process running)
- `/health/ready` - Kubernetes readiness (dependencies healthy)
- `/health/startup` - Kubernetes startup (initialization complete)
- `/status` - Detailed status with circuit breaker states

---

## 🚀 Deployment

**Platform:** Spaceship Hyperlift

**Required Environment Variables:**
| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | ✅ | App runtime LLM |
| `COPILOTKIT_API_KEY` | ✅ | Frontend AI chat |
| `DATABASE_URL` | ✅ | PostgreSQL connection |
| `CACHE_HOST` | ✅ | Dragonfly/Redis |
| `SPACEMAIL_API_KEY` | Optional | Email service |
| `JWT_PUBLIC_KEY` | ✅ | Auth verification |

**Manifests:** `infrastructure/spaceship/*.yaml`

---

*Built with Windsurf Cascade + Claude Opus 4*
