"""
Brain AI Models - Data Models for AI Integration

Python dataclasses for AI provider configuration, embeddings, and RAG components.

Usage:
    from brain.ai.models import AIProvider, ProviderConfig, VectorDocument
    
    # Create provider configuration
    config = ProviderConfig(
        provider=AIProvider.OLLAMA,
        model="llama3"
    )
    
    # Create a vector document
    doc = VectorDocument(
        content="I completed my morning workout",
        source_type="habit",
        source_id="habit_123"
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class AIProvider(Enum):
    """
    Supported AI providers.
    
    - OLLAMA: Local LLM, no API key required
    - OPENAI: OpenAI GPT models, requires API key
    - ANTHROPIC: Anthropic Claude models, requires API key
    - GEMINI: Google Gemini models, requires API key
    - GROQ: Groq fast inference, requires API key
    - OPENROUTER: OpenRouter aggregator, requires API key
    """
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GROQ = "groq"
    OPENROUTER = "openrouter"


class ProviderStatus(Enum):
    """Status of an AI provider configuration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNCONFIGURED = "unconfigured"


@dataclass
class ProviderConfig:
    """
    Configuration for an AI provider.
    
    Attributes:
        id: Unique identifier for this configuration
        provider: The AI provider (Ollama, OpenAI, etc.)
        model: Model name to use
        api_key: API key for cloud providers (None for Ollama)
        base_url: Custom base URL (for proxies)
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature (0.0 - 2.0)
        ollama_host: Ollama server URL (for local)
        organization: OpenAI organization ID
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider: AIProvider = AIProvider.OLLAMA
    model: str = "llama3"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.7
    
    # Ollama-specific
    ollama_host: str = "http://localhost:11434"
    
    # Cloud provider options
    organization: Optional[str] = None
    
    # Status
    status: ProviderStatus = ProviderStatus.UNCONFIGURED
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> bool:
        """
        Validate configuration has required fields.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if self.provider == AIProvider.OLLAMA:
            # Ollama doesn't require API key
            return True
        
        # All other providers require API key
        return self.api_key is not None and len(self.api_key.strip()) > 0
    
    def get_default_model(self) -> str:
        """Get the default model for this provider."""
        defaults = {
            AIProvider.OLLAMA: "llama3",
            AIProvider.OPENAI: "gpt-4o-mini",
            AIProvider.ANTHROPIC: "claude-3-haiku-20240307",
            AIProvider.GEMINI: "gemini-1.5-flash",
            AIProvider.GROQ: "llama-3.1-8b-instant",
            AIProvider.OPENROUTER: "openai/gpt-4o-mini",
        }
        return defaults.get(self.provider, "unknown")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'provider': self.provider.value,
            'model': self.model,
            'api_key': '***' if self.api_key else None,  # Never expose full key
            'base_url': self.base_url,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'ollama_host': self.ollama_host,
            'organization': self.organization,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProviderConfig':
        """Create instance from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            provider=AIProvider(data.get('provider', 'ollama')),
            model=data.get('model', 'llama3'),
            api_key=data.get('api_key'),
            base_url=data.get('base_url'),
            max_tokens=data.get('max_tokens', 2048),
            temperature=data.get('temperature', 0.7),
            ollama_host=data.get('ollama_host', 'http://localhost:11434'),
            organization=data.get('organization'),
            status=ProviderStatus(data.get('status', 'unconfigured')),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
        )


@dataclass
class EmbeddingConfig:
    """
    Configuration for embedding generation.
    
    Attributes:
        model_name: Name of the sentence-transformer model
        provider: Embedding provider ('sentence-transformers', 'openai', 'ollama')
        api_key: API key for cloud providers (openai)
        chunk_size: Characters per chunk for document splitting
        chunk_overlap: Overlap between chunks
        batch_size: Number of embeddings to generate per batch
        enable_cache: Whether to cache embeddings
        cache_ttl_hours: Cache time-to-live in hours
    """
    model_name: str = "all-MiniLM-L6-v2"
    provider: str = "sentence-transformers"  # 'sentence-transformers', 'openai', 'ollama'
    api_key: Optional[str] = None
    chunk_size: int = 500
    chunk_overlap: int = 50
    batch_size: int = 32
    
    # Cache settings
    enable_cache: bool = True
    cache_ttl_hours: int = 24
    
    def get_dimension(self) -> int:
        """Get the embedding dimension for the model."""
        dimensions = {
            "all-MiniLM-L6-v2": 384,
            "all-mpnet-base-v2": 768,
            "e5-large-v2": 1024,
            "e5-small-v2": 384,
            "bge-small-en-v1.5": 384,
            "bge-base-en-v1.5": 768,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "nomic-embed-text": 768,
        }
        return dimensions.get(self.model_name, 384)


@dataclass
class VectorDocument:
    """
    A document stored in the vector database.
    
    Attributes:
        id: Unique identifier
        content: Text content of the document
        embedding: Vector embedding (generated)
        metadata: Additional metadata
        source_type: Type of source (habit, task, health, etc.)
        source_id: ID of the source entity
        created_at: When document was created
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Source tracking
    source_type: str = ""  # 'habit', 'task', 'health', 'journal', 'goal'
    source_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for ChromaDB."""
        return {
            'id': self.id,
            'content': self.content,
            'embedding': self.embedding,
            'metadata': {
                **self.metadata,
                'source_type': self.source_type,
                'source_id': self.source_id,
                'created_at': self.created_at.isoformat(),
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VectorDocument':
        """Create instance from dictionary."""
        metadata = data.get('metadata', {})
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            content=data.get('content', ''),
            embedding=data.get('embedding'),
            metadata=metadata,
            source_type=metadata.get('source_type', ''),
            source_id=metadata.get('source_id', ''),
            created_at=datetime.fromisoformat(metadata['created_at']) if metadata.get('created_at') else datetime.now(),
        )


@dataclass
class RAGContext:
    """
    Context retrieved for a RAG query.
    
    Attributes:
        query: The original query text
        query_embedding: Embedding of the query
        retrieved_docs: Documents retrieved from vector store
        relevance_scores: Similarity scores for each document
        total_tokens: Total tokens used
        retrieval_time_ms: Time taken for retrieval
    """
    query: str = ""
    query_embedding: Optional[List[float]] = None
    retrieved_docs: List[VectorDocument] = field(default_factory=list)
    relevance_scores: List[float] = field(default_factory=list)
    total_tokens: int = 0
    retrieval_time_ms: float = 0.0
    
    def get_context_text(self, max_docs: int = 5) -> str:
        """
        Get concatenated context text for LLM prompt.
        
        Args:
            max_docs: Maximum number of documents to include
            
        Returns:
            Concatenated text from retrieved documents
        """
        docs = self.retrieved_docs[:max_docs]
        return "\n\n".join(doc.content for doc in docs if doc.content)
    
    def get_sources(self) -> List[Dict[str, Any]]:
        """Get list of sources for attribution."""
        return [
            {
                'source_type': doc.source_type,
                'source_id': doc.source_id,
                'relevance': score,
            }
            for doc, score in zip(self.retrieved_docs, self.relevance_scores)
        ]


@dataclass
class ChatMessage:
    """
    A single chat message.
    
    Attributes:
        id: Unique identifier
        role: Message role (user, assistant, system)
        content: Message content
        timestamp: When message was created
        context_used: RAG context used (for assistant messages)
        tokens_used: Tokens consumed
        model: Model used for generation
        provider: Provider used
        latency_ms: Response latency
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: str = "user"  # 'user', 'assistant', 'system'
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Context (assistant only)
    context_used: Optional[RAGContext] = None
    tokens_used: int = 0
    
    # Metadata
    model: str = ""
    provider: str = ""
    latency_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'tokens_used': self.tokens_used,
            'model': self.model,
            'provider': self.provider,
            'latency_ms': self.latency_ms,
        }


@dataclass
class ChatSession:
    """
    A chat session with message history.
    
    Attributes:
        id: Unique session identifier
        user_id: User who owns this session
        title: Session title (auto-generated or user-set)
        messages: List of messages in the session
        created_at: When session was created
        updated_at: When session was last updated
        provider_config_id: ID of the provider configuration used
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    title: str = "New Chat"
    messages: List[ChatMessage] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Configuration
    provider_config_id: str = ""
    
    def add_message(self, role: str, content: str, **kwargs) -> ChatMessage:
        """
        Add a message to the session.
        
        Args:
            role: Message role
            content: Message content
            **kwargs: Additional message attributes
            
        Returns:
            The created message
        """
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            **kwargs
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def get_context_window(self, max_messages: int = 10) -> List[ChatMessage]:
        """
        Get recent messages for context window.
        
        Args:
            max_messages: Maximum messages to return
            
        Returns:
            List of recent messages
        """
        return self.messages[-max_messages:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'messages': [m.to_dict() for m in self.messages],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'provider_config_id': self.provider_config_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create instance from dictionary."""
        messages_data = data.get('messages', [])
        messages = [ChatMessage(**m) if isinstance(m, dict) else m for m in messages_data]
        
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            title=data.get('title', 'New Chat'),
            messages=messages,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
            provider_config_id=data.get('provider_config_id', ''),
        )


@dataclass
class GenerationResult:
    """
    Result from an LLM generation.
    
    Attributes:
        content: Generated text content
        success: Whether generation succeeded
        error_message: Error message if failed
        tokens_used: Total tokens consumed
        latency_ms: Generation latency
        model: Model used
        provider: Provider used
        finish_reason: Why generation stopped
    """
    content: str = ""
    success: bool = True
    error_message: Optional[str] = None
    tokens_used: int = 0
    latency_ms: float = 0.0
    model: str = ""
    provider: str = ""
    finish_reason: str = "stop"  # 'stop', 'length', 'error'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'content': self.content,
            'success': self.success,
            'error_message': self.error_message,
            'tokens_used': self.tokens_used,
            'latency_ms': self.latency_ms,
            'model': self.model,
            'provider': self.provider,
            'finish_reason': self.finish_reason,
        }