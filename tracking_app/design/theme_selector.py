"""
Theme Selector Component

Provides a reusable theme selector component that can be added to any page
or sidebar for switching between available themes.

Available Themes:
- Light: Clean, bright interface
- Dark: Dark mode with neon accents
- Bento Earth: Warm earthy palette with bento grid layout
- Neobrutalist Forge: Bold, high-contrast, playful
- Calm Tide: ADHD-friendly, soft, soothing colors
- RPG Forge: Dark gamified theme with XP and levels

Usage:
    from tracking_app.design.theme_selector import render_theme_selector
    
    # In sidebar
    with st.sidebar:
        render_theme_selector()
    
    # Or in main content
    render_theme_selector(location="main")
"""

import streamlit as st
from typing import Literal


# Theme metadata with descriptions and icons
THEME_INFO = {
    "light": {
        "name": "Light",
        "icon": "☀️",
        "description": "Clean, bright interface",
        "preview_colors": ["#ffffff", "#f9fafb", "#6366f1"],
    },
    "dark": {
        "name": "Dark",
        "icon": "🌙",
        "description": "Dark mode with neon accents",
        "preview_colors": ["#030712", "#111827", "#818cf8"],
    },
    "bento_earth": {
        "name": "Bento Earth",
        "icon": "🎨",
        "description": "Warm earthy palette, elegant serif fonts",
        "preview_colors": ["#f2ece4", "#a47764", "#b17a50"],
    },
    "neobrutalist_forge": {
        "name": "Neobrutalist Forge",
        "icon": "🔨",
        "description": "Bold outlines, raw contrast, playful",
        "preview_colors": ["#f5f0e8", "#000000", "#4fffb0"],
    },
    "calm_tide": {
        "name": "Calm Tide",
        "icon": "🌊",
        "description": "ADHD-friendly, soft, soothing",
        "preview_colors": ["#f8fafb", "#1a8ab0", "#8fa5b0"],
    },
    "rpg_forge": {
        "name": "RPG Forge",
        "icon": "⚔️",
        "description": "Gamified dark theme with XP system",
        "preview_colors": ["#0f0e17", "#6c63ff", "#ff5c5c"],
    },
}


def render_theme_selector(
    location: Literal["sidebar", "main", "expander"] = "sidebar",
    show_descriptions: bool = True,
    show_preview: bool = True,
):
    """
    Render a theme selector component.

    Args:
        location: Where to render - "sidebar", "main", or "expander"
        show_descriptions: Whether to show theme descriptions
        show_preview: Whether to show color preview swatches

    Example:
        >>> render_theme_selector(location="sidebar", show_descriptions=True)
    """
    # Get current theme
    current_theme = st.session_state.get("theme", "dark")
    
    # Create theme options list
    theme_options = [
        "Light",
        "Dark",
        "Bento Earth",
        "Neobrutalist Forge",
        "Calm Tide",
        "RPG Forge",
    ]
    
    # Find current theme index
    current_label = THEME_INFO.get(current_theme, THEME_INFO["dark"])["name"]
    try:
        default_index = theme_options.index(current_label)
    except ValueError:
        default_index = 1  # Default to Dark
    
    # Render based on location
    if location == "sidebar":
        _render_sidebar_selector(theme_options, default_index, show_descriptions, show_preview)
    elif location == "main":
        _render_main_selector(theme_options, default_index, show_descriptions, show_preview)
    elif location == "expander":
        _render_expander_selector(theme_options, default_index, show_descriptions, show_preview)


def _render_sidebar_selector(theme_options, default_index, show_descriptions, show_preview):
    """Render theme selector in sidebar."""
    st.subheader("🎨 Theme")
    
    selected = st.selectbox(
        "Choose theme",
        theme_options,
        index=default_index,
        key="theme_selector_sidebar",
        label_visibility="collapsed" if not show_descriptions else "visible",
    )
    
    _handle_theme_change(selected)
    
    if show_descriptions:
        _render_theme_info()
    
    if show_preview:
        _render_color_preview()


def _render_main_selector(theme_options, default_index, show_descriptions, show_preview):
    """Render theme selector in main content area."""
    cols = st.columns([2, 1])
    
    with cols[0]:
        st.markdown("### 🎨 Choose Your Theme")
        st.caption("Select a theme to customize your experience")
    
    with cols[1]:
        selected = st.selectbox(
            "Theme",
            theme_options,
            index=default_index,
            key="theme_selector_main",
        )
    
    _handle_theme_change(selected)
    
    if show_descriptions:
        st.divider()
        _render_theme_grid()
    
    if show_preview:
        _render_color_preview()


def _render_expander_selector(theme_options, default_index, show_descriptions, show_preview):
    """Render theme selector in an expander."""
    with st.expander("🎨 Theme Settings"):
        selected = st.selectbox(
            "Choose theme",
            theme_options,
            index=default_index,
            key="theme_selector_expander",
        )
        
        _handle_theme_change(selected)
        
        if show_descriptions:
            _render_theme_info()
        
        if show_preview:
            _render_color_preview()


def _handle_theme_change(selected_label: str):
    """Handle theme change and trigger rerun."""
    # Convert label to theme key
    theme_key = selected_label.lower().replace(" ", "_")
    
    if st.session_state.get("theme") != theme_key:
        st.session_state.theme = theme_key
        st.rerun()


def _render_theme_info():
    """Render current theme information."""
    current_theme = st.session_state.get("theme", "dark")
    info = THEME_INFO.get(current_theme, THEME_INFO["dark"])
    
    st.caption(f"{info['icon']} {info['description']}")


def _render_color_preview():
    """Render color palette preview for current theme."""
    current_theme = st.session_state.get("theme", "dark")
    info = THEME_INFO.get(current_theme, THEME_INFO["dark"])
    
    if "preview_colors" in info:
        cols = st.columns(3)
        for idx, color in enumerate(info["preview_colors"]):
            with cols[idx]:
                st.markdown(f"""
                <div style="
                    background: {color};
                    height: 40px;
                    border-radius: 8px;
                    border: 1px solid rgba(0,0,0,0.1);
                "></div>
                """, unsafe_allow_html=True)


def _render_theme_grid():
    """Render a grid of all available themes with descriptions."""
    st.markdown("### Available Themes")
    
    # Create 3x2 grid
    cols = st.columns(3)
    
    for idx, (theme_key, info) in enumerate(THEME_INFO.items()):
        col_idx = idx % 3
        with cols[col_idx]:
            st.markdown(f"""
            <div style="
                background: var(--bg-secondary, #f9fafb);
                border: 1px solid var(--border, #e5e7eb);
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 12px;
            ">
                <div style="font-size: 24px; margin-bottom: 8px;">{info['icon']}</div>
                <div style="font-weight: 600; margin-bottom: 4px;">{info['name']}</div>
                <div style="font-size: 12px; color: var(--text-secondary, #6b7280);">
                    {info['description']}
                </div>
            </div>
            """, unsafe_allow_html=True)


def get_theme_options() -> list:
    """
    Get list of available theme names.

    Returns:
        List of theme display names
    """
    return [info["name"] for info in THEME_INFO.values()]


def get_theme_metadata(theme_key: str) -> dict:
    """
    Get metadata for a specific theme.

    Args:
        theme_key: Theme key (e.g., "bento_earth", "rpg_forge")

    Returns:
        Dictionary with theme metadata
    """
    return THEME_INFO.get(theme_key, THEME_INFO["dark"])


__all__ = [
    "render_theme_selector",
    "get_theme_options",
    "get_theme_metadata",
    "THEME_INFO",
]
