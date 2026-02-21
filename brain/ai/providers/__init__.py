"""
Brain AI Providers - Multi-Provider LLM Support

This module provides a unified interface for multiple LLM providers:
- Ollama (local, no API key required)
- OpenAI (cloud)
- Anthropic (cloud)
- Google Gemini (cloud)
- Groq (cloud)

All providers implement the AIProviderBase interface.

Usage:
    from brain.ai.providers import ProviderFactory
    from brain.ai.models import ProviderConfig, AIProvider
    
    # Create provider
    config = ProviderConfig(provider=AIProvider.OLLAMA, model="llama3")
    provider = ProviderFactory.create(config)
    
    # Generate response
    result = provider.generate("Why have I been tired?", context=["Sleep data..."])
    
    # Generate embedding
    embedding = provider.embed("I completed my workout")
"""

from brain.ai.providers.base import AIProviderBase
from brain.ai.providers.factory import ProviderFactory

__all__ = [
    'AIProviderBase',
    'ProviderFactory',
]

__version__ = '1.0.0'