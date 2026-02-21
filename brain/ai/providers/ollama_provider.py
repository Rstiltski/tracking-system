"""
Brain AI Ollama Provider - Local LLM Support

Ollama allows running LLMs locally without cloud API keys.
Requires Ollama to be installed and running.

Installation:
    curl -fsSL https://ollama.ai/install.sh | sh
    ollama pull llama3

Usage:
    from brain.ai.providers.ollama_provider import OllamaProvider
    from brain.ai.models import ProviderConfig, AIProvider
    
    config = ProviderConfig(provider=AIProvider.OLLAMA, model="llama3")
    provider = OllamaProvider(config)
    provider.initialize()
    
    result = provider.generate("Why have I been tired?")
"""

import time
from typing import List, Optional, Dict, Any, AsyncGenerator
from brain.ai.models import ProviderConfig, GenerationResult
from brain.ai.providers.base import AIProviderBase


class OllamaProvider(AIProviderBase):
    """
    Ollama provider for local LLM inference.
    
    Ollama runs models locally, providing privacy and no API costs.
    No API key required.
    
    Attributes:
        config: Provider configuration
        client: Ollama client instance
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize Ollama provider.
        
        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.client = None
        self._embedding_model = "nomic-embed-text"  # Default embedding model
    
    def initialize(self) -> bool:
        """
        Initialize the Ollama connection.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            import ollama
            
            # Set host if specified
            host = self.config.ollama_host
            if host != "http://localhost:11434":
                ollama.host = host
            
            self.client = ollama
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
        Generate a response from Ollama.
        
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
                    error_message="Ollama not available. Please install: pip install ollama",
                    model=self.config.model,
                    provider="ollama"
                )
        
        # Type narrowing: after successful initialization, client is guaranteed non-None
        assert self.client is not None
        
        start_time = time.time()
        
        try:
            # Build messages
            messages = self.build_messages(prompt, context, system_prompt)
            
            # Get parameters
            temperature = kwargs.get('temperature', self.config.temperature)
            
            # Call Ollama
            response = self.client.chat(
                model=self.config.model,
                messages=messages,
                options={
                    'temperature': temperature,
                    'num_predict': self.config.max_tokens,
                }
            )
            
            latency = (time.time() - start_time) * 1000
            
            return GenerationResult(
                content=response['message']['content'],
                success=True,
                tokens_used=response.get('eval_count', 0) + response.get('prompt_eval_count', 0),
                latency_ms=latency,
                model=self.config.model,
                provider="ollama",
                finish_reason="stop"
            )
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return GenerationResult(
                content="",
                success=False,
                error_message=str(e),
                latency_ms=latency,
                model=self.config.model,
                provider="ollama",
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
        Generate a streaming response from Ollama.
        
        Args:
            prompt: User prompt/query
            context: Optional context documents for RAG
            system_prompt: Optional system prompt override
            
        Yields:
            Chunks of the response
        """
        if not self._is_initialized:
            if not self.initialize():
                yield "Error: Ollama not available"
                return
        
        # Type narrowing: after successful initialization, client is guaranteed non-None
        assert self.client is not None
        
        try:
            # Build messages
            messages = self.build_messages(prompt, context, system_prompt)
            
            # Stream from Ollama
            for chunk in self.client.chat(
                model=self.config.model,
                messages=messages,
                stream=True
            ):
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def embed(self, text: str) -> List[float]:
        """
        Generate an embedding vector for text.
        
        Uses nomic-embed-text model by default for embeddings.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not self._is_initialized:
            self.initialize()
        
        # Type narrowing: after initialization attempt, check client
        if self.client is None:
            return [0.0] * 768
        
        try:
            response = self.client.embeddings(
                model=self._embedding_model,
                prompt=text
            )
            return response['embedding']
        except Exception:
            # Fallback: return zero vector
            return [0.0] * 768
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        return [self.embed(text) for text in texts]
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in text.
        
        This is an approximation since Ollama doesn't expose tokenization directly.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated number of tokens
        """
        # Approximate: ~4 characters per token for English
        return len(text) // 4
    
    def list_models(self) -> List[str]:
        """
        List available models in Ollama.
        
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
            models = self.client.list()
            return [m['name'] for m in models.get('models', [])]
        except Exception:
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """
        Pull (download) a model from Ollama registry.
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            True if successful
        """
        if not self._is_initialized:
            if not self.initialize():
                return False
        
        # Type narrowing: after successful initialization, client is guaranteed non-None
        if self.client is None:
            return False
        
        try:
            self.client.pull(model_name)
            return True
        except Exception:
            return False
    
    def test_connection(self) -> bool:
        """
        Test the connection to Ollama.
        
        Returns:
            True if Ollama is running and accessible
        """
        try:
            if not self._is_initialized:
                if not self.initialize():
                    return False
            
            # Type narrowing: after successful initialization, client is guaranteed non-None
            if self.client is None:
                return False
            
            # Try to list models as connection test
            self.client.list()
            return True
        except Exception:
            return False
    
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
- Respond in a friendly, conversational tone"""