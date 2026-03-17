"""
Design Components - Reusable UI Components

Phase 12: UI/UX Redesign - Component Library

This module provides all reusable UI components for the design system.

Components:
    - buttons: Button variants and groups
    - cards: Card layouts (stat, metric, content, achievement)
    - inputs: Form inputs (text, select, checkbox, textarea, etc.)
    - navigation: Navigation patterns (headers, breadcrumbs, tabs)
    - feedback: Alerts, toasts, notifications, loading states

Usage:
    from tracking_app.design.components import (
        render_button,
        render_stat_card,
        render_text_input,
        render_alert,
        render_page_header,
    )
"""

from .buttons import (
    render_button,
    render_button_group,
    render_icon_button,
    render_action_buttons,
    ButtonVariant,
    ButtonSize,
)

from .cards import (
    render_card,
    render_stat_card,
    render_metric_card,
    render_content_card,
    render_interactive_card,
    render_achievement_card,
    render_progress_card,
    render_info_card,
    CardVariant,
    CardSize,
)

from .inputs import (
    render_text_input,
    render_number_input,
    render_select_input,
    render_multiselect,
    render_checkbox,
    render_toggle,
    render_textarea,
    render_radio_buttons,
    render_slider,
    render_date_input,
    render_file_uploader,
    render_form_input_group,
    InputSize,
    InputVariant,
)

from .navigation import (
    render_page_header,
    render_breadcrumbs,
    render_tabs,
    render_section_header,
    render_sidebar_section,
    render_pagination,
    render_quick_links,
    render_search_bar,
    TabStyle,
)

from .feedback import (
    render_alert,
    render_info_alert,
    render_success_alert,
    render_warning_alert,
    render_error_alert,
    render_toast,
    render_notification,
    render_status_message,
    render_empty_state,
    render_loading_state,
    render_confirmation_dialog,
    AlertVariant,
    ToastPosition,
)

__all__ = [
    # Buttons
    "render_button",
    "render_button_group",
    "render_icon_button",
    "render_action_buttons",
    "ButtonVariant",
    "ButtonSize",
    # Cards
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
    # Inputs
    "render_text_input",
    "render_number_input",
    "render_select_input",
    "render_multiselect",
    "render_checkbox",
    "render_toggle",
    "render_textarea",
    "render_radio_buttons",
    "render_slider",
    "render_date_input",
    "render_file_uploader",
    "render_form_input_group",
    "InputSize",
    "InputVariant",
    # Navigation
    "render_page_header",
    "render_breadcrumbs",
    "render_tabs",
    "render_section_header",
    "render_sidebar_section",
    "render_pagination",
    "render_quick_links",
    "render_search_bar",
    "TabStyle",
    # Feedback
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
