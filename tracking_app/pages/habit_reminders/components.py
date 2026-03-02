"""
UI components for the Habit Reminders page.

Contains all render functions for the reminders interface.
"""

from datetime import time
from typing import Dict, Any, List, Optional

import streamlit as st

from .constants import (
    DEFAULT_REMINDER_TIME_HOUR,
    DEFAULT_REMINDER_TIME_MINUTE,
    DEFAULT_SNOOZE_DURATION,
    DEFAULT_MIN_SAMPLES,
    DEFAULT_CONFIDENCE_THRESHOLD,
    MIN_SAMPLES_RANGE,
    CONFIDENCE_RANGE,
    DEFAULT_WARNING_HOURS,
    DEFAULT_ESCALATION_HOURS,
    DEFAULT_CRITICAL_HOURS,
    DEFAULT_SNOOZE_OPTIONS,
    ALL_SNOOZE_OPTIONS,
    DEFAULT_MAX_SNOOZES,
    MAX_SNOOZES_RANGE,
    DAYS_OF_WEEK,
)
from .helpers import parse_time, get_user_habits, get_today_reminders
from .session_state import get_settings, update_settings


def render_general_settings() -> Dict[str, Any]:
    """
    Render general reminder settings.
    
    Returns:
        Dictionary of general settings
    """
    st.header("General Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_reminder_time = st.time_input(
            "Default Reminder Time",
            value=time(DEFAULT_REMINDER_TIME_HOUR, DEFAULT_REMINDER_TIME_MINUTE),
            help="Default time for new habit reminders"
        )
    
    with col2:
        default_snooze = st.select_slider(
            "Default Snooze Duration",
            options=[5, 10, 15, 20, 30],
            value=DEFAULT_SNOOZE_DURATION,
            help="Default snooze duration in minutes"
        )
    
    st.divider()
    
    return {
        'default_time': default_reminder_time.strftime("%H:%M"),
        'default_snooze': default_snooze,
    }


def render_smart_scheduling() -> Dict[str, Any]:
    """
    Render smart scheduling settings.
    
    Returns:
        Dictionary of smart scheduling settings
    """
    st.header("🧠 Smart Scheduling")
    st.caption("Let the system learn optimal reminder times based on your completion patterns.")
    
    smart_enabled = st.toggle(
        "Enable Smart Scheduling",
        value=True,
        help="Uses your completion history to find optimal reminder times"
    )
    
    settings = {'smart_enabled': smart_enabled}
    
    if smart_enabled:
        col1, col2 = st.columns(2)
        
        with col1:
            min_samples = st.slider(
                "Minimum Samples for Smart Timing",
                min_value=MIN_SAMPLES_RANGE[0],
                max_value=MIN_SAMPLES_RANGE[1],
                value=DEFAULT_MIN_SAMPLES,
                help="Number of completions needed before smart timing activates"
            )
        
        with col2:
            confidence_threshold = st.slider(
                "Confidence Threshold",
                min_value=CONFIDENCE_RANGE[0],
                max_value=CONFIDENCE_RANGE[1],
                value=DEFAULT_CONFIDENCE_THRESHOLD,
                step=0.05,
                help="Minimum confidence required to use smart timing"
            )
        
        settings['min_samples'] = min_samples
        settings['confidence_threshold'] = confidence_threshold
    
    st.divider()
    
    return settings


def render_streak_protection() -> Dict[str, Any]:
    """
    Render streak protection settings.
    
    Returns:
        Dictionary of streak protection settings
    """
    st.header("🔥 Streak Protection")
    st.caption("Configure how the system protects your streaks with escalating reminders.")
    
    streak_protection_enabled = st.toggle(
        "Enable Streak Protection",
        value=True,
        help="Sends escalating reminders when streak is at risk"
    )
    
    settings = {'streak_protection': streak_protection_enabled}
    
    if streak_protection_enabled:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            warning_hours = st.number_input(
                "Warning Start (hours before midnight)",
                min_value=1,
                max_value=12,
                value=DEFAULT_WARNING_HOURS,
                help="When to start sending streak warnings"
            )
        
        with col2:
            escalation_hours = st.number_input(
                "Escalation Start (hours before midnight)",
                min_value=1,
                max_value=6,
                value=DEFAULT_ESCALATION_HOURS,
                help="When to escalate to high priority"
            )
        
        with col3:
            critical_hours = st.number_input(
                "Critical Alert (hours before midnight)",
                min_value=1,
                max_value=3,
                value=DEFAULT_CRITICAL_HOURS,
                help="When to send critical alerts"
            )
        
        settings['warning_hours'] = warning_hours
        settings['escalation_hours'] = escalation_hours
        settings['critical_hours'] = critical_hours
    
    st.divider()
    
    return settings


def render_individual_reminders(scheduler, smart_enabled: bool) -> None:
    """
    Render individual habit reminder configurations.
    
    Args:
        scheduler: Notification scheduler instance
        smart_enabled: Whether smart scheduling is enabled
    """
    st.header("📋 Individual Habit Reminders")
    st.caption("Configure reminders for each habit.")
    
    from .session_state import get_storage, get_user_id
    storage = get_storage()
    user_id = get_user_id()
    
    habits = get_user_habits(user_id, storage)
    
    if habits:
        for habit in habits:
            with st.expander(f"🎯 {habit['name']}", expanded=False):
                _render_habit_reminder_config(habit, smart_enabled)
    else:
        st.info("No habits found. Create habits first to configure reminders.")
    
    st.divider()


def _render_habit_reminder_config(habit: Dict[str, Any], smart_enabled: bool) -> None:
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
            value=parse_time(habit.get('reminder_time', '08:00')),
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
            options=DAYS_OF_WEEK,
            default=habit.get('days', DAYS_OF_WEEK),
            key=f"days_{habit['id']}",
            disabled=not enabled
        )
    
    # Show smart timing info if enabled
    if use_smart and habit.get('smart_time'):
        st.info(f"🧠 Smart time calculated: **{habit['smart_time']}** (confidence: {habit.get('confidence', 0):.0%})")


def render_today_schedule(scheduler) -> None:
    """
    Render today's reminder schedule.
    
    Args:
        scheduler: Notification scheduler instance
    """
    st.header("📅 Today's Reminder Schedule")
    
    from .session_state import get_user_id
    user_id = get_user_id()
    
    reminders = get_today_reminders(user_id, scheduler)
    
    if reminders:
        for reminder in reminders:
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


def render_snooze_preferences() -> Dict[str, Any]:
    """
    Render snooze preference settings.
    
    Returns:
        Dictionary of snooze settings
    """
    st.header("😴 Snooze Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_snoozes = st.number_input(
            "Maximum Snoozes per Reminder",
            min_value=MAX_SNOOZES_RANGE[0],
            max_value=MAX_SNOOZES_RANGE[1],
            value=DEFAULT_MAX_SNOOZES,
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
        options=ALL_SNOOZE_OPTIONS,
        default=DEFAULT_SNOOZE_OPTIONS,
        help="Snooze options shown to user"
    )
    
    st.divider()
    
    return {
        'max_snoozes': max_snoozes,
        'snooze_escalation': snooze_escalation,
        'snooze_options': snooze_options,
    }