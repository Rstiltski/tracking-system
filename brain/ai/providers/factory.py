"""
Brain AI Provider Factory - Factory Pattern for Provider Instantiation

Creates provider instances based on configuration.
"""

from typing import Optional, Type
from brain.ai.models import AIProvider, ProviderConfig
from brain.ai.providers.base import AIProviderBase


class ProviderFactory:
    """
    Factory for creating AI provider instances.
    
    Usage:
        from brain.ai.providers import ProviderFactory
        from brain.ai.models import ProviderConfig, AIProvider
        
        config = ProviderConfig(provider=AIProvider.OLLAMA, model="llama3")
        provider = ProviderFactory.create(config)
    """
    
    # Registry of provider classes (populated on demand)
    _registry: dict = {}
    
    @classmethod
    def create(cls, config: ProviderConfig) -> AIProviderBase:
        """
        Create a provider instance based on configuration.
        
        Args:
            config: Provider configuration
            
        Returns:
            Instantiated provider
            
        Raises:
            ValueError: If provider is not supported or config is invalid
        """
        # Validate configuration
        if not config.validate():
            raise ValueError(
                f"Invalid configuration for {config.provider.value}: "
                f"API key required for cloud providers"
            )
        
        # Get provider class
        provider_class = cls._get_provider_class(config.provider)
        
        # Create instance
        return provider_class(config)
    
    @classmethod
    def _get_provider_class(cls, provider: AIProvider) -> Type[AIProviderBase]:
        """
        Get the provider class for a provider type.
        
        Uses lazy loading to avoid importing all providers unnecessarily.
        
        Args:
            provider: Provider type
            
        Returns:
            Provider class
        """
        # Check cache
        if provider in cls._registry:
            return cls._registry[provider]
        
        # Lazy load provider class
        if provider == AIProvider.OLLAMA:
            from brain.ai.providers.ollama_provider import OllamaProvider
            cls._registry[provider] = OllamaProvider
            return OllamaProvider
        
        elif provider == AIProvider.OPENAI:
            from brain.ai.providers.openai_provider import OpenAIProvider
            cls._registry[provider] = OpenAIProvider
            return OpenAIProvider
        
        elif provider == AIProvider.ANTHROPIC:
            try:
                from brain.ai.providers.anthropic_provider import AnthropicProvider  # type: ignore[import-unresolved]
                cls._registry[provider] = AnthropicProvider
                return AnthropicProvider
            except ImportError:
                raise ImportError(
                    "Anthropic provider not available. "
                    "Please install: pip install anthropic"
                )
        
        elif provider == AIProvider.GEMINI:
            try:
                from brain.ai.providers.gemini_provider import GeminiProvider  # type: ignore[import-unresolved]
                cls._registry[provider] = GeminiProvider
                return GeminiProvider
            except ImportError:
                raise ImportError(
                    "Gemini provider not available. "
                    "Please install: pip install google-generativeai"
                )
        
        elif provider == AIProvider.GROQ:
            try:
                from brain.ai.providers.groq_provider import GroqProvider  # type: ignore[import-unresolved]
                cls._registry[provider] = GroqProvider
                return GroqProvider
            except ImportError:
                raise ImportError(
                    "Groq provider not available. "
                    "Please install: pip install groq"
                )
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @classmethod
    def register(cls, provider: AIProvider, provider_class: Type[AIProviderBase]):
        """
        Register a custom provider class.
        
        Args:
            provider: Provider type enum
            provider_class: Provider class (must inherit from AIProviderBase)
        """
        if not issubclass(provider_class, AIProviderBase):
            raise TypeError(
                f"Provider class must inherit from AIProviderBase, "
                f"got {provider_class.__name__}"
            )
        cls._registry[provider] = provider_class
    
    @classmethod
    def list_providers(cls) -> list:
        """
        List all supported providers.
        
        Returns:
            List of provider names
        """
        return [p.value for p in AIProvider]
    
    @classmethod
    def get_default_config(cls, provider: AIProvider) -> ProviderConfig:
        """
        Get default configuration for a provider.
        
        Args:
            provider: Provider type
            
        Returns:
            Default ProviderConfig
        """
        return ProviderConfig(provider=provider)
    
    @classmethod
    def is_provider_available(cls, provider: AIProvider) -> bool:
        """
        Check if a provider is available (dependencies installed).
        
        Args:
            provider: Provider type
            
        Returns:
            True if provider can be instantiated
        """
        try:
            provider_class = cls._get_provider_class(provider)
            # Check if dependencies are available
            if provider == AIProvider.OLLAMA:
                import ollama  # type: ignore[import-unresolved]
            elif provider == AIProvider.OPENAI:
                import openai  # type: ignore[import-unresolved]
            elif provider == AIProvider.ANTHROPIC:
                import anthropic  # type: ignore[import-unresolved]
            elif provider == AIProvider.GEMINI:
                import google.generativeai  # type: ignore[import-unresolved]
            elif provider == AIProvider.GROQ:
                import groq  # type: ignore[import-unresolved]
            return True
        except ImportError:
            return False


# Convenience functions
def create_provider(config: ProviderConfig) -> AIProviderBase:
    """
    Create a provider instance.
    
    Args:
        config: Provider configuration
        
    Returns:
        AIProviderBase instance
    """
    return ProviderFactory.create(config)


def create_ollama_provider(model: str = "llama3", host: str = "http://localhost:11434") -> AIProviderBase:
    """
    Create an Ollama provider with default settings.
    
    Args:
        model: Model name
        host: Ollama host URL
        
    Returns:
        Ollama provider instance
    """
    config = ProviderConfig(
        provider=AIProvider.OLLAMA,
        model=model,
        ollama_host=host
    )
    return ProviderFactory.create(config)


def create_openai_provider(api_key: str, model: str = "gpt-4o-mini") -> AIProviderBase:
    """
    Create an OpenAI provider.
    
    Args:
        api_key: OpenAI API key
        model: Model name
        
    Returns:
        OpenAI provider instance
    """
    config = ProviderConfig(
        provider=AIProvider.OPENAI,
        model=model,
        api_key=api_key
    )
    return ProviderFactory.create(config)