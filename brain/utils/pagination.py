"""
Pagination Utilities - Performance Optimization

Provides efficient pagination for large datasets.
Following PROJECT_RULES.md:
- Python-first implementation
- Type-safe operations
- Works with SQLite
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, List, Optional, TypeVar, Any, Dict
from datetime import date, datetime
import json
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class Page(Generic[T]):
    """A page of results with metadata."""
    items: List[T]
    page_number: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool = False
    has_prev: bool = False
    next_page: Optional[int] = None
    prev_page: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "items": self.items,
            "page_number": self.page_number,
            "page_size": self.page_size,
            "total_items": self.total_items,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
            "next_page": self.next_page,
            "prev_page": self.prev_page
        }


class Paginator(Generic[T]):
    """
    Efficient paginator for large datasets.
    
    Features:
    - Offset-based pagination
    - Cursor-based pagination (for real-time data)
    - Works with SQLite LIMIT/OFFSET
    - Type-safe results
    
    Usage:
        paginator = Paginator(page_size=20)
        
        # Paginate habits
        page = paginator.paginate(
            query="SELECT * FROM habits ORDER BY created_at DESC",
            count_query="SELECT COUNT(*) FROM habits",
            db=db,
            page=1
        )
    """
    
    def __init__(self, page_size: int = 20, max_page_size: int = 100):
        """
        Initialize paginator.
        
        Args:
            page_size: Default items per page
            max_page_size: Maximum allowed page size
        """
        self.default_page_size = page_size
        self.max_page_size = max_page_size
    
    def paginate(
        self,
        query: str,
        count_query: str,
        db,
        page: int = 1,
        page_size: Optional[int] = None,
        params: tuple = (),
        model_class: Optional[type] = None
    ) -> Page[T]:
        """
        Paginate a query.
        
        Args:
            query: Base SELECT query (without LIMIT/OFFSET)
            count_query: Query to count total items
            db: Database instance
            page: Page number (1-indexed)
            page_size: Items per page
            params: Query parameters
            model_class: Optional model class to instantiate
            
        Returns:
            Page with items and metadata
        """
        # Validate page size
        size = min(page_size or self.default_page_size, self.max_page_size)
        
        # Ensure page is at least 1
        page = max(1, page)
        
        # Calculate offset
        offset = (page - 1) * size
        
        # Get total count
        count_result = db.fetch_one(count_query, params)
        total_items = count_result.get("COUNT(*)", list(count_result.values())[0]) if count_result else 0
        
        # Calculate total pages
        total_pages = (total_items + size - 1) // size if total_items > 0 else 1
        
        # Fetch items
        paginated_query = f"{query} LIMIT ? OFFSET ?"
        rows = db.fetch_all(paginated_query, params + (size, offset))
        
        # Convert to model instances if provided
        items = []
        for row in rows:
            if model_class and hasattr(model_class, 'from_dict'):
                items.append(model_class.from_dict(row))
            else:
                items.append(row)
        
        # Build page metadata
        has_next = page < total_pages
        has_prev = page > 1
        
        return Page(
            items=items,
            page_number=page,
            page_size=size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            next_page=page + 1 if has_next else None,
            prev_page=page - 1 if has_prev else None
        )
    
    def paginate_lazy(
        self,
        query: str,
        db,
        page: int = 1,
        page_size: Optional[int] = None,
        params: tuple = (),
        model_class: Optional[type] = None
    ):
        """
        Lazy generator for paginated results.
        
        Yields items one at a time for memory efficiency.
        
        Args:
            query: Base SELECT query
            db: Database instance
            page: Starting page
            page_size: Items per page
            params: Query parameters
            model_class: Optional model class
            
        Yields:
            Individual items
        """
        size = min(page_size or self.default_page_size, self.max_page_size)
        offset = (page - 1) * size
        
        paginated_query = f"{query} LIMIT ? OFFSET ?"
        rows = db.fetch_all(paginated_query, params + (size, offset))
        
        for row in rows:
            if model_class and hasattr(model_class, 'from_dict'):
                yield model_class.from_dict(row)
            else:
                yield row


class CursorPaginator(Generic[T]):
    """
    Cursor-based pagination for real-time data.
    
    Better for data that changes frequently as it doesn't skip
    items when new data is inserted.
    
    Usage:
        paginator = CursorPaginator(page_size=20)
        
        # First page
        page = paginator.paginate(
            query="SELECT * FROM habit_entries WHERE habit_id = ?",
            db=db,
            cursor=None,
            cursor_column="entry_date",
            params=(habit_id,)
        )
        
        # Next page
        next_page = paginator.paginate(
            query="SELECT * FROM habit_entries WHERE habit_id = ?",
            db=db,
            cursor=page.cursor,
            cursor_column="entry_date",
            params=(habit_id,)
        )
    """
    
    def __init__(self, page_size: int = 20, max_page_size: int = 100):
        self.default_page_size = page_size
        self.max_page_size = max_page_size
    
    def paginate(
        self,
        query: str,
        db,
        cursor: Optional[str] = None,
        cursor_column: str = "id",
        cursor_direction: str = "DESC",
        page_size: Optional[int] = None,
        params: tuple = (),
        model_class: Optional[type] = None
    ) -> "CursorPage[T]":
        """
        Paginate using cursor.
        
        Args:
            query: Base SELECT query
            db: Database instance
            cursor: Cursor value from previous page
            cursor_column: Column to use for cursor
            cursor_direction: ASC or DESC
            page_size: Items per page
            params: Query parameters
            model_class: Optional model class
            
        Returns:
            CursorPage with items and next cursor
        """
        size = min(page_size or self.default_page_size, self.max_page_size)
        
        # Build query with cursor condition
        cursor_condition = ""
        cursor_params = params
        
        if cursor:
            op = "<" if cursor_direction == "DESC" else ">"
            cursor_condition = f" AND {cursor_column} {op} ?"
            cursor_params = params + (cursor,)
        
        # Add ordering and limit
        direction_sql = f"ORDER BY {cursor_column} {cursor_direction}" if "ORDER BY" not in query.upper() else ""
        paginated_query = f"{query} {cursor_condition} {direction_sql} LIMIT ?"
        
        rows = db.fetch_all(paginated_query, cursor_params + (size,))
        
        # Convert to model instances
        items = []
        for row in rows:
            if model_class and hasattr(model_class, 'from_dict'):
                items.append(model_class.from_dict(row))
            else:
                items.append(row)
        
        # Get next cursor
        next_cursor = None
        if len(items) == size and items:
            last_item = items[-1] if isinstance(items[-1], dict) else items[-1].to_dict() if hasattr(items[-1], 'to_dict') else {}
            next_cursor = last_item.get(cursor_column)
        
        return CursorPage(
            items=items,
            cursor=next_cursor,
            has_more=next_cursor is not None
        )


@dataclass
class CursorPage(Generic[T]):
    """A page of results with cursor for next page."""
    items: List[T]
    cursor: Optional[str] = None
    has_more: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "items": self.items,
            "cursor": self.cursor,
            "has_more": self.has_more
        }


# Convenience functions
def paginate_query(
    query: str,
    count_query: str,
    db,
    page: int = 1,
    page_size: int = 20,
    params: tuple = (),
    model_class: Optional[type] = None
) -> Page:
    """
    Convenience function for pagination.
    
    Args:
        query: Base SELECT query
        count_query: Count query
        db: Database instance
        page: Page number
        page_size: Items per page
        params: Query parameters
        model_class: Optional model class
        
    Returns:
        Page with items and metadata
    """
    paginator = Paginator(page_size=page_size)
    return paginator.paginate(query, count_query, db, page, page_size, params, model_class)


# Export
__all__ = [
    "Page",
    "Paginator",
    "CursorPage",
    "CursorPaginator",
    "paginate_query",
]