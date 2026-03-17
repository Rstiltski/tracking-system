"""
Button Components - Consistent Button Styles

Phase 11: UI/UX Redesign - Component Layer

Provides reusable button components with consistent styling,
multiple variants, sizes, and states.

Usage:
    from tracking_app.design.components.buttons import render_button, render_button_group
    
    # Single button
    if render_button("Save Changes", key="save_btn", variant="primary"):
        # Handle save
        pass
    
    # Button group
    render_button_group([
        {"label": "Cancel", "variant": "ghost"},
        {"label": "Save", "variant": "primary"},
    ])
"""

import streamlit as st
from typing import Literal, Optional, Callable, Dict, Any, List

ButtonVariant = Literal["primary", "secondary", "success", "warning", "danger", "ghost", "outline"]
ButtonSize = Literal["sm", "md", "lg", "xl"]


def render_button(
    label: str,
    key: str,
    variant: ButtonVariant = "primary",
    size: ButtonSize = "md",
    icon: Optional[str] = None,
    disabled: bool = False,
    help_text: Optional[str] = None,
    on_click: Optional[Callable] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
    type: Literal["primary", "secondary", "tertiary"] = "primary",
    use_container_width: bool = False,
) -> bool:
    """
    Render a styled button with consistent design system styling.
    
    Args:
        label: Button text
        key: Unique Streamlit key
        variant: Visual style variant
        size: Button size
        icon: Optional emoji icon (displayed before label)
        disabled: Whether button is disabled
        help_text: Optional tooltip/help text
        on_click: Click handler callback
        args: Arguments for on_click callback
        kwargs: Keyword arguments for on_click callback
        type: Button type (for Streamlit)
        use_container_width: Whether button should fill container
    
    Returns:
        True if button was clicked, False otherwise
    
    Example:
        >>> if render_button("Save", key="save", icon="💾", variant="success"):
        ...     save_data()
    """
    
    # Build button label with icon
    button_label = f"{icon} {label}" if icon else label
    
    # Map variants to Streamlit types
    type_mapping = {
        "primary": "primary",
        "secondary": "secondary",
        "success": "primary",
        "warning": "secondary",
        "danger": "secondary",
        "ghost": "secondary",
        "outline": "secondary",
    }
    
    btn_type = type_mapping.get(variant, "primary")
    
    # Render button
    clicked = st.button(
        label=button_label,
        key=key,
        disabled=disabled,
        on_click=on_click,
        args=args or (),
        kwargs=kwargs or {},
        type=btn_type,
        use_container_width=use_container_width,
        help=help_text,
    )
    
    # Apply custom styling based on variant
    _apply_button_variant_style(variant, key)
    
    return clicked


def _apply_button_variant_style(variant: ButtonVariant, key: str):
    """
    Apply variant-specific custom CSS styling.
    
    This is a helper that injects variant-specific styles.
    """
    variant_styles = {
        "success": """
            <style>
            #{} button {{
                background-color: var(--success) !important;
                color: white !important;
            }}
            #{} button:hover {{
                background-color: #047857 !important;
                box-shadow: var(--glow-success) !important;
            }}
            </style>
        """.format(key, key),
        "warning": """
            <style>
            #{} button {{
                background-color: var(--warning) !important;
                color: white !important;
            }}
            #{} button:hover {{
                background-color: #b45309 !important;
            }}
            </style>
        """.format(key, key),
        "danger": """
            <style>
            #{} button {{
                background-color: var(--error) !important;
                color: white !important;
            }}
            #{} button:hover {{
                background-color: #b91c1c !important;
                box-shadow: 0 0 15px rgba(220, 38, 38, 0.4) !important;
            }}
            </style>
        """.format(key, key),
        "ghost": """
            <style>
            #{} button {{
                background-color: transparent !important;
                color: var(--text-secondary) !important;
                border: 1px solid transparent !important;
            }}
            #{} button:hover {{
                background-color: var(--bg-tertiary) !important;
                color: var(--text-primary) !important;
            }}
            </style>
        """.format(key, key),
        "outline": """
            <style>
            #{} button {{
                background-color: transparent !important;
                color: var(--primary) !important;
                border: 2px solid var(--primary) !important;
            }}
            #{} button:hover {{
                background-color: var(--primary) !important;
                color: white !important;
            }}
            </style>
        """.format(key, key),
    }
    
    if variant in variant_styles:
        st.markdown(variant_styles[variant], unsafe_allow_html=True)


def render_button_group(
    buttons: List[Dict[str, Any]],
    key_prefix: str = "btn_group",
    columns: Optional[int] = None,
    gap: str = "small",
) -> Optional[str]:
    """
    Render a group of buttons in a horizontal row.
    
    Args:
        buttons: List of button configurations. Each dict can contain:
            - label: Button text (required)
            - variant: Button variant (default: "primary")
            - size: Button size (default: "md")
            - icon: Optional emoji icon
            - disabled: Whether disabled (default: False)
            - key: Custom key (auto-generated if not provided)
        key_prefix: Prefix for auto-generated keys
        columns: Number of columns (defaults to number of buttons)
        gap: Gap between buttons ("small", "medium", "large")
    
    Returns:
        Key of clicked button, or None if no button clicked
    
    Example:
        >>> clicked = render_button_group([
        ...     {"label": "Cancel", "variant": "ghost", "icon": "❌"},
        ...     {"label": "Save", "variant": "success", "icon": "💾"},
        ... ])
        >>> if clicked == "action_save":
        ...     save_data()
    """
    
    n_buttons = len(buttons)
    n_cols = columns or n_buttons
    
    cols = st.columns(n_cols, gap=gap)
    
    for i, btn_config in enumerate(buttons):
        with cols[i]:
            btn_key = btn_config.get("key", f"{key_prefix}_{i}")
            label = btn_config.get("label", f"Button {i}")
            variant = btn_config.get("variant", "primary")
            size = btn_config.get("size", "md")
            icon = btn_config.get("icon")
            disabled = btn_config.get("disabled", False)
            help_text = btn_config.get("help")
            
            if render_button(
                label=label,
                key=btn_key,
                variant=variant,
                size=size,
                icon=icon,
                disabled=disabled,
                help_text=help_text,
                use_container_width=True,
            ):
                return btn_key
    
    return None


def render_icon_button(
    icon: str,
    key: str,
    label: Optional[str] = None,
    variant: ButtonVariant = "ghost",
    size: ButtonSize = "sm",
    disabled: bool = False,
    help_text: Optional[str] = None,
    on_click: Optional[Callable] = None,
) -> bool:
    """
    Render an icon-only button (compact, square).
    
    Args:
        icon: Emoji icon
        key: Unique key
        label: Optional label (for accessibility)
        variant: Button variant
        size: Button size
        disabled: Whether disabled
        help_text: Tooltip/help text
        on_click: Click handler
    
    Returns:
        True if clicked
    
    Example:
        >>> if render_icon_button("🗑️", key="delete", help_text="Delete"):
        ...     delete_item()
    """
    
    return render_button(
        label=label or "",
        key=key,
        variant=variant,
        size=size,
        icon=icon,
        disabled=disabled,
        help_text=help_text,
        on_click=on_click,
    )


def render_action_buttons(
    actions: Dict[str, Dict[str, Any]],
    key_prefix: str = "action",
) -> Optional[str]:
    """
    Render a set of action buttons with predefined configurations.
    
    Args:
        actions: Dict of action configurations:
            {
                "save": {"label": "Save", "icon": "💾", "variant": "success"},
                "cancel": {"label": "Cancel", "icon": "❌", "variant": "ghost"},
            }
        key_prefix: Prefix for button keys
    
    Returns:
        Key of clicked action, or None
    
    Example:
        >>> actions = {
        ...     "save": {"label": "Save", "icon": "💾", "variant": "success"},
        ...     "delete": {"label": "Delete", "icon": "🗑️", "variant": "danger"},
        ... }
        >>> clicked = render_action_buttons(actions)
        >>> if clicked == "action_save":
        ...     save_data()
    """
    
    buttons = []
    for action_key, config in actions.items():
        buttons.append({
            "label": config.get("label", action_key),
            "icon": config.get("icon"),
            "variant": config.get("variant", "primary"),
            "key": f"{key_prefix}_{action_key}",
            "disabled": config.get("disabled", False),
            "help": config.get("help"),
        })
    
    return render_button_group(buttons, key_prefix=f"{key_prefix}_btn")


__all__ = [
    "render_button",
    "render_button_group",
    "render_icon_button",
    "render_action_buttons",
    "ButtonVariant",
    "ButtonSize",
]
