"""Base agent class with common functionality."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from utils.token_counter import token_counter
from utils.logger import get_logger


class BaseAgent(ABC):
    """Abstract base for all agents in the system."""
    
    def __init__(self, name: str, llm: Any = None):
        self.name = name
        self.llm = llm
        self.logger = get_logger(f"agent.{name}")
        self.metadata: Dict[str, Any] = {}
    
    def _record_tokens(self, text: str, operation: str = "", meta: Dict = None):
        """Record token consumption for this operation."""
        return token_counter.record(
            agent_name=self.name,
            text=text,
            operation=operation,
            metadata=meta or {}
        )
    
    async def _llm_call(self, prompt: str, system_prompt: str = "") -> str:
        """Make an LLM call and record tokens."""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        self._record_tokens(full_prompt, operation="llm_call")
        
        if self.llm:
            return await self.llm.generate(prompt, system_prompt)
        return ""
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the agent's primary task."""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metadata."""
        return {
            "name": self.name,
            "metadata": self.metadata,
            "token_summary": token_counter.get_agent_summary(self.name)
        }
