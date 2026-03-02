"""
Component render functions for the Task Alerts page.
"""

import streamlit as st
from datetime import time, datetime, timedelta
from typing import List, Dict, Any, Optional

from .constants import (
    PAGE_TITLE,
    PAGE_ICON,
    PAGE_LAYOUT,
    DEFAULT_USER_ID,
    CHANNEL_OPTIONS,
    ALL_CHANNELS_OPTION,
    URGENCY_COLORS,
    PRIORITY_ICONS,
    REMINDER_FREQUENCY_OPTIONS,
)
from .helpers import (
    get_urgency_icon,
    get_priority_icon,
    get_channel_options_with_all,
    get_mock_today_alerts,
    get_default_priority_settings,
)
from .session_state import (
    init_session_state,
    get_task_alerts_enabled,
    set_task_alerts_enabled,
    get_progressive_enabled,
    get_digest_enabled,
    get_overdue_enabled,
    get_priority_settings,
)


def render_general_settings() -> None:
    """Render general task alert settings."""
    st.header("General Settings")
    
    task_alerts_enabled = st.toggle(
        "Enable Task Alerts",
        value=get_task_alerts_enabled(),
        help="Master toggle for all task deadline alerts"
    )
    set_task_alerts_enabled(task_alerts_enabled)
    
    st.divider()


def render_deadline_thresholds() -> None:
    """Render deadline warning threshold settings."""
    st.header("⏰ Deadline Warning Thresholds")
    st.caption("Configure when to send deadline warnings.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Early Warning")
        early_hours = st.number_input(
            "Hours Before Deadline",
            min_value=1,
            max_value=72,
            value=st.session_state.early_warning_hours,
            help="Send early warning this many hours before deadline"
        )
        st.session_state.early_warning_hours = early_hours
        
        early_channel = st.selectbox(
            "Notification Channel",
            options=CHANNEL_OPTIONS,
            index=CHANNEL_OPTIONS.index(st.session_state.early_channel) if st.session_state.early_channel in CHANNEL_OPTIONS else 0,
            key="early_channel_input"
        )
        st.session_state.early_channel = early_channel
    
    with col2:
        st.subheader("Final Warning")
        final_hours = st.number_input(
            "Hours Before Deadline",
            min_value=1,
            max_value=12,
            value=st.session_state.final_warning_hours,
            help="Send final warning this many hours before deadline",
            key="final_hours_input"
        )
        st.session_state.final_warning_hours = final_hours
        
        channel_options_all = get_channel_options_with_all()
        final_channel = st.selectbox(
            "Notification Channel",
            options=channel_options_all,
            index=channel_options_all.index(st.session_state.final_channel) if st.session_state.final_channel in channel_options_all else 3,
            key="final_channel_input"
        )
        st.session_state.final_channel = final_channel
    
    st.divider()


def render_progressive_urgency() -> None:
    """Render progressive urgency settings."""
    st.header("📈 Progressive Urgency")
    st.caption("Configure how alerts escalate as deadlines approach.")
    
    progressive_enabled = st.toggle(
        "Enable Progressive Urgency",
        value=st.session_state.progressive_enabled,
        help="Alerts become more urgent as deadline approaches"
    )
    st.session_state.progressive_enabled = progressive_enabled
    
    if progressive_enabled:
        st.markdown("**Urgency Levels:**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("LOW", "> 24 hours", delta=None)
            st.caption("Email notification")
        
        with col2:
            st.metric("MEDIUM", "4-24 hours", delta=None)
            st.caption("Browser push")
        
        with col3:
            st.metric("HIGH", "1-4 hours", delta=None)
            st.caption("Priority push")
        
        with col4:
            st.metric("CRITICAL", "< 1 hour", delta="Overdue")
            st.caption("All channels")
        
        # Custom thresholds
        st.subheader("Custom Thresholds")
        
        col1, col2 = st.columns(2)
        
        with col1:
            medium_threshold = st.slider(
                "MEDIUM starts (hours)",
                min_value=4,
                max_value=24,
                value=st.session_state.medium_threshold,
                help="When to start MEDIUM priority alerts"
            )
            st.session_state.medium_threshold = medium_threshold
        
        with col2:
            high_threshold = st.slider(
                "HIGH starts (hours)",
                min_value=1,
                max_value=8,
                value=st.session_state.high_threshold,
                help="When to start HIGH priority alerts"
            )
            st.session_state.high_threshold = high_threshold
    
    st.divider()


def render_daily_digest() -> None:
    """Render daily digest settings."""
    st.header("📰 Daily Digest")
    st.caption("Receive a daily summary of your tasks.")
    
    digest_enabled = st.toggle(
        "Enable Daily Digest",
        value=st.session_state.digest_enabled,
        help="Receive a daily summary of tasks"
    )
    st.session_state.digest_enabled = digest_enabled
    
    if digest_enabled:
        col1, col2 = st.columns(2)
        
        with col1:
            digest_time = st.time_input(
                "Digest Time",
                value=st.session_state.digest_time,
                help="When to send the daily digest"
            )
            st.session_state.digest_time = digest_time
        
        with col2:
            digest_channel = st.selectbox(
                "Delivery Channel",
                options=CHANNEL_OPTIONS,
                index=CHANNEL_OPTIONS.index(st.session_state.digest_channel) if st.session_state.digest_channel in CHANNEL_OPTIONS else 0,
                key="digest_channel_input"
            )
            st.session_state.digest_channel = digest_channel
        
        # Digest content options
        st.subheader("Digest Content")
        
        include_due_today = st.checkbox("Tasks due today", value=st.session_state.include_due_today)
        st.session_state.include_due_today = include_due_today
        
        include_overdue = st.checkbox("Overdue tasks", value=st.session_state.include_overdue)
        st.session_state.include_overdue = include_overdue
        
        include_upcoming = st.checkbox("Upcoming tasks (next 7 days)", value=st.session_state.include_upcoming)
        st.session_state.include_upcoming = include_upcoming
        
        include_completed = st.checkbox("Recently completed", value=st.session_state.include_completed)
        st.session_state.include_completed = include_completed
    
    st.divider()


def render_overdue_settings() -> None:
    """Render overdue task handling settings."""
    st.header("⚠️ Overdue Task Handling")
    st.caption("Configure how overdue tasks are handled.")
    
    overdue_enabled = st.toggle(
        "Enable Overdue Alerts",
        value=st.session_state.overdue_enabled,
        help="Send alerts for overdue tasks"
    )
    st.session_state.overdue_enabled = overdue_enabled
    
    if overdue_enabled:
        col1, col2 = st.columns(2)
        
        with col1:
            overdue_frequency = st.select_slider(
                "Reminder Frequency",
                options=REMINDER_FREQUENCY_OPTIONS,
                value=st.session_state.overdue_frequency,
                help="How often to remind about overdue tasks"
            )
            st.session_state.overdue_frequency = overdue_frequency
        
        with col2:
            max_reminders = st.number_input(
                "Maximum Reminders",
                min_value=1,
                max_value=10,
                value=st.session_state.max_reminders,
                help="Stop reminding after this many notifications"
            )
            st.session_state.max_reminders = max_reminders
    
    st.divider()


def render_priority_settings() -> None:
    """Render priority-based alert settings."""
    st.header("🎯 Priority-Based Alerts")
    st.caption("Configure alerts based on task priority.")
    
    priority_settings = get_priority_settings()
    channel_options_all = get_channel_options_with_all()
    
    for priority in ['high', 'medium', 'low']:
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                enabled = st.checkbox(
                    f"{priority.capitalize()} Priority Tasks",
                    value=priority_settings[priority]['enabled'],
                    key=f"priority_{priority}"
                )
                priority_settings[priority]['enabled'] = enabled
            
            with col2:
                channel = st.selectbox(
                    "Channel",
                    options=channel_options_all,
                    index=channel_options_all.index(priority_settings[priority]['channel']) if priority_settings[priority]['channel'] in channel_options_all else 0,
                    key=f"channel_{priority}",
                    disabled=not enabled
                )
                priority_settings[priority]['channel'] = channel
            
            with col3:
                icon = get_priority_icon(priority)
                st.markdown(f"### {icon}")
    
    st.session_state.priority_settings = priority_settings
    st.divider()


def render_today_alerts(user_id: str = DEFAULT_USER_ID) -> None:
    """Render today's task alerts preview."""
    st.header("📅 Today's Task Alerts")
    
    today_alerts = get_mock_today_alerts(user_id)
    
    if today_alerts:
        for alert in today_alerts:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    icon = get_urgency_icon(alert['urgency'])
                    st.markdown(f"**{icon} {alert['task_name']}**")
                    st.caption(f"Due: {alert['due_date']}")
                
                with col2:
                    st.markdown(f"Alert at: **{alert['alert_time']}**")
                    st.caption(f"Channel: {alert['channel']}")
                
                with col3:
                    if alert['status'] == 'sent':
                        st.success("✅")
                    elif alert['status'] == 'pending':
                        st.info("⏳")
                    else:
                        st.warning("⏰")
                
                st.divider()
    else:
        st.info("No task alerts scheduled for today.")
    
    st.divider()


def render_save_button() -> None:
    """Render the save settings button."""
    if st.button("💾 Save All Settings", type="primary", use_container_width=True):
        st.success("✅ Task alert settings saved successfully!")


def render_task_alerts_page(user_id: str = DEFAULT_USER_ID) -> None:
    """
    Render the complete task alerts settings page.
    
    Args:
        user_id: User ID to manage settings for
    """
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=PAGE_LAYOUT
    )
    
    st.title(f"{PAGE_ICON} Task Alert Settings")
    st.markdown("Configure deadline alerts and daily digest for your tasks.")
    
    # Initialize session state
    init_session_state()
    
    # Render all sections
    render_general_settings()
    render_deadline_thresholds()
    render_progressive_urgency()
    render_daily_digest()
    render_overdue_settings()
    render_priority_settings()
    render_today_alerts(user_id)
    render_save_button()