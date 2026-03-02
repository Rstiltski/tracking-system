"""
Friends Page - Social accountability management.

Usage:
    streamlit run tracking_app/pages/friends.py
"""
import streamlit as st

from brain.social.friend_manager import FriendManager

from tracking_app.pages.friends import (
    init_session_state,
    render_friends_tab,
    render_requests_tab,
    render_feed_tab,
    render_settings_tab,
)
from tracking_app.pages.friends.constants import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    INITIAL_SIDEBAR_STATE,
)


# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)


def main():
    """Main friends page."""
    # Initialize
    init_session_state()
    
    storage = st.session_state.storage
    user_id = st.session_state.user_id
    
    # Initialize manager
    manager = FriendManager(storage, user_id)
    
    # Header
    st.title("👥 Friends & Accountability")
    st.markdown("Connect with friends for mutual support and accountability!")
    
    # Tabs
    tab_friends, tab_requests, tab_feed, tab_settings = st.tabs([
        "👫 My Friends",
        "📨 Requests",
        "📰 Activity Feed",
        "⚙️ Privacy"
    ])
    
    with tab_friends:
        render_friends_tab(manager)
    
    with tab_requests:
        render_requests_tab(manager)
    
    with tab_feed:
        render_feed_tab(manager)
    
    with tab_settings:
        render_settings_tab(manager)


if __name__ == "__main__":
    main()