"""
Brain AI Assistant - Main AI Assistant Class

The main AI Assistant class that combines all components:
- Multi-provider LLM support
- RAG context retrieval
- Chat session management
- Prompt building

Usage:
    from brain.ai.assistant import AIAssistant
    from brain.ai.models import ProviderConfig, AIProvider
    
    config = ProviderConfig(provider=AIProvider.OLLAMA, model="llama3")
    assistant = AIAssistant(config)
    
    response = assistant.chat("How am I doing with my habits?")
    print(response.content)
"""

from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime
import uuid

from brain.ai.models import ProviderConfig, AIProvider, GenerationResult
from brain.ai.providers.factory import ProviderFactory
from brain.ai.vector_store import VectorStore
from brain.ai.context_retriever import ContextRetriever, RetrievedContext
from brain.ai.chat_session import ChatSession, ChatSessionManager, MessageRole
from brain.ai.prompts import SystemPromptBuilder


class AIAssistant:
    """
    Main AI Assistant for Veryfyn.
    
    Combines:
    - Multi-provider LLM support (Ollama, OpenAI, Anthropic, etc.)
    - RAG context retrieval from vector store
    - Chat session management with persistence
    - Dynamic prompt building
    
    Usage:
        # Simple usage
        assistant = AIAssistant()
        response = assistant.chat("Hello!")
        
        # With configuration
        config = ProviderConfig(provider=AIProvider.OPENAI, model="gpt-4o")
        assistant = AIAssistant(config)
        response = assistant.chat("Analyze my habits")
    """
    
    def __init__(
        self,
        config: Optional[ProviderConfig] = None,
        vector_store: Optional[VectorStore] = None,
        session_manager: Optional[ChatSessionManager] = None
    ):
        """
        Initialize the AI Assistant.
        
        Args:
            config: Provider configuration (defaults to Ollama)
            vector_store: VectorStore for RAG retrieval
            session_manager: Session persistence manager
        """
        # Provider configuration
        self.config = config or ProviderConfig(
            provider=AIProvider.OLLAMA,
            model="llama3"
        )
        
        # Components
        self._provider = None
        self._vector_store = vector_store
        self._session_manager = session_manager or ChatSessionManager()
        self._context_retriever = ContextRetriever(vector_store) if vector_store else None
        
        # Current session
        self._session: Optional[ChatSession] = None
        
        # User profile for context
        self._user_profile: Dict[str, Any] = {}
    
    @property
    def provider(self):
        """Get the LLM provider."""
        if self._provider is None:
            self._provider = ProviderFactory.create(self.config)
        return self._provider
    
    @property
    def session(self) -> ChatSession:
        """Get the current chat session."""
        if self._session is None:
            self._session = ChatSession(session_id=str(uuid.uuid4()))
        return self._session
    
    def initialize(self) -> bool:
        """
        Initialize all components.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialize provider
            if not self.provider.initialize():
                return False
            
            # Initialize vector store if provided
            if self._vector_store and hasattr(self._vector_store, 'initialize'):
                if not self._vector_store.initialize():
                    pass  # Non-fatal, continue without RAG
            
            # Initialize context retriever
            if self._vector_store:
                self._context_retriever = ContextRetriever(self._vector_store)
            
            return True
            
        except Exception as e:
            print(f"Error initializing assistant: {e}")
            return False
    
    def set_user_profile(self, profile: Dict[str, Any]) -> None:
        """
        Set the user profile for context.
        
        Args:
            profile: User profile dictionary
        """
        self._user_profile = profile
    
    def start_session(self, session_id: Optional[str] = None) -> ChatSession:
        """
        Start a new chat session.
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            New ChatSession instance
        """
        if session_id:
            # Try to load existing session
            existing = self._session_manager.load_session(session_id)
            if existing:
                self._session = existing
                return self._session
        
        # Create new session
        self._session = ChatSession(
            session_id=session_id or str(uuid.uuid4())
        )
        return self._session
    
    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Load a previous session.
        
        Args:
            session_id: Session ID to load
            
        Returns:
            ChatSession if found, None otherwise
        """
        self._session = self._session_manager.load_session(session_id)
        return self._session
    
    def save_session(self) -> bool:
        """
        Save the current session.
        
        Returns:
            True if successful
        """
        if self._session is None:
            return False
        return self._session_manager.save_session(self._session)
    
    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List recent sessions.
        
        Args:
            limit: Maximum sessions to return
            
        Returns:
            List of session summaries
        """
        return self._session_manager.list_sessions(limit)
    
    def _build_context(self, query: str) -> str:
        """
        Build context string for the query.
        
        Args:
            query: User query
            
        Returns:
            Context string
        """
        if not self._context_retriever:
            return ""
        
        # Retrieve relevant context
        contexts = self._context_retriever.retrieve(
            query=query,
            n_results=5
        )
        
        if not contexts:
            return ""
        
        return self._context_retriever.build_context_string(contexts)
    
    def _build_system_prompt(self, context: str = "") -> str:
        """
        Build the system prompt.
        
        Args:
            context: Context string to include
            
        Returns:
            System prompt string
        """
        return SystemPromptBuilder.build(
            context=context,
            user_profile=self._user_profile
        )
    
    def chat(
        self,
        message: str,
        include_context: bool = True,
        max_context_messages: int = 20
    ) -> GenerationResult:
        """
        Send a message and get a response.
        
        Args:
            message: User message
            include_context: Whether to include RAG context
            max_context_messages: Maximum messages in context window
            
        Returns:
            GenerationResult with response
        """
        try:
            # Add user message to session
            self.session.add_message(MessageRole.USER, message)
            
            # Build context
            context = ""
            if include_context:
                context = self._build_context(message)
            
            # Build system prompt
            system_prompt = self._build_system_prompt(context)
            
            # Get messages for LLM
            messages = self.session.get_messages_for_llm(max_messages=max_context_messages)
            
            # Add system prompt
            messages.insert(0, {
                "role": "system",
                "content": system_prompt
            })
            
            # Generate response
            result = self.provider.generate(
                prompt=message,
                context=[m["content"] for m in messages]
            )
            
            # Add response to session
            if result.success:
                self.session.add_message(MessageRole.ASSISTANT, result.content)
            else:
                error_msg = f"I apologize, but I encountered an error: {result.error_message}"
                self.session.add_message(MessageRole.ASSISTANT, error_msg)
            
            return result
            
        except Exception as e:
            # Create error result
            error_result = GenerationResult(
                content=f"I apologize, but an error occurred: {str(e)}",
                success=False,
                error_message=str(e)
            )
            self.session.add_message(MessageRole.ASSISTANT, error_result.content)
            return error_result
    
    def chat_with_context(
        self,
        message: str,
        source_types: Optional[List[str]] = None,
        n_context: int = 5
    ) -> GenerationResult:
        """
        Chat with specific context sources.
        
        Args:
            message: User message
            source_types: Types of sources to include
            n_context: Number of context items
            
        Returns:
            GenerationResult with response
        """
        try:
            # Add user message
            self.session.add_message(MessageRole.USER, message)
            
            # Build context with specific sources
            context = ""
            if self._context_retriever:
                contexts = self._context_retriever.retrieve(
                    query=message,
                    n_results=n_context,
                    source_types=source_types
                )
                context = self._context_retriever.build_context_string(contexts)
            
            # Build system prompt
            system_prompt = self._build_system_prompt(context)
            
            # Get messages
            messages = self.session.get_messages_for_llm()
            messages.insert(0, {"role": "system", "content": system_prompt})
            
            # Generate
            result = self.provider.generate(
                prompt=message,
                context=[m["content"] for m in messages]
            )
            
            if result.success:
                self.session.add_message(MessageRole.ASSISTANT, result.content)
            
            return result
            
        except Exception as e:
            return GenerationResult(
                content=f"Error: {str(e)}",
                success=False,
                error_message=str(e)
            )
    
    def clear_session(self) -> None:
        """Clear the current session messages."""
        if self._session:
            self._session.clear_messages()
    
    def new_session(self) -> ChatSession:
        """Start a fresh session."""
        return self.start_session()
    
    def get_session_history(self) -> List[Dict[str, Any]]:
        """
        Get current session message history.
        
        Returns:
            List of message dictionaries
        """
        if not self._session:
            return []
        return [msg.to_dict() for msg in self._session.messages]
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the assistant.
        
        Returns:
            Dictionary with assistant info
        """
        return {
            "provider": self.config.provider.value if self.config else None,
            "model": self.config.model if self.config else None,
            "session_id": self._session.session_id if self._session else None,
            "message_count": len(self._session.messages) if self._session else 0,
            "vector_store_initialized": self._vector_store is not None,
            "context_retriever_initialized": self._context_retriever is not None
        }


# Singleton instance
_default_assistant: Optional[AIAssistant] = None


def get_assistant(config: Optional[ProviderConfig] = None) -> AIAssistant:
    """
    Get the default AI assistant instance.
    
    Args:
        config: Optional provider configuration
        
    Returns:
        AIAssistant instance
    """
    global _default_assistant
    if _default_assistant is None:
        _default_assistant = AIAssistant(config)
    return _default_assistant


def chat(message: str, **kwargs) -> GenerationResult:
    """
    Convenience function for quick chat.
    
    Args:
        message: User message
        **kwargs: Additional arguments
        
    Returns:
        GenerationResult
    """
    return get_assistant().chat(message, **kwargs)