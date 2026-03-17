"""
Design System - UI/UX Redesign Module

Phase 11: Visual Excellence & Design System Overhaul

This module provides a complete design system for the Veryfyn Tracking System,
including design tokens, theme providers, components, and utilities.

Structure:
    design/
    ├── __init__.py          # This file - Module exports
    ├── tokens.py            # Design tokens (colors, spacing, typography)
    ├── theme.py             # Theme provider (light/dark modes)
    ├── components/          # Reusable UI components
    │   ├── buttons.py       # Button variants
    │   ├── cards.py         # Card layouts
    │   ├── inputs.py        # Form inputs
    │   └── navigation.py    # Navigation patterns
    └── utils/
        ├── responsive.py    # Responsive utilities
        └── accessibility.py # Accessibility helpers

Usage:
    from tracking_app.design import apply_design_system
    
    # In your Streamlit app
    apply_design_system(theme="dark")
"""

from .tokens import (
    # Data classes
    ColorPalette,
    SpacingScale,
    TypographyScale,
    BorderRadius,
    Shadow,
    Transition,
    ZIndex,
    # Singleton instances
    COLORS,
    SPACING,
    TYPOGRAPHY,
    RADIUS,
    SHADOW,
    TRANSITION,
    Z_INDEX,
    # Utility functions
    get_spacing_value,
    get_color_value,
    clamp_font_size,
)

from .theme import (
    apply_design_system,
    render_theme_toggle,
    get_current_theme,
    get_theme_colors,
    ThemeMode,
)

from .theme_selector import (
    render_theme_selector,
    get_theme_options,
    get_theme_metadata,
    THEME_INFO,
)

__version__ = "11.0.0"
__author__ = "Veryfyn Design Team"


def get_design_system_info() -> dict:
    """
    Get information about the design system.

    Returns:
        Dict with design system metadata
    """
    return {
        "version": __version__,
        "name": "Veryfyn Design System",
        "phase": "Phase 11 + v2 Special Themes",
        "tokens": {
            "colors": len([attr for attr in dir(COLORS) if not attr.startswith('_')]),
            "spacing_values": len([attr for attr in dir(SPACING) if not attr.startswith('_')]),
            "typography_values": len([attr for attr in dir(TYPOGRAPHY) if not attr.startswith('_')]),
            "radius_values": len([attr for attr in dir(RADIUS) if not attr.startswith('_')]),
            "shadow_values": len([attr for attr in dir(SHADOW) if not attr.startswith('_')]),
        },
        "themes": {
            "standard": ["Light", "Dark"],
            "special": ["Bento Earth", "Neobrutalist Forge", "Calm Tide", "RPG Forge"],
        },
        "features": [
            "Light and dark theme support",
            "4 special themed UIs (v2)",
            "8px baseline grid spacing",
            "Fluid typography scale",
            "Consistent border radius",
            "Elevation and glow shadows",
            "Smooth transitions",
            "WCAG 2.1 AA accessibility",
            "Mobile-first responsive design",
            "Bento grid layouts",
            "Neobrutalist design",
            "ADHD-friendly Calm Tide theme",
            "Gamified RPG Forge theme",
        ],
    }


__all__ = [
    # Version info
    "__version__",
    "__author__",
    "get_design_system_info",
    # Data classes
    "ColorPalette",
    "SpacingScale",
    "TypographyScale",
    "BorderRadius",
    "Shadow",
    "Transition",
    "ZIndex",
    # Singleton instances
    "COLORS",
    "SPACING",
    "TYPOGRAPHY",
    "RADIUS",
    "SHADOW",
    "TRANSITION",
    "Z_INDEX",
    # Utility functions
    "get_spacing_value",
    "get_color_value",
    "clamp_font_size",
    # Theme functions
    "apply_design_system",
    "render_theme_toggle",
    "get_current_theme",
    "get_theme_colors",
    "ThemeMode",
    # Theme selector
    "render_theme_selector",
    "get_theme_options",
    "get_theme_metadata",
    "THEME_INFO",
]
