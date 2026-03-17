"""
Feedback Components - Alerts, Toasts, and Notifications

Phase 12: UI/UX Redesign - Component Layer

Provides reusable feedback components for user notifications,
alerts, and status messages with consistent styling.

Usage:
    from tracking_app.design.components.feedback import (
        render_alert,
        render_toast,
        render_notification,
        render_status_message,
    )
"""

import streamlit as st
from typing import Literal, Optional, Dict, Any
from ...design.tokens import COLORS, RADIUS, SHADOW

AlertVariant = Literal["info", "success", "warning", "error"]
ToastPosition = Literal["top-right", "top-left", "bottom-right", "bottom-left"]


def render_alert(
    title: str,
    message: str,
    variant: AlertVariant = "info",
    icon: Optional[str] = None,
    dismissible: bool = True,
    key: Optional[str] = None,
    action_label: Optional[str] = None,
    on_action: Optional[str] = None,
):
    """
    Render an alert banner.
    
    Args:
        title: Alert title
        message: Alert message
        variant: Alert type (info, success, warning, error)
        icon: Optional custom icon
        dismissible: Whether alert can be dismissed
        key: Unique key for dismissible alerts
        action_label: Optional action button label
        on_action: Optional action handler
    
    Example:
        >>> render_alert(
        ...     title="Success!",
        ...     message="Your habit has been saved.",
        ...     variant="success",
        ...     icon="✅"
        ... )
    """
    
    # Default icons by variant
    default_icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
    }
    
    # Colors by variant
    variant_colors = {
        "info": {"bg": "var(--info-bg, rgba(2, 132, 199, 0.1))", "border": "var(--info)", "text": "var(--info)"},
        "success": {"bg": "var(--success-bg, rgba(16, 185, 129, 0.1))", "border": "var(--success)", "text": "var(--success)"},
        "warning": {"bg": "var(--warning-bg, rgba(245, 158, 11, 0.1))", "border": "var(--warning)", "text": "var(--warning)"},
        "error": {"bg": "var(--error-bg, rgba(220, 38, 38, 0.1))", "border": "var(--error)", "text": "var(--error)"},
    }
    
    colors = variant_colors.get(variant, variant_colors["info"])
    alert_icon = icon or default_icons[variant]
    
    # Dismiss button
    dismiss_html = ""
    if dismissible and key:
        dismiss_html = f'''
        <button 
            onclick="document.getElementById('{key}').style.display='none'"
            style="
                background: transparent;
                border: none;
                color: var(--text-secondary);
                cursor: pointer;
                font-size: 1.25rem;
                padding: 0.25rem;
                line-height: 1;
            "
        >×</button>
        '''
    
    # Action button
    action_html = ""
    if action_label:
        action_html = f'''
        <button 
            {f'onclick="{on_action}"' if on_action else ''}
            style="
                background: {colors['border']};
                color: white;
                border: none;
                border-radius: var(--radius-md);
                padding: 0.5rem 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: var(--transition-fast);
                margin-left: auto;
            "
        >{action_label}</button>
        '''
    
    st.markdown(f"""
    <div id="{key}" style="
        background: {colors['bg']};
        border: 1px solid {colors['border']};
        border-left: 4px solid {colors['border']};
        border-radius: var(--radius-lg);
        padding: 1rem 1.25rem;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-sm);
    ">
        <span style="font-size: 1.25rem; flex-shrink: 0;">{alert_icon}</span>
        <div style="flex: 1;">
            <div style="font-weight: 600; color: {colors['text']}; margin-bottom: 0.25rem;">
                {title}
            </div>
            <div style="color: var(--text-primary); font-size: 0.875rem; line-height: 1.5;">
                {message}
            </div>
        </div>
        {action_html}
        {dismiss_html}
    </div>
    """, unsafe_allow_html=True)


def render_info_alert(title: str, message: str, **kwargs):
    """Render an info alert."""
    render_alert(title, message, variant="info", **kwargs)


def render_success_alert(title: str, message: str, **kwargs):
    """Render a success alert."""
    render_alert(title, message, variant="success", **kwargs)


def render_warning_alert(title: str, message: str, **kwargs):
    """Render a warning alert."""
    render_alert(title, message, variant="warning", **kwargs)


def render_error_alert(title: str, message: str, **kwargs):
    """Render an error alert."""
    render_alert(title, message, variant="error", **kwargs)


def render_toast(
    message: str,
    variant: AlertVariant = "info",
    position: ToastPosition = "top-right",
    duration: int = 5000,
    icon: Optional[str] = None,
    key: str = "toast",
):
    """
    Render a toast notification.
    
    Note: Toast requires JavaScript for auto-dismiss. This is a
    simplified version using Streamlit.
    
    Args:
        message: Toast message
        variant: Toast type
        position: Toast position
        duration: Auto-dismiss duration in ms
        icon: Optional icon
        key: Unique key
    
    Example:
        >>> render_toast(
        ...     message="Changes saved successfully!",
        ...     variant="success",
        ...     position="top-right"
        ... )
    """
    
    # Position styles
    position_styles = {
        "top-right": "top: 1rem; right: 1rem;",
        "top-left": "top: 1rem; left: 1rem;",
        "bottom-right": "bottom: 1rem; right: 1rem;",
        "bottom-left": "bottom: 1rem; left: 1rem;",
    }
    
    # Variant colors
    variant_colors = {
        "info": "var(--info)",
        "success": "var(--success)",
        "warning": "var(--warning)",
        "error": "var(--error)",
    }
    
    # Default icons
    default_icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
    }
    
    toast_icon = icon or default_icons[variant]
    color = variant_colors.get(variant, variant_colors["info"])
    pos_style = position_styles.get(position, position_styles["top-right"])
    
    # Store toast state in session
    if f"{key}_visible" not in st.session_state:
        st.session_state[f"{key}_visible"] = True
    
    if not st.session_state[f"{key}_visible"]:
        return
    
    st.markdown(f"""
    <div id="{key}" style="
        position: fixed;
        {pos_style}
        background: var(--bg-secondary);
        border: 1px solid {color};
        border-left: 4px solid {color};
        border-radius: var(--radius-lg);
        padding: 1rem 1.25rem;
        box-shadow: var(--shadow-xl);
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        min-width: 300px;
        max-width: 500px;
        animation: slideIn 0.3s ease-out;
    ">
        <span style="font-size: 1.25rem;">{toast_icon}</span>
        <div style="flex: 1; color: var(--text-primary);">{message}</div>
        <button 
            onclick="document.getElementById('{key}').style.display='none'"
            style="
                background: transparent;
                border: none;
                color: var(--text-secondary);
                cursor: pointer;
                font-size: 1.25rem;
                padding: 0.25rem;
                line-height: 1;
            "
        >×</button>
    </div>
    
    <style>
    @keyframes slideIn {{
        from {{
            transform: translateX(100%);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


def render_notification(
    title: str,
    message: str,
    variant: AlertVariant = "info",
    timestamp: Optional[str] = None,
    unread: bool = True,
    icon: Optional[str] = None,
):
    """
    Render a notification item (for notification lists).
    
    Args:
        title: Notification title
        message: Notification message
        variant: Notification type
        timestamp: Optional timestamp
        unread: Whether notification is unread
        icon: Optional icon
    
    Example:
        >>> render_notification(
        ...     title="Habit Completed",
        ...     message="You completed your morning exercise!",
        ...     variant="success",
        ...     timestamp="2 min ago",
        ...     unread=True
        ... )
    """
    
    default_icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
    }
    
    notif_icon = icon or default_icons[variant]
    
    # Unread indicator
    unread_dot = f'<span style="color: var(--primary); font-size: 1.5rem;">●</span>' if unread else ''
    
    # Timestamp
    timestamp_html = f'<span style="color: var(--text-disabled); font-size: 0.75rem;">{timestamp}</span>' if timestamp else ''
    
    st.markdown(f"""
    <div style="
        background: {'var(--bg-tertiary)' if unread else 'var(--bg-secondary)'};
        border: 1px solid {'var(--primary)' if unread else 'var(--border)'};
        border-radius: var(--radius-lg);
        padding: 1rem;
        margin-bottom: 0.75rem;
        display: flex;
        gap: 0.75rem;
        transition: var(--transition-fast);
    " onmouseover="this.style.transform='translateX(4px)'" onmouseout="this.style.transform='translateX(0)'">
        <span style="font-size: 1.25rem; flex-shrink: 0;">{notif_icon}</span>
        <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                <span style="font-weight: 600; color: var(--text-primary);">{title}</span>
                {unread_dot}
                {timestamp_html}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.875rem; line-height: 1.5;">
                {message}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_status_message(
    message: str,
    variant: AlertVariant = "info",
    icon: Optional[str] = None,
    centered: bool = True,
):
    """
    Render a simple status message.
    
    Args:
        message: Status message
        variant: Message type
        icon: Optional icon
        centered: Whether to center the message
    
    Example:
        >>> render_status_message(
        ...     message="No habits found. Create your first habit!",
        ...     variant="info",
        ...     icon="📝"
        ... )
    """
    
    default_icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
    }
    
    status_icon = icon or default_icons[variant]
    
    variant_colors = {
        "info": "var(--info)",
        "success": "var(--success)",
        "warning": "var(--warning)",
        "error": "var(--error)",
    }
    
    color = variant_colors.get(variant, variant_colors["info"])
    
    st.markdown(f"""
    <div style="
        text-align: {'center' if centered else 'left'};
        padding: 2rem 1rem;
        color: var(--text-secondary);
    ">
        <div style="font-size: 3rem; margin-bottom: 1rem;">{status_icon}</div>
        <div style="font-size: 1rem; color: {color}; font-weight: 600; margin-bottom: 0.5rem;">
            {message}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(
    title: str,
    description: str,
    icon: str = "📭",
    action_label: Optional[str] = None,
    action_key: Optional[str] = None,
    on_action: Optional[str] = None,
):
    """
    Render an empty state for when there's no data.
    
    Args:
        title: Empty state title
        description: Description text
        icon: Icon emoji
        action_label: Optional CTA button label
        action_key: Optional button key
        on_action: Optional action handler
    
    Example:
        >>> render_empty_state(
        ...     title="No Habits Yet",
        ...     description="Start tracking your first habit!",
        ...     icon="🌱",
        ...     action_label="+ Add Habit",
        ...     action_key="add_first_habit"
        ... )
    """
    
    action_html = ""
    if action_label and action_key:
        action_html = f'''
        <button 
            id="{action_key}"
            {f'onclick="{on_action}"' if on_action else ''}
            style="
                background: var(--primary);
                color: white;
                border: none;
                border-radius: var(--radius-md);
                padding: 0.75rem 1.5rem;
                font-weight: 600;
                cursor: pointer;
                transition: var(--transition-fast);
                margin-top: 1rem;
            "
            onmouseover="this.style.background='var(--primary-hover)'"
            onmouseout="this.style.background='var(--primary)'"
        >{action_label}</button>
        '''
    
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 3rem 1rem;
        background: var(--bg-secondary);
        border: 2px dashed var(--border);
        border-radius: var(--radius-xl);
    ">
        <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
        <h3 style="color: var(--text-primary); margin-bottom: 0.5rem;">{title}</h3>
        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">{description}</p>
        {action_html}
    </div>
    """, unsafe_allow_html=True)


def render_loading_state(
    message: str = "Loading...",
    variant: Literal["spinner", "skeleton", "progress"] = "spinner",
    progress: float = 0.0,
):
    """
    Render a loading state.
    
    Args:
        message: Loading message
        variant: Loading style (spinner, skeleton, progress)
        progress: Progress value (0-100) for progress variant
    
    Example:
        >>> render_loading_state(
        ...     message="Loading your habits...",
        ...     variant="progress",
        ...     progress=45
        ... )
    """
    
    if variant == "spinner":
        st.markdown(f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem;
        ">
            <div style="
                width: 48px;
                height: 48px;
                border: 4px solid var(--bg-tertiary);
                border-top-color: var(--primary);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            "></div>
            <div style="color: var(--text-secondary); margin-top: 1rem;">{message}</div>
        </div>
        
        <style>
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        </style>
        """, unsafe_allow_html=True)
    
    elif variant == "progress":
        st.markdown(f"""
        <div style="padding: 2rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: var(--text-secondary);">{message}</span>
                <span style="color: var(--primary); font-weight: 600;">{progress:.0f}%</span>
            </div>
            <div style="
                height: 8px;
                background: var(--bg-tertiary);
                border-radius: var(--radius-full);
                overflow: hidden;
            ">
                <div style="
                    height: 100%;
                    width: {progress}%;
                    background: var(--gradient-xp);
                    border-radius: var(--radius-full);
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    elif variant == "skeleton":
        st.markdown(f"""
        <div style="padding: 1rem;">
            <div style="
                height: 24px;
                background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-secondary) 50%, var(--bg-tertiary) 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                border-radius: var(--radius-md);
                margin-bottom: 0.75rem;
            "></div>
            <div style="
                height: 24px;
                background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-secondary) 50%, var(--bg-tertiary) 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                border-radius: var(--radius-md);
                margin-bottom: 0.75rem;
            "></div>
            <div style="
                height: 24px;
                background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-secondary) 50%, var(--bg-tertiary) 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                border-radius: var(--radius-md);
            "></div>
            <div style="color: var(--text-secondary); margin-top: 1rem; text-align: center;">{message}</div>
        </div>
        
        <style>
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        </style>
        """, unsafe_allow_html=True)


def render_confirmation_dialog(
    title: str,
    message: str,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    confirm_key: str = "confirm",
    cancel_key: str = "cancel",
    variant: AlertVariant = "warning",
) -> Optional[bool]:
    """
    Render a confirmation dialog.
    
    Args:
        title: Dialog title
        message: Confirmation message
        confirm_label: Confirm button label
        cancel_label: Cancel button label
        confirm_key: Confirm button key
        cancel_key: Cancel button key
        variant: Dialog type
    
    Returns:
        True if confirmed, False if cancelled, None if neither
    
    Example:
        >>> result = render_confirmation_dialog(
        ...     title="Delete Habit?",
        ...     message="This action cannot be undone.",
        ...     confirm_label="Delete",
        ...     variant="error"
        ... )
    """
    
    render_alert(
        title=title,
        message=message,
        variant=variant,
        dismissible=False,
    )
    
    cols = st.columns(2)
    
    with cols[0]:
        if st.button(cancel_label, key=cancel_key, use_container_width=True):
            return False
    
    with cols[1]:
        if st.button(confirm_label, key=confirm_key, type="primary", use_container_width=True):
            return True
    
    return None


__all__ = [
    "render_alert",
    "render_info_alert",
    "render_success_alert",
    "render_warning_alert",
    "render_error_alert",
    "render_toast",
    "render_notification",
    "render_status_message",
    "render_empty_state",
    "render_loading_state",
    "render_confirmation_dialog",
    "AlertVariant",
    "ToastPosition",
]
