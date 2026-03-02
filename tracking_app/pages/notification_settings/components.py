"""
UI components for the Notification Settings page.

Contains all render functions for the notification preferences interface.
"""

from datetime import time, datetime
from typing import Dict, Any, Tuple

import streamlit as st

from brain.notifications.models import NotificationPreferences

from .constants import (
    NOTIFICATION_TYPES,
    MIN_LEAD_MINUTES,
    MAX_LEAD_MINUTES,
    HISTORY_LIMIT,
)
from .helpers import get_type_icon, get_default_quiet_hours_start, get_default_quiet_hours_end, calculate_success_rate
from .session_state import get_user_id, get_preference_manager


def render_global_controls(current_prefs) -> Tuple[bool, bool]:
    """
    Render global notification controls.
    
    Args:
        current_prefs: Current notification preferences
        
    Returns:
        Tuple of (global_enabled, status_changed)
    """
    st.header("General Settings")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        global_enabled = st.toggle(
            "Enable Notifications",
            value=current_prefs.enabled,
            help="Master toggle for all notifications"
        )
    
    with col2:
        if current_prefs.enabled:
            st.success("✅ Notifications Active")
        else:
            st.warning("⚠️ Notifications Paused")
    
    st.divider()
    
    return global_enabled, global_enabled != current_prefs.enabled


def render_channel_preferences(current_prefs, global_enabled: bool) -> Tuple[bool, bool, str]:
    """
    Render delivery channel preferences.
    
    Args:
        current_prefs: Current notification preferences
        global_enabled: Whether notifications are globally enabled
        
    Returns:
        Tuple of (browser_enabled, email_enabled, email_address)
    """
    st.header("Delivery Channels")
    st.caption("Choose how you want to receive notifications.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        browser_enabled = st.checkbox(
            "🌐 Browser Notifications",
            value=current_prefs.browser_notifications_enabled,
            disabled=not global_enabled,
            help="Receive push notifications in your browser"
        )
    
    with col2:
        email_enabled = st.checkbox(
            "📧 Email Notifications",
            value=current_prefs.email_notifications_enabled,
            disabled=not global_enabled,
            help="Receive notifications via email"
        )
    
    with col3:
        st.checkbox(
            "📱 In-App Notifications",
            value=True,
            disabled=True,
            help="Always enabled - shows in the app"
        )
    
    # Email address input
    if email_enabled and global_enabled:
        email_address = st.text_input(
            "Email Address",
            value=current_prefs.email_address or "",
            placeholder="your@email.com",
            help="Email address for notification delivery"
        )
    else:
        email_address = current_prefs.email_address
    
    st.divider()
    
    return browser_enabled, email_enabled, email_address


def render_quiet_hours(current_prefs, global_enabled: bool) -> Tuple[bool, time, time]:
    """
    Render quiet hours configuration.
    
    Args:
        current_prefs: Current notification preferences
        global_enabled: Whether notifications are globally enabled
        
    Returns:
        Tuple of (quiet_hours_enabled, start_time, end_time)
    """
    st.header("🌙 Quiet Hours")
    st.caption("Notifications will be suppressed during this window.")
    
    quiet_hours_enabled = st.toggle(
        "Enable Quiet Hours",
        value=current_prefs.quiet_hours_start is not None,
        disabled=not global_enabled
    )
    
    if quiet_hours_enabled and global_enabled:
        col1, col2 = st.columns(2)
        
        with col1:
            start_time = st.time_input(
                "Start Time",
                value=current_prefs.quiet_hours_start or get_default_quiet_hours_start(),
                help="When quiet hours begin"
            )
        
        with col2:
            end_time = st.time_input(
                "End Time",
                value=current_prefs.quiet_hours_end or get_default_quiet_hours_end(),
                help="When quiet hours end"
            )
        
        # Show current status
        if current_prefs.is_quiet_hours():
            st.info("🔇 Currently in quiet hours - notifications are paused")
        else:
            st.success("🔔 Outside quiet hours - notifications active")
    else:
        start_time = None
        end_time = None
    
    st.divider()
    
    return quiet_hours_enabled, start_time, end_time


def render_category_preferences(current_prefs, global_enabled: bool) -> Dict[str, bool]:
    """
    Render notification category preferences.
    
    Args:
        current_prefs: Current notification preferences
        global_enabled: Whether notifications are globally enabled
        
    Returns:
        Dictionary of type overrides
    """
    st.header("Category Preferences")
    st.caption("Enable or disable specific notification types.")
    
    types_cols = st.columns(3)
    
    # Map type keys to preference attributes
    pref_attrs = {
        'habit': 'habit_reminders_enabled',
        'task': 'task_reminders_enabled',
        'goal': 'goal_reminders_enabled',
        'achievement': 'achievement_notifications_enabled',
        'streak_warning': 'streak_warnings_enabled',
        'daily_digest': 'daily_digest_enabled',
    }
    
    type_overrides = {}
    
    for idx, (type_key, label, help_text) in enumerate(NOTIFICATION_TYPES):
        with types_cols[idx % 3]:
            attr_name = pref_attrs.get(type_key, f'{type_key}_enabled')
            default = getattr(current_prefs, attr_name, True)
            
            type_overrides[type_key] = st.toggle(
                label,
                value=default,
                disabled=not global_enabled,
                help=help_text,
                key=f"toggle_{type_key}"
            )
    
    st.divider()
    
    return type_overrides


def render_smart_scheduling(current_prefs, global_enabled: bool) -> Tuple[bool, int]:
    """
    Render smart scheduling configuration.
    
    Args:
        current_prefs: Current notification preferences
        global_enabled: Whether notifications are globally enabled
        
    Returns:
        Tuple of (smart_enabled, lead_minutes)
    """
    st.header("🧠 Smart Scheduling")
    st.caption("Let the system learn optimal reminder times based on your behavior.")
    
    smart_enabled = st.toggle(
        "Enable Smart Scheduling",
        value=current_prefs.smart_scheduling_enabled,
        disabled=not global_enabled,
        help="Uses your completion history to find optimal reminder times"
    )
    
    if smart_enabled and global_enabled:
        lead_minutes = st.slider(
            "Reminder Lead Time (minutes)",
            min_value=MIN_LEAD_MINUTES,
            max_value=MAX_LEAD_MINUTES,
            value=current_prefs.min_reminder_lead_minutes,
            help="How many minutes before the typical completion time to send reminders"
        )
    else:
        lead_minutes = current_prefs.min_reminder_lead_minutes
    
    st.divider()
    
    return smart_enabled, lead_minutes


def render_save_actions(
    current_prefs,
    global_enabled: bool,
    browser_enabled: bool,
    email_enabled: bool,
    email_address: str,
    quiet_hours_enabled: bool,
    start_time: time,
    end_time: time,
    type_overrides: Dict[str, bool],
    smart_enabled: bool,
    lead_minutes: int
) -> None:
    """
    Render save and action buttons.
    
    Args:
        All preference values from other render functions
    """
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        save_button = st.button("💾 Save Changes", type="primary", use_container_width=True)
    
    with col2:
        reset_button = st.button("🔄 Reset to Defaults", use_container_width=True)
    
    with col3:
        test_button = st.button("🧪 Send Test", use_container_width=True)
    
    # Handle actions
    if save_button:
        _handle_save(
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
    
    if reset_button:
        _handle_reset()
    
    if test_button:
        _handle_test()
    
    st.divider()


def _handle_save(
    current_prefs,
    global_enabled: bool,
    browser_enabled: bool,
    email_enabled: bool,
    email_address: str,
    quiet_hours_enabled: bool,
    start_time: time,
    end_time: time,
    type_overrides: Dict[str, bool],
    smart_enabled: bool,
    lead_minutes: int
) -> None:
    """Handle save button click."""
    pm = get_preference_manager()
    user_id = get_user_id()
    
    updated_prefs = NotificationPreferences(
        user_id=user_id,
        enabled=global_enabled,
        quiet_hours_start=start_time if quiet_hours_enabled else None,
        quiet_hours_end=end_time if quiet_hours_enabled else None,
        browser_notifications_enabled=browser_enabled,
        email_notifications_enabled=email_enabled,
        email_address=email_address if email_enabled else None,
        habit_reminders_enabled=type_overrides.get('habit', True),
        task_reminders_enabled=type_overrides.get('task', True),
        goal_reminders_enabled=type_overrides.get('goal', True),
        achievement_notifications_enabled=type_overrides.get('achievement', True),
        streak_warnings_enabled=type_overrides.get('streak_warning', True),
        daily_digest_enabled=type_overrides.get('daily_digest', False),
        smart_scheduling_enabled=smart_enabled,
        min_reminder_lead_minutes=lead_minutes,
        updated_at=datetime.now()
    )
    
    if pm.save_preferences(updated_prefs):
        st.success("✅ Preferences saved successfully!")
        st.rerun()
    else:
        st.error("❌ Failed to save preferences. Please try again.")


def _handle_reset() -> None:
    """Handle reset button click."""
    pm = get_preference_manager()
    user_id = get_user_id()
    
    if pm.reset_to_defaults(user_id):
        st.success("✅ Preferences reset to defaults!")
        st.rerun()
    else:
        st.error("❌ Failed to reset preferences. Please try again.")


def _handle_test() -> None:
    """Handle test notification button click."""
    pm = get_preference_manager()
    user_id = get_user_id()
    
    with st.spinner("Sending test notification..."):
        result = pm.send_test_notification(user_id)
    
    if result.get('success'):
        st.success("✅ Test notification sent!")
        with st.expander("View Details"):
            st.json(result)
    else:
        st.warning("⚠️ Test notification could not be sent to all channels")
        with st.expander("View Details"):
            st.json(result)


def render_notification_history() -> None:
    """Render notification history section."""
    st.header("📜 Recent Notifications")
    
    pm = get_preference_manager()
    user_id = get_user_id()
    history = pm.get_notification_history(user_id, limit=HISTORY_LIMIT)
    
    if history:
        for item in history:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    icon = get_type_icon(item.get('type', 'system'))
                    st.markdown(f"**{icon} {item.get('title', 'Unknown')}**")
                    st.caption(item.get('message', '')[:100] + "...")
                
                with col2:
                    channel = item.get('channel', 'in_app')
                    status = item.get('delivery_status', 'unknown')
                    st.markdown(f"Channel: `{channel}`")
                    st.markdown(f"Status: `{status}`")
                
                with col3:
                    created = item.get('created_at', '')
                    if created:
                        st.caption(created)
                    
                    if item.get('read'):
                        st.caption("✅ Read")
                    else:
                        st.caption("📬 Unread")
                
                st.divider()
    else:
        st.info("No notifications yet. They will appear here once you start receiving them.")


def render_statistics() -> None:
    """Render notification statistics."""
    with st.expander("📊 Notification Statistics"):
        pm = get_preference_manager()
        user_id = get_user_id()
        stats = pm.get_notification_stats(user_id)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Notifications", stats.get('total_notifications', 0))
        
        with col2:
            st.metric("Unread", stats.get('unread_count', 0))
        
        with col3:
            success_rate = calculate_success_rate(stats)
            st.metric("Delivery Rate", f"{success_rate:.1f}%")