"""
Brain AI Embeddings - Text Embedding Pipeline

Provides text embedding generation using multiple backends:
- Sentence-transformers (local, default)
- OpenAI embeddings (cloud)
- Ollama embeddings (local LLM)

Usage:
    from brain.ai.embeddings import EmbeddingEngine
    
    engine = EmbeddingEngine()
    
    # Generate single embedding
    embedding = engine.embed("I completed my morning workout")
    
    # Generate batch embeddings
    embeddings = engine.embed_batch([
        "Went for a 5km run",
        "Meditated for 20 minutes"
    ])
"""

import time
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json

from brain.ai.models import EmbeddingConfig

# Type aliases for optional imports
SentenceTransformer: Any = None
OpenAI: Any = None
ollama: Any = None


@dataclass
class EmbeddingResult:
    """Result of an embedding operation."""
    
    embedding: List[float]
    text: str
    model: str
    dimension: int
    latency_ms: float
    success: bool = True
    error_message: Optional[str] = None


class EmbeddingEngine:
    """
    Text embedding engine with multiple backend support.
    
    Supports:
    - sentence-transformers (local, no API key)
    - OpenAI text-embedding-3-small (cloud)
    - Ollama nomic-embed-text (local)
    
    Default: sentence-transformers with all-MiniLM-L6-v2
    
    Attributes:
        config: Embedding configuration
        model: Loaded embedding model
    """
    
    # Default models for each backend
    DEFAULT_MODELS = {
        "sentence-transformers": "all-MiniLM-L6-v2",
        "openai": "text-embedding-3-small",
        "ollama": "nomic-embed-text",
    }
    
    # Dimensions for common models
    MODEL_DIMENSIONS = {
        "all-MiniLM-L6-v2": 384,
        "all-mpnet-base-v2": 768,
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "nomic-embed-text": 768,
    }
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        Initialize the embedding engine.
        
        Args:
            config: Embedding configuration. Uses defaults if None.
        """
        self.config = config or EmbeddingConfig()
        self._model = None
        self._provider = None
        self._dimension = None
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self.config.model_name or "all-MiniLM-L6-v2"
    
    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        if self._dimension is None:
            self._dimension = self.MODEL_DIMENSIONS.get(
                self.model_name, 
                768  # Default dimension
            )
        return self._dimension
    
    def initialize(self) -> bool:
        """
        Initialize the embedding model.
        
        Returns:
            True if successful, False otherwise
        """
        provider = self.config.provider
        
        if provider == "sentence-transformers" or provider is None:
            return self._init_sentence_transformers()
        elif provider == "openai":
            return self._init_openai()
        elif provider == "ollama":
            return self._init_ollama()
        else:
            # Default to sentence-transformers
            return self._init_sentence_transformers()
    
    def _init_sentence_transformers(self) -> bool:
        """Initialize sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore[import-unresolved]
            
            model_name = self.model_name
            self._model = SentenceTransformer(model_name)
            self._dimension = self._model.get_sentence_embedding_dimension()
            self._provider = "sentence-transformers"
            return True
            
        except ImportError:
            return False
    
    def _init_openai(self) -> bool:
        """Initialize OpenAI embeddings."""
        try:
            from openai import OpenAI  # type: ignore[import-unresolved]
            from brain.ai.api_keys import get_api_key
            
            api_key = self.config.api_key or get_api_key("openai")
            if not api_key:
                return False
            
            self._model = OpenAI(api_key=api_key)
            self._dimension = self.MODEL_DIMENSIONS.get(self.model_name, 1536)
            self._provider = "openai"
            return True
            
        except ImportError:
            return False
    
    def _init_ollama(self) -> bool:
        """Initialize Ollama embeddings."""
        try:
            import ollama  # type: ignore[import-unresolved]
            
            self._model = ollama
            self._dimension = self.MODEL_DIMENSIONS.get(self.model_name, 768)
            self._provider = "ollama"
            return True
            
        except ImportError:
            return False
    
    def embed(self, text: str) -> EmbeddingResult:
        """
        Generate an embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            EmbeddingResult with the embedding vector
        """
        if self._model is None:
            if not self.initialize():
                return EmbeddingResult(
                    embedding=[0.0] * self.dimension,
                    text=text,
                    model=self.model_name,
                    dimension=self.dimension,
                    latency_ms=0,
                    success=False,
                    error_message="Could not initialize embedding model"
                )
        
        # Type narrowing: after successful initialization, _model is guaranteed non-None
        assert self._model is not None
        
        start_time = time.time()
        
        try:
            if self._provider == "sentence-transformers":
                embedding = self._model.encode(text).tolist()  # type: ignore[union-attr]
            
            elif self._provider == "openai":
                response = self._model.embeddings.create(  # type: ignore[union-attr]
                    model=self.model_name,
                    input=text
                )
                embedding = response.data[0].embedding
            
            elif self._provider == "ollama":
                response = self._model.embeddings(  # type: ignore[union-attr]
                    model=self.model_name,
                    prompt=text
                )
                embedding = response['embedding']
            
            else:
                raise ValueError(f"Unknown provider: {self._provider}")
            
            latency = (time.time() - start_time) * 1000
            
            return EmbeddingResult(
                embedding=embedding,
                text=text,
                model=self.model_name,
                dimension=len(embedding),
                latency_ms=latency,
                success=True
            )
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return EmbeddingResult(
                embedding=[0.0] * self.dimension,
                text=text,
                model=self.model_name,
                dimension=self.dimension,
                latency_ms=latency,
                success=False,
                error_message=str(e)
            )
    
    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of EmbeddingResults
        """
        if self._model is None:
            if not self.initialize():
                return [
                    EmbeddingResult(
                        embedding=[0.0] * self.dimension,
                        text=text,
                        model=self.model_name,
                        dimension=self.dimension,
                        latency_ms=0,
                        success=False,
                        error_message="Could not initialize embedding model"
                    )
                    for text in texts
                ]
        
        # Type narrowing: after successful initialization, _model is guaranteed non-None
        assert self._model is not None
        
        start_time = time.time()
        
        try:
            embeddings = []
            
            if self._provider == "sentence-transformers":
                # sentence-transformers supports batch encoding
                batch_embeddings = self._model.encode(texts)  # type: ignore[union-attr]
                embeddings = [emb.tolist() for emb in batch_embeddings]
            
            elif self._provider == "openai":
                # OpenAI supports batch encoding
                response = self._model.embeddings.create(  # type: ignore[union-attr]
                    model=self.model_name,
                    input=texts
                )
                embeddings = [item.embedding for item in response.data]
            
            elif self._provider == "ollama":
                # Ollama doesn't support batch, embed individually
                embeddings = [
                    self._model.embeddings(  # type: ignore[union-attr]
                        model=self.model_name,
                        prompt=text
                    )['embedding']
                    for text in texts
                ]
            
            latency = (time.time() - start_time) * 1000
            per_text_latency = latency / len(texts)
            
            return [
                EmbeddingResult(
                    embedding=emb,
                    text=text,
                    model=self.model_name,
                    dimension=len(emb),
                    latency_ms=per_text_latency,
                    success=True
                )
                for emb, text in zip(embeddings, texts)
            ]
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return [
                EmbeddingResult(
                    embedding=[0.0] * self.dimension,
                    text=text,
                    model=self.model_name,
                    dimension=self.dimension,
                    latency_ms=latency,
                    success=False,
                    error_message=str(e)
                )
                for text in texts
            ]
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (-1 to 1)
        """
        import math
        
        # Dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        
        # Magnitudes
        mag1 = math.sqrt(sum(a * a for a in embedding1))
        mag2 = math.sqrt(sum(b * b for b in embedding2))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding engine.
        
        Returns:
            Dictionary with engine info
        """
        return {
            "provider": self._provider,
            "model": self.model_name,
            "dimension": self.dimension,
            "initialized": self._model is not None,
        }


# Singleton for convenience
_default_engine: Optional[EmbeddingEngine] = None


def get_embedding_engine() -> EmbeddingEngine:
    """
    Get the default embedding engine instance.
    
    Returns:
        Singleton EmbeddingEngine instance
    """
    global _default_engine
    if _default_engine is None:
        _default_engine = EmbeddingEngine()
    return _default_engine


def embed_text(text: str) -> List[float]:
    """
    Convenience function to embed a single text.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector
    """
    result = get_embedding_engine().embed(text)
    return result.embedding


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Convenience function to embed multiple texts.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    results = get_embedding_engine().embed_batch(texts)
    return [r.embedding for r in results]