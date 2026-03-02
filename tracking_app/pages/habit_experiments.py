"""
Habit Experiments Page - A/B testing for habits.

Usage:
    streamlit run tracking_app/pages/habit_experiments.py
"""
import streamlit as st

from tracking_app.pages.habit_experiments import (
    init_session_state,
    render_template_browser,
    render_active_experiments,
    render_custom_experiment,
    render_experiment_history,
)
from tracking_app.pages.habit_experiments.constants import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    TAB_BROWSE,
    TAB_ACTIVE,
    TAB_CREATE,
    TAB_HISTORY,
)


# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT
)


def main():
    """Main experiments page."""
    # Initialize
    init_session_state()
    
    storage = st.session_state.storage
    user_id = st.session_state.user_id
    
    # Header
    st.title("🧪 Habit Experiments")
    st.markdown("Test different approaches to find what works best for you!")
    
    # Initialize tracker
    from brain.analytics.experiment_tracker import ExperimentTracker
    tracker = ExperimentTracker(storage, user_id)
    
    # Tabs
    tab_browse, tab_active, tab_create, tab_history = st.tabs([
        TAB_BROWSE,
        TAB_ACTIVE,
        TAB_CREATE,
        TAB_HISTORY
    ])
    
    with tab_browse:
        render_template_browser(tracker)
    
    with tab_active:
        render_active_experiments(tracker)
    
    with tab_create:
        render_custom_experiment(tracker)
    
    with tab_history:
        render_experiment_history(tracker)


if __name__ == "__main__":
    main()