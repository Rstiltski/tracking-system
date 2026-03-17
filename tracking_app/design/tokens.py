"""
Design Tokens - Centralized Visual Properties

Phase 11: UI/UX Redesign - Foundation Layer

This module defines all visual design tokens used throughout the application.
Tokens follow a systematic naming convention and provide consistent values for:
- Colors (light/dark mode variants)
- Spacing (8px baseline grid)
- Typography (scale, weights, line-heights)
- Border Radius
- Shadows
- Transitions

Usage:
    from tracking_app.design.tokens import (
        COLORS, SPACING, TYPOGRAPHY, RADIUS, SHADOW, TRANSITION
    )
    
    # Access token values
    primary_color = COLORS.primary_light
    spacing_md = SPACING.md
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ColorPalette:
    """
    Complete color palette with light/dark variants.
    
    All colors are defined as hex strings. Semantic colors
    (success, warning, error, info) have distinct meanings:
    - success: Positive actions, completions, achievements
    - warning: Caution, deadlines approaching, moderate risk
    - error: Destructive actions, failures, critical issues
    - info: Informational messages, neutral highlights
    """
    
    # Primary Brand Colors
    primary_light: str = "#6366f1"      # Indigo 500
    primary_dark: str = "#818cf8"       # Indigo 400
    primary_hover_light: str = "#4f46e5"  # Indigo 600
    primary_hover_dark: str = "#a5b4fc"   # Indigo 300
    primary_active_light: str = "#4338ca" # Indigo 700
    primary_active_dark: str = "#c7d2fe"  # Indigo 200
    
    # Secondary Brand Colors
    secondary_light: str = "#8b5cf6"    # Violet 500
    secondary_dark: str = "#a78bfa"     # Violet 400
    secondary_hover_light: str = "#7c3aed"  # Violet 600
    secondary_hover_dark: str = "#c4b5fd"   # Violet 300
    
    # Accent Colors (Gamification)
    accent_gold: str = "#f59e0b"        # Amber 500 - XP, achievements
    accent_gold_light: str = "#fbbf24"  # Amber 400
    accent_cyan: str = "#06b6d4"        # Cyan 500 - Special highlights
    accent_cyan_light: str = "#22d3ee"  # Cyan 400
    accent_emerald: str = "#10b981"     # Emerald 500 - Success, completion
    accent_emerald_light: str = "#34d399" # Emerald 400
    accent_purple: str = "#a855f7"      # Purple 500 - Premium features
    accent_purple_light: str = "#c084fc"  # Purple 400
    accent_rose: str = "#f43f5e"        # Rose 500 - Streaks, passion
    
    # Semantic Colors - Light Mode
    success_light: str = "#059669"      # Emerald 600
    success_bg_light: str = "#d1fae5"   # Emerald 100
    success_border_light: str = "#6ee7b7" # Emerald 300
    
    warning_light: str = "#d97706"      # Amber 600
    warning_bg_light: str = "#fef3c7"   # Amber 100
    warning_border_light: str = "#fcd34d" # Amber 300
    
    error_light: str = "#dc2626"        # Red 600
    error_bg_light: str = "#fee2e2"     # Red 100
    error_border_light: str = "#fca5a5" # Red 300
    
    info_light: str = "#0284c7"         # Sky 600
    info_bg_light: str = "#e0f2fe"      # Sky 100
    info_border_light: str = "#7dd3fc"  # Sky 300
    
    # Semantic Colors - Dark Mode
    success_dark: str = "#34d399"       # Emerald 400
    success_bg_dark: str = "rgba(16, 185, 129, 0.1)"
    success_border_dark: str = "#059669"  # Emerald 600
    
    warning_dark: str = "#fbbf24"       # Amber 400
    warning_bg_dark: str = "rgba(245, 158, 11, 0.1)"
    warning_border_dark: str = "#d97706"  # Amber 600
    
    error_dark: str = "#f87171"         # Red 400
    error_bg_dark: str = "rgba(220, 38, 38, 0.1)"
    error_border_dark: str = "#dc2626"    # Red 600
    
    info_dark: str = "#38bdf8"          # Sky 400
    info_bg_dark: str = "rgba(2, 132, 199, 0.1)"
    info_border_dark: str = "#0284c7"     # Sky 600
    
    # Neutral Colors - Light Mode
    bg_primary_light: str = "#ffffff"
    bg_secondary_light: str = "#f9fafb"   # Gray 50
    bg_tertiary_light: str = "#f3f4f6"    # Gray 100
    bg_elevated_light: str = "#ffffff"
    
    text_primary_light: str = "#111827"   # Gray 900
    text_secondary_light: str = "#6b7280"  # Gray 500
    text_disabled_light: str = "#9ca3af"   # Gray 400
    text_inverse_light: str = "#ffffff"
    
    border_light: str = "#e5e7eb"         # Gray 200
    border_subtle_light: str = "#f3f4f6"  # Gray 100
    
    # Neutral Colors - Dark Mode
    bg_primary_dark: str = "#030712"      # Gray 950
    bg_secondary_dark: str = "#111827"    # Gray 900
    bg_tertiary_dark: str = "#1f2937"     # Gray 800
    bg_elevated_dark: str = "#1f2937"     # Gray 800
    
    text_primary_dark: str = "#f9fafb"    # Gray 50
    text_secondary_dark: str = "#9ca3af"   # Gray 400
    text_disabled_dark: str = "#6b7280"    # Gray 500
    text_inverse_dark: str = "#030712"
    
    border_dark: str = "rgba(255, 255, 255, 0.1)"
    border_subtle_dark: str = "rgba(255, 255, 255, 0.05)"
    
    # Overlay Colors
    overlay_light: str = "rgba(0, 0, 0, 0.5)"
    overlay_dark: str = "rgba(0, 0, 0, 0.7)"
    
    # Glassmorphism
    glass_light: str = "rgba(255, 255, 255, 0.7)"
    glass_dark: str = "rgba(31, 41, 55, 0.7)"
    
    # Gradient Definitions
    gradient_primary: str = "linear-gradient(135deg, #6366f1, #a855f7)"
    gradient_success: str = "linear-gradient(135deg, #10b981, #34d399)"
    gradient_gold: str = "linear-gradient(135deg, #f59e0b, #fbbf24)"
    gradient_accent: str = "linear-gradient(135deg, #06b6d4, #a855f7)"

    # XP Progress Gradient
    gradient_xp: str = "linear-gradient(90deg, #6366f1, #a855f7)"

    # Streak Fire Gradient
    gradient_streak: str = "linear-gradient(135deg, #f59e0b, #ef4444)"

    # ============================================================
    # SPECIAL THEMES - v2 Design Concepts
    # ============================================================

    # -------------------------------------------------------------
    # BENTO EARTH THEME - Warm earthy palette, elegant serif fonts
    # -------------------------------------------------------------
    bento_bg: str = "#f2ece4"           # Warm paper background
    bento_card: str = "#faf6f0"          # Card background
    bento_mocha: str = "#a47764"         # Primary accent
    bento_clay: str = "#c99383"          # Secondary accent
    bento_wood: str = "#b17a50"          # Primary action color
    bento_ink: str = "#2d1f14"           # Primary text
    bento_muted: str = "#9a8070"         # Secondary text
    bento_soft: str = "#e8ddd4"          # Subtle backgrounds
    bento_green: str = "#5a7a5c"         # Success color
    bento_amber: str = "#c8842a"         # Warning/highlight
    bento_border: str = "#dfd3c6"        # Border color

    # -------------------------------------------------------------
    # NEOBRUTALIST FORGE - Bold, high contrast, playful
    # -------------------------------------------------------------
    neo_bg: str = "#f5f0e8"              # Off-white background
    neo_card: str = "#ffffff"            # Pure white cards
    neo_black: str = "#000000"           # Stark black borders/text
    neo_red: str = "#ff5c5c"             # Primary accent red
    neo_green: str = "#4fffb0"           # Bright green accent
    neo_yellow: str = "#ffe033"          # Bold yellow
    neo_blue: str = "#5ca0ff"            # Soft blue
    neo_text: str = "#000000"            # Black text
    neo_muted: str = "#999999"           # Gray muted text
    neo_border: str = "#000000"          # Solid black borders

    # -------------------------------------------------------------
    # CALM TIDE - ADHD-friendly, soft, soothing colors
    # -------------------------------------------------------------
    calm_bg: str = "#f8fafb"             # Soft blue-gray background
    calm_card: str = "#ffffff"           # White cards
    calm_primary: str = "#1a8ab0"        # Calm blue primary
    calm_primary_hover: str = "#1a7fa0"  # Slightly darker hover
    calm_text: str = "#2d3a40"           # Dark blue-gray text
    calm_text_secondary: str = "#8fa5b0" # Muted blue-gray
    calm_border: str = "#e8eff3"         # Soft border
    calm_green_bg: str = "#dff5e3"       # Wellness area bg
    calm_green_accent: str = "#1e8a3e"   # Wellness accent
    calm_blue_bg: str = "#d8eaf4"        # Growth area bg
    calm_blue_accent: str = "#1a6fa0"    # Growth accent
    calm_orange_bg: str = "#fde8d8"      # Health area bg
    calm_orange_accent: str = "#e05a20"  # Health accent

    # -------------------------------------------------------------
    # RPG FORGE - Dark gamified theme with neon accents
    # -------------------------------------------------------------
    rpg_bg: str = "#0f0e17"              # Dark purple-black background
    rpg_card: str = "rgba(255,255,255,0.04)"  # Semi-transparent cards
    rpg_text: str = "#fffffe"            # Near-white text
    rpg_text_muted: str = "rgba(255,255,254,0.4)"  # Muted text
    rpg_primary: str = "#6c63ff"         # Purple primary
    rpg_primary_light: str = "#a78bfa"   # Light purple
    rpg_accent_red: str = "#ff5c5c"      # Red accent (health)
    rpg_accent_green: str = "#00c9a7"    # Teal accent (wellness)
    rpg_accent_orange: str = "#ff9f43"   # Orange accent (streaks)
    rpg_border: str = "rgba(255,255,255,0.07)"  # Subtle borders
    rpg_glow: str = "rgba(108,99,255,0.4)"  # Primary glow


@dataclass
class SpacingScale:
    """
    8px baseline grid spacing system.
    
    All spacing values are multiples of 8px (0.5rem) to maintain
    visual rhythm and consistency throughout the application.
    
    Usage in CSS: var(--spacing-md) or use Python constants directly
    """
    
    none: str = "0"
    xs: str = "4px"     # 0.25rem - Tight spacing
    sm: str = "8px"     # 0.5rem  - Small gaps
    md: str = "16px"    # 1rem    - Base spacing
    lg: str = "24px"    # 1.5rem  - Section gaps
    xl: str = "32px"    # 2rem    - Large gaps
    xxl: str = "48px"   # 3rem    - XL gaps
    xxxl: str = "64px"  # 4rem    - XXL gaps
    xxxxl: str = "80px" # 5rem    - XXXL gaps


@dataclass
class TypographyScale:
    """
    Typography hierarchy with proper sizing and line-heights.
    
    Uses a mobile-first approach with clamp() for fluid scaling.
    Font sizes automatically scale between mobile and desktop.
    """
    
    # Font Families
    font_primary: str = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    font_mono: str = "'JetBrains Mono', 'Fira Code', 'Consolas', monospace"
    
    # Font Sizes (mobile base, scales up with viewport)
    xs: str = "0.75rem"      # 12px - Captions, labels
    sm: str = "0.875rem"     # 14px - Small text, secondary
    base: str = "1rem"       # 16px - Body text
    lg: str = "1.125rem"     # 18px - Large body
    xl: str = "1.25rem"      # 20px - H5
    xxl: str = "1.5rem"      # 24px - H4
    xxxl: str = "1.875rem"   # 30px - H3
    xxxxl: str = "2.25rem"   # 36px - H2
    xxxxxl: str = "3rem"     # 48px - H1
    
    # Font Weights
    font_thin: str = "100"
    font_extralight: str = "200"
    font_light: str = "300"
    font_normal: str = "400"
    font_medium: str = "500"
    font_semibold: str = "600"
    font_bold: str = "700"
    font_extrabold: str = "800"
    font_black: str = "900"
    
    # Line Heights (unitless multiplier)
    line_none: str = "1"
    line_tight: str = "1.25"
    line_snug: str = "1.375"
    line_normal: str = "1.5"
    line_relaxed: str = "1.625"
    line_loose: str = "2"
    
    # Letter Spacing
    tracking_tighter: str = "-0.05em"
    tracking_tight: str = "-0.025em"
    tracking_normal: str = "0"
    tracking_wide: str = "0.025em"
    tracking_wider: str = "0.05em"
    tracking_widest: str = "0.1em"
    
    # Heading Styles (mobile → desktop)
    h1: Dict = None  # Initialized below
    h2: Dict = None
    h3: Dict = None
    h4: Dict = None
    h5: Dict = None
    h6: Dict = None
    
    def __post_init__(self):
        """Initialize heading configurations."""
        self.h1 = {
            "size_mobile": "1.875rem",
            "size_desktop": "3rem",
            "weight": "800",
            "line_height": "1.1",
            "tracking": "-0.025em",
            "margin_bottom": "1.5rem",
        }
        self.h2 = {
            "size_mobile": "1.5rem",
            "size_desktop": "2.25rem",
            "weight": "700",
            "line_height": "1.2",
            "tracking": "-0.025em",
            "margin_bottom": "1.25rem",
        }
        self.h3 = {
            "size_mobile": "1.25rem",
            "size_desktop": "1.875rem",
            "weight": "600",
            "line_height": "1.25",
            "tracking": "0",
            "margin_bottom": "1rem",
        }
        self.h4 = {
            "size_mobile": "1.125rem",
            "size_desktop": "1.5rem",
            "weight": "600",
            "line_height": "1.3",
            "tracking": "0",
            "margin_bottom": "0.75rem",
        }
        self.h5 = {
            "size_mobile": "1rem",
            "size_desktop": "1.25rem",
            "weight": "600",
            "line_height": "1.4",
            "tracking": "0",
            "margin_bottom": "0.5rem",
        }
        self.h6 = {
            "size_mobile": "0.875rem",
            "size_desktop": "1rem",
            "weight": "600",
            "line_height": "1.4",
            "tracking": "0.025em",
            "margin_bottom": "0.5rem",
        }


@dataclass
class BorderRadius:
    """
    Consistent border radius values.
    
    Use smaller radii for subtle rounding, larger for
    pill-shaped or fully rounded elements.
    """
    
    none: str = "0"
    xs: str = "2px"     # Minimal rounding
    sm: str = "4px"     # Small radius (buttons, inputs)
    md: str = "8px"     # Medium radius (cards)
    lg: str = "12px"    # Large radius (modals)
    xl: str = "16px"    # XL radius
    xxl: str = "24px"   # XXL radius
    xxxl: str = "32px"  # XXXL radius
    full: str = "9999px"  # Fully rounded (pills, avatars)


@dataclass
class Shadow:
    """
    Elevation shadows for depth and hierarchy.
    
    Shadows are layered to create realistic depth perception.
    Use glow shadows for interactive/gamified elements.
    """
    
    # Elevation Shadows - Light Mode
    sm_light: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    md_light: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    lg_light: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    xl_light: str = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
    xxl_light: str = "0 25px 50px -12px rgba(0, 0, 0, 0.25)"
    
    # Elevation Shadows - Dark Mode
    sm_dark: str = "0 1px 2px 0 rgba(0, 0, 0, 0.3)"
    md_dark: str = "0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3)"
    lg_dark: str = "0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3)"
    xl_dark: str = "0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4)"
    xxl_dark: str = "0 25px 50px -12px rgba(0, 0, 0, 0.6)"
    
    # Glow Effects (Gamification)
    glow_primary: str = "0 0 20px rgba(99, 102, 241, 0.4)"
    glow_primary_strong: str = "0 0 30px rgba(99, 102, 241, 0.6)"
    glow_success: str = "0 0 20px rgba(16, 185, 129, 0.4)"
    glow_success_strong: str = "0 0 30px rgba(16, 185, 129, 0.6)"
    glow_gold: str = "0 0 20px rgba(245, 158, 11, 0.4)"
    glow_gold_strong: str = "0 0 30px rgba(245, 158, 11, 0.6)"
    glow_cyan: str = "0 0 20px rgba(6, 182, 212, 0.4)"
    glow_cyan_strong: str = "0 0 30px rgba(6, 182, 212, 0.6)"
    glow_purple: str = "0 0 20px rgba(168, 85, 247, 0.4)"
    glow_purple_strong: str = "0 0 30px rgba(168, 85, 247, 0.6)"
    glow_error: str = "0 0 20px rgba(220, 38, 38, 0.4)"
    glow_error_strong: str = "0 0 30px rgba(220, 38, 38, 0.6)"
    
    # Inner Shadows
    inner_sm: str = "inset 0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    inner_md: str = "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)"
    inner_lg: str = "inset 0 4px 8px 0 rgba(0, 0, 0, 0.1)"


@dataclass
class Transition:
    """
    Animation and transition timings.
    
    Consistent timing creates a cohesive feel.
    Use cubic-bezier for natural motion.
    """
    
    # Duration
    instant: str = "0ms"
    fastest: str = "100ms"
    fast: str = "150ms"
    normal: str = "200ms"
    slow: str = "300ms"
    slower: str = "500ms"
    slowest: str = "1000ms"
    
    # Easing Functions
    ease_linear: str = "linear"
    ease_in: str = "cubic-bezier(0.4, 0, 1, 1)"
    ease_out: str = "cubic-bezier(0, 0, 0.2, 1)"
    ease_in_out: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    ease_bounce: str = "cubic-bezier(0.68, -0.55, 0.265, 1.55)"
    ease_spring: str = "cubic-bezier(0.175, 0.885, 0.32, 1.275)"
    
    # Preset Transitions
    transform_fast: str = "transform 150ms cubic-bezier(0.4, 0, 0.2, 1)"
    transform_normal: str = "transform 200ms cubic-bezier(0.4, 0, 0.2, 1)"
    transform_slow: str = "transform 300ms cubic-bezier(0.4, 0, 0.2, 1)"
    transform_bounce: str = "transform 500ms cubic-bezier(0.68, -0.55, 0.265, 1.55)"
    
    color_fast: str = "color 150ms ease, background-color 150ms ease"
    color_normal: str = "color 200ms ease, background-color 200ms ease"
    
    all_fast: str = "all 150ms ease"
    all_normal: str = "all 200ms ease"
    all_slow: str = "all 300ms ease"


@dataclass
class ZIndex:
    """
    Z-index scale for layering.
    
    Use these values to ensure consistent stacking order.
    """
    
    base: int = 0
    dropdown: int = 1000
    sticky: int = 1100
    fixed: int = 1200
    modal_backdrop: int = 1300
    modal: int = 1400
    popover: int = 1500
    tooltip: int = 1600
    toast: int = 1700


# Singleton instances for easy import
COLORS = ColorPalette()
SPACING = SpacingScale()
TYPOGRAPHY = TypographyScale()
RADIUS = BorderRadius()
SHADOW = Shadow()
TRANSITION = Transition()
Z_INDEX = ZIndex()


# Utility functions
def get_spacing_value(key: str) -> str:
    """Get spacing value by key."""
    return getattr(SPACING, key, SPACING.md)


def get_color_value(key: str, theme: str = "dark") -> str:
    """Get color value by key and theme."""
    attr = f"{key}_{theme}"
    return getattr(COLORS, attr, COLORS.text_primary_dark if theme == "dark" else COLORS.text_primary_light)


def clamp_font_size(mobile: str, desktop: str, min_vw: str = "320px", max_vw: str = "1920px") -> str:
    """
    Generate CSS clamp() for fluid typography.
    
    Args:
        mobile: Font size at minimum viewport
        desktop: Font size at maximum viewport
        min_vw: Minimum viewport width
        max_vw: Maximum viewport width
    
    Returns:
        CSS clamp() string
    """
    return f"clamp({mobile}, {mobile} + {desktop} * ((100vw - {min_vw}) / ({max_vw} - {min_vw})), {desktop})"


__all__ = [
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
]
