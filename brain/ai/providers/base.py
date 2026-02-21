"""
Brain AI Providers Base - Abstract Base Class for AI Providers

This module defines the interface that all AI providers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncGenerator
from brain.ai.models import ProviderConfig, GenerationResult


class AIProviderBase(ABC):
    """
    Abstract base class for AI providers.
    
    All LLM providers (Ollama, OpenAI, Anthropic, etc.) must implement
    this interface for unified access.
    
    Attributes:
        config: Provider configuration
        name: Human-readable provider name
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize the provider.
        
        Args:
            config: Provider configuration
        """
        self.config = config
        self._is_initialized = False
    
    @property
    def name(self) -> str:
        """Get the provider name."""
        return self.config.provider.value
    
    @property
    def model(self) -> str:
        """Get the model name."""
        return self.config.model
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the provider connection.
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        context: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> GenerationResult:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt/query
            context: Optional context documents for RAG
            system_prompt: Optional system prompt override
            **kwargs: Additional provider-specific parameters
            
        Returns:
            GenerationResult with the response
        """
        pass
    
    @abstractmethod
    async def generate_stream(
        self, 
        prompt: str, 
        context: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the LLM.
        
        Args:
            prompt: User prompt/query
            context: Optional context documents for RAG
            system_prompt: Optional system prompt override
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Chunks of the response as they arrive
        """
        pass
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        Generate an embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        pass
    
    def build_messages(
        self, 
        prompt: str, 
        context: Optional[List[str]] = None,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build message list for chat completion.
        
        Args:
            prompt: User prompt
            context: Context documents
            system_prompt: System prompt
            
        Returns:
            List of message dictionaries
        """
        messages = []
        
        # System prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": self._default_system_prompt()})
        
        # Context
        if context:
            context_text = "\n\n".join(context)
            messages.append({
                "role": "system", 
                "content": f"Here is relevant context from the user's data:\n\n{context_text}"
            })
        
        # User prompt
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _default_system_prompt(self) -> str:
        """Get the default system prompt for this provider."""
        return """You are a helpful AI assistant integrated with a personal tracking system called Veryfyn.
Your role is to help users understand their habits, health, productivity, and goals.

Guidelines:
- Be concise but thorough
- Ground your responses in the provided context
- If you don't have enough information, say so
- Provide actionable recommendations when appropriate
- Be supportive and encouraging
- Avoid making medical or financial advice"""
    
    def test_connection(self) -> bool:
        """
        Test the connection to the provider.
        
        Returns:
            True if connection is working, False otherwise
        """
        try:
            result = self.generate("Hello")
            return result.success
        except Exception:
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the provider.
        
        Returns:
            Dictionary with provider information
        """
        return {
            "provider": self.name,
            "model": self.model,
            "initialized": self._is_initialized,
            "config": self.config.to_dict(),
        }


class EmbeddingProviderBase(ABC):
    """
    Abstract base class for embedding-only providers.
    
    Some providers (like sentence-transformers) only provide embeddings,
    not text generation.
    """
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name."""
        pass