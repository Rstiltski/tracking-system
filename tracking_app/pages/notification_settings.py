"""
Notification Settings Page - Manage notification preferences.

This page provides controls for:
- Global notification settings
- Delivery channel preferences
- Quiet hours configuration
- Category preferences
- Smart scheduling

Architecture:
- Constants defined in constants.py
- Helpers in helpers.py
- Session state in session_state.py
- UI components in components.py
"""

import streamlit as st

from tracking_app.pages.notification_settings.constants import PAGE_TITLE, PAGE_ICON, PAGE_LAYOUT
from tracking_app.pages.notification_settings.session_state import init_session_state, get_current_preferences
from tracking_app.pages.notification_settings.components import (
    render_global_controls,
    render_channel_preferences,
    render_quiet_hours,
    render_category_preferences,
    render_smart_scheduling,
    render_save_actions,
    render_notification_history,
    render_statistics,
)


def main() -> None:
    """Main entry point for the notification settings page."""
    # Page configuration
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=PAGE_LAYOUT
    )
    
    # Initialize session state
    init_session_state()
    
    # Get current preferences
    current_prefs = get_current_preferences()
    
    # Page header
    st.title("🔔 Notification Settings")
    st.markdown("Configure how and when you receive notifications.")
    
    # Render global controls
    global_enabled, _ = render_global_controls(current_prefs)
    
    # Render channel preferences
    browser_enabled, email_enabled, email_address = render_channel_preferences(
        current_prefs, global_enabled
    )
    
    # Render quiet hours
    quiet_hours_enabled, start_time, end_time = render_quiet_hours(
        current_prefs, global_enabled
    )
    
    # Render category preferences
    type_overrides = render_category_preferences(current_prefs, global_enabled)
    
    # Render smart scheduling
    smart_enabled, lead_minutes = render_smart_scheduling(current_prefs, global_enabled)
    
    # Render save actions
    render_save_actions(
        current_prefs,
        global_enabled,
        browser_enabled,
        email_enabled,
        email_address,
        quiet_hours_enabled,
        start_time,
        end_time,
        type_overrides,
        smart_enabled,
        lead_minutes
    )
    
    # Render notification history
    render_notification_history()
    
    # Render statistics
    render_statistics()


if __name__ == "__main__":
    main()