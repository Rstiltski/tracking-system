"""
UI components for the Goal Alerts page.

Contains all render functions for the goal alerts interface.
"""

from typing import Dict, Any, List

import streamlit as st

from .constants import (
    CELEBRATION_STYLES,
    GOAL_CATEGORIES,
    DEFAULT_WARNING_DAYS,
    DEFAULT_FINAL_WARNING_DAYS,
    DEFAULT_PROGRESS_THRESHOLD,
    DEFAULT_CUSTOM_MILESTONES,
)
from .helpers import get_user_goals, get_recent_milestones, get_goal_progress


def render_general_settings() -> bool:
    """
    Render general goal alert settings.
    
    Returns:
        Boolean indicating if goal alerts are enabled
    """
    st.header("General Settings")
    
    goal_alerts_enabled = st.toggle(
        "Enable Goal Alerts",
        value=True,
        help="Master toggle for all goal alerts"
    )
    
    st.divider()
    return goal_alerts_enabled


def render_milestone_settings() -> Dict[str, Any]:
    """
    Render milestone celebration settings.
    
    Returns:
        Dictionary of milestone settings
    """
    st.header("🎉 Milestone Celebrations")
    st.caption("Celebrate when you reach progress milestones.")
    
    milestone_enabled = st.toggle(
        "Enable Milestone Alerts",
        value=True,
        help="Send notifications when reaching milestones"
    )
    
    settings = {
        'enabled': milestone_enabled,
        'milestones': {},
        'custom_milestones': DEFAULT_CUSTOM_MILESTONES,
        'celebration_style': CELEBRATION_STYLES[1]
    }
    
    if milestone_enabled:
        st.markdown("**Milestone Thresholds:**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            quarter_enabled = st.checkbox("🎯 25%", value=True)
            st.caption("Quarter way there!")
            settings['milestones'][25] = quarter_enabled
        
        with col2:
            half_enabled = st.checkbox("🌟 50%", value=True)
            st.caption("Halfway done!")
            settings['milestones'][50] = half_enabled
        
        with col3:
            three_quarter_enabled = st.checkbox("🚀 75%", value=True)
            st.caption("Almost there!")
            settings['milestones'][75] = three_quarter_enabled
        
        with col4:
            complete_enabled = st.checkbox("🏆 100%", value=True)
            st.caption("Goal Completed!")
            settings['milestones'][100] = complete_enabled
        
        # Custom milestones
        st.subheader("Custom Milestones")
        
        custom_milestones = st.text_input(
            "Additional Milestone Percentages",
            value="10, 90",
            help="Comma-separated percentages for additional milestones"
        )
        settings['custom_milestones'] = custom_milestones
        
        # Celebration style
        st.subheader("Celebration Style")
        
        celebration_style = st.radio(
            "How to celebrate milestones",
            options=CELEBRATION_STYLES,
            index=1,
            help="Choose how milestones are celebrated"
        )
        settings['celebration_style'] = celebration_style
    
    st.divider()
    return settings


def render_deadline_settings() -> Dict[str, Any]:
    """
    Render deadline warning settings.
    
    Returns:
        Dictionary of deadline settings
    """
    st.header("⏰ Deadline Warnings")
    st.caption("Get notified before goal deadlines approach.")
    
    deadline_enabled = st.toggle(
        "Enable Deadline Warnings",
        value=True,
        help="Send warnings before goal deadlines"
    )
    
    settings = {
        'enabled': deadline_enabled,
        'warning_days': DEFAULT_WARNING_DAYS,
        'final_warning_days': DEFAULT_FINAL_WARNING_DAYS,
        'progress_warning': True,
        'progress_threshold': DEFAULT_PROGRESS_THRESHOLD
    }
    
    if deadline_enabled:
        col1, col2 = st.columns(2)
        
        with col1:
            warning_days = st.number_input(
                "Days Before Deadline",
                min_value=1,
                max_value=30,
                value=DEFAULT_WARNING_DAYS,
                help="Send first warning this many days before deadline"
            )
            settings['warning_days'] = warning_days
        
        with col2:
            final_days = st.number_input(
                "Final Warning (days)",
                min_value=1,
                max_value=7,
                value=DEFAULT_FINAL_WARNING_DAYS,
                help="Send final warning this many days before deadline"
            )
            settings['final_warning_days'] = final_days
        
        # Progress-based warnings
        st.subheader("Progress-Based Warnings")
        
        progress_warning = st.checkbox(
            "Warn if behind schedule",
            value=True,
            help="Alert if progress is behind expected pace"
        )
        settings['progress_warning'] = progress_warning
        
        if progress_warning:
            progress_threshold = st.slider(
                "Alert if progress below expected (%)",
                min_value=50,
                max_value=90,
                value=DEFAULT_PROGRESS_THRESHOLD,
                help="Alert if current progress is below this percentage of expected"
            )
            settings['progress_threshold'] = progress_threshold
    
    st.divider()
    return settings


def render_category_settings() -> Dict[str, bool]:
    """
    Render goal category settings.
    
    Returns:
        Dictionary of category settings
    """
    st.header("📊 Goal Category Settings")
    st.caption("Configure alerts by goal category.")
    
    category_settings = {}
    
    for cat_id, cat_name, default_enabled in GOAL_CATEGORIES:
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
            
            category_settings[cat_id] = {
                'enabled': cat_enabled,
                'milestones': cat_milestones,
                'deadline': cat_deadline
            }
    
    st.divider()
    return category_settings


def render_individual_goal_settings(user_id: str) -> None:
    """
    Render individual goal alert settings.
    
    Args:
        user_id: User ID to fetch goals for
    """
    st.header("📋 Individual Goal Alerts")
    st.caption("Configure alerts for each goal.")
    
    goals = get_user_goals(user_id)
    
    if goals:
        for goal in goals:
            with st.expander(f"🎯 {goal['name']}", expanded=False):
                _render_goal_alert_config(goal)
    else:
        st.info("No goals found. Create goals first to configure alerts.")


def _render_goal_alert_config(goal: Dict[str, Any]) -> None:
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


def render_recent_milestones(user_id: str) -> None:
    """
    Render recent milestones section.
    
    Args:
        user_id: User ID to fetch milestones for
    """
    st.header("🏆 Recent Milestones")
    
    recent_milestones = get_recent_milestones(user_id)
    
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


def render_progress_overview(user_id: str) -> None:
    """
    Render goal progress overview section.
    
    Args:
        user_id: User ID to fetch progress for
    """
    st.header("📈 Goal Progress Overview")
    
    progress_data = get_goal_progress(user_id)
    
    if progress_data:
        for goal in progress_data:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{goal['name']}**")
                    st.progress(goal['progress'] / 100)
                    st.caption(f"{goal['progress']}% complete")
                
                with col2:
                    if goal['on_track']:
                        st.success("✅ On Track")
                    else:
                        st.warning("⚠️ Behind")
                
                st.divider()
    else:
        st.info("No active goals to display.")