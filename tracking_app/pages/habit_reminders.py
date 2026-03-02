"""
Habit Reminders Settings Page

Streamlit UI for configuring habit-specific reminder settings.
Provides controls for reminder times, smart scheduling, snooze preferences,
and streak protection settings.

Phase 4.2 Feature: Habit Reminder Settings UI

Usage:
    streamlit run tracking_app/pages/habit_reminders.py
"""

import streamlit as st

from tracking_app.pages.habit_reminders import (
    init_session_state,
    render_general_settings,
    render_smart_scheduling,
    render_streak_protection,
    render_individual_reminders,
    render_today_schedule,
    render_snooze_preferences,
)
from tracking_app.pages.habit_reminders.constants import (
    PAGE_TITLE,
    PAGE_ICON,
    PAGE_LAYOUT,
)
from tracking_app.pages.habit_reminders.session_state import (
    get_scheduler,
    update_settings,
)


# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=PAGE_LAYOUT
)


def main():
    """Main habit reminders settings page."""
    # Initialize
    init_session_state()
    
    # Get scheduler
    scheduler = get_scheduler()
    
    # Header
    st.title("🎯 Habit Reminder Settings")
    st.markdown("Configure personalized reminders for your habits.")
    
    # Render sections and collect settings
    general_settings = render_general_settings()
    smart_settings = render_smart_scheduling()
    streak_settings = render_streak_protection()
    render_individual_reminders(scheduler, smart_settings.get('smart_enabled', True))
    render_today_schedule(scheduler)
    snooze_settings = render_snooze_preferences()
    
    # Save Button
    if st.button("💾 Save All Settings", type="primary", use_container_width=True):
        # Combine all settings
        all_settings = {}
        all_settings.update(general_settings)
        all_settings.update(smart_settings)
        all_settings.update(streak_settings)
        all_settings.update(snooze_settings)
        
        # Save to session state
        update_settings(all_settings)
        st.success("✅ Settings saved successfully!")


if __name__ == "__main__":
    main()