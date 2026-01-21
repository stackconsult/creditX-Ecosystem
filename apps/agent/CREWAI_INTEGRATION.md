# CrewAI Integration with CopilotKit

This document describes the integration of CrewAI SDK with CopilotKit in the CreditX Agent Orchestrator.

## Overview

The integration allows you to:
- Define CrewAI agents (both Crew-based and Flow-based)
- Execute agents through CopilotKit
- Stream state and messages to CopilotKit
- Emit tool calls from CrewAI agents

## Architecture

### Components

1. **Agent Configuration** (`app/crewai_agents/config.py`)
   - Defines CrewAI agents and their capabilities
   - Configures both Crew-based and Flow-based agents
   - Sets up agent registry for CopilotKit

2. **Service Layer** (`app/crewai_agents/service.py`)
   - Manages CrewAI agent lifecycle
   - Handles CopilotKit integration
   - Provides streaming capabilities

3. **API Routes** (`app/routes/copilotkit.py`)
   - Exposes REST endpoints for CopilotKit
   - Handles agent execution requests
   - Provides streaming via SSE

### Available Agents

| Agent Name | Type | Description | Capabilities |
|------------|------|-------------|--------------|
| credit_optimizer | Crew | Optimizes credit scores | credit_analysis, score_optimization |
| dispute_handler | Crew | Handles credit disputes | dispute_filing, bureau_communication |
| risk_assessor | Crew | Assesses credit risk | risk_scoring, fraud_detection |
| underwriter | Crew | Performs underwriting | application_review, decision_making |
| credit_optimizer_flow | Flow | Flow-based optimization | Multi-step process |

## API Endpoints

### Execute Agent
```http
POST /api/v1/copilotkit/execute
Content-Type: application/json

{
  "agent_name": "credit_optimizer",
  "input_data": {
    "credit_score": "650",
    "goal": "improve_score"
  }
}
```

### List Agents
```http
GET /api/v1/copilotkit/agents
```

### Stream Agent Execution
```http
POST /api/v1/copilotkit/stream
Content-Type: application/json

{
  "agent_name": "credit_optimizer_flow",
  "input_data": {...}
}
```

### Emit Tool Call
```http
POST /api/v1/copilotkit/tools/SearchTool
Content-Type: application/json

{
  "query": "credit repair tips"
}
```

### Emit Message
```http
POST /api/v1/copilotkit/message
Content-Type: application/json

{
  "message": "Step 1 of 5 completed"
}
```

## CopilotKit Integration Functions

### copilotkit_predict_state
Streams state updates to CopilotKit:
```python
await copilotkit_predict_state({
    "status": "processing",
    "progress": 50,
    "current_step": "analysis"
})
```

### copilotkit_emit_message
Emits a message to CopilotKit:
```python
await copilotkit_emit_message("Analyzing credit report...")
```

### copilotkit_emit_tool_call
Emits a tool call to CopilotKit:
```python
await copilotkit_emit_tool_call(
    name="SearchTool",
    args={"query": "credit laws"}
)
```

## Testing

Run the test script to verify integration:
```bash
cd apps/agent
python test_crewai.py
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for CrewAI LLM integration
- `ANTHROPIC_API_KEY`: Optional, for Claude models

### Dependencies
- `crewai>=0.63.0`
- `copilotkit[crewai]>=0.4.0`
- `sse-starlette>=1.6.0`

## Usage Examples

### Executing a Crew-based Agent
```python
from app.crewai_agents.service import crewai_service

result = await crewai_service.execute_agent(
    agent_name="credit_optimizer",
    input_data={
        "credit_report": "...",
        "goal": "improve_score"
    },
    tenant_id="tenant_123"
)
```

### Executing a Flow-based Agent
```python
result = await crewai_service.execute_agent(
    agent_name="credit_optimizer_flow",
    input_data={
        "credit_score": "650",
        "target_score": "750"
    },
    tenant_id="tenant_123"
)
```

## Multi-Tenancy

All agent executions include tenant context:
- `x-tenant-id`: Tenant identifier
- `x-face`: Application face (consumer/partner/internal)
- `x-request-id`: Request correlation ID

## Error Handling

The integration provides comprehensive error handling:
- Agent not found errors
- Execution failures
- CopilotKit connection issues
- Validation errors

## Monitoring

All operations are logged with structured logging:
- Agent execution start/completion
- State transitions
- Error conditions
- Performance metrics

## Security

- Input validation on all endpoints
- Tenant isolation
- Request context propagation
- Secure API key handling
