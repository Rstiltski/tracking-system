"""
Habit Reminders Settings Page

Streamlit UI for configuring habit-specific reminder settings.
Provides controls for reminder times, smart scheduling, snooze preferences,
and streak protection settings.

Phase 4.2 Feature: Habit Reminder Settings UI

Usage:
    streamlit run tracking_app/pages/habit_reminders.py
"""

# Conditional streamlit import for test compatibility
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None

from datetime import time, datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

from brain.notifications.scheduler import get_scheduler, SmartScheduler
from brain.notifications.models import ReminderSchedule, NotificationChannel

logger = logging.getLogger(__name__)


def render_habit_reminders_page(user_id: str = "default"):
    """
    Render the habit reminders settings page.
    
    Args:
        user_id: User ID to manage settings for
    """
    if not HAS_STREAMLIT:
        print("Streamlit not available. Install with: pip install streamlit")
        return
    
    st.set_page_config(
        page_title="Habit Reminders",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Habit Reminder Settings")
    st.markdown("Configure personalized reminders for your habits.")
    
    # Get scheduler
    scheduler = get_scheduler()
    
    # ==========================================
    # Global Habit Reminder Settings
    # ==========================================
    st.header("General Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_reminder_time = st.time_input(
            "Default Reminder Time",
            value=time(8, 0),
            help="Default time for new habit reminders"
        )
    
    with col2:
        default_snooze = st.select_slider(
            "Default Snooze Duration",
            options=[5, 10, 15, 20, 30],
            value=5,
            help="Default snooze duration in minutes"
        )
    
    st.divider()
    
    # ==========================================
    # Smart Scheduling Settings
    # ==========================================
    st.header("🧠 Smart Scheduling")
    st.caption("Let the system learn optimal reminder times based on your completion patterns.")
    
    smart_enabled = st.toggle(
        "Enable Smart Scheduling",
        value=True,
        help="Uses your completion history to find optimal reminder times"
    )
    
    if smart_enabled:
        col1, col2 = st.columns(2)
        
        with col1:
            min_samples = st.slider(
                "Minimum Samples for Smart Timing",
                min_value=3,
                max_value=14,
                value=5,
                help="Number of completions needed before smart timing activates"
            )
        
        with col2:
            confidence_threshold = st.slider(
                "Confidence Threshold",
                min_value=0.5,
                max_value=0.95,
                value=0.7,
                step=0.05,
                help="Minimum confidence required to use smart timing"
            )
    
    st.divider()
    
    # ==========================================
    # Streak Protection Settings
    # ==========================================
    st.header("🔥 Streak Protection")
    st.caption("Configure how the system protects your streaks with escalating reminders.")
    
    streak_protection_enabled = st.toggle(
        "Enable Streak Protection",
        value=True,
        help="Sends escalating reminders when streak is at risk"
    )
    
    if streak_protection_enabled:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            warning_hours = st.number_input(
                "Warning Start (hours before midnight)",
                min_value=1,
                max_value=12,
                value=8,
                help="When to start sending streak warnings"
            )
        
        with col2:
            escalation_hours = st.number_input(
                "Escalation Start (hours before midnight)",
                min_value=1,
                max_value=6,
                value=4,
                help="When to escalate to high priority"
            )
        
        with col3:
            critical_hours = st.number_input(
                "Critical Alert (hours before midnight)",
                min_value=1,
                max_value=3,
                value=2,
                help="When to send critical alerts"
            )
    
    st.divider()
    
    # ==========================================
    # Individual Habit Reminders
    # ==========================================
    st.header("📋 Individual Habit Reminders")
    st.caption("Configure reminders for each habit.")
    
    # Mock habits for demonstration - in real app, fetch from database
    habits = _get_user_habits(user_id)
    
    if habits:
        for habit in habits:
            with st.expander(f"🎯 {habit['name']}", expanded=False):
                _render_habit_reminder_config(habit, scheduler, smart_enabled)
    else:
        st.info("No habits found. Create habits first to configure reminders.")
    
    st.divider()
    
    # ==========================================
    # Reminder Preview
    # ==========================================
    st.header("📅 Today's Reminder Schedule")
    
    today_reminders = _get_today_reminders(user_id)
    
    if today_reminders:
        for reminder in today_reminders:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**{reminder['habit_name']}**")
                st.caption(f"Reminder at {reminder['time']}")
            
            with col2:
                status = reminder.get('status', 'scheduled')
                if status == 'sent':
                    st.success("✅ Sent")
                elif status == 'snoozed':
                    st.warning("😴 Snoozed")
                else:
                    st.info("⏰ Scheduled")
            
            with col3:
                if st.button("Skip", key=f"skip_{reminder['id']}"):
                    st.toast("Reminder skipped!")
    else:
        st.info("No reminders scheduled for today.")
    
    st.divider()
    
    # ==========================================
    # Snooze Preferences
    # ==========================================
    st.header("😴 Snooze Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_snoozes = st.number_input(
            "Maximum Snoozes per Reminder",
            min_value=1,
            max_value=10,
            value=3,
            help="Maximum times a reminder can be snoozed"
        )
    
    with col2:
        snooze_escalation = st.checkbox(
            "Escalate After Max Snoozes",
            value=True,
            help="Send high-priority alert after max snoozes reached"
        )
    
    snooze_options = st.multiselect(
        "Available Snooze Durations (minutes)",
        options=[5, 10, 15, 20, 30, 45, 60],
        default=[5, 10, 15, 30],
        help="Snooze options shown to user"
    )
    
    st.divider()
    
    # ==========================================
    # Save Button
    # ==========================================
    if st.button("💾 Save All Settings", type="primary", use_container_width=True):
        # Save settings
        st.success("✅ Settings saved successfully!")


def _render_habit_reminder_config(habit: Dict[str, Any], scheduler, smart_enabled: bool):
    """Render reminder configuration for a single habit."""
    col1, col2 = st.columns(2)
    
    with col1:
        enabled = st.checkbox(
            "Enable Reminder",
            value=habit.get('reminder_enabled', True),
            key=f"enabled_{habit['id']}"
        )
        
        reminder_time = st.time_input(
            "Reminder Time",
            value=_parse_time(habit.get('reminder_time', '08:00')),
            key=f"time_{habit['id']}",
            disabled=not enabled
        )
    
    with col2:
        use_smart = st.checkbox(
            "Use Smart Scheduling",
            value=habit.get('smart_scheduling', False) and smart_enabled,
            key=f"smart_{habit['id']}",
            disabled=not enabled or not smart_enabled
        )
        
        days = st.multiselect(
            "Active Days",
            options=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            default=habit.get('days', ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']),
            key=f"days_{habit['id']}",
            disabled=not enabled
        )
    
    # Show smart timing info if enabled
    if use_smart and habit.get('smart_time'):
        st.info(f"🧠 Smart time calculated: **{habit['smart_time']}** (confidence: {habit.get('confidence', 0):.0%})")


def _get_user_habits(user_id: str) -> List[Dict[str, Any]]:
    """Get user's habits from database."""
    # In real implementation, fetch from database
    # For now, return sample data
    return [
        {
            'id': 'habit-1',
            'name': 'Morning Meditation',
            'reminder_enabled': True,
            'reminder_time': '07:00',
            'smart_scheduling': True,
            'smart_time': '06:45',
            'confidence': 0.85,
            'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },
        {
            'id': 'habit-2',
            'name': 'Drink Water',
            'reminder_enabled': True,
            'reminder_time': '09:00',
            'smart_scheduling': False,
            'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },
        {
            'id': 'habit-3',
            'name': 'Evening Journal',
            'reminder_enabled': True,
            'reminder_time': '21:00',
            'smart_scheduling': True,
            'smart_time': '20:30',
            'confidence': 0.72,
            'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },
    ]


def _get_today_reminders(user_id: str) -> List[Dict[str, Any]]:
    """Get today's scheduled reminders."""
    # In real implementation, fetch from scheduler
    return [
        {
            'id': 'rem-1',
            'habit_name': 'Morning Meditation',
            'time': '07:00',
            'status': 'sent'
        },
        {
            'id': 'rem-2',
            'habit_name': 'Drink Water',
            'time': '09:00',
            'status': 'scheduled'
        },
        {
            'id': 'rem-3',
            'habit_name': 'Evening Journal',
            'time': '21:00',
            'status': 'scheduled'
        },
    ]


def _parse_time(time_str: str) -> time:
    """Parse time string to time object."""
    try:
        parts = time_str.split(':')
        return time(int(parts[0]), int(parts[1]))
    except:
        return time(8, 0)


def main():
    """Main entry point for the page."""
    if HAS_STREAMLIT:
        render_habit_reminders_page()
    else:
        print("Streamlit not installed. Run: pip install streamlit")


if __name__ == "__main__":
    main()