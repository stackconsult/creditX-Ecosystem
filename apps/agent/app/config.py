"""Configuration for the Agent Orchestrator."""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "creditx-agent-orchestrator"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    host: str = "0.0.0.0"
    port: int = 8010
    
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    llm_provider: str = "openai"
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096
    
    dragonfly_host: str = "localhost"
    dragonfly_port: int = 6379
    dragonfly_password: str = ""
    
    creditx_service_url: str = "http://localhost:8000"
    threat_service_url: str = "http://localhost:8001"
    guardian_service_url: str = "http://localhost:8002"
    apps_service_url: str = "http://localhost:8003"
    phones_service_url: str = "http://localhost:8004"
    
    hitl_timeout_seconds: int = 3600
    max_agent_iterations: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
