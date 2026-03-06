"""
Responsive UI Components - Mobile Optimization

Provides responsive layout components for Streamlit.
Following PROJECT_RULES.md:
- Python-first implementation
- Works with Streamlit
- Mobile-first approach
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class Breakpoint:
    """Responsive breakpoint definition."""
    name: str
    min_width: int
    max_width: int
    columns: int
    description: str


# Standard breakpoints
BREAKPOINTS = {
    "mobile": Breakpoint(
        name="mobile",
        min_width=0,
        max_width=575,
        columns=1,
        description="Single column, collapsible nav"
    ),
    "tablet": Breakpoint(
        name="tablet",
        min_width=576,
        max_width=991,
        columns=2,
        description="Two columns, simplified charts"
    ),
    "desktop": Breakpoint(
        name="desktop",
        min_width=992,
        max_width=float('inf'),
        columns=3,
        description="Full layout"
    ),
}


class ResponsiveLayout:
    """
    Responsive layout manager for Streamlit.
    
    Detects screen size and adjusts layout accordingly.
    
    Usage:
        layout = ResponsiveLayout()
        
        # Get current breakpoint
        bp = layout.get_breakpoint()
        
        # Render responsive columns
        with layout.columns() as cols:
            with cols[0]:
                st.write("Column 1")
    """
    
    def __init__(
        self,
        mobile_breakpoint: int = 576,
        tablet_breakpoint: int = 992
    ):
        """
        Initialize responsive layout.
        
        Args:
            mobile_breakpoint: Max width for mobile (default 576px)
            tablet_breakpoint: Max width for tablet (default 992px)
        """
        self.mobile_bp = mobile_breakpoint
        self.tablet_bp = tablet_breakpoint
        self._current_breakpoint: Optional[str] = None
    
    def get_breakpoint(self, width: Optional[int] = None) -> Breakpoint:
        """
        Get the current breakpoint based on width.
        
        Args:
            width: Screen width in pixels (uses session state if None)
            
        Returns:
            Breakpoint object
        """
        # Try to get from session state
        import streamlit as st
        
        if width is None:
            width = st.session_state.get('screen_width', 1200)
        
        if width < self.mobile_bp:
            self._current_breakpoint = "mobile"
            return BREAKPOINTS["mobile"]
        elif width < self.tablet_bp:
            self._current_breakpoint = "tablet"
            return BREAKPOINTS["tablet"]
        else:
            self._current_breakpoint = "desktop"
            return BREAKPOINTS["desktop"]
    
    def is_mobile(self) -> bool:
        """Check if current view is mobile."""
        bp = self.get_breakpoint()
        return bp.name == "mobile"
    
    def is_tablet(self) -> bool:
        """Check if current view is tablet."""
        bp = self.get_breakpoint()
        return bp.name == "tablet"
    
    def is_desktop(self) -> bool:
        """Check if current view is desktop."""
        bp = self.get_breakpoint()
        return bp.name == "desktop"
    
    def get_columns(self, count: Optional[int] = None) -> int:
        """
        Get number of columns for current breakpoint.
        
        Args:
            count: Override column count (uses breakpoint default if None)
            
        Returns:
            Number of columns
        """
        bp = self.get_breakpoint()
        return count if count is not None else bp.columns
    
    def columns(self, count: Optional[int] = None, **kwargs):
        """
        Create responsive columns.
        
        Args:
            count: Number of columns (uses breakpoint default if None)
            **kwargs: Additional arguments for st.columns
            
        Returns:
            Streamlit columns context manager
        """
        import streamlit as st
        
        num_cols = self.get_columns(count)
        return st.columns(num_cols, **kwargs)
    
    def sidebar_toggle(self) -> bool:
        """
        Check if sidebar should be toggleable (mobile).
        
        Returns:
            True if sidebar should be collapsible
        """
        return self.is_mobile()


class TouchFriendly:
    """
    Touch-friendly UI components for mobile.
    
    Provides larger touch targets and mobile-optimized interactions.
    """
    
    MIN_TOUCH_SIZE = 44  # Minimum recommended touch target size in pixels
    
    @staticmethod
    def button(
        label: str,
        key: Optional[str] = None,
        on_click: Optional[Callable] = None,
        **kwargs
    ) -> bool:
        """
        Create a touch-friendly button.
        
        Args:
            label: Button label
            key: Unique key for the button
            on_click: Click handler
            **kwargs: Additional st.button arguments
            
        Returns:
            True if clicked
        """
        import streamlit as st
        
        # Add padding for touch target
        touch_label = f"\n{label}\n"  # Add vertical padding
        
        return st.button(
            touch_label,
            key=key,
            on_click=on_click,
            use_container_width=True,
            **kwargs
        )
    
    @staticmethod
    def icon_button(
        icon: str,
        label: str,
        key: Optional[str] = None,
        on_click: Optional[Callable] = None,
        **kwargs
    ) -> bool:
        """
        Create a touch-friendly icon button.
        
        Args:
            icon: Emoji or icon
            label: Button label
            key: Unique key
            on_click: Click handler
            **kwargs: Additional arguments
            
        Returns:
            True if clicked
        """
        import streamlit as st
        
        button_label = f"{icon} {label}"
        return TouchFriendly.button(button_label, key, on_click, **kwargs)
    
    @staticmethod
    def action_row(
        actions: List[Dict[str, Any]],
        key_prefix: str = "action"
    ) -> Optional[str]:
        """
        Create a row of touch-friendly action buttons.
        
        Args:
            actions: List of action dicts with 'icon', 'label', 'key'
            key_prefix: Prefix for button keys
            
        Returns:
            Key of clicked action, or None
        """
        import streamlit as st
        
        layout = ResponsiveLayout()
        num_cols = min(len(actions), layout.get_columns())
        
        cols = st.columns(num_cols)
        clicked = None
        
        for i, (col, action) in enumerate(zip(cols, actions)):
            with col:
                if st.button(
                    f"{action.get('icon', '🔘')} {action.get('label', '')}",
                    key=f"{key_prefix}_{action.get('key', i)}",
                    use_container_width=True
                ):
                    clicked = action.get('key')
        
        return clicked


class MobileNavigation:
    """
    Mobile-optimized navigation components.
    """
    
    @staticmethod
    def hamburger_menu(
        items: List[Dict[str, Any]],
        title: str = "Menu",
        key: str = "mobile_nav"
    ) -> Optional[str]:
        """
        Create a hamburger menu for mobile navigation.
        
        Args:
            items: List of menu items with 'label', 'icon', 'key'
            title: Menu title
            key: Unique key
            
        Returns:
            Key of selected item, or None
        """
        import streamlit as st
        
        layout = ResponsiveLayout()
        
        if not layout.is_mobile():
            return None
        
        # Use expander for mobile nav
        with st.expander(f"☰ {title}", expanded=False):
            for item in items:
                if st.button(
                    f"{item.get('icon', '📄')} {item.get('label', '')}",
                    key=f"{key}_{item.get('key')}",
                    use_container_width=True
                ):
                    return item.get('key')
        
        return None
    
    @staticmethod
    def tab_bar(
        tabs: List[Dict[str, Any]],
        key: str = "tab_bar"
    ) -> Optional[str]:
        """
        Create a mobile-friendly tab bar.
        
        Args:
            tabs: List of tab dicts with 'label', 'icon', 'key'
            key: Unique key
            
        Returns:
            Selected tab key
        """
        import streamlit as st
        
        layout = ResponsiveLayout()
        
        # For mobile, show in a row with icons
        if layout.is_mobile():
            cols = st.columns(len(tabs))
            for col, tab in zip(cols, tabs):
                with col:
                    if st.button(
                        tab.get('icon', '📄'),
                        key=f"{key}_{tab.get('key')}",
                        use_container_width=True
                    ):
                        return tab.get('key')
        else:
            # Desktop: use tabs
            tab_names = [f"{t.get('icon', '')} {t.get('label', '')}" for t in tabs]
            selected = st.select_slider(
                "View",
                options=tab_names,
                key=key
            )
            for tab, name in zip(tabs, tab_names):
                if name == selected:
                    return tab.get('key')
        
        return None


class SwipeGesture:
    """
    Swipe gesture handling for mobile.
    
    Note: Streamlit doesn't natively support swipe gestures,
    but we can simulate them with navigation buttons.
    """
    
    @staticmethod
    def swipe_navigation(
        current_index: int,
        total_items: int,
        key_prefix: str = "swipe"
    ) -> Tuple[bool, bool, int]:
        """
        Create swipe-like navigation buttons.
        
        Args:
            current_index: Current item index (0-based)
            total_items: Total number of items
            key_prefix: Unique key prefix
            
        Returns:
            Tuple of (went_left, went_right, new_index)
        """
        import streamlit as st
        
        layout = ResponsiveLayout()
        
        if not layout.is_mobile():
            # Desktop: show prev/next buttons side by side
            col1, col2, col3 = st.columns([1, 3, 1])
        else:
            # Mobile: show swipe buttons
            col1, col2, col3 = st.columns([2, 1, 2])
        
        went_left = False
        went_right = False
        new_index = current_index
        
        with col1:
            if current_index > 0:
                if st.button("◀ Previous", key=f"{key_prefix}_prev"):
                    went_left = True
                    new_index = current_index - 1
        
        with col3:
            if current_index < total_items - 1:
                if st.button("Next ▶", key=f"{key_prefix}_next"):
                    went_right = True
                    new_index = current_index + 1
        
        return went_left, went_right, new_index


class ResponsiveChart:
    """
    Responsive chart sizing and optimization.
    """
    
    @staticmethod
    def get_chart_height(default_height: int = 400) -> int:
        """
        Get appropriate chart height for current screen.
        
        Args:
            default_height: Default height for desktop
            
        Returns:
            Adjusted height
        """
        layout = ResponsiveLayout()
        
        if layout.is_mobile():
            return int(default_height * 0.6)  # 60% for mobile
        elif layout.is_tablet():
            return int(default_height * 0.8)  # 80% for tablet
        return default_height
    
    @staticmethod
    def get_chart_width() -> Optional[int]:
        """
        Get appropriate chart width for current screen.
        
        Returns:
            Width in pixels, or None for auto
        """
        import streamlit as st
        layout = ResponsiveLayout()
        
        width = st.session_state.get('screen_width', 1200)
        
        if layout.is_mobile():
            return min(width - 40, 350)  # Account for padding
        elif layout.is_tablet():
            return min(width // 2 - 40, 500)
        
        return None  # Auto width for desktop
    
    @staticmethod
    def simplify_for_mobile(chart_config: Dict) -> Dict:
        """
        Simplify chart configuration for mobile.
        
        Args:
            chart_config: Plotly chart configuration
            
        Returns:
            Simplified configuration
        """
        import copy
        layout = ResponsiveLayout()
        
        if not layout.is_mobile():
            return chart_config
        
        config = copy.deepcopy(chart_config)
        
        # Reduce data points
        if 'data' in config:
            for trace in config['data']:
                if 'x' in trace and len(trace['x']) > 20:
                    # Sample every other point
                    step = 2
                    trace['x'] = trace['x'][::step]
                    if 'y' in trace:
                        trace['y'] = trace['y'][::step]
        
        # Simplify layout
        if 'layout' in config:
            # Hide legend on mobile
            config['layout']['showlegend'] = False
            
            # Smaller fonts
            if 'title' in config['layout']:
                config['layout']['title']['font'] = {'size': 12}
            
            # Reduce margins
            config['layout']['margin'] = {'l': 40, 'r': 20, 't': 40, 'b': 40}
        
        return config


class TextSizing:
    """
    Responsive text sizing utilities.
    """
    
    @staticmethod
    def get_heading_size(default: int = 24) -> int:
        """Get responsive heading size."""
        layout = ResponsiveLayout()
        if layout.is_mobile():
            return int(default * 0.7)
        elif layout.is_tablet():
            return int(default * 0.85)
        return default
    
    @staticmethod
    def get_body_size(default: int = 14) -> int:
        """Get responsive body text size."""
        layout = ResponsiveLayout()
        if layout.is_mobile():
            return max(12, int(default * 0.9))
        return default


# Export
__all__ = [
    "Breakpoint",
    "BREAKPOINTS",
    "ResponsiveLayout",
    "TouchFriendly",
    "MobileNavigation",
    "SwipeGesture",
    "ResponsiveChart",
    "TextSizing",
]