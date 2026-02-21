"""
Brain AI Context Retriever - RAG Context Retrieval

Provides context retrieval for the AI Assistant using RAG (Retrieval-Augmented Generation).
Retrieves relevant context from the vector store based on user queries.

Usage:
    from brain.ai.context_retriever import ContextRetriever
    from brain.ai.vector_store import VectorStore
    
    retriever = ContextRetriever(vector_store)
    results = retriever.retrieve("How am I doing with my habits?")
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class RetrievedContext:
    """
    A retrieved context item.
    
    Attributes:
        content: The text content
        source_type: Type of source (habit, goal, health, etc.)
        source_id: ID of the source document
        score: Relevance score (0-1)
        metadata: Additional metadata
    """
    content: str
    source_type: str
    source_id: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "score": self.score,
            "metadata": self.metadata
        }


class ContextRetriever:
    """
    Context retriever for Veryfyn personal data.
    
    Supports:
    - Semantic similarity search via vector store
    - Source type filtering (habit, task, health, goal, etc.)
    - Date range filtering
    - Multi-query expansion
    - Relevance threshold filtering
    
    Usage:
        retriever = ContextRetriever(vector_store)
        
        # Basic retrieval
        results = retriever.retrieve("exercise patterns", n_results=5)
        
        # Filtered retrieval
        results = retriever.retrieve_for_habits("why am I tired?")
    """
    
    # Source type categories
    SOURCE_TYPES = {
        "habit": ["habit", "habit_completion", "habit_streak"],
        "health": ["health", "sleep", "mood", "exercise", "energy"],
        "goal": ["goal", "goal_progress", "milestone"],
        "task": ["task", "task_completion"],
        "finance": ["expense", "income", "budget"],
        "note": ["note", "journal", "reflection"],
    }
    
    def __init__(self, vector_store: Any = None):
        """
        Initialize the context retriever.
        
        Args:
            vector_store: VectorStore instance for semantic search
        """
        self.vector_store = vector_store
        self._initialized = vector_store is not None
    
    def initialize(self, vector_store: Any) -> bool:
        """
        Initialize with a vector store.
        
        Args:
            vector_store: VectorStore instance
            
        Returns:
            True if successful
        """
        self.vector_store = vector_store
        self._initialized = vector_store is not None
        return self._initialized
    
    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        source_types: Optional[List[str]] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None,
        min_relevance: float = 0.0,
        include_metadata: bool = True
    ) -> List[RetrievedContext]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query or search text
            n_results: Maximum number of results
            source_types: Filter by source types (e.g., ["habit", "health"])
            date_range: Optional (start_date, end_date) tuple
            min_relevance: Minimum relevance score threshold
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of RetrievedContext objects
        """
        if not self._initialized or self.vector_store is None:
            return []
        
        try:
            # Expand source types to include subcategories
            expanded_types = self._expand_source_types(source_types)
            
            # Build where clause for filtering
            where_clause = None
            if expanded_types:
                where_clause = {"source_type": {"$in": expanded_types}}
            
            # Search vector store
            search_results = self.vector_store.search(
                query=query,
                n_results=n_results * 2,  # Get extra for filtering
                where=where_clause
            )
            
            # Process and filter results
            contexts = []
            for result in search_results:
                # Handle different result formats
                if hasattr(result, 'document'):
                    doc = result.document
                    score = getattr(result, 'score', 0.5)
                elif isinstance(result, dict):
                    doc = result.get('document', result)
                    score = result.get('score', 0.5)
                else:
                    continue
                
                # Get content
                if hasattr(doc, 'content'):
                    content = doc.content
                    metadata = getattr(doc, 'metadata', {})
                elif isinstance(doc, dict):
                    content = doc.get('content', str(doc))
                    metadata = doc.get('metadata', {})
                else:
                    content = str(doc)
                    metadata = {}
                
                # Apply filters
                if score < min_relevance:
                    continue
                
                # Date range filter
                if date_range:
                    doc_date = metadata.get('date')
                    if doc_date:
                        if isinstance(doc_date, str):
                            doc_date = datetime.fromisoformat(doc_date)
                        if not (date_range[0] <= doc_date <= date_range[1]):
                            continue
                
                # Create context
                context = RetrievedContext(
                    content=content,
                    source_type=metadata.get('source_type', 'unknown'),
                    source_id=metadata.get('source_id', ''),
                    score=score,
                    metadata=metadata if include_metadata else {}
                )
                contexts.append(context)
                
                # Stop if we have enough
                if len(contexts) >= n_results:
                    break
            
            return contexts
            
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []
    
    def _expand_source_types(self, source_types: Optional[List[str]]) -> Optional[List[str]]:
        """
        Expand source types to include subcategories.
        
        Args:
            source_types: List of source type categories
            
        Returns:
            Expanded list of source types
        """
        if not source_types:
            return None
        
        expanded = []
        for st in source_types:
            # Check if it's a category
            if st in self.SOURCE_TYPES:
                expanded.extend(self.SOURCE_TYPES[st])
            else:
                expanded.append(st)
        
        return list(set(expanded))  # Remove duplicates
    
    def retrieve_for_habits(self, query: str, n_results: int = 5) -> List[RetrievedContext]:
        """
        Retrieve habit-related context.
        
        Args:
            query: User query
            n_results: Maximum results
            
        Returns:
            List of habit-related contexts
        """
        return self.retrieve(
            query=query,
            source_types=["habit"],
            n_results=n_results
        )
    
    def retrieve_for_health(self, query: str, n_results: int = 5) -> List[RetrievedContext]:
        """
        Retrieve health-related context.
        
        Args:
            query: User query
            n_results: Maximum results
            
        Returns:
            List of health-related contexts
        """
        return self.retrieve(
            query=query,
            source_types=["health"],
            n_results=n_results
        )
    
    def retrieve_for_goals(self, query: str, n_results: int = 5) -> List[RetrievedContext]:
        """
        Retrieve goal-related context.
        
        Args:
            query: User query
            n_results: Maximum results
            
        Returns:
            List of goal-related contexts
        """
        return self.retrieve(
            query=query,
            source_types=["goal"],
            n_results=n_results
        )
    
    def retrieve_recent(
        self,
        days: int = 7,
        n_results: int = 10,
        source_types: Optional[List[str]] = None
    ) -> List[RetrievedContext]:
        """
        Retrieve recent activity across all types.
        
        Args:
            days: Number of days to look back
            n_results: Maximum results
            source_types: Optional source type filter
            
        Returns:
            List of recent contexts
        """
        start_date = datetime.now() - timedelta(days=days)
        return self.retrieve(
            query="recent activity updates",
            n_results=n_results,
            source_types=source_types,
            date_range=(start_date, datetime.now())
        )
    
    def retrieve_by_date(
        self,
        date: datetime,
        n_results: int = 10,
        source_types: Optional[List[str]] = None
    ) -> List[RetrievedContext]:
        """
        Retrieve context for a specific date.
        
        Args:
            date: The date to retrieve for
            n_results: Maximum results
            source_types: Optional source type filter
            
        Returns:
            List of contexts for the date
        """
        start = datetime(date.year, date.month, date.day, 0, 0, 0)
        end = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        return self.retrieve(
            query=f"activity on {date.strftime('%Y-%m-%d')}",
            n_results=n_results,
            source_types=source_types,
            date_range=(start, end)
        )
    
    def multi_query_retrieve(
        self,
        queries: List[str],
        n_results_per_query: int = 3,
        **kwargs
    ) -> List[RetrievedContext]:
        """
        Retrieve using multiple queries and combine results.
        
        Args:
            queries: List of query strings
            n_results_per_query: Results per query
            **kwargs: Additional arguments for retrieve()
            
        Returns:
            Combined and deduplicated contexts
        """
        all_contexts = {}
        
        for query in queries:
            results = self.retrieve(
                query=query,
                n_results=n_results_per_query,
                **kwargs
            )
            
            for ctx in results:
                # Deduplicate by source_id, keeping highest score
                key = ctx.source_id or ctx.content[:100]
                if key not in all_contexts or ctx.score > all_contexts[key].score:
                    all_contexts[key] = ctx
        
        # Sort by score and return
        return sorted(all_contexts.values(), key=lambda x: x.score, reverse=True)
    
    def build_context_string(
        self,
        contexts: List[RetrievedContext],
        max_length: int = 2000,
        include_sources: bool = True
    ) -> str:
        """
        Build a context string from retrieved contexts.
        
        Args:
            contexts: List of retrieved contexts
            max_length: Maximum string length
            include_sources: Include source attribution
            
        Returns:
            Formatted context string
        """
        if not contexts:
            return "No relevant context available."
        
        parts = []
        total_length = 0
        
        for ctx in contexts:
            # Build context entry
            if include_sources:
                entry = f"[{ctx.source_type}] {ctx.content}"
            else:
                entry = ctx.content
            
            # Check length
            if total_length + len(entry) + 2 > max_length:
                break
            
            parts.append(entry)
            total_length += len(entry) + 2
        
        if not parts:
            return "No relevant context available."
        
        return "\n".join(parts)


# Convenience function
def retrieve_context(query: str, n_results: int = 5) -> List[RetrievedContext]:
    """
    Convenience function for quick context retrieval.
    
    Args:
        query: User query
        n_results: Maximum results
        
    Returns:
        List of RetrievedContext objects
    """
    from brain.ai.vector_store import get_vector_store
    
    store = get_vector_store()
    retriever = ContextRetriever(store)
    return retriever.retrieve(query, n_results=n_results)