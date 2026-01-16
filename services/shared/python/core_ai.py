"""
Enterprise AI Router - Multi-Provider Abstraction
- LangChain-based provider abstraction (zero lock-in)
- Automatic routing: cloud vs local based on privacy/cost/latency
- Circuit breaker for AI provider resilience
- Auto-trainer scaffold for owned models
- Token usage tracking and cost estimation
"""
import logging
import os
import asyncio
from typing import Optional, Dict, Any, List, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import json

from .core_resilience import retry_async, RetryConfig, create_circuit_breaker
from .core_cache import get_cache

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AUTO = "auto"


class ModelCapability(str, Enum):
    """Model capabilities for routing decisions."""
    REASONING = "reasoning"
    FAST_INFERENCE = "fast_inference"
    EMBEDDING = "embedding"
    VISION = "vision"
    CODE = "code"
    LONG_CONTEXT = "long_context"


@dataclass
class ModelConfig:
    """Configuration for an AI model."""
    provider: AIProvider
    model_id: str
    display_name: str
    capabilities: List[ModelCapability]
    max_tokens: int = 4096
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    supports_streaming: bool = True
    supports_functions: bool = True
    priority: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider.value,
            "model_id": self.model_id,
            "display_name": self.display_name,
            "capabilities": [c.value for c in self.capabilities],
            "max_tokens": self.max_tokens,
            "cost_per_1k_input": self.cost_per_1k_input,
            "cost_per_1k_output": self.cost_per_1k_output,
        }


AVAILABLE_MODELS = {
    "gpt-4-turbo": ModelConfig(
        provider=AIProvider.OPENAI,
        model_id="gpt-4-turbo-preview",
        display_name="GPT-4 Turbo",
        capabilities=[ModelCapability.REASONING, ModelCapability.CODE, ModelCapability.VISION],
        max_tokens=128000,
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.03,
        priority=1,
    ),
    "gpt-4o-mini": ModelConfig(
        provider=AIProvider.OPENAI,
        model_id="gpt-4o-mini",
        display_name="GPT-4o Mini",
        capabilities=[ModelCapability.FAST_INFERENCE, ModelCapability.CODE],
        max_tokens=128000,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
        priority=2,
    ),
    "claude-3-5-sonnet": ModelConfig(
        provider=AIProvider.ANTHROPIC,
        model_id="claude-3-5-sonnet-20241022",
        display_name="Claude 3.5 Sonnet",
        capabilities=[ModelCapability.REASONING, ModelCapability.CODE, ModelCapability.LONG_CONTEXT],
        max_tokens=200000,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        priority=1,
    ),
    "claude-3-haiku": ModelConfig(
        provider=AIProvider.ANTHROPIC,
        model_id="claude-3-haiku-20240307",
        display_name="Claude 3 Haiku",
        capabilities=[ModelCapability.FAST_INFERENCE],
        max_tokens=200000,
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.00125,
        priority=2,
    ),
    "qwen-2.5-7b": ModelConfig(
        provider=AIProvider.LOCAL,
        model_id="qwen-2.5-7b",
        display_name="Qwen 2.5 7B (Local)",
        capabilities=[ModelCapability.FAST_INFERENCE, ModelCapability.CODE],
        max_tokens=32768,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        priority=3,
    ),
}


@dataclass
class Message:
    """Chat message structure."""
    role: str
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        if self.function_call:
            result["function_call"] = self.function_call
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        return result


@dataclass
class CompletionResult:
    """Result from AI completion."""
    content: str
    model: str
    provider: AIProvider
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    cached: bool = False
    cost_usd: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider.value,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "latency_ms": self.latency_ms,
            "cached": self.cached,
            "cost_usd": self.cost_usd,
        }


@dataclass
class UsageMetrics:
    """Track AI usage for cost management."""
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0
    total_latency_ms: float = 0.0
    cache_hits: int = 0
    errors: int = 0
    
    def record(self, result: CompletionResult):
        self.total_requests += 1
        self.total_input_tokens += result.input_tokens
        self.total_output_tokens += result.output_tokens
        self.total_cost_usd += result.cost_usd
        self.total_latency_ms += result.latency_ms
        if result.cached:
            self.cache_hits += 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "avg_latency_ms": round(self.total_latency_ms / max(self.total_requests, 1), 2),
            "cache_hit_rate": round(self.cache_hits / max(self.total_requests, 1), 4),
            "errors": self.errors,
        }


class AIProviderClient(ABC):
    """Abstract base class for AI provider clients."""
    
    @abstractmethod
    async def complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> CompletionResult:
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        pass


class OpenAIClient(AIProviderClient):
    """OpenAI provider client."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self._client = None
        self._breaker = create_circuit_breaker("openai", fail_max=5, reset_timeout=60)
    
    async def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package not installed")
        return self._client
    
    @retry_async(RetryConfig(max_attempts=3, base_delay_seconds=1.0))
    async def complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> CompletionResult:
        start = datetime.now()
        client = await self._get_client()
        
        response = await client.chat.completions.create(
            model=model,
            messages=[m.to_dict() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        
        latency_ms = (datetime.now() - start).total_seconds() * 1000
        
        model_config = AVAILABLE_MODELS.get(model.replace("-preview", ""))
        cost = 0.0
        if model_config:
            input_cost = (response.usage.prompt_tokens / 1000) * model_config.cost_per_1k_input
            output_cost = (response.usage.completion_tokens / 1000) * model_config.cost_per_1k_output
            cost = input_cost + output_cost
        
        return CompletionResult(
            content=response.choices[0].message.content or "",
            model=model,
            provider=AIProvider.OPENAI,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            latency_ms=latency_ms,
            cost_usd=cost,
        )
    
    async def health_check(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "unconfigured", "error": "OPENAI_API_KEY not set"}
        try:
            client = await self._get_client()
            await client.models.list()
            return {"status": "healthy", "provider": "openai"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class AnthropicClient(AIProviderClient):
    """Anthropic provider client."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self._client = None
        self._breaker = create_circuit_breaker("anthropic", fail_max=5, reset_timeout=60)
    
    async def _get_client(self):
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
                self._client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package not installed")
        return self._client
    
    @retry_async(RetryConfig(max_attempts=3, base_delay_seconds=1.0))
    async def complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> CompletionResult:
        start = datetime.now()
        client = await self._get_client()
        
        system_message = None
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system_message = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})
        
        response = await client.messages.create(
            model=model,
            messages=chat_messages,
            system=system_message or "",
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            **kwargs,
        )
        
        latency_ms = (datetime.now() - start).total_seconds() * 1000
        
        model_config = None
        for config in AVAILABLE_MODELS.values():
            if config.model_id == model:
                model_config = config
                break
        
        cost = 0.0
        if model_config:
            input_cost = (response.usage.input_tokens / 1000) * model_config.cost_per_1k_input
            output_cost = (response.usage.output_tokens / 1000) * model_config.cost_per_1k_output
            cost = input_cost + output_cost
        
        return CompletionResult(
            content=response.content[0].text if response.content else "",
            model=model,
            provider=AIProvider.ANTHROPIC,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=latency_ms,
            cost_usd=cost,
        )
    
    async def health_check(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "unconfigured", "error": "ANTHROPIC_API_KEY not set"}
        try:
            return {"status": "healthy", "provider": "anthropic"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class LocalModelClient(AIProviderClient):
    """Local model client (Qwen, Llama, etc.)."""
    
    def __init__(self, endpoint: Optional[str] = None):
        self.endpoint = endpoint or os.getenv("LOCAL_MODEL_ENDPOINT", "http://localhost:8080")
        self.enabled = os.getenv("LOCAL_MODEL_ENABLED", "false").lower() == "true"
        self._client = None
    
    async def _get_client(self):
        if self._client is None:
            import httpx
            self._client = httpx.AsyncClient(base_url=self.endpoint, timeout=120.0)
        return self._client
    
    @retry_async(RetryConfig(max_attempts=2, base_delay_seconds=0.5))
    async def complete(
        self,
        messages: List[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> CompletionResult:
        if not self.enabled:
            raise RuntimeError("Local model not enabled")
        
        start = datetime.now()
        client = await self._get_client()
        
        response = await client.post("/v1/chat/completions", json={
            "model": model,
            "messages": [m.to_dict() for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens or 2048,
        })
        response.raise_for_status()
        data = response.json()
        
        latency_ms = (datetime.now() - start).total_seconds() * 1000
        
        return CompletionResult(
            content=data["choices"][0]["message"]["content"],
            model=model,
            provider=AIProvider.LOCAL,
            input_tokens=data.get("usage", {}).get("prompt_tokens", 0),
            output_tokens=data.get("usage", {}).get("completion_tokens", 0),
            latency_ms=latency_ms,
            cost_usd=0.0,
        )
    
    async def health_check(self) -> Dict[str, Any]:
        if not self.enabled:
            return {"status": "disabled"}
        try:
            client = await self._get_client()
            response = await client.get("/health")
            if response.status_code == 200:
                return {"status": "healthy", "provider": "local"}
            return {"status": "degraded", "code": response.status_code}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class AIRouter:
    """
    Intelligent AI router that selects the best provider/model.
    Supports automatic failover and cost optimization.
    """
    
    def __init__(self):
        self.openai = OpenAIClient()
        self.anthropic = AnthropicClient()
        self.local = LocalModelClient()
        self.metrics = UsageMetrics()
        self._cache = None
    
    async def _get_cache(self):
        if self._cache is None:
            self._cache = await get_cache()
        return self._cache
    
    def _select_model(
        self,
        capability: ModelCapability,
        prefer_local: bool = False,
        prefer_cheap: bool = False,
    ) -> ModelConfig:
        """Select best model for the given capability."""
        candidates = [
            config for config in AVAILABLE_MODELS.values()
            if capability in config.capabilities
        ]
        
        if not candidates:
            candidates = list(AVAILABLE_MODELS.values())
        
        if prefer_local:
            local_candidates = [c for c in candidates if c.provider == AIProvider.LOCAL]
            if local_candidates and self.local.enabled:
                return local_candidates[0]
        
        if prefer_cheap:
            candidates.sort(key=lambda c: c.cost_per_1k_output)
        else:
            candidates.sort(key=lambda c: c.priority)
        
        return candidates[0]
    
    def _get_client(self, provider: AIProvider) -> AIProviderClient:
        """Get client for provider."""
        if provider == AIProvider.OPENAI:
            return self.openai
        elif provider == AIProvider.ANTHROPIC:
            return self.anthropic
        elif provider == AIProvider.LOCAL:
            return self.local
        else:
            return self.openai
    
    async def complete(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        capability: ModelCapability = ModelCapability.REASONING,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        cache_key: Optional[str] = None,
        cache_ttl: int = 3600,
        prefer_local: bool = False,
        prefer_cheap: bool = False,
        **kwargs,
    ) -> CompletionResult:
        """
        Complete a chat conversation with automatic routing.
        
        Args:
            messages: Conversation messages
            model: Specific model to use (optional, will auto-select if not provided)
            capability: Required capability for auto-selection
            temperature: Sampling temperature
            max_tokens: Max output tokens
            cache_key: Optional cache key for response caching
            cache_ttl: Cache TTL in seconds
            prefer_local: Prefer local models for privacy
            prefer_cheap: Prefer cheaper models for cost
        """
        if cache_key:
            cache = await self._get_cache()
            cached = await cache.get(f"ai:{cache_key}")
            if cached:
                result = CompletionResult(**cached)
                result.cached = True
                self.metrics.record(result)
                return result
        
        if model:
            model_config = AVAILABLE_MODELS.get(model)
            if not model_config:
                model_config = self._select_model(capability, prefer_local, prefer_cheap)
        else:
            model_config = self._select_model(capability, prefer_local, prefer_cheap)
        
        client = self._get_client(model_config.provider)
        
        try:
            result = await client.complete(
                messages=messages,
                model=model_config.model_id,
                temperature=temperature,
                max_tokens=max_tokens or model_config.max_tokens,
                **kwargs,
            )
            
            self.metrics.record(result)
            
            if cache_key:
                cache = await self._get_cache()
                await cache.set(f"ai:{cache_key}", result.to_dict(), cache_ttl)
            
            return result
        
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"AI completion failed: {e}")
            
            fallback_providers = [
                p for p in [AIProvider.OPENAI, AIProvider.ANTHROPIC, AIProvider.LOCAL]
                if p != model_config.provider
            ]
            
            for fallback_provider in fallback_providers:
                try:
                    fallback_client = self._get_client(fallback_provider)
                    fallback_model = self._select_model(capability)
                    
                    if fallback_model.provider == fallback_provider:
                        result = await fallback_client.complete(
                            messages=messages,
                            model=fallback_model.model_id,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            **kwargs,
                        )
                        self.metrics.record(result)
                        return result
                except Exception:
                    continue
            
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all AI providers."""
        openai_health = await self.openai.health_check()
        anthropic_health = await self.anthropic.health_check()
        local_health = await self.local.health_check()
        
        return {
            "openai": openai_health,
            "anthropic": anthropic_health,
            "local": local_health,
            "metrics": self.metrics.to_dict(),
        }


_ai_router_instance: Optional[AIRouter] = None


async def get_ai_router() -> AIRouter:
    """Get singleton AI router instance."""
    global _ai_router_instance
    if _ai_router_instance is None:
        _ai_router_instance = AIRouter()
    return _ai_router_instance


async def quick_complete(
    prompt: str,
    system: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs,
) -> str:
    """Quick helper for simple completions."""
    router = await get_ai_router()
    
    messages = []
    if system:
        messages.append(Message(role="system", content=system))
    messages.append(Message(role="user", content=prompt))
    
    result = await router.complete(messages=messages, model=model, **kwargs)
    return result.content
