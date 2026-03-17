# 🎨 Phase 12: UI/UX Redesign - Comprehensive Design System

**Phase Name:** Visual Excellence & Design System Overhaul
**Status:** IN PROGRESS (Phase 12.1 Foundation - 20% Complete)
**Created:** March 11, 2026
**Priority:** HIGH (Foundation for all future features)

---

## 📋 Executive Summary

This phase transforms the Veryfyn Tracking System from a functional gamified app into a **professionally designed, cohesive experience** with a complete design system. The existing Gamevibe theme provides a foundation, but lacks systematic design tokens, consistent component patterns, and proper responsive behavior.

### Why This Phase Now?

| Current State | After Phase 12 |
|---------------|----------------|
| Basic neon dark theme | Professional design system with tokens |
| Inconsistent spacing | 8px baseline grid system |
| Limited component states | Full hover/focus/active/disabled states |
| Desktop-first mindset | Mobile-first responsive design |
| Ad-hoc color usage | Semantic color palette |
| No accessibility focus | WCAG 2.1 AA compliant |

---

## 🎯 Phase Objectives

### Primary Goals
1. **Create Design Token System** - Centralized variables for all visual properties
2. **Establish Typography Hierarchy** - Clear, readable type scale
3. **Build Component Library** - Reusable, consistent UI components
4. **Implement Responsive Grid** - Works on all screen sizes
5. **Add Light/Dark Themes** - User-selectable themes
6. **Ensure Accessibility** - WCAG 2.1 AA compliance

### Success Metrics
- [ ] All 45+ pages use the new design system
- [ ] All 28+ components follow consistent patterns
- [ ] Mobile usability score > 90 (Google Lighthouse)
- [ ] Color contrast ratios meet WCAG AA standards
- [ ] Page load time remains under 3 seconds
- [ ] User feedback indicates improved usability

---

## 🏗️ Architecture

### Design Token Structure

```
tracking_app/
├── design/
│   ├── __init__.py
│   ├── tokens.py           # Design tokens (colors, spacing, typography)
│   ├── theme.py            # Theme provider (light/dark)
│   ├── components/         # Redesigned components
│   │   ├── __init__.py
│   │   ├── buttons.py      # Button variants
│   │   ├── inputs.py       # Form inputs
│   │   ├── cards.py        # Card layouts
│   │   ├── navigation.py   # Navigation patterns
│   │   └── feedback.py     # Alerts, toasts, notifications
│   └── utils/
│       ├── __init__.py
│       ├── responsive.py   # Responsive utilities
│       └── accessibility.py # Accessibility helpers
```

---

## 📐 1. DESIGN TOKENS

### 1.1 Color Palette

#### Primary Colors (Brand)

| Token | Light Mode | Dark Mode | Usage |
|-------|------------|-----------|-------|
| `--primary` | `#6366f1` (Indigo) | `#818cf8` | Primary actions, links |
| `--primary-hover` | `#4f46e5` | `#a5b4fc` | Hover states |
| `--primary-active` | `#4338ca` | `#c7d2fe` | Active states |

#### Secondary Colors

| Token | Light Mode | Dark Mode | Usage |
|-------|------------|-----------|-------|
| `--secondary` | `#8b5cf6` (Violet) | `#a78bfa` | Secondary actions |
| `--secondary-hover` | `#7c3aed` | `#c4b5fd` | Hover states |

#### Accent Colors (Gamification)

| Token | Value | Usage |
|-------|-------|-------|
| `--accent-gold` | `#f59e0b` | XP, achievements, streaks |
| `--accent-cyan` | `#06b6d4` | Special highlights |
| `--accent-purple` | `#a855f7` | Premium features |
| `--accent-emerald` | `#10b981` | Success, completion |

#### Semantic Colors

| Token | Light Mode | Dark Mode | Usage |
|-------|------------|-----------|-------|
| `--success` | `#059669` | `#34d399` | Success states |
| `--warning` | `#d97706` | `#fbbf24` | Warnings |
| `--error` | `#dc2626` | `#f87171` | Errors, destructive |
| `--info` | `#0284c7` | `#38bdf8` | Informational |

#### Neutral Colors

| Token | Light Mode | Dark Mode | Usage |
|-------|------------|-----------|-------|
| `--bg-primary` | `#ffffff` | `#030712` | Main background |
| `--bg-secondary` | `#f9fafb` | `#111827` | Cards, sections |
| `--bg-tertiary` | `#f3f4f6` | `#1f2937` | Inputs, borders |
| `--text-primary` | `#111827` | `#f9fafb` | Primary text |
| `--text-secondary` | `#6b7280` | `#9ca3af` | Secondary text |
| `--text-disabled` | `#9ca3af` | `#6b7280` | Disabled text |

#### Implementation

```python
# tracking_app/design/tokens.py
"""Design Tokens - Centralized Visual Properties"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class ColorPalette:
    """Complete color palette with light/dark variants."""
    
    # Primary
    primary_light: str = "#6366f1"
    primary_dark: str = "#818cf8"
    primary_hover_light: str = "#4f46e5"
    primary_hover_dark: str = "#a5b4fc"
    
    # Secondary
    secondary_light: str = "#8b5cf6"
    secondary_dark: str = "#a78bfa"
    
    # Accent (Gamification)
    accent_gold: str = "#f59e0b"
    accent_cyan: str = "#06b6d4"
    accent_emerald: str = "#10b981"
    accent_purple: str = "#a855f7"
    
    # Semantic
    success_light: str = "#059669"
    success_dark: str = "#34d399"
    warning_light: str = "#d97706"
    warning_dark: str = "#fbbf24"
    error_light: str = "#dc2626"
    error_dark: str = "#f87171"
    info_light: str = "#0284c7"
    info_dark: str = "#38bdf8"
    
    # Neutral - Light Mode
    bg_primary_light: str = "#ffffff"
    bg_secondary_light: str = "#f9fafb"
    bg_tertiary_light: str = "#f3f4f6"
    text_primary_light: str = "#111827"
    text_secondary_light: str = "#6b7280"
    
    # Neutral - Dark Mode
    bg_primary_dark: str = "#030712"
    bg_secondary_dark: str = "#111827"
    bg_tertiary_dark: str = "#1f2937"
    text_primary_dark: str = "#f9fafb"
    text_secondary_dark: str = "#9ca3af"


@dataclass
class SpacingScale:
    """8px baseline grid spacing system."""
    
    none: str = "0"
    xs: str = "4px"    # 0.25rem
    sm: str = "8px"    # 0.5rem
    md: str = "16px"   # 1rem
    lg: str = "24px"   # 1.5rem
    xl: str = "32px"   # 2rem
    xxl: str = "48px"  # 3rem
    xxxl: str = "64px" # 4rem


@dataclass
class TypographyScale:
    """Typography hierarchy with proper sizing and line-heights."""
    
    # Font Families
    font_primary: str = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    font_mono: str = "'JetBrains Mono', 'Fira Code', monospace"
    
    # Font Sizes (mobile-first, scales up)
    xs: str = "0.75rem"     # 12px
    sm: str = "0.875rem"    # 14px
    base: str = "1rem"      # 16px
    lg: str = "1.125rem"    # 18px
    xl: str = "1.25rem"     # 20px
    xxl: str = "1.5rem"     # 24px
    xxxl: str = "1.875rem"  # 30px
    xxxxl: str = "2.25rem"  # 36px
    
    # Font Weights
    font_normal: str = "400"
    font_medium: str = "500"
    font_semibold: str = "600"
    font_bold: str = "700"
    font_extrabold: str = "800"
    
    # Line Heights
    line_tight: str = "1.25"
    line_normal: str = "1.5"
    line_relaxed: str = "1.75"
    
    # Letter Spacing
    tracking_tight: str = "-0.025em"
    tracking_normal: str = "0"
    tracking_wide: str = "0.025em"


@dataclass
class BorderRadius:
    """Consistent border radius values."""
    
    none: str = "0"
    sm: str = "4px"
    md: str = "8px"
    lg: str = "12px"
    xl: str = "16px"
    xxl: str = "24px"
    full: str = "9999px"


@dataclass
class Shadow:
    """Elevation shadows for depth."""
    
    sm: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    md: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    lg: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    xl: str = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
    glow_primary: str = "0 0 20px rgba(99, 102, 241, 0.4)"
    glow_success: str = "0 0 20px rgba(16, 185, 129, 0.4)"
    glow_gold: str = "0 0 20px rgba(245, 158, 11, 0.4)"


@dataclass
class Transition:
    """Animation and transition timings."""
    
    fast: str = "150ms ease"
    normal: str = "300ms ease"
    slow: str = "500ms ease"
    bounce: str = "500ms cubic-bezier(0.68, -0.55, 0.265, 1.55)"


# Singleton instances
COLORS = ColorPalette()
SPACING = SpacingScale()
TYPOGRAPHY = TypographyScale()
RADIUS = BorderRadius()
SHADOW = Shadow()
TRANSITION = Transition()
```

---

## 📐 2. TYPOGRAPHY SYSTEM

### Type Scale

| Element | Mobile | Tablet | Desktop | Weight | Line Height |
|---------|--------|--------|---------|--------|-------------|
| H1 | 1.875rem | 2.25rem | 3rem | 800 | 1.1 |
| H2 | 1.5rem | 1.875rem | 2.25rem | 700 | 1.2 |
| H3 | 1.25rem | 1.5rem | 1.875rem | 600 | 1.25 |
| H4 | 1.125rem | 1.25rem | 1.5rem | 600 | 1.3 |
| H5 | 1rem | 1.125rem | 1.25rem | 600 | 1.4 |
| H6 | 0.875rem | 1rem | 1.125rem | 600 | 1.4 |
| Body | 1rem | 1rem | 1rem | 400 | 1.6 |
| Small | 0.875rem | 0.875rem | 0.875rem | 400 | 1.5 |
| Caption | 0.75rem | 0.75rem | 0.75rem | 400 | 1.4 |

### Implementation

```python
# tracking_app/design/utils/typography.py
"""Typography utilities for consistent text styling."""

import streamlit as st

def render_heading(level: int, text: str, **kwargs):
    """Render a heading with proper typography."""
    styles = {
        1: "font-size: clamp(1.875rem, 5vw, 3rem); font-weight: 800; line-height: 1.1; letter-spacing: -0.025em;",
        2: "font-size: clamp(1.5rem, 4vw, 2.25rem); font-weight: 700; line-height: 1.2; letter-spacing: -0.025em;",
        3: "font-size: clamp(1.25rem, 3vw, 1.875rem); font-weight: 600; line-height: 1.25;",
        4: "font-size: clamp(1.125rem, 2.5vw, 1.5rem); font-weight: 600; line-height: 1.3;",
        5: "font-size: clamp(1rem, 2vw, 1.25rem); font-weight: 600; line-height: 1.4;",
        6: "font-size: clamp(0.875rem, 1.5vw, 1.125rem); font-weight: 600; line-height: 1.4;",
    }
    
    style = styles.get(level, styles[3])
    st.markdown(f"<h{level} style='{style}'>{text}</h{level}>", unsafe_allow_html=True)


def render_body_text(text: str, variant: str = "default", **kwargs):
    """Render body text with proper typography."""
    variants = {
        "default": "font-size: 1rem; line-height: 1.6; color: var(--text-primary);",
        "secondary": "font-size: 0.875rem; line-height: 1.5; color: var(--text-secondary);",
        "caption": "font-size: 0.75rem; line-height: 1.4; color: var(--text-disabled);",
        "lead": "font-size: 1.125rem; line-height: 1.7; color: var(--text-primary);",
    }
    
    style = variants.get(variant, variants["default"])
    st.markdown(f"<p style='{style}'>{text}</p>", unsafe_allow_html=True)
```

---

## 🎨 3. THEME SYSTEM

### Light & Dark Mode Support

```python
# tracking_app/design/theme.py
"""Theme Provider - Light/Dark Mode Support"""

import streamlit as st
from .tokens import COLORS, SPACING, TYPOGRAPHY, RADIUS, SHADOW, TRANSITION


def apply_design_system(theme: str = "dark"):
    """
    Apply the complete design system to the Streamlit app.
    
    Args:
        theme: "light" or "dark"
    """
    c = COLORS
    t = TYPOGRAPHY
    r = RADIUS
    s = SHADOW
    
    # Select color palette based on theme
    if theme == "light":
        bg_primary = c.bg_primary_light
        bg_secondary = c.bg_secondary_light
        bg_tertiary = c.bg_tertiary_light
        text_primary = c.text_primary_light
        text_secondary = c.text_secondary_light
        primary = c.primary_light
        primary_hover = c.primary_hover_light
    else:
        bg_primary = c.bg_primary_dark
        bg_secondary = c.bg_secondary_dark
        bg_tertiary = c.bg_tertiary_dark
        text_primary = c.text_primary_dark
        text_secondary = c.text_secondary_dark
        primary = c.primary_dark
        primary_hover = c.primary_hover_dark
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {{
        /* Colors */
        --bg-primary: {bg_primary};
        --bg-secondary: {bg_secondary};
        --bg-tertiary: {bg_tertiary};
        --text-primary: {text_primary};
        --text-secondary: {text_secondary};
        --primary: {primary};
        --primary-hover: {primary_hover};
        --success: {c.success_dark if theme == 'dark' else c.success_light};
        --warning: {c.warning_dark if theme == 'dark' else c.warning_light};
        --error: {c.error_dark if theme == 'dark' else c.error_light};
        --info: {c.info_dark if theme == 'dark' else c.info_light};
        --accent-gold: {c.accent_gold};
        --accent-cyan: {c.accent_cyan};
        --accent-emerald: {c.accent_emerald};
        --accent-purple: {c.accent_purple};
        
        /* Typography */
        --font-primary: {t.font_primary};
        --font-mono: {t.font_mono};
        
        /* Spacing */
        --spacing-xs: {s.xs};
        --spacing-sm: {s.sm};
        --spacing-md: {s.md};
        --spacing-lg: {s.lg};
        --spacing-xl: {s.xl};
        
        /* Border Radius */
        --radius-sm: {r.sm};
        --radius-md: {r.md};
        --radius-lg: {r.lg};
        --radius-xl: {r.xl};
        
        /* Shadows */
        --shadow-sm: {s.sm};
        --shadow-md: {s.md};
        --shadow-lg: {s.lg};
        
        /* Transitions */
        --transition-fast: {TRANSITION.fast};
        --transition-normal: {TRANSITION.normal};
    }}
    
    /* Global Styles */
    .stApp {{
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: var(--font-primary);
    }}
    
    /* Headings */
    h1 {{ color: var(--text-primary) !important; font-weight: 800 !important; }}
    h2 {{ color: var(--text-primary) !important; font-weight: 700 !important; }}
    h3 {{ color: var(--text-primary) !important; font-weight: 600 !important; }}
    
    /* Buttons */
    .stButton > button {{
        background-color: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: var(--transition-normal) !important;
        box-shadow: var(--shadow-sm) !important;
    }}
    .stButton > button:hover {{
        background-color: var(--primary-hover) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md) !important;
    }}
    
    /* Cards */
    [data-testid="stMetric"] {{
        background: var(--bg-secondary) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
        transition: var(--transition-normal) !important;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-4px) !important;
        box-shadow: var(--shadow-lg) !important;
    }}
    
    /* Inputs */
    .stTextInput > div > div > input {{
        background-color: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: var(--radius-md) !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{ visibility: hidden !important; }}
    footer {{ visibility: hidden !important; }}
    header {{ visibility: hidden !important; }}
    </style>
    """, unsafe_allow_html=True)


def get_theme_colors(theme: str = "dark") -> dict:
    """Get theme color dictionary for programmatic use."""
    c = COLORS
    if theme == "light":
        return {
            "bg": c.bg_primary_light,
            "bg_secondary": c.bg_secondary_light,
            "text": c.text_primary_light,
            "text_secondary": c.text_secondary_light,
            "primary": c.primary_light,
        }
    else:
        return {
            "bg": c.bg_primary_dark,
            "bg_secondary": c.bg_secondary_dark,
            "text": c.text_primary_dark,
            "text_secondary": c.text_secondary_dark,
            "primary": c.primary_dark,
        }
```

---

## 🧩 4. COMPONENT LIBRARY

### 4.1 Button System

```python
# tracking_app/design/components/buttons.py
"""Button Components - Consistent Button Styles"""

import streamlit as st
from typing import Literal, Optional


ButtonVariant = Literal["primary", "secondary", "success", "warning", "danger", "ghost"]
ButtonSize = Literal["sm", "md", "lg"]


def render_button(
    label: str,
    key: str,
    variant: ButtonVariant = "primary",
    size: ButtonSize = "md",
    icon: Optional[str] = None,
    disabled: bool = False,
    on_click: Optional[callable] = None,
    **kwargs
):
    """
    Render a styled button.
    
    Args:
        label: Button text
        key: Unique key for the button
        variant: Button style variant
        size: Button size
        icon: Optional emoji icon
        disabled: Whether button is disabled
        on_click: Optional click handler
    """
    
    variant_styles = {
        "primary": {
            "bg": "var(--primary)",
            "color": "white",
            "hover_bg": "var(--primary-hover)",
        },
        "secondary": {
            "bg": "var(--bg-tertiary)",
            "color": "var(--text-primary)",
            "hover_bg": "var(--bg-secondary)",
        },
        "success": {
            "bg": "var(--success)",
            "color": "white",
            "hover_bg": "#047857",
        },
        "warning": {
            "bg": "var(--warning)",
            "color": "white",
            "hover_bg": "#b45309",
        },
        "danger": {
            "bg": "var(--error)",
            "color": "white",
            "hover_bg": "#b91c1c",
        },
        "ghost": {
            "bg": "transparent",
            "color": "var(--text-secondary)",
            "hover_bg": "var(--bg-tertiary)",
        },
    }
    
    size_styles = {
        "sm": "padding: 0.375rem 0.75rem; font-size: 0.875rem;",
        "md": "padding: 0.5rem 1rem; font-size: 1rem;",
        "lg": "padding: 0.75rem 1.5rem; font-size: 1.125rem;",
    }
    
    style = variant_styles[variant]
    size_style = size_styles[size]
    
    button_content = f"{icon} {label}" if icon else label
    
    col = st.columns(kwargs.get("columns", 1))[0]
    
    with col:
        if st.button(
            button_content,
            key=key,
            disabled=disabled,
            on_click=on_click,
            **kwargs.get("button_kwargs", {})
        ):
            return True
    
    return False


def render_button_group(
    buttons: list,
    key_prefix: str = "btn_group"
):
    """
    Render a group of buttons in a row.
    
    Args:
        buttons: List of button configs (label, variant, on_click)
        key_prefix: Prefix for button keys
    """
    cols = st.columns(len(buttons))
    
    for i, btn in enumerate(buttons):
        with cols[i]:
            render_button(
                label=btn.get("label", f"Button {i}"),
                key=f"{key_prefix}_{i}",
                variant=btn.get("variant", "primary"),
                on_click=btn.get("on_click"),
                icon=btn.get("icon"),
            )
```

### 4.2 Card System

```python
# tracking_app/design/components/cards.py
"""Card Components - Consistent Card Layouts"""

import streamlit as st
from typing import Optional, List


def render_card(
    content: str,
    title: Optional[str] = None,
    icon: Optional[str] = None,
    variant: str = "default",
    interactive: bool = False,
    on_click: Optional[callable] = None,
):
    """
    Render a content card.
    
    Args:
        content: Card content (markdown allowed)
        title: Optional card title
        icon: Optional emoji icon
        variant: Card style variant
        interactive: Whether card is clickable
        on_click: Click handler for interactive cards
    """
    
    variants = {
        "default": "border: 1px solid rgba(255,255,255,0.1);",
        "elevated": "box-shadow: var(--shadow-lg); border: none;",
        "highlighted": "border: 2px solid var(--primary); box-shadow: var(--glow-primary);",
        "success": "border: 1px solid var(--success); background: rgba(16, 185, 129, 0.05);",
        "warning": "border: 1px solid var(--warning); background: rgba(245, 158, 11, 0.05);",
        "error": "border: 1px solid var(--error); background: rgba(220, 38, 38, 0.05);",
    }
    
    border_style = variants.get(variant, variants["default"])
    interactive_style = "cursor: pointer; transition: var(--transition-normal);" if interactive else ""
    
    header_html = ""
    if title or icon:
        header_html = f"""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
            {f'<span style="font-size: 1.5rem;">{icon}</span>' if icon else ''}
            {f'<h3 style="margin: 0; font-size: 1.125rem; font-weight: 600;">{title}</h3>' if title else ''}
        </div>
        """
    
    st.markdown(f"""
    <div style="
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        {border_style}
        {interactive_style}
    " {f"onclick='{on_click}'" if interactive and on_click else ''}>
        {header_html}
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    icon: str = "📊",
    trend: Optional[str] = None,
):
    """
    Render a statistics/metric card.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional change indicator (+5%, -2%, etc.)
        icon: Emoji icon
        trend: "up", "down", or "neutral"
    """
    
    trend_colors = {
        "up": "var(--success)",
        "down": "var(--error)",
        "neutral": "var(--text-secondary)",
    }
    
    trend_icons = {
        "up": "↑",
        "down": "↓",
        "neutral": "→",
    }
    
    trend_color = trend_colors.get(trend, trend_colors["neutral"])
    trend_icon = trend_icons.get(trend, trend_icons["neutral"])
    
    delta_html = ""
    if delta:
        delta_html = f"""
        <div style="display: flex; align-items: center; gap: 0.25rem; color: {trend_color}; font-size: 0.875rem; font-weight: 600; margin-top: 0.5rem;">
            <span>{trend_icon}</span>
            <span>{delta}</span>
        </div>
        """
    
    st.markdown(f"""
    <div style="
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        transition: var(--transition-normal);
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='var(--shadow-lg)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <span style="color: var(--text-secondary); font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;">{label}</span>
        </div>
        <div style="font-size: 2rem; font-weight: 800; color: var(--text-primary);">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)
```

### 4.3 Form Inputs

```python
# tracking_app/design/components/inputs.py
"""Form Input Components - Consistent Input Styles"""

import streamlit as st
from typing import Optional, List, Any


def render_text_input(
    label: str,
    key: str,
    placeholder: Optional[str] = None,
    help_text: Optional[str] = None,
    required: bool = False,
    **kwargs
) -> Optional[str]:
    """
    Render a styled text input.
    
    Args:
        label: Input label
        key: Unique key
        placeholder: Placeholder text
        help_text: Help text below input
        required: Whether field is required
    """
    
    required_marker = " <span style='color: var(--error);'>*</span>" if required else ""
    
    value = st.text_input(
        label=f"{label}{required_marker}",
        key=key,
        placeholder=placeholder,
        help=help_text,
        **kwargs
    )
    
    return value


def render_select_input(
    label: str,
    key: str,
    options: List[Any],
    placeholder: Optional[str] = None,
    help_text: Optional[str] = None,
    required: bool = False,
    **kwargs
) -> Optional[Any]:
    """
    Render a styled select dropdown.
    
    Args:
        label: Input label
        key: Unique key
        options: List of options
        placeholder: Placeholder text
        help_text: Help text
        required: Whether field is required
    """
    
    required_marker = " <span style='color: var(--error);'>*</span>" if required else ""
    
    value = st.selectbox(
        label=f"{label}{required_marker}",
        key=key,
        options=options,
        placeholder=placeholder,
        help=help_text,
        **kwargs
    )
    
    return value
```

---

## 📱 5. RESPONSIVE SYSTEM

### Breakpoint Definitions

```python
# tracking_app/design/utils/responsive.py
"""Responsive Utilities - Mobile-First Breakpoints"""

from enum import Enum


class Breakpoint(Enum):
    """Responsive breakpoints (mobile-first)."""
    
    MOBILE = "320px"      # Mobile phones
    MOBILE_LG = "480px"   # Large phones
    TABLET = "768px"      # Tablets
    TABLET_LG = "1024px"  # Large tablets
    DESKTOP = "1280px"    # Desktops
    DESKTOP_LG = "1920px" # Large desktops


def get_responsive_columns(n_columns: int = 3, mobile_stack: bool = True):
    """
    Get responsive column layout.
    
    Args:
        n_columns: Number of columns on desktop
        mobile_stack: Whether to stack on mobile
    
    Returns:
        Streamlit columns configured for responsiveness
    """
    if mobile_stack:
        # On mobile, everything stacks vertically
        # On desktop, use specified columns
        return st.columns(n_columns)
    else:
        return st.columns(n_columns)


def render_responsive_container(content: str, max_width: str = "1200px"):
    """
    Render content in a responsive container.
    
    Args:
        content: Content to render
        max_width: Maximum container width
    """
    st.markdown(f"""
    <div style="
        max-width: {max_width};
        margin: 0 auto;
        padding: var(--spacing-md);
    ">
        {content}
    </div>
    """, unsafe_allow_html=True)
```

---

## ♿ 6. ACCESSIBILITY GUIDELINES

### WCAG 2.1 AA Compliance

```python
# tracking_app/design/utils/accessibility.py
"""Accessibility Utilities - WCAG 2.1 AA Compliance"""

from typing import Tuple


# WCAG 2.1 AA contrast ratios
MIN_CONTRAST_NORMAL = 4.5  # Normal text
MIN_CONTRAST_LARGE = 3.0   # Large text (18px+ or 14px+ bold)


def check_contrast_ratio(fg_color: str, bg_color: str) -> float:
    """
    Calculate contrast ratio between two colors.
    
    Args:
        fg_color: Foreground color (hex)
        bg_color: Background color (hex)
    
    Returns:
        Contrast ratio (1.0 to 21.0)
    """
    # Implementation would use WCAG luminance formula
    # This is a placeholder
    return 4.5


def is_accessible(fg_color: str, bg_color: str, text_size: str = "normal") -> bool:
    """
    Check if color combination meets WCAG standards.
    
    Args:
        fg_color: Foreground color
        bg_color: Background color
        text_size: "normal" or "large"
    
    Returns:
        Whether the combination is accessible
    """
    ratio = check_contrast_ratio(fg_color, bg_color)
    threshold = MIN_CONTRAST_LARGE if text_size == "large" else MIN_CONTRAST_NORMAL
    return ratio >= threshold


def add_focus_indicator(element_id: str) -> str:
    """
    Generate CSS for focus indicator.
    
    Args:
        element_id: Element ID
    
    Returns:
        CSS string for focus indicator
    """
    return f"""
    #{element_id}:focus {{
        outline: 2px solid var(--primary);
        outline-offset: 2px;
        border-radius: var(--radius-sm);
    }}
    """
```

---

## 🗺️ 7. IMPLEMENTATION ROADMAP

### Phase 12.1: Foundation (Weeks 1-2)

| Task | Files | Priority |
|------|-------|----------|
| Create design tokens | `design/tokens.py` | P0 |
| Create theme provider | `design/theme.py` | P0 |
| Update app.py to use new theme | `app.py` | P0 |
| Create responsive utilities | `design/utils/responsive.py` | P1 |
| Create accessibility utilities | `design/utils/accessibility.py` | P1 |

### Phase 12.2: Core Components (Weeks 3-4)

| Task | Files | Priority |
|------|-------|----------|
| Button system | `design/components/buttons.py` | P0 |
| Card system | `design/components/cards.py` | P0 |
| Form inputs | `design/components/inputs.py` | P0 |
| Navigation patterns | `design/components/navigation.py` | P1 |
| Feedback components | `design/components/feedback.py` | P1 |

### Phase 12.3: Page Migration (Weeks 5-8)

| Week | Pages | Focus |
|------|-------|-------|
| 5 | Dashboard, Habits | High-traffic pages |
| 6 | Tasks, Goals, Time | Planning category |
| 7 | Health, Emotional Health, Energy | Wellness category |
| 8 | Finances, Achievements | Remaining major pages |

### Phase 12.4: Polish & Testing (Weeks 9-10)

| Task | Description |
|------|-------------|
| Mobile testing | Test all pages on mobile breakpoints |
| Accessibility audit | Run WCAG compliance checks |
| Performance optimization | Ensure fast load times |
| User feedback | Collect and incorporate feedback |

---

## 📊 8. VISUAL HIERARCHY EXAMPLES

### Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│  [H1] Dashboard                              [User Level]   │
│  [H2] Welcome back, [Name]                                  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Habit   │  │   Task   │  │  Streak  │  │    XP    │   │
│  │  Score   │  │ Complete │  │  Counter │  │  Total   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
├─────────────────────────────────────────────────────────────┤
│  [H3] Today's Focus                                         │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  │
│  │   Habits to Complete    │  │   Upcoming Deadlines    │  │
│  │   - [ ] Habit 1         │  │   - Task 1 (Tomorrow)   │  │
│  │   - [ ] Habit 2         │  │   - Task 2 (Wed)        │  │
│  └─────────────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 9. QUALITY CHECKLIST

### Before Marking Complete

- [ ] All design tokens defined and documented
- [ ] Light and dark themes working
- [ ] All buttons use consistent styling
- [ ] All cards follow same pattern
- [ ] Form inputs have proper labels and help text
- [ ] Mobile layout tested (320px - 768px)
- [ ] Tablet layout tested (768px - 1024px)
- [ ] Desktop layout tested (1024px+)
- [ ] Color contrast meets WCAG AA
- [ ] Focus indicators visible on all interactive elements
- [ ] Page load time under 3 seconds
- [ ] No console errors in browser dev tools

---

## 📚 10. DOCUMENTATION

### For Future Development

Create `tracking_app/design/README.md` with:
- Design token reference
- Component usage examples
- Responsive guidelines
- Accessibility checklist
- Theme customization guide

---

## 🔗 Cross-References

| Related File | Purpose |
|--------------|---------|
| `tracking_app/theme.py` | Existing Gamevibe theme (to be enhanced) |
| `PROJECT_RULES.md` | UI/UX rules (UI_001-005) |
| `brain/CORE_RULES.md` | Design system rules |
| `patterns/page_module.md` | Page pattern for migrations |

---

**Created:** March 11, 2026  
**Phase:** 11  
**Status:** Ready for Implementation  
**Next Step:** Begin Phase 11.1 - Foundation (create design tokens)
