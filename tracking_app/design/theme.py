"""
Theme Provider - Light/Dark Mode Support

Phase 11: UI/UX Redesign - Theme Layer

This module provides theme management for the design system, including:
- Light and dark mode themes
- CSS variable injection
- Theme persistence in session state
- Theme toggle component

Usage:
    from tracking_app.design.theme import apply_design_system, render_theme_toggle
    
    # Apply theme at app startup
    apply_design_system(theme="dark")
    
    # Add theme toggle in sidebar
    render_theme_toggle()
"""

import streamlit as st
from typing import Literal, Optional
from .tokens import (
    COLORS,
    SPACING,
    TYPOGRAPHY,
    RADIUS,
    SHADOW,
    TRANSITION,
)

ThemeMode = Literal["light", "dark", "system", "bento_earth", "neobrutalist_forge", "calm_tide", "rpg_forge"]


def apply_design_system(theme: ThemeMode = "dark", special_theme_config: dict = None):
    """
    Apply the complete design system to the Streamlit app.

    This injects CSS custom properties (variables) and global styles
    that define the visual appearance of the application.

    Args:
        theme: Theme mode - "light", "dark", "system", or special themes:
               "bento_earth", "neobrutalist_forge", "calm_tide", "rpg_forge"
        special_theme_config: Optional dict with custom config for special themes

    Example:
        >>> apply_design_system("dark")
        # Applies dark theme with neon accents
        >>> apply_design_system("bento_earth")
        # Applies warm earthy Bento Earth theme
    """
    # Resolve system theme
    if theme == "system":
        # Default to dark for system, can be enhanced with JS detection
        theme = "dark"

    c = COLORS
    t = TYPOGRAPHY
    r = RADIUS
    s = SHADOW
    p = SPACING

    # Check if this is a special theme
    is_special_theme = theme in ["bento_earth", "neobrutalist_forge", "calm_tide", "rpg_forge"]

    # Select color palette based on theme
    if theme == "bento_earth":
        bg_primary = c.bento_bg
        bg_secondary = c.bento_card
        bg_tertiary = c.bento_card
        bg_elevated = c.bento_card
        text_primary = c.bento_ink
        text_secondary = c.bento_muted
        text_disabled = c.bento_muted
        border = c.bento_border
        border_subtle = c.bento_soft
        primary = c.bento_wood
        primary_hover = c.bento_mocha
        success = c.bento_green
        warning = c.bento_amber
        error = c.bento_clay
        info = c.bento_muted
    elif theme == "neobrutalist_forge":
        bg_primary = c.neo_bg
        bg_secondary = c.neo_card
        bg_tertiary = c.neo_card
        bg_elevated = c.neo_card
        text_primary = c.neo_text
        text_secondary = c.neo_muted
        text_disabled = c.neo_muted
        border = c.neo_border
        border_subtle = c.neo_muted
        primary = c.neo_green
        primary_hover = c.neo_yellow
        success = c.neo_green
        warning = c.neo_yellow
        error = c.neo_red
        info = c.neo_blue
    elif theme == "calm_tide":
        bg_primary = c.calm_bg
        bg_secondary = c.calm_card
        bg_tertiary = c.calm_card
        bg_elevated = c.calm_card
        text_primary = c.calm_text
        text_secondary = c.calm_text_secondary
        text_disabled = c.calm_text_secondary
        border = c.calm_border
        border_subtle = c.calm_border
        primary = c.calm_primary
        primary_hover = c.calm_primary_hover
        success = c.calm_green_accent
        warning = c.calm_orange_accent
        error = c.calm_orange_accent
        info = c.calm_blue_accent
    elif theme == "rpg_forge":
        bg_primary = c.rpg_bg
        bg_secondary = c.rpg_card
        bg_tertiary = "rgba(255,255,255,0.03)"
        bg_elevated = "rgba(255,255,255,0.04)"
        text_primary = c.rpg_text
        text_secondary = c.rpg_text_muted
        text_disabled = c.rpg_text_muted
        border = c.rpg_border
        border_subtle = "rgba(255,255,255,0.05)"
        primary = c.rpg_primary
        primary_hover = c.rpg_primary_light
        success = c.rpg_accent_green
        warning = c.rpg_accent_orange
        error = c.rpg_accent_red
        info = c.rpg_primary
    elif theme == "light":
        bg_primary = c.bg_primary_light
        bg_secondary = c.bg_secondary_light
        bg_tertiary = c.bg_tertiary_light
        bg_elevated = c.bg_elevated_light
        text_primary = c.text_primary_light
        text_secondary = c.text_secondary_light
        text_disabled = c.text_disabled_light
        border = c.border_light
        border_subtle = c.border_subtle_light
        success = c.success_light
        warning = c.warning_light
        error = c.error_light
        info = c.info_light
        primary = c.primary_light
        primary_hover = c.primary_hover_light
    else:
        bg_primary = c.bg_primary_dark
        bg_secondary = c.bg_secondary_dark
        bg_tertiary = c.bg_tertiary_dark
        bg_elevated = c.bg_elevated_dark
        text_primary = c.text_primary_dark
        text_secondary = c.text_secondary_dark
        text_disabled = c.text_disabled_dark
        border = c.border_dark
        border_subtle = c.border_subtle_dark
        success = c.success_dark
        warning = c.warning_dark
        error = c.error_dark
        info = c.info_dark
        primary = c.primary_dark
        primary_hover = c.primary_hover_dark
    
    # Inject CSS with design tokens
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* ============================================================
       CSS Custom Properties (Design Tokens)
       ============================================================ */
    :root {{
        /* Colors */
        --bg-primary: {bg_primary};
        --bg-secondary: {bg_secondary};
        --bg-tertiary: {bg_tertiary};
        --bg-elevated: {bg_elevated};
        
        --text-primary: {text_primary};
        --text-secondary: {text_secondary};
        --text-disabled: {text_disabled};
        
        --border: {border};
        --border-subtle: {border_subtle};
        
        --primary: {primary};
        --primary-hover: {primary_hover};
        
        --success: {success};
        --warning: {warning};
        --error: {error};
        --info: {info};
        
        --accent-gold: {c.accent_gold};
        --accent-cyan: {c.accent_cyan};
        --accent-emerald: {c.accent_emerald};
        --accent-purple: {c.accent_purple};
        --accent-rose: {c.accent_rose};
        
        /* Typography */
        --font-primary: {t.font_primary};
        --font-mono: {t.font_mono};
        
        /* Spacing */
        --spacing-xs: {p.xs};
        --spacing-sm: {p.sm};
        --spacing-md: {p.md};
        --spacing-lg: {p.lg};
        --spacing-xl: {p.xl};
        --spacing-xxl: {p.xxl};
        
        /* Border Radius */
        --radius-xs: {r.xs};
        --radius-sm: {r.sm};
        --radius-md: {r.md};
        --radius-lg: {r.lg};
        --radius-xl: {r.xl};
        --radius-xxl: {r.xxl};
        --radius-full: {r.full};
        
        /* Shadows */
        --shadow-sm: {s.sm_dark if theme == 'dark' else s.sm_light};
        --shadow-md: {s.md_dark if theme == 'dark' else s.md_light};
        --shadow-lg: {s.lg_dark if theme == 'dark' else s.lg_light};
        --shadow-xl: {s.xl_dark if theme == 'dark' else s.xl_light};
        
        /* Glows */
        --glow-primary: {s.glow_primary};
        --glow-success: {s.glow_success};
        --glow-gold: {s.glow_gold};
        --glow-cyan: {s.glow_cyan};
        --glow-purple: {s.glow_purple};
        
        /* Transitions */
        --transition-fast: {TRANSITION.fast};
        --transition-normal: {TRANSITION.normal};
        --transition-slow: {TRANSITION.slow};
        --ease-bounce: {TRANSITION.ease_bounce};
        --ease-spring: {TRANSITION.ease_spring};
        
        /* Gradients */
        --gradient-primary: {c.gradient_primary};
        --gradient-success: {c.gradient_success};
        --gradient-gold: {c.gradient_gold};
        --gradient-xp: {c.gradient_xp};
        --gradient-streak: {c.gradient_streak};
    }}
    
    /* ============================================================
       Global Styles
       ============================================================ */
    
    /* App Container */
    .stApp {{
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: var(--font-primary);
        background-image: 
            radial-gradient(ellipse at top, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at bottom right, rgba(168, 85, 247, 0.06) 0%, transparent 50%);
        background-attachment: fixed;
    }}
    
    /* Main Content Area */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1400px;
    }}
    
    /* ============================================================
       Typography
       ============================================================ */
    
    h1 {{
        color: var(--text-primary) !important;
        font-weight: 800 !important;
        font-size: clamp(1.875rem, 5vw, 3rem) !important;
        line-height: 1.1 !important;
        letter-spacing: -0.025em !important;
        margin-bottom: 1.5rem !important;
        text-shadow: 0 0 40px rgba(99, 102, 241, 0.3);
    }}
    
    h2 {{
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: clamp(1.5rem, 4vw, 2.25rem) !important;
        line-height: 1.2 !important;
        letter-spacing: -0.025em !important;
        margin-bottom: 1.25rem !important;
    }}
    
    h3 {{
        color: var(--accent-emerald) !important;
        font-weight: 600 !important;
        font-size: clamp(1.25rem, 3vw, 1.875rem) !important;
        line-height: 1.25 !important;
        margin-bottom: 1rem !important;
    }}
    
    h4 {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: clamp(1.125rem, 2.5vw, 1.5rem) !important;
        line-height: 1.3 !important;
        margin-bottom: 0.75rem !important;
    }}
    
    p {{
        font-size: 1rem;
        line-height: 1.6;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }}
    
    a {{
        color: var(--primary);
        text-decoration: none;
        transition: var(--transition-fast);
    }}
    a:hover {{
        color: var(--primary-hover);
        text-decoration: underline;
    }}
    
    /* ============================================================
       Buttons
       ============================================================ */
    
    .stButton > button {{
        background-color: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        padding: 0.625rem 1.25rem !important;
        transition: var(--transition-normal) !important;
        box-shadow: var(--shadow-sm) !important;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }}
    
    .stButton > button:hover {{
        background-color: var(--primary-hover) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md), var(--glow-primary) !important;
    }}
    
    .stButton > button:active {{
        transform: translateY(0) !important;
    }}
    
    /* ============================================================
       Metric Cards
       ============================================================ */
    
    [data-testid="stMetric"] {{
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
        transition: var(--transition-normal) !important;
        backdrop-filter: blur(10px);
    }}
    
    [data-testid="stMetric"]:hover {{
        transform: translateY(-4px) !important;
        box-shadow: var(--shadow-lg) !important;
        border-color: var(--primary) !important;
    }}
    
    [data-testid="stMetricValue"] {{
        color: var(--accent-gold) !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 20px rgba(245, 158, 11, 0.4);
    }}
    
    [data-testid="stMetricLabel"] {{
        color: var(--text-secondary) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
    }}
    
    /* ============================================================
       Form Inputs
       ============================================================ */
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
        transition: var(--transition-fast) !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        outline: none !important;
    }}
    
    .stSelectbox > div > div > select {{
        background-color: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
    }}
    
    .stCheckbox > label > div:first-child {{
        width: 20px !important;
        height: 20px !important;
        border: 2px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        background: var(--bg-tertiary) !important;
        transition: var(--transition-fast) !important;
    }}
    
    .stCheckbox > label > div:first-child[data-checked="true"] {{
        background-color: var(--primary) !important;
        border-color: var(--primary) !important;
    }}
    
    /* ============================================================
       Cards & Containers
       ============================================================ */
    
    div[data-testid="stCard"] {{
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-xl) !important;
        backdrop-filter: blur(10px);
        transition: var(--transition-normal) !important;
    }}
    
    div[data-testid="stCard"]:hover {{
        border-color: var(--border-subtle) !important;
    }}
    
    /* ============================================================
       Progress Bars
       ============================================================ */
    
    div[data-testid="stProgress"] > div {{
        background-color: var(--bg-tertiary) !important;
        border-radius: var(--radius-full) !important;
    }}
    
    div[data-testid="stProgress"] > div > div > div {{
        background: linear-gradient(90deg, #10b981, #059669) !important;
        border-radius: var(--radius-full) !important;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
        transition: width var(--transition-slow) !important;
    }}
    
    /* ============================================================
       Tabs
       ============================================================ */
    
    button[data-baseweb="tab"] {{
        background: transparent !important;
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        border-radius: var(--radius-md) !important;
        transition: var(--transition-fast) !important;
    }}
    
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--accent-emerald) !important;
        background: rgba(16, 185, 129, 0.1) !important;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
    }}
    
    /* ============================================================
       Sidebar
       ============================================================ */
    
    section[data-testid="stSidebar"] {{
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }}
    
    section[data-testid="stSidebar"] .stMarkdown {{
        color: var(--text-secondary) !important;
    }}
    
    /* ============================================================
       Expanders (Accordion)
       ============================================================ */
    
    details > summary {{
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        font-weight: 600 !important;
        padding: var(--spacing-md) !important;
        transition: var(--transition-fast) !important;
    }}
    
    details > summary:hover {{
        border-color: var(--primary) !important;
    }}
    
    details[open] > summary {{
        border-bottom-left-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
    }}
    
    details > div {{
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-bottom-left-radius: var(--radius-md) !important;
        border-bottom-right-radius: var(--radius-md) !important;
        padding: var(--spacing-md) !important;
    }}
    
    /* ============================================================
       Alerts & Notifications
       ============================================================ */
    
    div.stSuccess {{
        background: var(--success-bg) !important;
        border: 1px solid var(--success) !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: var(--glow-success) !important;
    }}
    
    div.stWarning {{
        background: var(--warning-bg) !important;
        border: 1px solid var(--warning) !important;
        border-radius: var(--radius-lg) !important;
    }}
    
    div.stError {{
        background: var(--error-bg) !important;
        border: 1px solid var(--error) !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: 0 0 20px rgba(220, 38, 38, 0.3) !important;
    }}
    
    div.stInfo {{
        background: var(--info-bg) !important;
        border: 1px solid var(--info) !important;
        border-radius: var(--radius-lg) !important;
    }}
    
    /* ============================================================
       Scrollbars
       ============================================================ */
    
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--bg-primary);
        border-radius: var(--radius-full);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--bg-tertiary);
        border-radius: var(--radius-full);
        border: 2px solid var(--bg-primary);
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--primary);
    }}
    
    /* ============================================================
       Special Theme: Bento Earth
       ============================================================ */
    .theme-bento-earth {{
        font-family: 'Georgia', 'Palatino', serif !important;
    }}
    .theme-bento-earth .stApp {{
        background-image: none !important;
    }}
    .theme-bento-earth h1 {{
        text-shadow: none !important;
        font-family: 'Georgia', serif !important;
    }}
    .theme-bento-earth .bento-grid {{
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 14px;
    }}
    .theme-bento-earth .bento-cell {{
        transition: box-shadow 0.25s ease, transform 0.25s ease !important;
    }}
    .theme-bento-earth .bento-cell:hover {{
        box-shadow: 0 12px 40px rgba(45,31,20,0.14) !important;
        transform: translateY(-3px) !important;
    }}

    /* ============================================================
       Special Theme: Neobrutalist Forge
       ============================================================ */
    .theme-neobrutalist-forge {{
        font-family: 'Arial Black', 'Impact', sans-serif !important;
    }}
    .theme-neobrutalist-forge .stApp {{
        background-image: none !important;
    }}
    .theme-neobrutalist-forge h1 {{
        text-transform: uppercase !important;
        letter-spacing: -3px !important;
    }}
    .theme-neobrutalist-forge .neo-card {{
        border: 2.5px solid #000 !important;
        box-shadow: 4px 4px 0px #000 !important;
        transition: all 0.1s !important;
    }}
    .theme-neobrutalist-forge .neo-card:hover {{
        transform: translate(-2px,-2px) !important;
        box-shadow: 6px 6px 0px #000 !important;
    }}
    .theme-neobrutalist-forge .neo-btn {{
        border: 2.5px solid #000 !important;
        box-shadow: 4px 4px 0px #000 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }}
    .theme-neobrutalist-forge .neo-btn:hover {{
        transform: translate(-3px, -3px) !important;
        box-shadow: 7px 7px 0px #000 !important;
    }}

    /* ============================================================
       Special Theme: Calm Tide
       ============================================================ */
    .theme-calm-tide {{
        font-family: 'Nunito', 'Segoe UI', sans-serif !important;
    }}
    .theme-calm-tide .stApp {{
        background-image: none !important;
    }}
    .theme-calm-tide h1 {{
        letter-spacing: -1px !important;
        font-weight: 800 !important;
    }}
    .theme-calm-tide .calm-card {{
        border: 1.5px solid #e8eff3 !important;
        border-radius: 18px !important;
        transition: all 0.2s !important;
    }}
    .theme-calm-tide .calm-card:hover {{
        opacity: 1 !important;
        transform: scale(1.02) !important;
    }}
    .theme-calm-tide .time-block {{
        transition: all 0.2s !important;
    }}
    .theme-calm-tide .time-block:hover {{
        opacity: 1 !important;
        transform: scaleY(1.06) !important;
    }}

    /* ============================================================
       Special Theme: RPG Forge
       ============================================================ */
    .theme-rpg-forge {{
        font-family: 'Segoe UI', system-ui, sans-serif !important;
    }}
    .theme-rpg-forge .stApp {{
        background-image:
            radial-gradient(ellipse at top, rgba(108, 99, 255, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at bottom right, rgba(255, 92, 92, 0.1) 0%, transparent 50%);
        background-attachment: fixed;
    }}
    .theme-rpg-forge h1 {{
        text-shadow: 0 0 30px rgba(108, 99, 255, 0.5) !important;
    }}
    .theme-rpg-forge .rpg-card {{
        transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1) !important;
    }}
    .theme-rpg-forge .rpg-card:hover {{
        transform: translateY(-3px) !important;
    }}
    .theme-rpg-forge .rpg-btn-primary {{
        box-shadow: 0 0 16px rgba(108,99,255,0.4) !important;
    }}
    .theme-rpg-forge .rpg-btn-primary:hover {{
        box-shadow: 0 0 30px rgba(108,99,255,0.7) !important;
        transform: translateY(-2px) !important;
    }}
    .theme-rpg-forge .xp-bar {{
        box-shadow: 0 0 10px rgba(108,99,255,0.6) !important;
    }}

    /* ============================================================
       Hide Streamlit Branding
       ============================================================ */

    #MainMenu {{ visibility: hidden !important; }}
    footer {{ visibility: hidden !important; }}
    header {{ visibility: hidden !important; }}

    /* ============================================================
       Animations
       ============================================================ */

    @keyframes fireGlow {{
        0%, 100% {{
            text-shadow: 0 0 5px var(--accent-gold);
        }}
        50% {{
            text-shadow: 0 0 15px #ef4444, 0 0 25px var(--accent-gold);
        }}
    }}

    @keyframes pulse {{
        0%, 100% {{
            opacity: 1;
        }}
        50% {{
            opacity: 0.5;
        }}
    }}

    @keyframes slideUp {{
        from {{
            opacity: 0;
            transform: translateY(20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    @keyframes bentoIn {{
        from {{
            transform: scale(0.94) translateY(8px);
            opacity: 0;
        }}
        to {{
            transform: scale(1) translateY(0);
            opacity: 1;
        }}
    }}

    @keyframes ringFill {{
        from {{
            stroke-dashoffset: 220;
        }}
        to {{
            stroke-dashoffset: var(--target);
        }}
    }}

    @keyframes bruteBounce {{
        0% {{ transform: scale(1); }}
        20% {{ transform: scale(0.85) rotate(-3deg); }}
        50% {{ transform: scale(1.15) rotate(2deg); }}
        100% {{ transform: scale(1) rotate(0); }}
    }}

    @keyframes calmFade {{
        from {{
            opacity: 0;
            transform: translateY(8px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    @keyframes xpGain {{
        0% {{
            transform: translateY(0);
            opacity: 1;
        }}
        100% {{
            transform: translateY(-40px);
            opacity: 0;
        }}
    }}

    @keyframes confettiBurst {{
        0% {{
            transform: scale(0) rotate(0);
            opacity: 1;
        }}
        100% {{
            transform: scale(2.5) rotate(180deg);
            opacity: 0;
        }}
    }}

    @keyframes rpgSlide {{
        from {{
            transform: translateX(-16px);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}

    @keyframes shimmer {{
        0% {{
            background-position: 200% center;
        }}
        100% {{
            background-position: -200% center;
        }}
    }}

    .animate-fireGlow {{
        animation: fireGlow 1.5s ease-in-out infinite;
    }}

    .animate-pulse {{
        animation: pulse 2s ease-in-out infinite;
    }}

    .animate-slideUp {{
        animation: slideUp 0.5s ease-out;
    }}

    .animate-bento-in {{
        animation: bentoIn 0.4s ease both;
    }}

    .animate-brute-bounce {{
        animation: bruteBounce 0.6s ease;
    }}

    .animate-calm-fade {{
        animation: calmFade 0.5s ease;
    }}

    .animate-xp-gain {{
        animation: xpGain 0.8s ease;
    }}

    .animate-rpg-slide {{
        animation: rpgSlide 0.4s ease;
    }}

    /* Theme class on body for theme-specific styling */
    .theme-{theme} {{
        /* Theme-specific root styles */
    }}
    </style>

    <!-- Add theme class to body -->
    <script>
    document.body.classList.add('theme-{theme}');
    </script>
    """, unsafe_allow_html=True)


def render_theme_toggle(key: str = "theme_toggle"):
    """
    Render a theme toggle component in the sidebar.

    Args:
        key: Unique key for the toggle component

    Example:
        >>> with st.sidebar:
        ...     render_theme_toggle()
    """
    st.sidebar.subheader("🎨 Appearance")

    theme = st.sidebar.selectbox(
        "Theme",
        ["System", "Light", "Dark", "Bento Earth", "Neobrutalist Forge", "Calm Tide", "RPG Forge"],
        index=2,  # Default to Dark
        key=key,
        help="Choose your preferred theme"
    )

    # Store theme in session state
    if "theme" not in st.session_state:
        st.session_state.theme = theme.lower()

    if theme != st.session_state.theme:
        st.session_state.theme = theme.lower()
        st.rerun()

    # Theme hint
    if theme == "Dark":
        st.sidebar.caption("🌙 Dark mode enabled")
    elif theme == "Light":
        st.sidebar.caption("☀️ Light mode enabled")
    elif theme == "System":
        st.sidebar.caption("🖥️ Using system theme")
    elif theme == "Bento Earth":
        st.sidebar.caption("🎨 Warm earthy Bento theme")
    elif theme == "Neobrutalist Forge":
        st.sidebar.caption("🔨 Bold, high-contrast theme")
    elif theme == "Calm Tide":
        st.sidebar.caption("🌊 ADHD-friendly calm theme")
    elif theme == "RPG Forge":
        st.sidebar.caption("⚔️ Gamified dark theme")


def get_current_theme() -> ThemeMode:
    """
    Get the current theme from session state.

    Returns:
        Current theme mode ('light', 'dark', 'system', 'bento_earth', 'neobrutalist_forge', 'calm_tide', 'rpg_forge')
    """
    if "theme" not in st.session_state:
        # Try to get from storage if available
        try:
            from tracking_app.storage import get_storage
            storage = get_storage()
            saved_theme = storage.get_user_data('theme')
            if saved_theme:
                st.session_state.theme = saved_theme
                return saved_theme
        except:
            pass
        return "dark"  # Default to dark

    theme = st.session_state.theme

    # Handle 'system' theme - detect from browser preference
    if theme == "system":
        # Could be enhanced with JS browser detection
        # For now, default to dark
        return "dark"

    # Handle special theme names with spaces
    if theme in ["bento earth", "neobrutalist forge", "calm tide", "rpg forge"]:
        # Convert to underscore format
        return theme.replace(" ", "_")

    return theme


def get_theme_colors(theme: Optional[ThemeMode] = None) -> dict:
    """
    Get theme color dictionary for programmatic use.
    
    Args:
        theme: Theme mode (defaults to current theme)
    
    Returns:
        Dictionary of color values
    """
    if theme is None:
        theme = get_current_theme()
    
    c = COLORS
    
    if theme == "light":
        return {
            "bg": c.bg_primary_light,
            "bg_secondary": c.bg_secondary_light,
            "bg_tertiary": c.bg_tertiary_light,
            "text": c.text_primary_light,
            "text_secondary": c.text_secondary_light,
            "primary": c.primary_light,
            "border": c.border_light,
        }
    else:
        return {
            "bg": c.bg_primary_dark,
            "bg_secondary": c.bg_secondary_dark,
            "bg_tertiary": c.bg_tertiary_dark,
            "text": c.text_primary_dark,
            "text_secondary": c.text_secondary_dark,
            "primary": c.primary_dark,
            "border": c.border_dark,
        }


__all__ = [
    "apply_design_system",
    "render_theme_toggle",
    "get_current_theme",
    "get_theme_colors",
    "ThemeMode",
]
