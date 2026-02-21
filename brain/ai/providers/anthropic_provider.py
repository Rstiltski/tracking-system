"""
Brain AI Anthropic Provider - Claude LLM Support

Anthropic Claude models via API. Requires ANTHROPIC_API_KEY.

Usage:
    from brain.ai.providers.anthropic_provider import AnthropicProvider
    from brain.ai.models import ProviderConfig, AIProvider
    
    config = ProviderConfig(
        provider=AIProvider.ANTHROPIC, 
        model="claude-3-sonnet-20240229",
        api_key="sk-ant-..."
    )
    provider = AnthropicProvider(config)
    provider.initialize()
    
    result = provider.generate("Why have I been tired?")
"""

import time
from typing import List, Optional, Dict, Any, AsyncGenerator
from brain.ai.models import ProviderConfig, GenerationResult
from brain.ai.providers.base import AIProviderBase


class AnthropicProvider(AIProviderBase):
    """
    Anthropic provider for cloud LLM inference.
    
    Requires API key. Supports Claude 3 models.
    
    Attributes:
        config: Provider configuration
        client: Anthropic client instance
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize Anthropic provider.
        
        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.client = None
    
    def initialize(self) -> bool:
        """
        Initialize the Anthropic client.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            import anthropic
            
            self.client = anthropic.Anthropic(api_key=self.config.api_key)
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
        Generate a response from Anthropic.
        
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
                    error_message="Anthropic not available. Please install: pip install anthropic",
                    model=self.config.model,
                    provider="anthropic"
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
            
            # Call Anthropic
            response = self.client.messages.create(
                model=self.config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            latency = (time.time() - start_time) * 1000
            
            return GenerationResult(
                content=response.content[0].text,
                success=True,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                latency_ms=latency,
                model=self.config.model,
                provider="anthropic",
                finish_reason=response.stop_reason
            )
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return GenerationResult(
                content="",
                success=False,
                error_message=str(e),
                latency_ms=latency,
                model=self.config.model,
                provider="anthropic",
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
        Generate a streaming response from Anthropic.
        
        Args:
            prompt: User prompt/query
            context: Optional context documents for RAG
            system_prompt: Optional system prompt override
            
        Yields:
            Chunks of the response
        """
        if not self._is_initialized:
            if not self.initialize():
                yield "Error: Anthropic not available"
                return
        
        # Type narrowing: after successful initialization, client is guaranteed non-None
        assert self.client is not None
        
        try:
            # Build messages
            messages = self.build_messages(prompt, context, system_prompt)
            
            # Get parameters
            temperature = kwargs.get('temperature', self.config.temperature)
            
            # Stream from Anthropic
            with self.client.messages.stream(
                model=self.config.model,
                messages=messages,
                temperature=temperature,
            ) as stream:
                for text in stream.text_stream:
                    yield text
                    
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
        Test the connection to Anthropic.
        
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
            self.client.messages.create(
                model=self.config.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
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