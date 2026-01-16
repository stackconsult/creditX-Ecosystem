"""Main FastAPI application for the Agent Orchestrator."""
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.routes import agents, executions, chat, health
from app.services.cache import CacheService


logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Agent Orchestrator", version=settings.app_version)
    
    cache = CacheService()
    await cache.connect()
    app.state.cache = cache
    
    yield
    
    await cache.disconnect()
    logger.info("Agent Orchestrator shutdown complete")


app = FastAPI(
    title="CreditX Agent Orchestrator",
    description="LangGraph-based AI agent system for CreditX ecosystem",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_context(request: Request, call_next):
    """Add request context for logging."""
    tenant_id = request.headers.get("x-tenant-id", "default")
    face = request.headers.get("x-face", "internal")
    
    structlog.contextvars.bind_contextvars(
        tenant_id=tenant_id,
        face=face,
        path=request.url.path,
    )
    
    response = await call_next(request)
    return response


app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(executions.router, prefix="/api/v1/executions", tags=["Executions"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
