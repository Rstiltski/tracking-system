"""
Notification Settings Page - Manage notification preferences (Phase 12 Design System)

Streamlit page for configuring notification preferences using the Phase 12 Design System
for consistent, accessible, and responsive UI.

This page provides controls for:
- Global notification settings
- Delivery channel preferences
- Quiet hours configuration
- Category preferences
- Smart scheduling

Features (Phase 12):
- ✅ Phase 12 design system components (cards, buttons, alerts)
- ✅ Responsive layout that works on mobile, tablet, and desktop
- ✅ Accessibility features (focus indicators, skip links, ARIA labels)
- ✅ Better visual hierarchy with design tokens
- ✅ Loading states and empty states
- ✅ Improved color contrast (WCAG 2.1 AA compliant)

Usage:
    streamlit run tracking_app/app.py
    # Navigate to Notifications from sidebar
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Phase 12 Design System
from tracking_app.design.theme import apply_design_system, get_current_theme
from tracking_app.design.components import (
    render_page_header,
    render_section_header,
    render_card,
    render_button,
    render_button_group,
    render_alert,
    render_success_alert,
    render_warning_alert,
    render_info_alert,
    render_empty_state,
    render_loading_state,
    render_tabs,
)
from tracking_app.design.utils import (
    get_responsive_columns,
    render_responsive_container,
    render_focus_styles,
    render_skip_link,
    is_mobile,
    render_spacer,
    render_divider,
)

# Import existing functionality
from tracking_app.components.sidebar import render_sidebar

# Import notification settings components
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


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

# Apply Phase 12 Design System theme
apply_design_system(theme=get_current_theme())

# Render accessibility features
render_focus_styles()


# =============================================================================
# MAIN CONTENT
# =============================================================================

def render_notification_settings_page():
    """Render the main notification settings page content."""
    # Initialize session state
    init_session_state()
    
    # Get current preferences
    current_prefs = get_current_preferences()
    
    # Render page header with Phase 12 styling
    render_page_header(
        title="🔔 Notification Settings",
        subtitle="Configure how and when you receive notifications",
        icon="🔔"
    )
    
    render_divider(height="md")
    
    # Use tabs for organized settings
    tab_names = ["General", "Channels", "Quiet Hours", "Categories", "History"]
    tabs = render_tabs(tab_names)
    
    # Tab 1: General Settings
    with tabs[0]:
        render_section_header("⚙️ General Settings")
        global_enabled, _ = render_global_controls(current_prefs)
        render_spacer(height="md")
        
        render_section_header("🧠 Smart Scheduling")
        smart_enabled, lead_minutes = render_smart_scheduling(current_prefs, global_enabled)
    
    # Tab 2: Channel Preferences
    with tabs[1]:
        render_section_header("📢 Delivery Channels")
        browser_enabled, email_enabled, email_address = render_channel_preferences(
            current_prefs, global_enabled
        )
    
    # Tab 3: Quiet Hours
    with tabs[2]:
        render_section_header("🌙 Quiet Hours")
        quiet_hours_enabled, start_time, end_time = render_quiet_hours(
            current_prefs, global_enabled
        )
    
    # Tab 4: Category Preferences
    with tabs[3]:
        render_section_header("📂 Category Settings")
        type_overrides = render_category_preferences(current_prefs, global_enabled)
    
    # Tab 5: History & Stats
    with tabs[4]:
        render_section_header("📜 Notification History")
        render_notification_history()
        render_spacer(height="lg")
        render_section_header("📊 Statistics")
        render_statistics()
    
    render_divider(height="lg")
    
    # Save actions section
    render_section_header("💾 Save Changes")
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


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main() -> None:
    """Main entry point for the Notification Settings page."""
    # Page configuration
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=PAGE_LAYOUT
    )
    
    # Render sidebar
    render_sidebar()
    
    # Render main content
    render_notification_settings_page()


if __name__ == "__main__":
    main()
