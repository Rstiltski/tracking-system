"""
Design Utilities - Helper Functions

Phase 12: UI/UX Redesign - Utility Layer

This module provides utility functions for the design system.

Utilities:
    - responsive: Responsive design utilities
    - accessibility: Accessibility helpers (WCAG 2.1 AA)

Usage:
    from tracking_app.design.utils import (
        get_responsive_columns,
        is_mobile,
        check_contrast_ratio,
        render_focus_styles,
    )
"""

from .responsive import (
    Breakpoint,
    get_responsive_columns,
    render_responsive_container,
    render_responsive_grid,
    close_responsive_grid,
    is_mobile,
    get_breakpoint,
    get_breakpoint_value,
    get_layout_config,
    render_mobile_friendly_card,
    render_adaptive_layout,
    render_spacer,
    render_divider,
)

from .accessibility import (
    # Contrast checking
    check_contrast_ratio,
    is_accessible,
    get_accessible_text_color,
    # Color utilities
    hex_to_rgb,
    get_relative_luminance,
    check_all_design_colors,
    render_accessible_color_palette,
    # Accessibility features
    render_skip_link,
    render_focus_styles,
    render_screen_reader_text,
    render_accessibility_statement,
    render_landmark_roles,
    check_keyboard_navigation,
    # ARIA helpers
    add_aria_label,
    # Constants
    MIN_CONTRAST_NORMAL_TEXT,
    MIN_CONTRAST_LARGE_TEXT,
    MIN_CONTRAST_UI_COMPONENTS,
)

__all__ = [
    # Responsive
    "Breakpoint",
    "get_responsive_columns",
    "render_responsive_container",
    "render_responsive_grid",
    "close_responsive_grid",
    "is_mobile",
    "get_breakpoint",
    "get_breakpoint_value",
    "get_layout_config",
    "render_mobile_friendly_card",
    "render_adaptive_layout",
    "render_spacer",
    "render_divider",
    # Accessibility
    "check_contrast_ratio",
    "is_accessible",
    "get_accessible_text_color",
    "hex_to_rgb",
    "get_relative_luminance",
    "check_all_design_colors",
    "render_accessible_color_palette",
    "render_skip_link",
    "render_focus_styles",
    "render_screen_reader_text",
    "render_accessibility_statement",
    "render_landmark_roles",
    "check_keyboard_navigation",
    "add_aria_label",
    "MIN_CONTRAST_NORMAL_TEXT",
    "MIN_CONTRAST_LARGE_TEXT",
    "MIN_CONTRAST_UI_COMPONENTS",
]
