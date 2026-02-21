"""
Brain AI Gemini Provider - Google Gemini LLM Support

Google Gemini models via API. Requires GOOGLE_API_KEY.

Usage:
    from brain.ai.providers.gemini_provider import GeminiProvider
    from brain.ai.models import ProviderConfig, AIProvider
    
    config = ProviderConfig(
        provider=AIProvider.GEMINI, 
        model="gemini-pro",
        api_key="..."
    )
    provider = GeminiProvider(config)
    provider.initialize()
    
    result = provider.generate("Why have I been tired?")
"""

import time
from typing import List, Optional, Dict, Any, AsyncGenerator
from brain.ai.models import ProviderConfig, GenerationResult
from brain.ai.providers.base import AIProviderBase


class GeminiProvider(AIProviderBase):
    """
    Gemini provider for cloud LLM inference.
    
    Requires API key. Supports Gemini Pro models.
    
    Attributes:
        config: Provider configuration
        client: Gemini client instance
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize Gemini provider.
        
        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.client = None
    
    def initialize(self) -> bool:
        """
        Initialize the Gemini client.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.config.api_key)
            self.client = genai.GenerativeModel(self.config.model)
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
        Generate a response from Gemini.
        
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
                    error_message="Gemini not available. Please install: pip install google-generativeai",
                    model=self.config.model,
                    provider="gemini"
                )
        
        # Type narrowing: after successful initialization, client is guaranteed non-None
        assert self.client is not None
        
        start_time = time.time()
        
        try:
            # Build full prompt with context
            full_prompt = prompt
            if context:
                context_str = "\n\n".join(context)
                full_prompt = f"Context:\n{context_str}\n\nQuestion: {prompt}"
            
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{full_prompt}"
            
            # Get parameters
            temperature = kwargs.get('temperature', self.config.temperature)
            
            # Call Gemini
            response = self.client.generate_content(
                full_prompt,
                generation_config={
                    'temperature': temperature,
                    'max_output_tokens': self.config.max_tokens,
                }
            )
            
            latency = (time.time() - start_time) * 1000
            
            return GenerationResult(
                content=response.text,
                success=True,
                tokens_used=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                latency_ms=latency,
                model=self.config.model,
                provider="gemini",
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
                provider="gemini",
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
        Generate a streaming response from Gemini.
        
        Args:
            prompt: User prompt/query
            context: Optional context documents for RAG
            system_prompt: Optional system prompt override
            
        Yields:
            Chunks of the response
        """
        if not self._is_initialized:
            if not self.initialize():
                yield "Error: Gemini not available"
                return
        
        # Type narrowing: after successful initialization, client is guaranteed non-None
        assert self.client is not None
        
        try:
            # Build full prompt with context
            full_prompt = prompt
            if context:
                context_str = "\n\n".join(context)
                full_prompt = f"Context:\n{context_str}\n\nQuestion: {prompt}"
            
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{full_prompt}"
            
            # Get parameters
            temperature = kwargs.get('temperature', self.config.temperature)
            
            # Stream from Gemini
            response = self.client.generate_content(
                full_prompt,
                generation_config={'temperature': temperature},
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        # Approximate: ~4 characters per token
        return len(text) // 4
    
    def test_connection(self) -> bool:
        """
        Test the connection to Gemini.
        
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
            
            # Simple test message
            self.client.generate_content("Hi")
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