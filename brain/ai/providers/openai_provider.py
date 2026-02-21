"""
Brain AI OpenAI Provider - Cloud LLM Support

OpenAI GPT models via API. Requires OPENAI_API_KEY.

Usage:
    from brain.ai.providers.openai_provider import OpenAIProvider
    from brain.ai.models import ProviderConfig, AIProvider
    
    config = ProviderConfig(
        provider=AIProvider.OPENAI, 
        model="gpt-4o-mini",
        api_key="sk-..."
    )
    provider = OpenAIProvider(config)
    provider.initialize()
    
    result = provider.generate("Why have I been tired?")
"""

import time
from typing import List, Optional, Dict, Any, AsyncGenerator
from brain.ai.models import ProviderConfig, GenerationResult
from brain.ai.providers.base import AIProviderBase


class OpenAIProvider(AIProviderBase):
    """
    OpenAI provider for cloud LLM inference.
    
    Requires API key. Supports GPT-4o, GPT-4o-mini, GPT-4, GPT-3.5-turbo.
    
    Attributes:
        config: Provider configuration
        client: OpenAI client instance
    """
    
    # Embedding model for OpenAI
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSION = 1536
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize OpenAI provider.
        
        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.client = None
    
    def initialize(self) -> bool:
        """
        Initialize the OpenAI client.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from openai import OpenAI
            
            # Create client with API key
            client_kwargs = {'api_key': self.config.api_key}
            
            # Add base URL if specified
            if self.config.base_url:
                client_kwargs['base_url'] = self.config.base_url
            
            # Add organization if specified
            if self.config.organization:
                client_kwargs['organization'] = self.config.organization
            
            self.client = OpenAI(**client_kwargs)
            self._is_initialized = True
            return True
            
        except ImportError:
            self._is_initialized = False
            return False
    
    def generate(
        self, 
        prompt: str, 
        context: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> GenerationResult:
        """
        Generate a response from OpenAI.
        
        Args:
            prompt: User prompt/query
            context: Optional context documents for RAG
            system_prompt: Optional system prompt override
            **kwargs: Additional parameters (temperature, etc.)
            
        Returns:
            GenerationResult with the response
        """
        if not self._is_initialized:
            if not self.initialize():
                return GenerationResult(
                    content="",
                    success=False,
                    error_message="OpenAI not available. Please install: pip install openai",
                    model=self.config.model,
                    provider="openai"
                )
        
        # Type narrowing: after successful initialization, client is guaranteed non-None
        assert self.client is not None
        
        start_time = time.time()
        
        try:
            # Build messages
            messages = self.build_messages(prompt, context, system_prompt)
            
            # Get parameters
            temperature = kwargs.get('temperature', self.config.temperature)
            max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            latency = (time.time() - start_time) * 1000
            
            # Extract usage info
            tokens_used = 0
            if response.usage:
                tokens_used = response.usage.total_tokens
            
            return GenerationResult(
                content=response.choices[0].message.content,
                success=True,
                tokens_used=tokens_used,
                latency_ms=latency,
                model=self.config.model,
                provider="openai",
                finish_reason=response.choices[0].finish_reason
            )
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            # Provide helpful error messages
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                error_msg = "Invalid API key. Please check your OPENAI_API_KEY."
            elif "rate_limit" in error_msg.lower():
                error_msg = "Rate limit exceeded. Please wait and try again."
            elif "insufficient_quota" in error_msg.lower():
                error_msg = "Insufficient quota. Please check your OpenAI billing."
            
            return GenerationResult(
                content="",
                success=False,
                error_message=error_msg,
                latency_ms=latency,
                model=self.config.model,
                provider="openai",
                finish_reason="error"
            )
    
    async def generate_stream(
        self, 
        prompt: str, 
        context: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from OpenAI.
        
        Args:
            prompt: User prompt/query
            context: Optional context documents for RAG
            system_prompt: Optional system prompt override
            
        Yields:
            Chunks of the response
        """
        if not self._is_initialized:
            if not self.initialize():
                yield "Error: OpenAI not available"
                return
        
        # Type narrowing: after successful initialization, client is guaranteed non-None
        assert self.client is not None
        
        try:
            # Build messages
            messages = self.build_messages(prompt, context, system_prompt)
            
            # Get parameters
            temperature = kwargs.get('temperature', self.config.temperature)
            
            # Stream from OpenAI
            stream = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def embed(self, text: str) -> List[float]:
        """
        Generate an embedding vector for text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not self._is_initialized:
            if not self.initialize():
                return [0.0] * self.EMBEDDING_DIMENSION
        
        # Type narrowing: after successful initialization, client is guaranteed non-None
        if self.client is None:
            return [0.0] * self.EMBEDDING_DIMENSION
        
        try:
            response = self.client.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception:
            return [0.0] * self.EMBEDDING_DIMENSION
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not self._is_initialized:
            if not self.initialize():
                return [[0.0] * self.EMBEDDING_DIMENSION for _ in texts]
        
        # Type narrowing: after successful initialization, client is guaranteed non-None
        if self.client is None:
            return [[0.0] * self.EMBEDDING_DIMENSION for _ in texts]
        
        try:
            response = self.client.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception:
            return [[0.0] * self.EMBEDDING_DIMENSION for _ in texts]
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in text using tiktoken.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        try:
            import tiktoken
            
            # Get encoding for the model
            encoding_name = "cl100k_base"  # Default for GPT-4/GPT-3.5-turbo
            if "gpt-4" in self.config.model or "gpt-3.5" in self.config.model:
                encoding_name = "cl100k_base"
            
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(text))
            
        except ImportError:
            # Fallback: approximate
            return len(text) // 4
    
    def test_connection(self) -> bool:
        """
        Test the connection to OpenAI.
        
        Returns:
            True if API key is valid
        """
        try:
            if not self._is_initialized:
                if not self.initialize():
                    return False
            
            # Type narrowing: after successful initialization, client is guaranteed non-None
            if self.client is None:
                return False
            
            # Try to list models as connection test
            self.client.models.list()
            return True
        except Exception:
            return False
    
    def list_available_models(self) -> List[str]:
        """
        List available models from OpenAI.
        
        Returns:
            List of model names
        """
        if not self._is_initialized:
            if not self.initialize():
                return []
        
        # Type narrowing: after successful initialization, client is guaranteed non-None
        if self.client is None:
            return []
        
        try:
            models = self.client.models.list()
            return [m.id for m in models.data if 'gpt' in m.id.lower()]
        except Exception:
            return []
    
    def _default_system_prompt(self) -> str:
        """Get the default system prompt for Veryfyn."""
        return """You are a helpful AI assistant integrated with a personal tracking system called Veryfyn.
Your role is to help users understand their habits, health, productivity, and goals.

Guidelines:
- Be concise but thorough
- Ground your responses in the provided context
- If you don't have enough information, say so
- Provide actionable recommendations when appropriate
- Be supportive and encouraging
- Avoid making medical or financial advice
- Respond in a friendly, conversational tone
- Use markdown formatting when helpful (bold, lists, etc.)"""