"""
LLM Simulator for demo mode — provides realistic responses without API calls.
Enables full system demonstration without requiring API keys.
"""
import asyncio
import random
from typing import Optional


class LLMSimulator:
    """
    Simulates LLM responses for demo purposes.
    In production, replace with actual OpenAI/Anthropic client.
    """
    
    def __init__(self, provider: str = "demo"):
        self.provider = provider
        self.call_count = 0
        self.total_tokens_simulated = 0
    
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        """Simulate an LLM generation call with realistic delay."""
        # Simulate network latency
        await asyncio.sleep(random.uniform(0.3, 1.2))
        
        self.call_count += 1
        # Estimate tokens
        estimated_tokens = len(prompt) // 3 + len(system_prompt) // 3
        self.total_tokens_simulated += estimated_tokens
        
        # Return a realistic acknowledgment
        return self._get_contextual_response(prompt, system_prompt)
    
    def _get_contextual_response(self, prompt: str, system_prompt: str) -> str:
        """Generate context-aware simulated response."""
        prompt_lower = prompt.lower()
        
        if "sentiment" in prompt_lower:
            return "Analysis shows predominantly mixed sentiment with key pain points around battery life and comfort."
        elif "critique" in prompt_lower or "evaluate" in prompt_lower:
            return "The copy shows strong technical accuracy but could benefit from more emotional appeal and social proof elements."
        elif "pain point" in prompt_lower:
            return "Top pain points identified: battery longevity, fit security, and Bluetooth stability."
        elif "localize" in prompt_lower or "translate" in prompt_lower:
            return "Localization complete with cultural adaptations for target market."
        elif "classify" in prompt_lower or "intent" in prompt_lower:
            return "Intent classified based on keyword and context analysis."
        else:
            return "Analysis complete. Results compiled successfully."
    
    def get_stats(self) -> dict:
        return {
            "provider": self.provider,
            "total_calls": self.call_count,
            "simulated_tokens": self.total_tokens_simulated
        }
