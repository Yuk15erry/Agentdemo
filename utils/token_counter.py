"""
Token consumption tracker for monitoring daily usage across agents.
Supports tiktoken-based counting and estimation.
"""
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


@dataclass
class TokenUsage:
    """Single token usage record."""
    agent_name: str
    tokens: int
    timestamp: float = field(default_factory=time.time)
    operation: str = ""
    metadata: Dict = field(default_factory=dict)


class TokenCounter:
    """
    Real-time token consumption tracker.
    
    Tracks per-agent, per-session, and cumulative usage.
    Alerts when approaching daily thresholds.
    """
    
    def __init__(self, daily_limit: int = 10_000_000):
        self.daily_limit = daily_limit
        self.usage_records: List[TokenUsage] = []
        self._encoder = None
        
        if HAS_TIKTOKEN:
            try:
                self._encoder = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self._encoder = None
    
    def count(self, text: str) -> int:
        """Count tokens in text using tiktoken or fallback estimation."""
        if self._encoder:
            return len(self._encoder.encode(text))
        # Fallback: ~4 chars per token for English, ~2 for CJK
        return len(text) // 3
    
    def record(self, agent_name: str, text: str, operation: str = "", metadata: Dict = None):
        """Record token usage for an agent operation."""
        tokens = self.count(text)
        usage = TokenUsage(
            agent_name=agent_name,
            tokens=tokens,
            operation=operation,
            metadata=metadata or {}
        )
        self.usage_records.append(usage)
        return tokens
    
    def get_agent_summary(self, agent_name: str, hours: int = 24) -> Dict:
        """Get token summary for a specific agent."""
        cutoff = time.time() - (hours * 3600)
        records = [r for r in self.usage_records 
                   if r.agent_name == agent_name and r.timestamp >= cutoff]
        total = sum(r.tokens for r in records)
        return {
            "agent": agent_name,
            "total_tokens": total,
            "operations": len(records),
            "period_hours": hours,
            "avg_per_operation": total // max(len(records), 1)
        }
    
    def get_daily_summary(self) -> Dict:
        """Get complete daily summary across all agents."""
        cutoff = time.time() - 86400
        records = [r for r in self.usage_records if r.timestamp >= cutoff]
        
        by_agent = defaultdict(int)
        for r in records:
            by_agent[r.agent_name] += r.tokens
        
        total = sum(by_agent.values())
        return {
            "total_tokens": total,
            "by_agent": dict(by_agent),
            "daily_limit": self.daily_limit,
            "usage_percent": round((total / self.daily_limit) * 100, 2) if self.daily_limit else 0,
            "alert": total >= self.daily_limit * 0.85,
            "timestamp": datetime.now().isoformat()
        }
    
    def estimate_cost(self, model: str = "gpt-4o-mini") -> Dict:
        """Estimate cost based on token usage."""
        # Approximate pricing per 1M tokens (as of 2024)
        pricing = {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
        }
        rates = pricing.get(model, {"input": 1.00, "output": 4.00})
        
        summary = self.get_daily_summary()
        total_tokens = summary["total_tokens"]
        # Assume 70% input, 30% output split
        input_tokens = int(total_tokens * 0.7)
        output_tokens = total_tokens - input_tokens
        
        cost = (input_tokens / 1_000_000) * rates["input"] + \
               (output_tokens / 1_000_000) * rates["output"]
        
        return {
            "model": model,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(cost, 2),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
    
    def reset(self):
        """Reset all records."""
        self.usage_records.clear()


# Global instance
token_counter = TokenCounter(daily_limit=10_000_000)
