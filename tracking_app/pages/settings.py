"""
pages/settings.py - Unified System Settings

Consolidates all system, data, and notification settings into a single tabbed interface 
to reduce sidebar clutter.
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.components.sidebar import render_sidebar

st.set_page_config(
    page_title="Settings & System - Veryfyn",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    render_sidebar()
    
    st.title("⚙️ Settings & System")
    st.markdown("Manage your app preferences, data, privacy, and notifications from one place.")
    st.divider()

    # Create tabs for all the consolidated modules
    tab_notif, tab_data, tab_privacy, tab_reports, tab_alerts, tab_widgets = st.tabs([
        "🔔 Notifications", 
        "💾 Data Management", 
        "🔒 Privacy", 
        "📈 Reports & Insights", 
        "🚨 Alerts",
        "🧩 Widgets"
    ])

    with tab_notif:
        st.subheader("Notification Preferences")
        st.info("💡 To manage your notifications, please navigate to the standalone page (migrating to tabs soon).")
        st.page_link("pages/notification_settings.py", label="Go to Notification Settings ➔")

    with tab_data:
        st.subheader("Data Management")
        st.markdown("Handle your backups, imports, exports, and data lifecycle.")
        col1, col2 = st.columns(2)
        with col1:
            st.page_link("pages/data_export.py", label="📤 Data Export")
            st.page_link("pages/data_import.py", label="📥 Data Import")
        with col2:
            st.page_link("pages/backup_restore.py", label="💾 Backup & Restore")
            st.page_link("pages/data_lifecycle.py", label="♻️ Data Lifecycle")

    with tab_privacy:
        st.subheader("Privacy Settings")
        st.page_link("pages/privacy_dashboard.py", label="🔒 Go to Privacy Dashboard ➔")

    with tab_reports:
        st.subheader("Analytics & Reporting")
        col1, col2 = st.columns(2)
        with col1:
            st.page_link("pages/reports.py", label="📋 Advanced Reports")
        with col2:
            st.page_link("pages/insights.py", label="💡 AI Insights")

    with tab_alerts:
        st.subheader("Actionable Alerts")
        st.markdown("Manage deep-level reminders and critical alerts for specific tracking modules.")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.page_link("pages/habit_reminders.py", label="⏰ Habit Reminders")
        with col2:
            st.page_link("pages/goal_alerts.py", label="🚨 Goal Alerts")
        with col3:
            st.page_link("pages/task_alerts.py", label="📌 Task Alerts")
            
    with tab_widgets:
        st.subheader("Widget Settings")
        st.page_link("pages/widget_settings.py", label="🧩 Configure Dashboard Widgets ➔")


if __name__ == "__main__":
    main()
