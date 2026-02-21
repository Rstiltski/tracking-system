"""
Brain AI Vector Store - ChromaDB Integration

Provides vector storage and retrieval using ChromaDB for RAG functionality.

Usage:
    from brain.ai.vector_store import VectorStore
    from brain.ai.models import VectorDocument
    
    # Initialize store
    store = VectorStore()
    
    # Add documents
    doc = VectorDocument(
        content="I completed my morning workout",
        source_type="habit",
        source_id="habit_123"
    )
    store.add_document(doc)
    
    # Search
    results = store.search("exercise habits", n_results=5)
"""

import time
from typing import List, Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from brain.ai.models import VectorDocument, RAGContext, EmbeddingConfig
from brain.ai.embeddings import EmbeddingEngine, get_embedding_engine


@dataclass
class SearchResult:
    """Result from a vector search."""
    
    document: VectorDocument
    score: float  # Similarity score (0-1 for cosine, distance for others)
    distance: float  # Raw distance metric


class VectorStore:
    """
    Vector store using ChromaDB for persistent storage.
    
    Provides:
    - Document storage with automatic embedding
    - Similarity search
    - Filtering by metadata (source_type, etc.)
    - Collection management
    
    Attributes:
        persist_directory: Directory for ChromaDB storage
        collection_name: Name of the ChromaDB collection
        embedding_engine: Engine for generating embeddings
    """
    
    DEFAULT_PERSIST_DIR = ".veryfyn/chroma_db"
    DEFAULT_COLLECTION = "veryfyn_docs"
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = DEFAULT_COLLECTION,
        embedding_engine: Optional[EmbeddingEngine] = None,
        embedding_config: Optional[EmbeddingConfig] = None
    ):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Directory for ChromaDB storage
            collection_name: Name of the collection
            embedding_engine: Pre-configured embedding engine
            embedding_config: Config for creating embedding engine
        """
        self.persist_directory = persist_directory or self.DEFAULT_PERSIST_DIR
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        
        # Embedding engine
        if embedding_engine:
            self._embedding_engine = embedding_engine
        else:
            self._embedding_engine = EmbeddingEngine(embedding_config)
    
    @property
    def embedding_engine(self) -> EmbeddingEngine:
        """Get the embedding engine."""
        return self._embedding_engine
    
    def initialize(self) -> bool:
        """
        Initialize ChromaDB connection.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Create persist directory
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            
            # Create client
            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            return True
            
        except ImportError:
            return False
        except Exception:
            return False
    
    def add_document(
        self, 
        document: VectorDocument,
        generate_embedding: bool = True
    ) -> bool:
        """
        Add a document to the vector store.
        
        Args:
            document: Document to add
            generate_embedding: Whether to generate embedding if not present
            
        Returns:
            True if successful
        """
        if self._collection is None:
            if not self.initialize():
                return False
        
        # Type narrowing: after successful initialization, _collection is guaranteed non-None
        assert self._collection is not None
        
        try:
            # Generate embedding if needed
            if document.embedding is None and generate_embedding:
                result = self._embedding_engine.embed(document.content)
                if result.success:
                    document.embedding = result.embedding
                else:
                    return False
            
            # Add to collection
            self._collection.add(
                ids=[document.id],
                documents=[document.content],
                embeddings=[document.embedding] if document.embedding else None,
                metadatas=[{
                    'source_type': document.source_type,
                    'source_id': document.source_id,
                    'created_at': document.created_at.isoformat(),
                    **document.metadata
                }]
            )
            
            return True
            
        except Exception:
            return False
    
    def add_documents(
        self,
        documents: List[VectorDocument],
        generate_embeddings: bool = True
    ) -> int:
        """
        Add multiple documents to the vector store.
        
        Args:
            documents: Documents to add
            generate_embeddings: Whether to generate embeddings
            
        Returns:
            Number of documents successfully added
        """
        if self._collection is None:
            if not self.initialize():
                return 0
        
        # Type narrowing: after successful initialization, _collection is guaranteed non-None
        assert self._collection is not None
        
        try:
            # Generate embeddings if needed
            if generate_embeddings:
                contents = [d.content for d in documents if d.embedding is None]
                if contents:
                    results = self._embedding_engine.embed_batch(contents)
                    # Assign embeddings
                    idx = 0
                    for doc in documents:
                        if doc.embedding is None:
                            if results[idx].success:
                                doc.embedding = results[idx].embedding
                            idx += 1
            
            # Filter to documents with embeddings
            valid_docs = [d for d in documents if d.embedding is not None]
            
            if not valid_docs:
                return 0
            
            # Add to collection
            self._collection.add(
                ids=[d.id for d in valid_docs],
                documents=[d.content for d in valid_docs],
                embeddings=[d.embedding for d in valid_docs],
                metadatas=[{
                    'source_type': d.source_type,
                    'source_id': d.source_id,
                    'created_at': d.created_at.isoformat(),
                    **d.metadata
                } for d in valid_docs]
            )
            
            return len(valid_docs)
            
        except Exception:
            return 0
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        source_type: Optional[str] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query: Query text
            n_results: Maximum number of results
            source_type: Filter by source type (habit, task, etc.)
            where: Additional ChromaDB where clause
            
        Returns:
            List of SearchResult objects
        """
        if self._collection is None:
            if not self.initialize():
                return []
        
        # Type narrowing: after successful initialization, _collection is guaranteed non-None
        assert self._collection is not None
        
        try:
            # Generate query embedding
            query_result = self._embedding_engine.embed(query)
            if not query_result.success:
                return []
            
            # Build where clause
            where_clause = where or {}
            if source_type:
                where_clause['source_type'] = source_type
            
            # Query collection
            results = self._collection.query(
                query_embeddings=[query_result.embedding],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Build results
            search_results = []
            
            if results and results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    doc = VectorDocument(
                        id=doc_id,
                        content=results['documents'][0][i] if results['documents'] else "",
                        metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                        source_type=results['metadatas'][0][i].get('source_type', '') if results['metadatas'] else '',
                        source_id=results['metadatas'][0][i].get('source_id', '') if results['metadatas'] else '',
                        created_at=datetime.fromisoformat(
                            results['metadatas'][0][i].get('created_at', datetime.now().isoformat())
                        ) if results['metadatas'] else datetime.now()
                    )
                    
                    distance = results['distances'][0][i] if results['distances'] else 0.0
                    # Convert distance to similarity score (for cosine, distance is 1 - similarity)
                    score = 1.0 - distance
                    
                    search_results.append(SearchResult(
                        document=doc,
                        score=score,
                        distance=distance
                    ))
            
            return search_results
            
        except Exception:
            return []
    
    def search_by_embedding(
        self,
        embedding: List[float],
        n_results: int = 5,
        source_type: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search using a pre-computed embedding.
        
        Args:
            embedding: Query embedding vector
            n_results: Maximum number of results
            source_type: Filter by source type
            
        Returns:
            List of SearchResult objects
        """
        if self._collection is None:
            if not self.initialize():
                return []
        
        # Type narrowing: after successful initialization, _collection is guaranteed non-None
        assert self._collection is not None
        
        try:
            where_clause = {}
            if source_type:
                where_clause['source_type'] = source_type
            
            results = self._collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=['documents', 'metadatas', 'distances']
            )
            
            search_results = []
            
            if results and results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    doc = VectorDocument(
                        id=doc_id,
                        content=results['documents'][0][i] if results['documents'] else "",
                        metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                        source_type=results['metadatas'][0][i].get('source_type', '') if results['metadatas'] else '',
                        source_id=results['metadatas'][0][i].get('source_id', '') if results['metadatas'] else ''
                    )
                    
                    distance = results['distances'][0][i] if results['distances'] else 0.0
                    score = 1.0 - distance
                    
                    search_results.append(SearchResult(
                        document=doc,
                        score=score,
                        distance=distance
                    ))
            
            return search_results
            
        except Exception:
            return []
    
    def get_document(self, document_id: str) -> Optional[VectorDocument]:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            VectorDocument if found, None otherwise
        """
        if self._collection is None:
            if not self.initialize():
                return None
        
        # Type narrowing: after successful initialization, _collection is guaranteed non-None
        assert self._collection is not None
        
        try:
            results = self._collection.get(
                ids=[document_id],
                include=['documents', 'metadatas', 'embeddings']
            )
            
            if results and results['ids']:
                return VectorDocument(
                    id=results['ids'][0],
                    content=results['documents'][0] if results['documents'] else "",
                    embedding=results['embeddings'][0] if results['embeddings'] else None,
                    metadata=results['metadatas'][0] if results['metadatas'] else {},
                    source_type=results['metadatas'][0].get('source_type', '') if results['metadatas'] else '',
                    source_id=results['metadatas'][0].get('source_id', '') if results['metadatas'] else ''
                )
            
            return None
            
        except Exception:
            return None
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted successfully
        """
        if self._collection is None:
            if not self.initialize():
                return False
        
        # Type narrowing: after successful initialization, _collection is guaranteed non-None
        assert self._collection is not None
        
        try:
            self._collection.delete(ids=[document_id])
            return True
        except Exception:
            return False
    
    def delete_by_source(self, source_type: str, source_id: str) -> int:
        """
        Delete all documents from a specific source.
        
        Args:
            source_type: Type of source
            source_id: Source ID
            
        Returns:
            Number of documents deleted
        """
        if self._collection is None:
            if not self.initialize():
                return 0
        
        # Type narrowing: after successful initialization, _collection is guaranteed non-None
        assert self._collection is not None
        
        try:
            # Get matching documents
            results = self._collection.get(
                where={
                    'source_type': source_type,
                    'source_id': source_id
                }
            )
            
            if results and results['ids']:
                count = len(results['ids'])
                self._collection.delete(ids=results['ids'])
                return count
            
            return 0
            
        except Exception:
            return 0
    
    def count(self) -> int:
        """
        Count total documents in the store.
        
        Returns:
            Number of documents
        """
        if self._collection is None:
            if not self.initialize():
                return 0
        
        # Type narrowing: after successful initialization, _collection is guaranteed non-None
        assert self._collection is not None
        
        try:
            return self._collection.count()
        except Exception:
            return 0
    
    def clear(self) -> bool:
        """
        Clear all documents from the collection.
        
        Returns:
            True if successful
        """
        if self._collection is None:
            if not self.initialize():
                return False
        
        # Type narrowing: after successful initialization, _collection is guaranteed non-None
        assert self._collection is not None
        
        try:
            # Get all IDs and delete
            results = self._collection.get()
            if results and results['ids']:
                self._collection.delete(ids=results['ids'])
            return True
        except Exception:
            return False
    
    def get_rag_context(
        self,
        query: str,
        n_results: int = 5,
        source_types: Optional[List[str]] = None
    ) -> RAGContext:
        """
        Get RAG context for a query.
        
        Args:
            query: Query text
            n_results: Number of documents to retrieve
            source_types: Optional filter by source types
            
        Returns:
            RAGContext with retrieved documents
        """
        start_time = time.time()
        
        # Generate query embedding
        query_result = self._embedding_engine.embed(query)
        
        # Search
        results = self.search(query, n_results=n_results)
        
        # Filter by source types if specified
        if source_types:
            results = [r for r in results if r.document.source_type in source_types]
        
        retrieval_time = (time.time() - start_time) * 1000
        
        return RAGContext(
            query=query,
            query_embedding=query_result.embedding if query_result.success else None,
            retrieved_docs=[r.document for r in results],
            relevance_scores=[r.score for r in results],
            retrieval_time_ms=retrieval_time
        )
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the vector store.
        
        Returns:
            Dictionary with store info
        """
        return {
            "persist_directory": self.persist_directory,
            "collection_name": self.collection_name,
            "document_count": self.count(),
            "embedding_engine": self._embedding_engine.get_info(),
            "initialized": self._collection is not None,
        }


# Singleton for convenience
_default_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """
    Get the default vector store instance.
    
    Returns:
        Singleton VectorStore instance
    """
    global _default_store
    if _default_store is None:
        _default_store = VectorStore()
    return _default_store