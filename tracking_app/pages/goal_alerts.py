"""
Goal Alerts Settings Page

Streamlit UI for configuring goal milestone celebrations and deadline warnings.
Provides controls for milestone alerts, progress tracking, and deadline notifications.

Phase 4.3 Feature: Goal Alert Settings UI

Usage:
    streamlit run tracking_app/pages/goal_alerts.py
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

from brain.notifications.goal_alerts import GoalAlertManager, Milestone

logger = logging.getLogger(__name__)


def render_goal_alerts_page(user_id: str = "default"):
    """
    Render the goal alerts settings page.
    
    Args:
        user_id: User ID to manage settings for
    """
    if not HAS_STREAMLIT:
        print("Streamlit not available. Install with: pip install streamlit")
        return
    
    st.set_page_config(
        page_title="Goal Alerts",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Goal Alert Settings")
    st.markdown("Configure milestone celebrations and deadline warnings for your goals.")
    
    # ==========================================
    # Global Goal Alert Settings
    # ==========================================
    st.header("General Settings")
    
    goal_alerts_enabled = st.toggle(
        "Enable Goal Alerts",
        value=True,
        help="Master toggle for all goal alerts"
    )
    
    st.divider()
    
    # ==========================================
    # Milestone Celebrations
    # ==========================================
    st.header("🎉 Milestone Celebrations")
    st.caption("Celebrate when you reach progress milestones.")
    
    milestone_enabled = st.toggle(
        "Enable Milestone Alerts",
        value=True,
        help="Send notifications when reaching milestones"
    )
    
    if milestone_enabled:
        st.markdown("**Milestone Thresholds:**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            quarter_enabled = st.checkbox("🎯 25%", value=True)
            st.caption("Quarter way there!")
        
        with col2:
            half_enabled = st.checkbox("🌟 50%", value=True)
            st.caption("Halfway done!")
        
        with col3:
            three_quarter_enabled = st.checkbox("🚀 75%", value=True)
            st.caption("Almost there!")
        
        with col4:
            complete_enabled = st.checkbox("🏆 100%", value=True)
            st.caption("Goal Completed!")
        
        # Custom milestones
        st.subheader("Custom Milestones")
        
        custom_milestones = st.text_input(
            "Additional Milestone Percentages",
            value="10, 90",
            help="Comma-separated percentages for additional milestones"
        )
        
        # Celebration style
        st.subheader("Celebration Style")
        
        celebration_style = st.radio(
            "How to celebrate milestones",
            options=["Simple notification", "Animated celebration", "Sound + Animation"],
            index=1,
            help="Choose how milestones are celebrated"
        )
    
    st.divider()
    
    # ==========================================
    # Deadline Warnings
    # ==========================================
    st.header("⏰ Deadline Warnings")
    st.caption("Get notified before goal deadlines approach.")
    
    deadline_enabled = st.toggle(
        "Enable Deadline Warnings",
        value=True,
        help="Send warnings before goal deadlines"
    )
    
    if deadline_enabled:
        col1, col2 = st.columns(2)
        
        with col1:
            warning_days = st.number_input(
                "Days Before Deadline",
                min_value=1,
                max_value=30,
                value=7,
                help="Send first warning this many days before deadline"
            )
        
        with col2:
            final_days = st.number_input(
                "Final Warning (days)",
                min_value=1,
                max_value=7,
                value=1,
                help="Send final warning this many days before deadline"
            )
        
        # Progress-based warnings
        st.subheader("Progress-Based Warnings")
        
        progress_warning = st.checkbox(
            "Warn if behind schedule",
            value=True,
            help="Alert if progress is behind expected pace"
        )
        
        if progress_warning:
            progress_threshold = st.slider(
                "Alert if progress below expected (%)",
                min_value=50,
                max_value=90,
                value=75,
                help="Alert if current progress is below this percentage of expected"
            )
    
    st.divider()
    
    # ==========================================
    # Goal Categories
    # ==========================================
    st.header("📊 Goal Category Settings")
    st.caption("Configure alerts by goal category.")
    
    categories = [
        ('health', '🏃 Health & Fitness', True),
        ('finance', '💰 Financial', True),
        ('learning', '📚 Learning', True),
        ('career', '💼 Career', True),
        ('personal', '🏠 Personal', True),
    ]
    
    for cat_id, cat_name, default_enabled in categories:
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                cat_enabled = st.checkbox(
                    cat_name,
                    value=default_enabled,
                    key=f"cat_{cat_id}"
                )
            
            with col2:
                cat_milestones = st.checkbox(
                    "Milestone alerts",
                    value=True,
                    key=f"cat_milestone_{cat_id}",
                    disabled=not cat_enabled
                )
            
            with col3:
                cat_deadline = st.checkbox(
                    "Deadline alerts",
                    value=True,
                    key=f"cat_deadline_{cat_id}",
                    disabled=not cat_enabled
                )
    
    st.divider()
    
    # ==========================================
    # Individual Goal Settings
    # ==========================================
    st.header("📋 Individual Goal Alerts")
    st.caption("Configure alerts for each goal.")
    
    goals = _get_user_goals(user_id)
    
    if goals:
        for goal in goals:
            with st.expander(f"🎯 {goal['name']}", expanded=False):
                _render_goal_alert_config(goal)
    else:
        st.info("No goals found. Create goals first to configure alerts.")
    
    st.divider()
    
    # ==========================================
    # Recent Milestones
    # ==========================================
    st.header("🏆 Recent Milestones")
    
    recent_milestones = _get_recent_milestones(user_id)
    
    if recent_milestones:
        for milestone in recent_milestones:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**{milestone['goal_name']}**")
                st.caption(f"Reached {milestone['percentage']}%")
            
            with col2:
                st.markdown(f"🎉 {milestone['milestone']}")
                st.caption(milestone['celebrated_at'])
            
            with col3:
                st.success("✅")
            
            st.divider()
    else:
        st.info("No milestones celebrated yet. Keep working towards your goals!")
    
    st.divider()
    
    # ==========================================
    # Goal Progress Overview
    # ==========================================
    st.header("📈 Goal Progress Overview")
    
    progress_data = _get_goal_progress(user_id)
    
    if progress_data:
        for goal in progress_data:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{goal['name']}**")
                    progress_bar = st.progress(goal['progress'] / 100)
                    st.caption(f"{goal['progress']}% complete")
                
                with col2:
                    if goal['on_track']:
                        st.success("✅ On Track")
                    else:
                        st.warning("⚠️ Behind")
                
                st.divider()
    else:
        st.info("No active goals to display.")
    
    st.divider()
    
    # ==========================================
    # Save Button
    # ==========================================
    if st.button("💾 Save All Settings", type="primary", use_container_width=True):
        st.success("✅ Goal alert settings saved successfully!")


def _render_goal_alert_config(goal: Dict[str, Any]):
    """Render alert configuration for a single goal."""
    col1, col2 = st.columns(2)
    
    with col1:
        enabled = st.checkbox(
            "Enable Alerts",
            value=goal.get('alerts_enabled', True),
            key=f"goal_enabled_{goal['id']}"
        )
        
        milestones = st.checkbox(
            "Milestone Celebrations",
            value=goal.get('milestones_enabled', True),
            key=f"goal_milestones_{goal['id']}",
            disabled=not enabled
        )
    
    with col2:
        deadline = st.checkbox(
            "Deadline Warnings",
            value=goal.get('deadline_enabled', True),
            key=f"goal_deadline_{goal['id']}",
            disabled=not enabled
        )
        
        if goal.get('deadline'):
            st.caption(f"Deadline: {goal['deadline']}")
    
    # Progress indicator
    st.progress(goal.get('progress', 0) / 100)
    st.caption(f"Current progress: {goal.get('progress', 0)}%")


def _get_user_goals(user_id: str) -> List[Dict[str, Any]]:
    """Get user's goals from database."""
    # In real implementation, fetch from database
    return [
        {
            'id': 'goal-1',
            'name': 'Run 100 miles this month',
            'progress': 67,
            'deadline': 'Feb 28, 2026',
            'alerts_enabled': True,
            'milestones_enabled': True,
            'deadline_enabled': True
        },
        {
            'id': 'goal-2',
            'name': 'Save $1000',
            'progress': 45,
            'deadline': 'Mar 31, 2026',
            'alerts_enabled': True,
            'milestones_enabled': True,
            'deadline_enabled': True
        },
        {
            'id': 'goal-3',
            'name': 'Read 12 books this year',
            'progress': 25,
            'deadline': 'Dec 31, 2026',
            'alerts_enabled': True,
            'milestones_enabled': True,
            'deadline_enabled': False
        },
    ]


def _get_recent_milestones(user_id: str) -> List[Dict[str, Any]]:
    """Get recently celebrated milestones."""
    return [
        {
            'goal_name': 'Run 100 miles this month',
            'percentage': 50,
            'milestone': 'Halfway there!',
            'celebrated_at': '2 days ago'
        },
        {
            'goal_name': 'Save $1000',
            'percentage': 25,
            'milestone': 'Quarter way!',
            'celebrated_at': '1 week ago'
        },
    ]


def _get_goal_progress(user_id: str) -> List[Dict[str, Any]]:
    """Get goal progress data."""
    return [
        {
            'name': 'Run 100 miles this month',
            'progress': 67,
            'on_track': True
        },
        {
            'name': 'Save $1000',
            'progress': 45,
            'on_track': True
        },
        {
            'name': 'Read 12 books this year',
            'progress': 25,
            'on_track': False
        },
    ]


def main():
    """Main entry point for the page."""
    if HAS_STREAMLIT:
        render_goal_alerts_page()
    else:
        print("Streamlit not installed. Run: pip install streamlit")


if __name__ == "__main__":
    main()