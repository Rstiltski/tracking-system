"""
Leaderboards page - Competitions and leaderboards for habit tracking.

This page provides a competitive element to habit tracking:
- Active competitions
- Create new competitions
- Competition archive

Architecture:
- Constants defined in constants.py
- Helpers in helpers.py
- Session state in session_state.py
- UI components in components.py
"""

import streamlit as st

from brain.social.leaderboard_manager import LeaderboardManager

from tracking_app.pages.leaderboards.constants import PAGE_TITLE, PAGE_ICON, PAGE_LAYOUT, TAB_ACTIVE, TAB_CREATE, TAB_ARCHIVE
from tracking_app.pages.leaderboards.session_state import init_session_state, get_storage, get_user_id
from tracking_app.pages.leaderboards.components import (
    render_active_competitions,
    render_create_competition,
    render_archive,
)


def main() -> None:
    """Main entry point for the leaderboards page."""
    # Page configuration
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=PAGE_LAYOUT
    )
    
    # Initialize session state
    init_session_state()
    
    # Get storage and create manager
    storage = get_storage()
    user_id = get_user_id()
    manager = LeaderboardManager(storage, user_id)
    
    # Page header
    st.title("🏆 Leaderboards")
    st.markdown("Compete with friends and track your progress on the leaderboard!")
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs([TAB_ACTIVE, TAB_CREATE, TAB_ARCHIVE])
    
    with tab1:
        render_active_competitions(manager)
    
    with tab2:
        render_create_competition(manager)
    
    with tab3:
        render_archive(manager)


if __name__ == "__main__":
    main()