"""LLM service for agent interactions."""
import structlog
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class LLMService:
    """LLM service supporting multiple providers."""
    
    def __init__(self):
        self._llm = self._create_llm()
    
    def _create_llm(self):
        """Create LLM instance based on config."""
        if settings.llm_provider == "openai":
            return ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                api_key=settings.openai_api_key,
            )
        elif settings.llm_provider == "anthropic":
            return ChatAnthropic(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                api_key=settings.anthropic_api_key,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """Send chat messages to LLM."""
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append(SystemMessage(content=system_prompt))
        
        for msg in messages:
            if msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted_messages.append(AIMessage(content=msg["content"]))
        
        try:
            response = await self._llm.ainvoke(formatted_messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from a single prompt."""
        return await self.chat([{"role": "user", "content": prompt}], system_prompt)
