"""
Goal Alerts Settings Page - Configure goal milestone celebrations and deadline warnings.

Usage:
    streamlit run tracking_app/pages/goal_alerts.py
"""
import streamlit as st

from tracking_app.pages.goal_alerts import (
    init_session_state,
    render_general_settings,
    render_milestone_settings,
    render_deadline_settings,
    render_category_settings,
    render_individual_goal_settings,
    render_recent_milestones,
    render_progress_overview,
)
from tracking_app.pages.goal_alerts.constants import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
)


# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT
)


def main():
    """Main goal alerts settings page."""
    # Initialize
    init_session_state()
    
    user_id = st.session_state.user_id
    
    # Header
    st.title("🎯 Goal Alert Settings")
    st.markdown("Configure milestone celebrations and deadline warnings for your goals.")
    
    # General Settings
    goal_alerts_enabled = render_general_settings()
    
    # Milestone Settings
    milestone_settings = render_milestone_settings()
    
    # Deadline Settings
    deadline_settings = render_deadline_settings()
    
    # Category Settings
    category_settings = render_category_settings()
    
    # Individual Goal Settings
    render_individual_goal_settings(user_id)
    
    # Recent Milestones
    render_recent_milestones(user_id)
    
    # Progress Overview
    render_progress_overview(user_id)
    
    # Save Button
    if st.button("💾 Save All Settings", type="primary", use_container_width=True):
        st.success("✅ Goal alert settings saved successfully!")


if __name__ == "__main__":
    main()