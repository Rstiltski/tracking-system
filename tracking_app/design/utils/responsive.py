"""
Responsive Utilities - Mobile-First Breakpoints

Phase 12: UI/UX Redesign - Utility Layer

Provides responsive design utilities for creating layouts that work
seamlessly across desktop, tablet, and mobile devices.

Usage:
    from tracking_app.design.utils.responsive import (
        get_responsive_columns,
        render_responsive_container,
        is_mobile,
        get_breakpoint,
    )
"""

import streamlit as st
from typing import Tuple, Optional, Dict, Any
from enum import Enum


class Breakpoint(Enum):
    """Responsive breakpoints (mobile-first)."""
    
    MOBILE = "320px"       # Mobile phones (portrait)
    MOBILE_LG = "480px"    # Mobile phones (landscape)
    TABLET = "768px"       # Tablets (portrait)
    TABLET_LG = "1024px"   # Tablets (landscape) / Small laptops
    DESKTOP = "1280px"     # Desktops
    DESKTOP_LG = "1920px"  # Large desktops


# Breakpoint values in pixels
BREAKPOINT_VALUES: Dict[Breakpoint, int] = {
    Breakpoint.MOBILE: 320,
    Breakpoint.MOBILE_LG: 480,
    Breakpoint.TABLET: 768,
    Breakpoint.TABLET_LG: 1024,
    Breakpoint.DESKTOP: 1280,
    Breakpoint.DESKTOP_LG: 1920,
}


def get_responsive_columns(
    n_columns: int = 3,
    mobile_stack: bool = True,
    gap: str = "small",
) -> Tuple:
    """
    Get responsive column layout that adapts to screen size.
    
    On mobile, columns stack vertically. On larger screens, they display
    horizontally.
    
    Args:
        n_columns: Number of columns on desktop
        mobile_stack: Whether to stack on mobile
        gap: Gap between columns ("small", "medium", "large")
    
    Returns:
        Streamlit columns tuple
    
    Example:
        >>> cols = get_responsive_columns(3, mobile_stack=True)
        >>> with cols[0]:
        ...     st.write("Column 1")
        >>> with cols[1]:
        ...     st.write("Column 2")
        >>> with cols[2]:
        ...     st.write("Column 3")
    """
    
    # Streamlit handles responsiveness automatically with columns
    # This function provides a consistent API for future enhancements
    return st.columns(n_columns, gap=gap)


from typing import Optional
from contextlib import contextmanager


@contextmanager
def render_responsive_container(
    content: str = "",
    max_width: str = "1400px",
    padding: str = "var(--spacing-md)",
    key: Optional[str] = None,
):
    """
    Render content in a responsive container with max-width.
    
    Can be used as a context manager or standalone function.
    
    Args:
        content: Content to render (markdown/HTML)
        max_width: Maximum container width
        padding: Container padding
        key: Optional unique key
    
    Example (as context manager):
        >>> with render_responsive_container(max_width="1200px"):
        ...     st.write("Content inside container")
    
    Example (standalone):
        >>> render_responsive_container(
        ...     content="## Welcome",
        ...     max_width="1200px",
        ...     padding="var(--spacing-lg)"
        ... )
    """
    
    st.markdown(f"""
    <div {f'id="{key}"' if key else ''} style="
        max-width: {max_width};
        margin: 0 auto;
        padding: {padding};
    ">
    {content}
    </div>
    """, unsafe_allow_html=True)
    
    # Yield to allow use as context manager
    yield


def is_mobile() -> bool:
    """
    Check if the current viewport is likely mobile.
    
    Note: This is an approximation since Streamlit doesn't provide
    direct viewport information. Uses browser user-agent detection.
    
    Returns:
        True if likely mobile device
    
    Example:
        >>> if is_mobile():
        ...     st.write("Mobile view")
        ... else:
        ...     st.write("Desktop view")
    """
    
    # Try to detect mobile from user agent
    try:
        user_agent = st.context.headers.get("user_agent", "")
        mobile_indicators = ["Mobile", "Android", "iPhone", "iPad"]
        return any(indicator in str(user_agent) for indicator in mobile_indicators)
    except:
        return False


def get_breakpoint(breakpoint: Breakpoint) -> str:
    """
    Get breakpoint value as CSS string.
    
    Args:
        breakpoint: Breakpoint enum value
    
    Returns:
        Breakpoint value in pixels
    
    Example:
        >>> get_breakpoint(Breakpoint.TABLET)
        '768px'
    """
    return breakpoint.value


def get_breakpoint_value(breakpoint: Breakpoint) -> int:
    """
    Get breakpoint value in pixels (integer).
    
    Args:
        breakpoint: Breakpoint enum value
    
    Returns:
        Breakpoint value in pixels
    
    Example:
        >>> get_breakpoint_value(Breakpoint.TABLET)
        768
    """
    return BREAKPOINT_VALUES[breakpoint]


def render_responsive_grid(
    columns: int = 3,
    gap: str = "var(--spacing-md)",
    min_column_width: str = "280px",
):
    """
    Render a responsive grid using CSS Grid.
    
    Creates a grid that automatically adjusts columns based on available space.
    
    Args:
        columns: Target number of columns
        gap: Gap between grid items
        min_column_width: Minimum column width before wrapping
    
    Example:
        >>> with render_responsive_grid(columns=3):
        ...     for i in range(6):
        ...         st.write(f"Item {i}")
    """
    
    # Create grid CSS
    grid_css = f"""
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax({min_column_width}, 1fr));
    gap: {gap};
    """
    
    st.markdown(f"""
    <div style="{grid_css}">
    """, unsafe_allow_html=True)


def close_responsive_grid():
    """Close a responsive grid container."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_mobile_friendly_card(
    content: str,
    title: Optional[str] = None,
    icon: Optional[str] = None,
):
    """
    Render a card optimized for mobile viewing.
    
    Uses larger touch targets and simplified layout on mobile.
    
    Args:
        content: Card content
        title: Optional title
        icon: Optional icon
    
    Example:
        >>> render_mobile_friendly_card(
        ...     title="Today's Habits",
        ...     content="5 habits completed",
        ...     icon="✅"
        ... )
    """
    
    # Mobile-optimized styling
    st.markdown(f"""
    <div style="
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        padding: clamp(1rem, 3vw, 1.5rem);
        border: 1px solid var(--border);
        transition: var(--transition-normal);
        touch-action: manipulation;
    " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-md)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
        {f'<div style="font-size: clamp(1.5rem, 4vw, 2rem); margin-bottom: 0.5rem;">{icon}</div>' if icon else ''}
        {f'<h3 style="font-size: clamp(1rem, 3vw, 1.25rem); margin-bottom: 0.5rem; color: var(--text-primary);">{title}</h3>' if title else ''}
        <div style="font-size: clamp(0.875rem, 2.5vw, 1rem); color: var(--text-primary); line-height: 1.6;">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_adaptive_layout(
    mobile_content: str,
    desktop_content: Optional[str] = None,
    breakpoint: Breakpoint = Breakpoint.TABLET,
):
    """
    Render different content for mobile vs desktop.
    
    Args:
        mobile_content: Content for mobile view
        desktop_content: Content for desktop view (defaults to mobile_content)
        breakpoint: Breakpoint for switching
    
    Example:
        >>> render_adaptive_layout(
        ...     mobile_content="Mobile: Simplified view",
        ...     desktop_content="Desktop: Full feature set"
        ... )
    """
    
    desktop = desktop_content or mobile_content
    
    # Note: True responsive content requires JavaScript
    # This is a simplified version
    if is_mobile():
        st.markdown(mobile_content, unsafe_allow_html=True)
    else:
        st.markdown(desktop, unsafe_allow_html=True)


def get_layout_config() -> Dict[str, Any]:
    """
    Get current layout configuration.
    
    Returns:
        Dict with layout settings
    
    Example:
        >>> config = get_layout_config()
        >>> if config['is_mobile']:
        ...     render_mobile_view()
    """
    
    return {
        "is_mobile": is_mobile(),
        "breakpoints": {bp.name: bp.value for bp in Breakpoint},
        "recommended_columns": 1 if is_mobile() else 3,
        "recommended_card_size": "sm" if is_mobile() else "md",
    }


def render_spacer(size: str = "md", responsive: bool = True):
    """
    Render a responsive spacer.
    
    Args:
        size: Spacer size (sm, md, lg, xl)
        responsive: Whether to scale on mobile
    
    Example:
        >>> render_spacer(size="lg")
    """
    
    sizes = {
        "sm": "var(--spacing-sm)",
        "md": "var(--spacing-md)",
        "lg": "var(--spacing-lg)",
        "xl": "var(--spacing-xl)",
    }
    
    space = sizes.get(size, sizes["md"])
    
    if responsive:
        space = f"clamp({space}, 3vw, {space})"
    
    st.markdown(f"""
    <div style="height: {space};"></div>
    """, unsafe_allow_html=True)


def render_divider(responsive: bool = True):
    """
    Render a responsive horizontal divider.
    
    Args:
        responsive: Whether to adjust on mobile
    
    Example:
        >>> render_divider()
    """
    
    st.markdown(f"""
    <hr style="
        border: none;
        border-top: 1px solid var(--border);
        margin: {'clamp(1rem, 3vw, 2rem) 0' if responsive else '2rem 0'};
    ">
    """, unsafe_allow_html=True)


__all__ = [
    # Enums
    "Breakpoint",
    # Column utilities
    "get_responsive_columns",
    # Container utilities
    "render_responsive_container",
    "render_responsive_grid",
    "close_responsive_grid",
    # Detection
    "is_mobile",
    "get_breakpoint",
    "get_breakpoint_value",
    "get_layout_config",
    # Mobile-optimized components
    "render_mobile_friendly_card",
    "render_adaptive_layout",
    # Spacing
    "render_spacer",
    "render_divider",
]
