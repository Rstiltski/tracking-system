"""
Optimized Sidebar - Lazy Loading Navigation

Provides an optimized sidebar with lazy loading for navigation.
Defers loading of non-active page modules until they are needed.

Usage:
    from tracking_app.components.sidebar import LazySidebar, create_sidebar
    
    # Create sidebar
    sidebar = create_sidebar()
    
    # Render sidebar and get selected page
    selected_page = sidebar.render()
    
    # Render current page
    sidebar.render_current_page()
"""

import streamlit as st
from typing import Dict, List, Callable, Any, Optional
import time
import logging
from dataclasses import dataclass, field
from collections import defaultdict

from tracking_app.components.lazy_loader import LazyPage
from brain.utils.performance_monitor import get_performance_monitor

logger = logging.getLogger(__name__)


def render_sidebar(**kwargs):
    """
    Render the sidebar navigation.
    
    This is a simple sidebar rendering function that provides
    basic navigation for the tracking application.
    
    Args:
        **kwargs: Additional keyword arguments (e.g., show_streak_freeze)
                  These are ignored for compatibility with existing calls.
    
    Returns:
        str: The selected page name from sidebar navigation
    """
    # Use the existing LazySidebar if available, otherwise create basic navigation
    try:
        sidebar = get_sidebar()
        if sidebar:
            return sidebar.render()
    except Exception:
        pass
    
    # Fallback: Do not create custom navigation - let Streamlit handle pages natively
    # Streamlit's multi-page apps automatically show pages in the sidebar
    return None



@dataclass
class PageConfig:
    """Configuration for a sidebar page."""
    func: Callable
    icon: str
    loading_text: str
    load_time: Optional[float] = None
    loaded: bool = False
    access_count: int = 0
    last_accessed: Optional[float] = None


class LazySidebar:
    """
    Optimized sidebar with lazy loading for navigation.
    
    Features:
    - Lazy loading of page modules
    - Performance monitoring
    - Memory optimization
    - Navigation state management
    """
    
    def __init__(self):
        self.pages: Dict[str, PageConfig] = {}
        self.current_page: Optional[str] = None
        self._navigation_history: List[str] = []
        self._total_load_time: float = 0.0
        self._page_load_times: Dict[str, List[float]] = defaultdict(list)
    
    def add_page(
        self, 
        name: str, 
        page_func: Callable, 
        icon: str = "📄",
        loading_text: str = "Loading page..."
    ) -> None:
        """
        Add a page with lazy loading.
        
        Args:
            name: Page name
            page_func: Function that renders the page
            icon: Icon to display with page name
            loading_text: Text to display during loading
        """
        self.pages[name] = PageConfig(
            func=page_func,
            icon=icon,
            loading_text=loading_text
        )
        
        # Set default current page
        if self.current_page is None:
            self.current_page = name
        
        logger.info(f"Added page: {name} with icon {icon}")
    
    def render(self) -> str:
        """
        Render the sidebar and return selected page name.
        
        Returns:
            Selected page name
        """
        # Sidebar header
        st.sidebar.title("🎯 Tracking System")
        
        # Performance stats
        self._render_performance_stats()
        
        st.sidebar.divider()
        
        # Navigation buttons
        selected_page = self._render_navigation()
        
        # Update current page if selection changed
        if selected_page and selected_page != self.current_page:
            self._navigation_history.append(self.current_page)
            self.current_page = selected_page
            
            # Limit history to last 10 navigations
            if len(self._navigation_history) > 10:
                self._navigation_history.pop(0)
            
            logger.info(f"Navigation: {selected_page}")
        
        # Sidebar footer
        self._render_sidebar_footer()
        
        return self.current_page
    
    def render_current_page(self) -> None:
        """
        Render the currently selected page with lazy loading.
        
        Raises:
            KeyError: If current page is not found
        """
        if not self.current_page or self.current_page not in self.pages:
            raise KeyError(f"Current page '{self.current_page}' not found")
        
        page_config = self.pages[self.current_page]
        
        # Create lazy page wrapper
        lazy_page = LazyPage(
            page_func=page_config.func,
            page_name=self.current_page,
            loading_text=page_config.loading_text,
            icon=page_config.icon
        )
        
        # Measure load time
        start_time = time.time()
        
        try:
            # Render the page
            lazy_page.render()
            
            # Record load time
            load_time = time.time() - start_time
            self._total_load_time += load_time
            self._page_load_times[self.current_page].append(load_time)
            
            # Update page config
            page_config.loaded = True
            page_config.load_time = load_time
            page_config.access_count += 1
            page_config.last_accessed = time.time()
            
            logger.info(
                f"Page '{self.current_page}' loaded in {load_time:.3f}s "
                f"(total: {self._total_load_time:.3f}s)"
            )
            
        except Exception as e:
            logger.error(f"Error rendering page '{self.current_page}': {e}")
            st.error(f"Error loading page: {e}")
    
    def _render_navigation(self) -> Optional[str]:
        """Render navigation buttons and return selected page."""
        selected_page = None
        
        # Group pages by priority (you can customize this logic)
        priority_groups = self._group_pages_by_priority()
        
        for group_name, page_names in priority_groups.items():
            if group_name != "All":
                st.sidebar.subheader(f"**{group_name}**")
            
            for page_name in page_names:
                page_config = self.pages[page_name]
                
                # Create button with status indicator
                button_label = self._get_button_label(page_name, page_config)
                
                if st.sidebar.button(button_label, key=f"nav_{page_name}"):
                    selected_page = page_name
            
            if group_name != "All":
                st.sidebar.divider()
        
        return selected_page
    
    def _render_performance_stats(self) -> None:
        """Render performance statistics in sidebar."""
        st.sidebar.subheader("⚡ Performance")
        
        # Overall stats
        total_pages = len(self.pages)
        loaded_pages = sum(1 for p in self.pages.values() if p.loaded)
        
        st.sidebar.write(f"**Loaded:** {loaded_pages}/{total_pages}")
        
        # Average load time
        if self._page_load_times:
            all_load_times = []
            for times in self._page_load_times.values():
                all_load_times.extend(times)
            
            if all_load_times:
                avg_load_time = sum(all_load_times) / len(all_load_times)
                st.sidebar.write(f"**Avg Load Time:** {avg_load_time:.3f}s")
        
        # Total load time
        if self._total_load_time > 0:
            st.sidebar.write(f"**Total Load Time:** {self._total_load_time:.3f}s")
        
        # Memory usage
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            st.sidebar.write(f"**Memory:** {memory_mb:.1f} MB")
        except ImportError:
            pass
        
        # Performance tips
        self._render_performance_tips()
    
    def _render_sidebar_footer(self) -> None:
        """Render sidebar footer with actions."""
        st.sidebar.divider()
        
        # Quick actions
        st.sidebar.subheader("🔧 Actions")
        
        if st.sidebar.button("🧹 Clear Page States", key="clear_states"):
            self.reset_all_page_states()
            st.rerun()
        
        if st.sidebar.button("📊 Show Stats", key="show_stats"):
            self.show_detailed_stats()
        
        # Navigation history
        if self._navigation_history:
            st.sidebar.subheader("🔙 History")
            for page in reversed(self._navigation_history[-5:]):  # Show last 5
                st.sidebar.write(f"- {page}")
    
    def _render_performance_tips(self) -> None:
        """Render performance optimization tips."""
        total_pages = len(self.pages)
        loaded_pages = sum(1 for p in self.pages.values() if p.loaded)
        
        if loaded_pages == 0:
            st.sidebar.success("✅ Excellent! No pages loaded yet.")
        elif loaded_pages < 3:
            st.sidebar.info("ℹ️ Good lazy loading in action!")
        elif loaded_pages > total_pages * 0.7:
            st.sidebar.warning("⚠️ Many pages loaded. Consider more aggressive lazy loading.")
        
        # Show not loaded pages
        not_loaded = [name for name, config in self.pages.items() if not config.loaded]
        if not_loaded:
            with st.sidebar.expander("📦 Not Loaded Pages"):
                for page in not_loaded[:5]:  # Show first 5
                    st.write(f"- {page}")
                if len(not_loaded) > 5:
                    st.write(f"... and {len(not_loaded) - 5} more")
    
    def _group_pages_by_priority(self) -> Dict[str, List[str]]:
        """
        Group pages by priority for organized navigation.
        
        Returns:
            Dictionary mapping group names to page name lists
        """
        # Define page priorities (customize as needed)
        priorities = {
            "🏠 Dashboard": ["Dashboard"],
            "📋 Core Tracking": ["Habits", "Tasks", "Goals"],
            "📊 Analytics": ["Habit Analytics", "Habit Experiments", "Insights"],
            "👥 Social": ["Friends", "Leaderboards", "Challenges"],
            "⚙️ Settings": ["Settings", "Data Export", "Backup & Restore"],
            "Other": []
        }
        
        # Add any pages not in predefined groups to "Other"
        all_priority_pages = set()
        for page_list in priorities.values():
            all_priority_pages.update(page_list)
        
        other_pages = [name for name in self.pages.keys() if name not in all_priority_pages]
        priorities["Other"] = other_pages
        
        # Return only groups that have pages
        return {name: pages for name, pages in priorities.items() if pages}
    
    def _get_button_label(self, page_name: str, page_config: PageConfig) -> str:
        """
        Get button label with status indicator.
        
        Args:
            page_name: Name of the page
            page_config: Page configuration
            
        Returns:
            Formatted button label
        """
        status_icon = "🟢" if page_config.loaded else "⚪"
        return f"{status_icon} {page_config.icon} {page_name}"
    
    def get_load_stats(self) -> Dict[str, Any]:
        """
        Get detailed load statistics.
        
        Returns:
            Dictionary with load statistics
        """
        stats = {
            'total_pages': len(self.pages),
            'loaded_pages': sum(1 for p in self.pages.values() if p.loaded),
            'total_load_time': self._total_load_time,
            'page_load_times': {},
            'not_loaded': [name for name, config in self.pages.items() if not config.loaded],
            'navigation_history': self._navigation_history.copy(),
            'current_page': self.current_page
        }
        
        # Page-specific load times
        for name, config in self.pages.items():
            if config.load_time is not None:
                stats['page_load_times'][name] = {
                    'load_time': config.load_time,
                    'access_count': config.access_count,
                    'loaded': config.loaded
                }
        
        # Calculate averages
        if stats['page_load_times']:
            load_times = [info['load_time'] for info in stats['page_load_times'].values()]
            stats['avg_load_time'] = sum(load_times) / len(load_times)
        
        return stats
    
    def reset_all_page_states(self) -> None:
        """Reset all page states (for testing or refresh)."""
        for page_config in self.pages.values():
            page_config.loaded = False
            page_config.load_time = None
            page_config.access_count = 0
            page_config.last_accessed = None
        
        self._total_load_time = 0.0
        self._page_load_times.clear()
        self._navigation_history.clear()
        
        logger.info("All page states reset")
    
    def show_detailed_stats(self) -> None:
        """Show detailed performance statistics."""
        stats = self.get_load_stats()
        
        st.subheader("📊 Detailed Performance Statistics")
        
        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Pages", stats['total_pages'])
        with col2:
            st.metric("Loaded Pages", stats['loaded_pages'])
        with col3:
            st.metric("Total Load Time", f"{stats['total_load_time']:.3f}s")
        
        # Page details
        if stats['page_load_times']:
            st.subheader("Page Load Times")
            
            for page_name, info in stats['page_load_times'].items():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{page_name}**")
                with col2:
                    st.write(f"⏱️ {info['load_time']:.3f}s")
                with col3:
                    st.write(f"👁️ {info['access_count']}")
        
        # Not loaded pages
        if stats['not_loaded']:
            st.subheader("Not Loaded Pages")
            for page in stats['not_loaded']:
                st.write(f"- {page}")
        
        # Navigation history
        if stats['navigation_history']:
            st.subheader("Navigation History")
            for i, page in enumerate(reversed(stats['navigation_history'][-10:]), 1):
                st.write(f"{i}. {page}")
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / 1024 / 1024
            }
        except ImportError:
            return {'error': 'psutil not available'}


# Global sidebar instance
_sidebar: Optional[LazySidebar] = None


def get_sidebar() -> LazySidebar:
    """Get the global sidebar instance."""
    global _sidebar
    if _sidebar is None:
        _sidebar = LazySidebar()
    return _sidebar


def create_sidebar() -> LazySidebar:
    """
    Create and configure the main sidebar.
    
    Returns:
        Configured LazySidebar instance
    """
    sidebar = get_sidebar()
    
    # Add pages with lazy loading
    # Note: Import pages here to avoid circular imports
    # You may need to adjust the import paths based on your project structure
    
    # High priority pages (frequently accessed)
    sidebar.add_page("Dashboard", lambda: st.write("Dashboard content"), "🏠", "Loading dashboard...")
    sidebar.add_page("Habits", lambda: st.write("Habits content"), "✅", "Loading habits...")
    sidebar.add_page("Tasks", lambda: st.write("Tasks content"), "📝", "Loading tasks...")
    sidebar.add_page("Goals", lambda: st.write("Goals content"), "🎯", "Loading goals...")
    
    # Medium priority pages
    sidebar.add_page("Health", lambda: st.write("Health content"), "❤️", "Loading health data...")
    sidebar.add_page("Finances", lambda: st.write("Finances content"), "💰", "Loading finances...")
    sidebar.add_page("Time", lambda: st.write("Time content"), "⏰", "Loading time tracking...")
    sidebar.add_page("Emotional Health", lambda: st.write("Emotional Health content"), "😊", "Loading mood data...")
    
    # Lower priority pages (less frequently accessed)
    sidebar.add_page("Achievements", lambda: st.write("Achievements content"), "🏆", "Loading achievements...")
    sidebar.add_page("Challenges", lambda: st.write("Challenges content"), "💪", "Loading challenges...")
    sidebar.add_page("Friends", lambda: st.write("Friends content"), "👥", "Loading friends...")
    sidebar.add_page("Leaderboards", lambda: st.write("Leaderboards content"), "📊", "Loading leaderboards...")
    
    # Analytics and settings pages
    sidebar.add_page("Habit Analytics", lambda: st.write("Habit Analytics content"), "📈", "Loading analytics...")
    sidebar.add_page("Habit Experiments", lambda: st.write("Habit Experiments content"), "🔬", "Loading experiments...")
    sidebar.add_page("Settings", lambda: st.write("Settings content"), "⚙️", "Loading settings...")
    
    logger.info(f"Sidebar created with {len(sidebar.pages)} pages")
    return sidebar


# Export
__all__ = [
    'LazySidebar',
    'create_sidebar',
    'get_sidebar',
    'PageConfig',
    'render_sidebar'
]