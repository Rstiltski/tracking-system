"""
Lazy Loader - Component-Level Lazy Loading

Provides lazy loading functionality for expensive components and pages.
Optimizes performance by deferring loading until actually needed.

Usage:
    from tracking_app.components.lazy_loader import LazyLoader, lazy_component
    
    # Create lazy loader
    loader = LazyLoader(expensive_function, "Loading...")
    result = loader.load()
    
    # Or use decorator
    @lazy_component("Loading charts...")
    def render_charts():
        return expensive_chart_rendering()
"""

import streamlit as st
from typing import Callable, Any, Optional, Union
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class LazyLoader:
    """
    Lazy loading wrapper for expensive components.
    
    Features:
    - Deferred loading until first access
    - Loading state management
    - Performance timing
    - Error handling
    - Reset functionality
    """
    
    def __init__(self, component_func: Callable, loading_text: str = "Loading..."):
        """
        Initialize lazy loader.
        
        Args:
            component_func: Function to load lazily
            loading_text: Text to display during loading
        """
        self.component_func = component_func
        self.loading_text = loading_text
        self._loaded = False
        self._result = None
        self._load_time = None
        self._error = None
    
    def load(self, *args, **kwargs) -> Any:
        """
        Load the component if not already loaded.
        
        Args:
            *args: Arguments to pass to component function
            **kwargs: Keyword arguments to pass to component function
            
        Returns:
            Result of component function
            
        Raises:
            Exception: If component loading fails
        """
        if not self._loaded:
            start_time = time.time()
            
            try:
                with st.spinner(self.loading_text):
                    self._result = self.component_func(*args, **kwargs)
                
                self._loaded = True
                self._load_time = time.time() - start_time
                
                logger.info(
                    f"Lazy loaded {self.component_func.__name__} "
                    f"in {self._load_time:.3f}s"
                )
                
            except Exception as e:
                self._error = e
                self._loaded = True  # Mark as loaded to prevent retry
                logger.error(
                    f"Failed to lazy load {self.component_func.__name__}: {e}"
                )
                raise
        
        if self._error:
            raise self._error
        
        return self._result
    
    def is_loaded(self) -> bool:
        """Check if component is loaded."""
        return self._loaded
    
    def get_load_time(self) -> Optional[float]:
        """Get component load time in seconds."""
        return self._load_time
    
    def has_error(self) -> bool:
        """Check if component failed to load."""
        return self._error is not None
    
    def get_error(self) -> Optional[Exception]:
        """Get the error that occurred during loading."""
        return self._error
    
    def reset(self) -> None:
        """Reset loaded state (for testing or refresh)."""
        self._loaded = False
        self._result = None
        self._load_time = None
        self._error = None
    
    def force_reload(self, *args, **kwargs) -> Any:
        """
        Force reload the component.
        
        Args:
            *args: Arguments to pass to component function
            **kwargs: Keyword arguments to pass to component function
            
        Returns:
            Result of component function
        """
        self.reset()
        return self.load(*args, **kwargs)


def lazy_component(
    loading_text: str = "Loading...",
    cache_key: Optional[str] = None
) -> Callable:
    """
    Decorator to create lazy-loaded components.
    
    Args:
        loading_text: Text to display during loading
        cache_key: Optional cache key for Streamlit caching
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create lazy loader instance
            loader = LazyLoader(func, loading_text)
            
            # Use Streamlit cache if cache_key provided
            if cache_key:
                @st.cache_data(ttl=300, show_spinner=False)
                def cached_loader():
                    return loader.load(*args, **kwargs)
                
                return cached_loader()
            else:
                return loader.load(*args, **kwargs)
        
        # Add loader methods to wrapper
        wrapper._lazy_loader = LazyLoader(func, loading_text)
        wrapper.is_loaded = lambda: wrapper._lazy_loader.is_loaded()
        wrapper.get_load_time = lambda: wrapper._lazy_loader.get_load_time()
        wrapper.has_error = lambda: wrapper._lazy_loader.has_error()
        wrapper.get_error = lambda: wrapper._lazy_loader.get_error()
        wrapper.reset = lambda: wrapper._lazy_loader.reset()
        wrapper.force_reload = lambda *args, **kwargs: wrapper._lazy_loader.force_reload(*args, **kwargs)
        
        return wrapper
    
    return decorator


class LazyPage:
    """
    Lazy loading wrapper for entire pages.
    
    Features:
    - Page-level lazy loading
    - Navigation integration
    - Performance tracking
    - Error recovery
    """
    
    def __init__(
        self,
        page_func: Callable,
        page_name: str,
        loading_text: str = "Loading page...",
        icon: str = "📄"
    ):
        """
        Initialize lazy page.
        
        Args:
            page_func: Function that renders the page
            page_name: Name of the page
            loading_text: Text to display during loading
            icon: Icon to display with page name
        """
        self.page_func = page_func
        self.page_name = page_name
        self.loading_text = loading_text
        self.icon = icon
        self._loaded = False
        self._load_time = None
        self._error = None
        self._access_count = 0
    
    def render(self) -> None:
        """
        Render the page with lazy loading.
        
        Raises:
            Exception: If page rendering fails
        """
        self._access_count += 1
        
        if not self._loaded:
            start_time = time.time()
            
            try:
                with st.spinner(self.loading_text):
                    self.page_func()
                
                self._loaded = True
                self._load_time = time.time() - start_time
                
                logger.info(
                    f"Lazy loaded page '{self.page_name}' "
                    f"in {self._load_time:.3f}s "
                    f"(access #{self._access_count})"
                )
                
            except Exception as e:
                self._error = e
                self._loaded = True  # Mark as loaded to prevent retry
                
                logger.error(
                    f"Failed to lazy load page '{self.page_name}': {e}"
                )
                
                # Display error in Streamlit
                st.error(f"Error loading page '{self.page_name}': {e}")
                st.info("Please try refreshing the page or contact support.")
                
        elif self._error:
            # Re-display error if it occurred
            st.error(f"Error loading page '{self.page_name}': {self._error}")
        else:
            # Page already loaded, just render it again
            self.page_func()
    
    def is_loaded(self) -> bool:
        """Check if page is loaded."""
        return self._loaded
    
    def get_load_time(self) -> Optional[float]:
        """Get page load time in seconds."""
        return self._load_time
    
    def get_access_count(self) -> int:
        """Get number of times page has been accessed."""
        return self._access_count
    
    def reset(self) -> None:
        """Reset loaded state."""
        self._loaded = False
        self._load_time = None
        self._error = None
        self._access_count = 0


def lazy_page(
    page_name: str,
    loading_text: str = "Loading page...",
    icon: str = "📄"
) -> Callable:
    """
    Decorator to create lazy-loaded pages.
    
    Args:
        page_name: Name of the page
        loading_text: Text to display during loading
        icon: Icon to display with page name
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper():
            page = LazyPage(func, page_name, loading_text, icon)
            page.render()
        
        # Add page methods to wrapper
        wrapper._lazy_page = LazyPage(func, page_name, loading_text, icon)
        wrapper.is_loaded = lambda: wrapper._lazy_page.is_loaded()
        wrapper.get_load_time = lambda: wrapper._lazy_page.get_load_time()
        wrapper.get_access_count = lambda: wrapper._lazy_page.get_access_count()
        wrapper.reset = lambda: wrapper._lazy_page.reset()
        
        return wrapper
    
    return decorator


# Utility functions for lazy loading management

def create_lazy_button(
    label: str,
    action_func: Callable,
    loading_text: str = "Processing...",
    key: Optional[str] = None
) -> bool:
    """
    Create a button that triggers lazy loading.
    
    Args:
        label: Button label
        action_func: Function to execute when button is clicked
        loading_text: Text to display during execution
        key: Optional key for the button
        
    Returns:
        True if button was clicked, False otherwise
    """
    if st.button(label, key=key):
        with st.spinner(loading_text):
            action_func()
        return True
    return False


def lazy_if(condition: bool, func: Callable, *args, **kwargs) -> Any:
    """
    Conditionally load a component based on a condition.
    
    Args:
        condition: Condition to check
        func: Function to call if condition is True
        *args: Arguments to pass to function
        **kwargs: Keyword arguments to pass to function
        
    Returns:
        Result of function if condition is True, None otherwise
    """
    if condition:
        return func(*args, **kwargs)
    return None


def lazy_cache(
    func: Callable,
    ttl: int = 300,
    max_entries: int = 100
) -> Callable:
    """
    Cache expensive computations with lazy loading.
    
    Args:
        func: Function to cache
        ttl: Time to live in seconds
        max_entries: Maximum number of cache entries
        
    Returns:
        Cached function
    """
    @st.cache_data(ttl=ttl, max_entries=max_entries, show_spinner=False)
    def cached_func(*args, **kwargs):
        return func(*args, **kwargs)
    
    return cached_func


# Export
__all__ = [
    'LazyLoader',
    'lazy_component',
    'LazyPage',
    'lazy_page',
    'create_lazy_button',
    'lazy_if',
    'lazy_cache'
]