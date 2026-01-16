"""
Enterprise Configuration Management
- Environment-based configuration
- Validation with Pydantic
- Feature flags
- Multi-tenant settings
"""
import os
from typing import Optional, List
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """PostgreSQL configuration."""
    url: str = Field(default="", alias="DATABASE_URL")
    min_connections: int = Field(default=5, alias="DB_MIN_CONNECTIONS")
    max_connections: int = Field(default=20, alias="DB_MAX_CONNECTIONS")
    command_timeout: float = Field(default=60.0, alias="DB_COMMAND_TIMEOUT")
    
    class Config:
        env_prefix = ""


class CacheSettings(BaseSettings):
    """Dragonfly cache configuration."""
    host: str = Field(default="dragonfly-cache.internal", alias="CACHE_HOST")
    port: int = Field(default=6379, alias="CACHE_PORT")
    db: int = Field(default=0, alias="CACHE_DB_MAIN")
    max_pool_size: int = Field(default=50, alias="CACHE_MAX_POOL_SIZE")
    timeout_ms: int = Field(default=5000, alias="CACHE_TIMEOUT_MS")
    key_prefix: str = Field(default="", alias="CACHE_KEY_PREFIX")
    
    class Config:
        env_prefix = ""


class AISettings(BaseSettings):
    """AI provider configuration."""
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    langchain_api_key: str = Field(default="", alias="LANGCHAIN_API_KEY")
    copilotkit_api_key: str = Field(default="", alias="COPILOTKIT_API_KEY")
    default_model: str = Field(default="gpt-4-turbo-preview", alias="DEFAULT_AI_MODEL")
    local_model_enabled: bool = Field(default=False, alias="LOCAL_MODEL_ENABLED")
    local_model_endpoint: str = Field(default="http://localhost:8080", alias="LOCAL_MODEL_ENDPOINT")
    
    class Config:
        env_prefix = ""


class ObservabilitySettings(BaseSettings):
    """Monitoring and logging configuration."""
    prometheus_endpoint: str = Field(default="http://prometheus.internal:9090", alias="PROMETHEUS_ENDPOINT")
    jaeger_agent_host: str = Field(default="jaeger.internal", alias="JAEGER_AGENT_HOST")
    jaeger_agent_port: int = Field(default=6831, alias="JAEGER_AGENT_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    
    class Config:
        env_prefix = ""


class SecuritySettings(BaseSettings):
    """Security and authentication configuration."""
    jwt_public_key: str = Field(default="", alias="JWT_PUBLIC_KEY")
    jwt_algorithm: str = Field(default="RS256", alias="JWT_ALGORITHM")
    oauth_issuer: str = Field(default="https://auth.ecosystem.ai", alias="OAUTH_ISSUER")
    encryption_key: str = Field(default="", alias="ENCRYPTION_KEY")
    
    class Config:
        env_prefix = ""


class SpaceshipSettings(BaseSettings):
    """Spaceship infrastructure configuration."""
    api_key: str = Field(default="", alias="SPACESHIP_API_KEY")
    hyperlift_api_key: str = Field(default="", alias="HYPERLIFT_API_KEY")
    cdn_url: str = Field(default="", alias="CDN_URL")
    spacemail_api_key: str = Field(default="", alias="SPACEMAIL_API_KEY")
    thunderbolt_domain: str = Field(default="", alias="THUNDERBOLT_DOMAIN")
    fastvpn_api_key: str = Field(default="", alias="FASTVPN_API_KEY")
    
    class Config:
        env_prefix = ""


class FeatureFlags(BaseSettings):
    """Feature toggles for gradual rollout."""
    creditx_enabled: bool = Field(default=True, alias="FEATURE_CREDITX_ENABLED")
    apps_91_enabled: bool = Field(default=True, alias="FEATURE_91_APPS_ENABLED")
    global_ai_alert_enabled: bool = Field(default=True, alias="FEATURE_GLOBAL_AI_ALERT_ENABLED")
    guardian_ai_enabled: bool = Field(default=True, alias="FEATURE_GUARDIAN_AI_ENABLED")
    stolen_phones_enabled: bool = Field(default=True, alias="FEATURE_STOLEN_PHONES_ENABLED")
    local_ai_enabled: bool = Field(default=False, alias="FEATURE_LOCAL_AI_ENABLED")
    
    class Config:
        env_prefix = ""


class TenantSettings(BaseSettings):
    """Multi-tenancy configuration."""
    default_tenant_id: str = Field(default="default", alias="DEFAULT_TENANT_ID")
    schema_prefix: str = Field(default="tenant_", alias="TENANT_SCHEMA_PREFIX")
    max_tenants: int = Field(default=1000, alias="MAX_TENANTS")
    
    class Config:
        env_prefix = ""


class Settings(BaseSettings):
    """Root configuration aggregating all settings."""
    
    app_name: str = Field(default="creditx-ecosystem", alias="APP_NAME")
    environment: str = Field(default="production", alias="NODE_ENV")
    region: str = Field(default="us-phx-1", alias="SPACES_REGION")
    debug: bool = Field(default=False, alias="DEBUG")
    
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    ai: AISettings = Field(default_factory=AISettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    spaceship: SpaceshipSettings = Field(default_factory=SpaceshipSettings)
    features: FeatureFlags = Field(default_factory=FeatureFlags)
    tenant: TenantSettings = Field(default_factory=TenantSettings)
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    class Config:
        env_prefix = ""
        env_nested_delimiter = "__"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
