"""
Brain AI Module - RAG Foundation and AI Integration

This module provides AI integration capabilities for the tracking system:
- Multi-provider LLM support (Ollama, OpenAI, Anthropic, Gemini, Groq)
- RAG (Retrieval-Augmented Generation) for querying personal data
- Vector storage with ChromaDB
- Embedding generation with sentence-transformers
- Secure API key management

Key Components:
- AIProvider: Enum of supported providers
- ProviderConfig: Configuration for AI providers
- AIProviderBase: Abstract base class for providers
- ProviderFactory: Factory for creating provider instances
- EmbeddingEngine: Generate embeddings from text
- VectorStore: ChromaDB wrapper for vector storage
- APIKeyManager: Secure API key storage and retrieval

Usage:
    from brain.ai import ProviderFactory, AIProvider, ProviderConfig
    from brain.ai import EmbeddingEngine, VectorStore
    
    # Create an AI provider
    config = ProviderConfig(provider=AIProvider.OLLAMA, model="llama3")
    provider = ProviderFactory.create(config)
    
    # Generate embeddings
    engine = EmbeddingEngine()
    embedding = engine.embed("I completed my morning workout")
    
    # Store in vector database
    store = VectorStore()
    store.add("doc1", "I completed my morning workout", embedding=embedding)
    
    # Query
    results = store.search("exercise habits", n_results=5)
    
    # Generate AI response
    response = provider.generate("Why have I been tired?", context=[r.content for r in results])

📚 REQUIRED READING BEFORE MODIFICATION:
- PROJECT_RULES.md (root level)
- docs/research/RAG_FOUNDATION_RESEARCH.md
- phases/PHASE_6_AI_INTEGRATION.md
"""

from brain.ai.models import (
    AIProvider,
    ProviderConfig,
    EmbeddingConfig,
    VectorDocument,
    RAGContext,
)
from brain.ai.api_keys import APIKeyManager

__all__ = [
    # Enums
    'AIProvider',
    
    # Configuration
    'ProviderConfig',
    'EmbeddingConfig',
    
    # Data Models
    'VectorDocument',
    'RAGContext',
    
    # Managers
    'APIKeyManager',
]

__version__ = '1.0.0'