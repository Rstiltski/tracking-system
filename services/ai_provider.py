"""
AI Provider Service

Provides AI completion services for the tracking system.
This is a stub implementation that can be extended with real AI providers.
"""

from typing import Optional, Any, Dict, List


class AIProvider:
    """
    AI Provider for immune system integration.
    
    This provides a minimal interface that the immune system worker expects.
    In a full implementation, this would connect to an LLM service.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.available = False  # Mark as unavailable by default
    
    async def complete(self, prompt: str, **kwargs: Any) -> Optional[str]:
        """
        Complete a prompt using AI.
        
        Returns None by default as this is a stub.
        Override or configure with a real provider for actual AI responses.
        """
        return None
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Optional[str]:
        """
        Chat completion interface.
        
        Returns None by default as this is a stub.
        """
        return None
    
    def is_available(self) -> bool:
        """Check if AI provider is configured and available."""
        return self.available


# Default ai_provider instance (stub)
ai_provider = AIProvider()
