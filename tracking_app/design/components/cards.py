"""
Card Components - Consistent Card Layouts

Phase 12: UI/UX Redesign - Component Layer

Provides reusable card components for displaying content, statistics,
metrics, and interactive elements with consistent styling.

Usage:
    from tracking_app.design.components.cards import (
        render_stat_card,
        render_metric_card,
        render_content_card,
        render_interactive_card,
    )
    
    # Stat card
    render_stat_card(
        label="Total Habits",
        value="24",
        delta="+3 this week",
        icon="✅",
        trend="up"
    )
"""

import streamlit as st
from typing import Literal, Optional, Dict, Any
from ...design.tokens import COLORS, RADIUS, SHADOW, TRANSITION

CardVariant = Literal[
    "default",
    "elevated",
    "highlighted",
    "success",
    "warning",
    "error",
    "info",
    "glass",
]

CardSize = Literal["sm", "md", "lg", "xl"]


def render_card(
    content: str,
    title: Optional[str] = None,
    icon: Optional[str] = None,
    variant: CardVariant = "default",
    size: CardSize = "md",
    interactive: bool = False,
    on_click: Optional[str] = None,
    key: Optional[str] = None,
):
    """
    Render a content card with consistent styling.
    
    Args:
        content: Card content (markdown allowed)
        title: Optional card title
        icon: Optional emoji icon
        variant: Card style variant
        size: Card size
        interactive: Whether card is clickable
        on_click: JavaScript onclick handler (for interactive cards)
        key: Optional unique key
    
    Example:
        >>> render_card(
        ...     content="Your habit streak is on fire!",
        ...     title="🔥 Great Job!",
        ...     variant="success"
        ... )
    """
    
    variant_styles = {
        "default": f"""
            background: var(--bg-secondary);
            border: 1px solid var(--border);
        """,
        "elevated": f"""
            background: var(--bg-secondary);
            border: none;
            box-shadow: var(--shadow-lg);
        """,
        "highlighted": f"""
            background: var(--bg-secondary);
            border: 2px solid var(--primary);
            box-shadow: var(--glow-primary);
        """,
        "success": f"""
            background: var(--success-bg, rgba(16, 185, 129, 0.05));
            border: 1px solid var(--success);
            box-shadow: var(--glow-success);
        """,
        "warning": f"""
            background: var(--warning-bg, rgba(245, 158, 11, 0.05));
            border: 1px solid var(--warning);
        """,
        "error": f"""
            background: var(--error-bg, rgba(220, 38, 38, 0.05));
            border: 1px solid var(--error);
            box-shadow: 0 0 20px rgba(220, 38, 38, 0.2);
        """,
        "info": f"""
            background: var(--info-bg, rgba(2, 132, 199, 0.05));
            border: 1px solid var(--info);
        """,
        "glass": f"""
            background: var(--glass, rgba(31, 41, 55, 0.7));
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
        """,
    }
    
    size_styles = {
        "sm": "padding: 1rem;",
        "md": "padding: 1.5rem;",
        "lg": "padding: 2rem;",
        "xl": "padding: 2.5rem;",
    }
    
    card_style = variant_styles.get(variant, variant_styles["default"])
    size_style = size_styles.get(size, size_styles["md"])
    interactive_style = "cursor: pointer; transition: var(--transition-normal);" if interactive else ""
    
    # Build header HTML
    header_html = ""
    if title or icon:
        header_html = f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--border);
        ">
            {f'<span style="font-size: 1.5rem;">{icon}</span>' if icon else ''}
            {f'<h3 style="margin: 0; font-size: 1.125rem; font-weight: 600; color: var(--text-primary);">{title}</h3>' if title else ''}
        </div>
        """
    
    # Build interactive handlers
    mouse_handlers = ""
    if interactive:
        mouse_handlers = """
            onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='var(--shadow-lg)'"
            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'"
        """
        if on_click:
            mouse_handlers += f' onclick="{on_click}"'
    
    # Render card
    st.markdown(f"""
    <div {f'id="{key}"' if key else ''} style="
        {card_style}
        {size_style}
        {interactive_style}
        border-radius: var(--radius-lg);
        transition: var(--transition-normal);
        {mouse_handlers}
    ">
        {header_html}
        <div style="color: var(--text-primary); line-height: 1.6;">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    icon: str = "📊",
    trend: Optional[Literal["up", "down", "neutral"]] = None,
    size: CardSize = "md",
):
    """
    Render a statistics/metric card with trend indicator.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional change indicator (+5%, -2%, etc.)
        icon: Emoji icon
        trend: Trend direction for styling
        size: Card size
    
    Example:
        >>> render_stat_card(
        ...     label="Weekly Completion",
        ...     value="87%",
        ...     delta="+12% from last week",
        ...     icon="📈",
        ...     trend="up"
        ... )
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
    
    # Size-based styling
    value_size = {"sm": "1.5rem", "md": "2rem", "lg": "2.5rem", "xl": "3rem"}.get(size, "2rem")
    label_size = {"sm": "0.7rem", "md": "0.75rem", "lg": "0.8rem", "xl": "0.85rem"}.get(size, "0.75rem")
    padding = {"sm": "1rem", "md": "1.5rem", "lg": "2rem", "xl": "2.5rem"}.get(size, "1.5rem")
    
    delta_html = ""
    if delta:
        delta_html = f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 0.25rem;
            color: {trend_color};
            font-size: 0.875rem;
            font-weight: 600;
            margin-top: 0.5rem;
        ">
            <span>{trend_icon}</span>
            <span>{delta}</span>
        </div>
        """
    
    st.markdown(f"""
    <div style="
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        padding: {padding};
        border: 1px solid var(--border);
        transition: var(--transition-normal);
    " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='var(--shadow-lg)'; this.style.borderColor='var(--primary)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'; this.style.borderColor='var(--border)'">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <span style="color: var(--text-secondary); font-size: {label_size}; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">{label}</span>
        </div>
        <div style="font-size: {value_size}; font-weight: 800; color: var(--accent-gold); text-shadow: 0 0 20px rgba(245, 158, 11, 0.4);">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    icon: str = "📊",
):
    """
    Render a simple metric card (Streamlit native style enhancement).
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta indicator
        icon: Emoji icon
    
    Example:
        >>> render_metric_card(
        ...     label="Total XP",
        ...     value="2,450",
        ...     delta="+150 today",
        ...     icon="⭐"
        ... )
    """
    render_stat_card(label=label, value=value, delta=delta, icon=icon, trend=None)


def render_content_card(
    title: str,
    content: str,
    icon: Optional[str] = None,
    variant: CardVariant = "default",
    footer: Optional[str] = None,
):
    """
    Render a content card with title and optional footer.
    
    Args:
        title: Card title
        content: Main content (markdown supported)
        icon: Optional emoji icon
        variant: Card style variant
        footer: Optional footer text
    
    Example:
        >>> render_content_card(
        ...     title="💡 Tip of the Day",
        ...     content="Stack your habits together for better consistency.",
        ...     variant="info",
        ...     footer="From: Behavioral Science"
        ... )
    """
    
    footer_html = ""
    if footer:
        footer_html = f"""
        <div style="
            margin-top: 1rem;
            padding-top: 0.75rem;
            border-top: 1px solid var(--border);
            color: var(--text-secondary);
            font-size: 0.875rem;
        ">
            {footer}
        </div>
        """
    
    render_card(
        content=content,
        title=title,
        icon=icon,
        variant=variant,
    )
    
    if footer:
        st.markdown(f"""
        <div style="
            margin-top: -1rem;
            margin-bottom: 1rem;
            padding: 0 1.5rem;
            color: var(--text-secondary);
            font-size: 0.875rem;
        ">
            {footer}
        </div>
        """, unsafe_allow_html=True)


def render_interactive_card(
    title: str,
    content: str,
    icon: Optional[str] = None,
    action_label: str = "Learn More",
    key: Optional[str] = None,
):
    """
    Render an interactive card with click action.
    
    Args:
        title: Card title
        content: Card content
        icon: Optional emoji icon
        action_label: Label for action button
        key: Unique key for the card
    
    Example:
        >>> if render_interactive_card(
        ...     title="🎯 Goal Setting",
        ...     content="Set SMART goals for better achievement",
        ...     action_label="View Goals",
        ...     key="goal_card"
        ... ):
        ...     st.switch_page("pages/goals.py")
    """
    
    # Use session state to track card clicks
    if key:
        if f"{key}_clicked" not in st.session_state:
            st.session_state[f"{key}_clicked"] = False
    
    render_card(
        content=content,
        title=title,
        icon=icon,
        variant="elevated",
        interactive=True,
    )
    
    # Add action button
    if st.button(action_label, key=f"{key}_btn" if key else "card_btn"):
        if key:
            st.session_state[f"{key}_clicked"] = True
        return True
    
    return False


def render_achievement_card(
    title: str,
    description: str,
    icon: str = "🏆",
    unlocked: bool = True,
    xp_reward: int = 0,
):
    """
    Render an achievement/badge card.
    
    Args:
        title: Achievement title
        description: Achievement description
        icon: Emoji icon
        unlocked: Whether achievement is unlocked
        xp_reward: XP reward amount
    
    Example:
        >>> render_achievement_card(
        ...     title="7-Day Streak",
        ...     description="Complete habits for 7 consecutive days",
        ...     icon="🔥",
        ...     unlocked=True,
        ...     xp_reward=50
        ... )
    """
    
    glow_color = "var(--accent-gold)" if unlocked else "var(--text-disabled)"
    opacity = "1" if unlocked else "0.5"
    lock_icon = "🔓" if unlocked else "🔒"
    
    xp_html = ""
    if xp_reward > 0:
        xp_html = f"""
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            background: rgba(245, 158, 11, 0.1);
            padding: 0.25rem 0.75rem;
            border-radius: var(--radius-full);
            color: var(--accent-gold);
            font-weight: 700;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        ">
            <span>⭐</span>
            <span>+{xp_reward} XP</span>
        </div>
        """
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.9), rgba(31, 41, 55, 0.8));
        border: 1px solid {glow_color}40;
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 15px {glow_color}20;
        opacity: {opacity};
        transition: var(--transition-normal);
    " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
        <div style="font-size: 3rem; filter: drop-shadow(0 0 8px {glow_color}80);">
            {icon if unlocked else lock_icon}
        </div>
        <div style="flex: 1;">
            <div style="color: {glow_color}; font-weight: 700; font-size: 1.125rem; margin-bottom: 0.25rem;">
                {title}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.875rem; line-height: 1.5;">
                {description}
            </div>
            {xp_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_progress_card(
    title: str,
    current: float,
    target: float,
    unit: str = "",
    icon: str = "🎯",
    show_percentage: bool = True,
):
    """
    Render a progress card with bar visualization.
    
    Args:
        title: Progress title
        current: Current progress value
        target: Target value
        unit: Unit of measurement
        icon: Emoji icon
        show_percentage: Whether to show percentage
    
    Example:
        >>> render_progress_card(
        ...     title="Weekly Goals",
        ...     current=5,
        ...     target=10,
        ...     unit=" completed",
        ...     icon="✅"
        ... )
    """
    
    percentage = min((current / target * 100) if target > 0 else 0, 100)
    
    st.markdown(f"""
    <div style="
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        border: 1px solid var(--border);
    ">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <span style="color: var(--text-primary); font-weight: 600;">{title}</span>
        </div>
        
        <div style="margin-bottom: 0.5rem;">
            <div style="height: 12px; background: var(--bg-tertiary); border-radius: var(--radius-full); overflow: hidden;">
                <div style="
                    height: 100%;
                    width: {percentage}%;
                    background: var(--gradient-xp);
                    border-radius: var(--radius-full);
                    box-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
                    transition: width var(--transition-slow);
                "></div>
            </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: var(--text-secondary); font-size: 0.875rem;">
                {current:.1f}{unit} / {target:.1f}{unit}
            </span>
            {f'<span style="color: var(--accent-gold); font-weight: 700; font-size: 0.875rem;">{percentage:.0f}%</span>' if show_percentage else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_info_card(
    title: str,
    content: str,
    variant: Literal["info", "warning", "error", "success"] = "info",
    icon: Optional[str] = None,
):
    """
    Render an informational alert card.
    
    Args:
        title: Alert title
        content: Alert content
        variant: Alert type
        icon: Optional custom icon
    
    Example:
        >>> render_info_card(
        ...     title="⚠️ Warning",
        ...     content="This action cannot be undone.",
        ...     variant="warning"
        ... )
    """
    
    default_icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅",
    }
    
    render_card(
        content=content,
        title=title,
        icon=icon or default_icons[variant],
        variant=variant,
    )


__all__ = [
    "render_card",
    "render_stat_card",
    "render_metric_card",
    "render_content_card",
    "render_interactive_card",
    "render_achievement_card",
    "render_progress_card",
    "render_info_card",
    "CardVariant",
    "CardSize",
]
