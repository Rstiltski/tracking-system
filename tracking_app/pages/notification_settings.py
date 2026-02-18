"""
Notification Settings Page

Streamlit UI for managing notification preferences.
Provides controls for global settings, quiet hours, per-type toggles,
and channel preferences.

Phase 4.4 Feature: Notification Settings UI

Usage:
    streamlit run tracking_app/pages/notification_settings.py
"""

# Conditional streamlit import for test compatibility
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None

from datetime import time
from typing import Optional, Dict, Any
import logging

# Import preference manager
from brain.notifications.preferences import PreferenceManager, get_preference_manager
from brain.notifications.models import NotificationType, NotificationChannel

logger = logging.getLogger(__name__)


def render_notification_settings(user_id: str = "default"):
    """
    Render the notification settings page.
    
    Args:
        user_id: User ID to manage settings for
    """
    if not HAS_STREAMLIT:
        print("Streamlit not available. Install with: pip install streamlit")
        return
    
    st.set_page_config(
        page_title="Notification Settings",
        page_icon="🔔",
        layout="wide"
    )
    
    st.title("🔔 Notification Settings")
    st.markdown("Configure how and when you receive notifications.")
    
    # Get preference manager
    pm = get_preference_manager()
    current_prefs = pm.get_user_preferences(user_id)
    
    # ==========================================
    # Global Controls
    # ==========================================
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
    
    # ==========================================
    # Channel Preferences
    # ==========================================
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
        # In-app is always enabled
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
    
    # ==========================================
    # Quiet Hours
    # ==========================================
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
                value=current_prefs.quiet_hours_start or time(22, 0),
                help="When quiet hours begin"
            )
        
        with col2:
            end_time = st.time_input(
                "End Time",
                value=current_prefs.quiet_hours_end or time(7, 0),
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
    
    # ==========================================
    # Category Preferences
    # ==========================================
    st.header("Category Preferences")
    st.caption("Enable or disable specific notification types.")
    
    types_cols = st.columns(3)
    
    notification_types = [
        ('habit', '🎯 Habits', 'Reminders for habit completion', current_prefs.habit_reminders_enabled),
        ('task', '📋 Tasks', 'Task deadline alerts', current_prefs.task_reminders_enabled),
        ('goal', '🎯 Goals', 'Goal milestone celebrations', current_prefs.goal_reminders_enabled),
        ('achievement', '🏆 Achievements', 'Achievement unlock notifications', current_prefs.achievement_notifications_enabled),
        ('streak_warning', '🔥 Streak Warnings', 'Alerts when streak is at risk', current_prefs.streak_warnings_enabled),
        ('daily_digest', '📰 Daily Digest', 'Morning summary of your day', current_prefs.daily_digest_enabled),
    ]
    
    type_overrides = {}
    
    for idx, (type_key, label, help_text, default) in enumerate(notification_types):
        with types_cols[idx % 3]:
            type_overrides[type_key] = st.toggle(
                label,
                value=default,
                disabled=not global_enabled,
                help=help_text,
                key=f"toggle_{type_key}"
            )
    
    st.divider()
    
    # ==========================================
    # Smart Scheduling
    # ==========================================
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
            min_value=5,
            max_value=60,
            value=current_prefs.min_reminder_lead_minutes,
            help="How many minutes before the typical completion time to send reminders"
        )
    else:
        lead_minutes = current_prefs.min_reminder_lead_minutes
    
    st.divider()
    
    # ==========================================
    # Save Button
    # ==========================================
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        save_button = st.button("💾 Save Changes", type="primary", use_container_width=True)
    
    with col2:
        reset_button = st.button("🔄 Reset to Defaults", use_container_width=True)
    
    with col3:
        test_button = st.button("🧪 Send Test", use_container_width=True)
    
    # Handle actions
    if save_button:
        # Build updated preferences
        from brain.notifications.models import NotificationPreferences
        from datetime import datetime
        
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
    
    if reset_button:
        if pm.reset_to_defaults(user_id):
            st.success("✅ Preferences reset to defaults!")
            st.rerun()
        else:
            st.error("❌ Failed to reset preferences. Please try again.")
    
    if test_button:
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
    
    st.divider()
    
    # ==========================================
    # Notification History
    # ==========================================
    st.header("📜 Recent Notifications")
    
    history = pm.get_notification_history(user_id, limit=10)
    
    if history:
        for item in history:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    icon = _get_type_icon(item.get('type', 'system'))
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
    
    # ==========================================
    # Statistics
    # ==========================================
    with st.expander("📊 Notification Statistics"):
        stats = pm.get_notification_stats(user_id)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Notifications", stats.get('total_notifications', 0))
        
        with col2:
            st.metric("Unread", stats.get('unread_count', 0))
        
        with col3:
            by_status = stats.get('by_status', {})
            sent = by_status.get('sent', 0)
            failed = by_status.get('failed', 0)
            total = sent + failed
            success_rate = (sent / total * 100) if total > 0 else 0
            st.metric("Delivery Rate", f"{success_rate:.1f}%")


def _get_type_icon(notification_type: str) -> str:
    """Get icon for notification type."""
    icons = {
        'habit_reminder': '🎯',
        'task_due': '📋',
        'goal_deadline': '🎯',
        'streak_warning': '🔥',
        'achievement': '🏆',
        'system': '⚙️',
        'reward': '🎁',
        'daily_digest': '📰',
    }
    return icons.get(notification_type, '🔔')


def main():
    """Main entry point for the page."""
    if HAS_STREAMLIT:
        render_notification_settings()
    else:
        print("Streamlit not installed. Run: pip install streamlit")


if __name__ == "__main__":
    main()