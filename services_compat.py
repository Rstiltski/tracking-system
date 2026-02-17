"""
Services Module - Compatibility Layer

This module provides compatibility for imports like 'import services'
by providing mock implementations.
"""

# Mock services module to satisfy imports
class MockService:
    def __init__(self, name):
        self.name = name

def get_service(service_name):
    """Get a mock service by name"""
    return MockService(service_name)

# Common services that might be imported
debug_console = MockService("debug_console")

# Additional services that may be imported
notifications = MockService("notifications")

# AI Provider stub for immune system worker
# This is a placeholder for the actual AI provider implementation
class AIProvider:
    """
    AI Provider stub for immune system integration.
    
    This provides a minimal interface that the immune system worker expects.
    In a full implementation, this would connect to an LLM service.
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.available = False  # Mark as unavailable by default
    
    async def complete(self, prompt: str, **kwargs):
        """
        Complete a prompt using AI.
        
        Returns None by default as this is a stub.
        Override or configure with a real provider for actual AI responses.
        """
        return None
    
    async def chat(self, messages: list, **kwargs):
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