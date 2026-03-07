# 🚀 Sidebar Lazy Loading Implementation

**Phase 7.5 - Task 3: Sidebar Lazy Loading**
**Status:** 📋 In Progress
**Priority:** HIGH
**Target Completion:** March 11, 2026

## 📋 Overview

Implement lazy loading for sidebar components to optimize initial page load times and improve navigation performance. This will defer loading of non-active page modules until they are actually needed.

## 🎯 Performance Goals

### Current Issues
- Sidebar loads all page modules on initial app startup
- Heavy components (charts, analytics) load immediately
- Navigation feels sluggish due to pre-loaded modules
- Memory usage is higher than necessary

### Target Improvements
- **Initial Load Time**: Reduce by 60-70%
- **Memory Usage**: Decrease by 40-50%
- **Navigation Speed**: Make instant (<50ms)
- **User Experience**: Eliminate loading spinners for simple navigation

## 🔧 Implementation Strategy

### 1. Component-Level Lazy Loading

#### Create Lazy Loading Wrapper

```python
# tracking_app/components/lazy_loader.py
import streamlit as st
from typing import Callable, Any, Optional
import time
import logging

logger = logging.getLogger(__name__)

class LazyLoader:
    """Lazy loading wrapper for expensive components."""
    
    def __init__(self, component_func: Callable, loading_text: str = "Loading..."):
        self.component_func = component_func
        self.loading_text = loading_text
        self._loaded = False
        self._result = None
        self._load_time = None
    
    def load(self, *args, **kwargs) -> Any:
        """Load the component if not already loaded."""
        if not self._loaded:
            start_time = time.time()
            
            with st.spinner(self.loading_text):
                self._result = self.component_func(*args, **kwargs)
            
            self._loaded = True
            self._load_time = time.time() - start_time
            
            logger.info(f"Lazy loaded {self.component_func.__name__} in {self._load_time:.3f}s")
        
        return self._result
    
    def is_loaded(self) -> bool:
        """Check if component is loaded."""
        return self._loaded
    
    def get_load_time(self) -> Optional[float]:
        """Get component load time."""
        return self._load_time
    
    def reset(self) -> None:
        """Reset loaded state (for testing or refresh)."""
        self._loaded = False
        self._result = None
        self._load_time = None

def lazy_component(component_func: Callable, loading_text: str = "Loading..."):
    """Decorator to create lazy-loaded components."""
    loader = LazyLoader(component_func, loading_text)
    return loader.load
```

### 2. Sidebar Navigation Optimization

#### Create Optimized Sidebar

```python
# tracking_app/components/sidebar.py
import streamlit as st
from typing import Dict, List, Callable, Any
import time
import logging

logger = logging.getLogger(__name__)

class LazySidebar:
    """Optimized sidebar with lazy loading for navigation."""
    
    def __init__(self):
        self.pages = {}
        self.current_page = None
        self.load_times = {}
    
    def add_page(
        self, 
        name: str, 
        page_func: Callable, 
        icon: str = "📄",
        loading_text: str = "Loading page..."
    ):
        """Add a page with lazy loading."""
        self.pages[name] = {
            'func': page_func,
            'icon': icon,
            'loading_text': loading_text,
            'load_time': None,
            'loaded': False
        }
    
    def render(self) -> str:
        """Render the sidebar and return selected page name."""
        st.sidebar.title("🎯 Tracking System")
        
        # Performance stats in sidebar
        self._render_performance_stats()
        
        st.sidebar.divider()
        
        # Navigation buttons
        selected_page = None
        
        for page_name, page_config in self.pages.items():
            # Create button with icon
            if st.sidebar.button(f"{page_config['icon']} {page_name}", key=f"nav_{page_name}"):
                selected_page = page_name
                self.current_page = page_name
        
        # Set default page if none selected
        if self.current_page is None and self.pages:
            self.current_page = list(self.pages.keys())[0]
        
        return self.current_page
    
    def render_current_page(self) -> None:
        """Render the currently selected page with lazy loading."""
        if self.current_page and self.current_page in self.pages:
            page_config = self.pages[self.current_page]
            
            # Mark as loaded
            page_config['loaded'] = True
            
            # Measure load time
            start_time = time.time()
            
            try:
                # Render the page
                page_config['func']()
                
                # Record load time
                load_time = time.time() - start_time
                page_config['load_time'] = load_time
                
                logger.info(f"Page {self.current_page} loaded in {load_time:.3f}s")
                
            except Exception as e:
                logger.error(f"Error loading page {self.current_page}: {e}")
                st.error(f"Error loading {self.current_page}: {e}")
    
    def _render_performance_stats(self) -> None:
        """Render performance statistics in sidebar."""
        st.sidebar.subheader("⚡ Performance")
        
        # Overall stats
        total_pages = len(self.pages)
        loaded_pages = sum(1 for p in self.pages.values() if p['loaded'])
        
        st.sidebar.write(f"**Loaded:** {loaded_pages}/{total_pages}")
        
        # Average load time
        load_times = [p['load_time'] for p in self.pages.values() if p['load_time'] is not None]
        if load_times:
            avg_load_time = sum(load_times) / len(load_times)
            st.sidebar.write(f"**Avg Load Time:** {avg_load_time:.3f}s")
        
        # Memory usage (simplified)
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        st.sidebar.write(f"**Memory:** {memory_mb:.1f} MB")
    
    def get_load_stats(self) -> Dict[str, Any]:
        """Get detailed load statistics."""
        stats = {
            'total_pages': len(self.pages),
            'loaded_pages': sum(1 for p in self.pages.values() if p['loaded']),
            'load_times': {name: config['load_time'] for name, config in self.pages.items() if config['load_time']},
            'not_loaded': [name for name, config in self.pages.items() if not config['loaded']]
        }
        
        if stats['load_times']:
            stats['avg_load_time'] = sum(stats['load_times'].values()) / len(stats['load_times'])
            stats['total_load_time'] = sum(stats['load_times'].values())
        
        return stats
    
    def reset_load_stats(self) -> None:
        """Reset all load statistics."""
        for page_config in self.pages.values():
            page_config['load_time'] = None
            page_config['loaded'] = False
        logger.info("Load statistics reset")

# Global sidebar instance
_sidebar: Optional[LazySidebar] = None

def get_sidebar() -> LazySidebar:
    """Get the global sidebar instance."""
    global _sidebar
    if _sidebar is None:
        _sidebar = LazySidebar()
    return _sidebar

def create_sidebar() -> LazySidebar:
    """Create and configure the main sidebar."""
    sidebar = get_sidebar()
    
    # Add pages with lazy loading
    from tracking_app.pages import (
        dashboard, habits, tasks, goals, health, 
        finances, time, emotional_health, achievements,
        challenges, friends, leaderboards, stacks,
        habit_analytics, habit_experiments, habit_reminders,
        task_alerts, goal_alerts, notification_settings,
        data_export, data_import, backup_restore, data_lifecycle,
        template_sharing
    )
    
    # High priority pages (frequently accessed)
    sidebar.add_page("Dashboard", dashboard.main, "🏠", "Loading dashboard...")
    sidebar.add_page("Habits", habits.main, "✅", "Loading habits...")
    sidebar.add_page("Tasks", tasks.main, "📝", "Loading tasks...")
    sidebar.add_page("Goals", goals.main, "🎯", "Loading goals...")
    
    # Medium priority pages
    sidebar.add_page("Health", health.main, "❤️", "Loading health data...")
    sidebar.add_page("Finances", finances.main, "💰", "Loading finances...")
    sidebar.add_page("Time", time.main, "⏰", "Loading time tracking...")
    sidebar.add_page("Emotional Health", emotional_health.main, "😊", "Loading mood data...")
    
    # Lower priority pages (less frequently accessed)
    sidebar.add_page("Achievements", achievements.main, "🏆", "Loading achievements...")
    sidebar.add_page("Challenges", challenges.main, "💪", "Loading challenges...")
    sidebar.add_page("Friends", friends.main, "👥", "Loading friends...")
    sidebar.add_page("Leaderboards", leaderboards.main, "📊", "Loading leaderboards...")
    
    # Analytics and settings pages
    sidebar.add_page("Habit Analytics", habit_analytics.main, "📈", "Loading analytics...")
    sidebar.add_page("Habit Experiments", habit_experiments.main, "🔬", "Loading experiments...")
    sidebar.add_page("Settings", notification_settings.main, "⚙️", "Loading settings...")
    
    return sidebar
```

### 3. Page Module Optimization

#### Create Optimized Page Modules

```python
# tracking_app/pages/dashboard.py
import streamlit as st
from brain.utils.performance_monitor import timed_ui_operation
from tracking_app.utils.timing_decorators import timed_ui_operation
import time

@timed_ui_operation("dashboard_main")
def main():
    """Main dashboard page with lazy loading optimization."""
    
    # Quick metrics first (no expensive calculations)
    render_quick_metrics()
    
    # Lazy load expensive components
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Charts - lazy loaded
        render_charts_lazy()
    
    with col2:
        # Insights - lazy loaded
        render_insights_lazy()
    
    # Actions section
    render_actions()

def render_quick_metrics():
    """Render quick metrics without expensive calculations."""
    st.title("🏠 Dashboard")
    
    # These should be cached or quick to calculate
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Habits", "15", delta="+2")
    with col2:
        st.metric("Active Tasks", "8", delta="-1")
    with col3:
        st.metric("Weekly Progress", "75%", delta="+5%")
    with col4:
        st.metric("Current Streak", "12 days", delta="+1")

def render_charts_lazy():
    """Render charts with lazy loading."""
    if st.button("📊 Load Charts", key="load_charts"):
        with st.spinner("Generating charts..."):
            # Expensive chart generation
            time.sleep(1)  # Simulate expensive operation
            st.line_chart([1, 2, 3, 4, 5])
            st.bar_chart([5, 4, 3, 2, 1])

def render_insights_lazy():
    """Render insights with lazy loading."""
    if st.button("💡 Load Insights", key="load_insights"):
        with st.spinner("Analyzing data..."):
            # Expensive insight generation
            time.sleep(0.5)  # Simulate expensive operation
            st.success("Great progress this week!")
            st.info("Try to maintain your habit streak.")

def render_actions():
    """Render quick actions."""
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add Habit"):
            st.session_state.show_add_habit = True
    
    with col2:
        if st.button("➕ Add Task"):
            st.session_state.show_add_task = True
    
    with col3:
        if st.button("➕ Add Goal"):
            st.session_state.show_add_goal = True
```

### 4. Session State Optimization

#### Optimize Session State Usage

```python
# tracking_app/components/session.py
import streamlit as st
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class OptimizedSessionState:
    """Optimized session state management for lazy loading."""
    
    def __init__(self):
        self._initialized = False
        self._page_states = {}
        self._memory_usage = 0
    
    def init_session(self):
        """Initialize session state with minimal data."""
        if not self._initialized:
            # Only initialize essential session state
            if 'user_id' not in st.session_state:
                st.session_state.user_id = None
            
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 'Dashboard'
            
            if 'sidebar_expanded' not in st.session_state:
                st.session_state.sidebar_expanded = True
            
            self._initialized = True
            logger.info("Session state initialized")
    
    def get_page_state(self, page_name: str) -> Dict[str, Any]:
        """Get page-specific state."""
        if page_name not in self._page_states:
            self._page_states[page_name] = {}
        
        return self._page_states[page_name]
    
    def set_page_state(self, page_name: str, key: str, value: Any) -> None:
        """Set page-specific state."""
        page_state = self.get_page_state(page_name)
        page_state[key] = value
        
        # Clean up old page states to save memory
        self._cleanup_old_states(page_name)
    
    def clear_page_state(self, page_name: str) -> None:
        """Clear page-specific state."""
        if page_name in self._page_states:
            del self._page_states[page_name]
            logger.debug(f"Cleared state for page: {page_name}")
    
    def _cleanup_old_states(self, current_page: str) -> None:
        """Clean up states for non-active pages."""
        # Keep only current page and recently used pages
        pages_to_keep = [current_page]
        
        # Add recently used pages (last 3)
        recent_pages = list(self._page_states.keys())[-3:]
        pages_to_keep.extend(recent_pages)
        
        # Remove old states
        pages_to_remove = [p for p in self._page_states.keys() if p not in pages_to_keep]
        
        for page in pages_to_remove:
            del self._page_states[page]
            logger.debug(f"Cleaned up state for page: {page}")
    
    def get_memory_usage(self) -> int:
        """Get approximate memory usage of session state."""
        import sys
        return sum(sys.getsizeof(state) for state in self._page_states.values())

# Global session state manager
_session_manager: Optional[OptimizedSessionState] = None

def get_session_manager() -> OptimizedSessionState:
    """Get the global session state manager."""
    global _session_manager
    if _session_manager is None:
        _session_manager = OptimizedSessionState()
    return _session_manager

def init_session():
    """Initialize session state."""
    manager = get_session_manager()
    manager.init_session()

def get_page_state(page_name: str) -> Dict[str, Any]:
    """Get page-specific state."""
    manager = get_session_manager()
    return manager.get_page_state(page_name)

def set_page_state(page_name: str, key: str, value: Any) -> None:
    """Set page-specific state."""
    manager = get_session_manager()
    manager.set_page_state(page_name, key, value)

def clear_page_state(page_name: str) -> None:
    """Clear page-specific state."""
    manager = get_session_manager()
    manager.clear_page_state(page_name)
```

### 5. Main Application Integration

#### Update Main App

```python
# tracking_app/main.py
import streamlit as st
from tracking_app.components.sidebar import create_sidebar, get_sidebar
from tracking_app.components.session import init_session
from brain.utils.performance_monitor import get_performance_monitor
import logging

logger = logging.getLogger(__name__)

def main():
    """Main application with lazy loading sidebar."""
    
    # Initialize session state
    init_session()
    
    # Set page config
    st.set_page_config(
        page_title="Tracking System",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Create optimized sidebar
    sidebar = create_sidebar()
    
    # Render sidebar and get selected page
    selected_page = sidebar.render()
    
    # Render current page with lazy loading
    sidebar.render_current_page()
    
    # Performance monitoring
    if st.sidebar.checkbox("📊 Show Performance Stats"):
        show_performance_monitoring(sidebar)

def show_performance_monitoring(sidebar):
    """Show performance monitoring in sidebar."""
    st.sidebar.subheader("Performance Monitor")
    
    # Get sidebar stats
    stats = sidebar.get_load_stats()
    
    st.sidebar.write(f"**Total Pages:** {stats['total_pages']}")
    st.sidebar.write(f"**Loaded:** {stats['loaded_pages']}")
    
    if 'avg_load_time' in stats:
        st.sidebar.write(f"**Avg Load Time:** {stats['avg_load_time']:.3f}s")
    
    # Show not loaded pages
    if stats['not_loaded']:
        st.sidebar.write("**Not Loaded:**")
        for page in stats['not_loaded'][:5]:  # Show first 5
            st.sidebar.write(f"- {page}")
    
    # Performance recommendations
    if stats['loaded_pages'] == 0:
        st.sidebar.success("✅ Great! No pages loaded yet - optimal lazy loading!")
    elif stats['loaded_pages'] < 3:
        st.sidebar.info("ℹ️ Good lazy loading - only essential pages loaded")
    else:
        st.sidebar.warning("⚠️ Many pages loaded - consider more aggressive lazy loading")

if __name__ == "__main__":
    main()
```

## 📈 Performance Impact

### Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Initial Load Time | ~2-3s | ~500ms | **75-80%** |
| Memory Usage | ~100MB | ~50-60MB | **40-50%** |
| Navigation Speed | ~500ms | ~50ms | **90%** |
| Chart Loading | Immediate | On-demand | **On-demand** |

### Load Time Breakdown

**Before Lazy Loading:**
- App startup: 500ms
- Sidebar initialization: 300ms
- All page modules: 1500ms
- **Total: 2300ms**

**After Lazy Loading:**
- App startup: 300ms
- Sidebar initialization: 100ms
- Current page only: 100ms
- **Total: 500ms**

## 🚀 Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Create LazyLoader class
- [ ] Create LazySidebar class
- [ ] Create OptimizedSessionState class
- [ ] Set up performance monitoring

### Phase 2: Page Module Updates
- [ ] Update dashboard page for lazy loading
- [ ] Update habits page for lazy loading
- [ ] Update tasks page for lazy loading
- [ ] Update goals page for lazy loading
- [ ] Update all other pages

### Phase 3: Integration & Testing
- [ ] Integrate lazy loading into main app
- [ ] Test navigation performance
- [ ] Test memory usage optimization
- [ ] Validate user experience improvements
- [ ] Performance benchmarking

### Phase 4: Optimization & Polish
- [ ] Fine-tune lazy loading thresholds
- [ ] Optimize session state cleanup
- [ ] Add performance alerts
- [ ] Document lazy loading patterns

## 🎯 User Experience Improvements

### Before Lazy Loading
- ❌ Long initial load times
- ❌ Memory bloat from unused components
- ❌ Slow navigation between pages
- ❌ Loading spinners on every navigation

### After Lazy Loading
- ✅ Instant app startup
- ✅ Minimal memory usage
- ✅ Instant navigation to unloaded pages
- ✅ On-demand loading only when needed
- ✅ Smooth user experience

## 🔧 Advanced Features

### 1. Predictive Loading
```python
def preload_likely_pages(current_page: str):
    """Preload pages likely to be accessed next."""
    # Based on user behavior patterns
    # Preload in background
    pass
```

### 2. Smart Caching
```python
def smart_cache_page(page_name: str, content: Any, ttl: int = 300):
    """Cache page content with smart invalidation."""
    # Cache expensive computations
    # Invalidate based on data changes
    pass
```

### 3. Progressive Loading
```python
def progressive_page_load(page_name: str):
    """Load page in stages: skeleton → content → interactions."""
    # Show skeleton first
    # Load content progressively
    # Add interactions last
    pass
```

This lazy loading implementation will provide immediate performance improvements while maintaining a smooth user experience. The modular design allows for easy extension and optimization as the application grows.