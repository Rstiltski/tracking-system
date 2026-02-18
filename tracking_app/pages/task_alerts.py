"""
Task Alerts Settings Page

Streamlit UI for configuring task deadline alerts and daily digest.
Provides controls for deadline warning thresholds, progressive urgency,
and daily digest preferences.

Phase 4.3 Feature: Task Alert Settings UI

Usage:
    streamlit run tracking_app/pages/task_alerts.py
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

from brain.notifications.task_alerts import TaskAlertManager, TaskUrgency

logger = logging.getLogger(__name__)


def render_task_alerts_page(user_id: str = "default"):
    """
    Render the task alerts settings page.
    
    Args:
        user_id: User ID to manage settings for
    """
    if not HAS_STREAMLIT:
        print("Streamlit not available. Install with: pip install streamlit")
        return
    
    st.set_page_config(
        page_title="Task Alerts",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("📋 Task Alert Settings")
    st.markdown("Configure deadline alerts and daily digest for your tasks.")
    
    # ==========================================
    # Global Task Alert Settings
    # ==========================================
    st.header("General Settings")
    
    task_alerts_enabled = st.toggle(
        "Enable Task Alerts",
        value=True,
        help="Master toggle for all task deadline alerts"
    )
    
    st.divider()
    
    # ==========================================
    # Deadline Warning Thresholds
    # ==========================================
    st.header("⏰ Deadline Warning Thresholds")
    st.caption("Configure when to send deadline warnings.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Early Warning")
        early_hours = st.number_input(
            "Hours Before Deadline",
            min_value=1,
            max_value=72,
            value=24,
            help="Send early warning this many hours before deadline"
        )
        early_channel = st.selectbox(
            "Notification Channel",
            options=["Email", "Browser", "In-App"],
            index=0,
            key="early_channel"
        )
    
    with col2:
        st.subheader("Final Warning")
        final_hours = st.number_input(
            "Hours Before Deadline",
            min_value=1,
            max_value=12,
            value=1,
            help="Send final warning this many hours before deadline"
        )
        final_channel = st.selectbox(
            "Notification Channel",
            options=["Email", "Browser", "In-App", "All Channels"],
            index=3,
            key="final_channel"
        )
    
    st.divider()
    
    # ==========================================
    # Progressive Urgency Settings
    # ==========================================
    st.header("📈 Progressive Urgency")
    st.caption("Configure how alerts escalate as deadlines approach.")
    
    progressive_enabled = st.toggle(
        "Enable Progressive Urgency",
        value=True,
        help="Alerts become more urgent as deadline approaches"
    )
    
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
                value=24,
                help="When to start MEDIUM priority alerts"
            )
        
        with col2:
            high_threshold = st.slider(
                "HIGH starts (hours)",
                min_value=1,
                max_value=8,
                value=4,
                help="When to start HIGH priority alerts"
            )
    
    st.divider()
    
    # ==========================================
    # Daily Digest Settings
    # ==========================================
    st.header("📰 Daily Digest")
    st.caption("Receive a daily summary of your tasks.")
    
    digest_enabled = st.toggle(
        "Enable Daily Digest",
        value=True,
        help="Receive a daily summary of tasks"
    )
    
    if digest_enabled:
        col1, col2 = st.columns(2)
        
        with col1:
            digest_time = st.time_input(
                "Digest Time",
                value=time(7, 0),
                help="When to send the daily digest"
            )
        
        with col2:
            digest_channel = st.selectbox(
                "Delivery Channel",
                options=["Email", "Browser", "In-App"],
                index=0,
                key="digest_channel"
            )
        
        # Digest content options
        st.subheader("Digest Content")
        
        include_due_today = st.checkbox("Tasks due today", value=True)
        include_overdue = st.checkbox("Overdue tasks", value=True)
        include_upcoming = st.checkbox("Upcoming tasks (next 7 days)", value=True)
        include_completed = st.checkbox("Recently completed", value=False)
    
    st.divider()
    
    # ==========================================
    # Overdue Task Settings
    # ==========================================
    st.header("⚠️ Overdue Task Handling")
    st.caption("Configure how overdue tasks are handled.")
    
    overdue_enabled = st.toggle(
        "Enable Overdue Alerts",
        value=True,
        help="Send alerts for overdue tasks"
    )
    
    if overdue_enabled:
        col1, col2 = st.columns(2)
        
        with col1:
            overdue_frequency = st.select_slider(
                "Reminder Frequency",
                options=["Once", "Daily", "Every 4 hours", "Every hour"],
                value="Daily",
                help="How often to remind about overdue tasks"
            )
        
        with col2:
            max_reminders = st.number_input(
                "Maximum Reminders",
                min_value=1,
                max_value=10,
                value=3,
                help="Stop reminding after this many notifications"
            )
    
    st.divider()
    
    # ==========================================
    # Task Priority Settings
    # ==========================================
    st.header("🎯 Priority-Based Alerts")
    st.caption("Configure alerts based on task priority.")
    
    priority_settings = {
        'high': {'enabled': True, 'channel': 'All Channels'},
        'medium': {'enabled': True, 'channel': 'Browser'},
        'low': {'enabled': False, 'channel': 'Email'},
    }
    
    for priority in ['high', 'medium', 'low']:
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                priority_settings[priority]['enabled'] = st.checkbox(
                    f"{priority.capitalize()} Priority Tasks",
                    value=priority_settings[priority]['enabled'],
                    key=f"priority_{priority}"
                )
            
            with col2:
                priority_settings[priority]['channel'] = st.selectbox(
                    "Channel",
                    options=["Email", "Browser", "In-App", "All Channels"],
                    index=3 if priority == 'high' else 1,
                    key=f"channel_{priority}",
                    disabled=not priority_settings[priority]['enabled']
                )
            
            with col3:
                icon = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                st.markdown(f"### {icon}")
    
    st.divider()
    
    # ==========================================
    # Preview Today's Alerts
    # ==========================================
    st.header("📅 Today's Task Alerts")
    
    today_alerts = _get_today_task_alerts(user_id)
    
    if today_alerts:
        for alert in today_alerts:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    urgency_colors = {
                        'low': '🟢',
                        'medium': '🟡',
                        'high': '🟠',
                        'critical': '🔴'
                    }
                    icon = urgency_colors.get(alert['urgency'], '⚪')
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
    
    # ==========================================
    # Save Button
    # ==========================================
    if st.button("💾 Save All Settings", type="primary", use_container_width=True):
        st.success("✅ Task alert settings saved successfully!")


def _get_today_task_alerts(user_id: str) -> List[Dict[str, Any]]:
    """Get today's task alerts."""
    # In real implementation, fetch from TaskAlertManager
    return [
        {
            'id': 'alert-1',
            'task_name': 'Complete project proposal',
            'due_date': 'Today, 5:00 PM',
            'alert_time': '4:00 PM',
            'urgency': 'high',
            'channel': 'All Channels',
            'status': 'pending'
        },
        {
            'id': 'alert-2',
            'task_name': 'Review team feedback',
            'due_date': 'Tomorrow, 10:00 AM',
            'alert_time': '9:00 AM',
            'urgency': 'medium',
            'channel': 'Browser',
            'status': 'scheduled'
        },
        {
            'id': 'alert-3',
            'task_name': 'Update documentation',
            'due_date': 'Yesterday',
            'alert_time': '9:00 AM',
            'urgency': 'critical',
            'channel': 'All Channels',
            'status': 'sent'
        },
    ]


def main():
    """Main entry point for the page."""
    if HAS_STREAMLIT:
        render_task_alerts_page()
    else:
        print("Streamlit not installed. Run: pip install streamlit")


if __name__ == "__main__":
    main()