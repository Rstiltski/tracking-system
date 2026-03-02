"""
Challenges Page - Group habit challenges.

Usage:
    streamlit run tracking_app/pages/challenges.py
"""
import streamlit as st

from tracking_app.pages.challenges import (
    init_session_state,
    get_challenge_manager,
    render_browse_challenges,
    render_my_challenges,
    render_create_challenge,
    render_certificates,
)


# Page configuration
st.set_page_config(
    page_title="Challenges - Veryfyn",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main challenges page."""
    # Initialize session state
    init_session_state()

    # Initialize manager
    manager = get_challenge_manager()

    if manager is None:
        st.error("Challenge system is not available. Please ensure the brain module is installed.")
        st.stop()

    # Header
    st.title("🎯 Group Challenges")
    st.markdown("Join challenges and achieve your goals together!")

    # Tabs
    tab_browse, tab_my, tab_create, tab_certificates = st.tabs([
        "🌍 Browse Challenges",
        "📋 My Challenges",
        "➕ Create Challenge",
        "🏆 Certificates"
    ])

    with tab_browse:
        render_browse_challenges(manager)

    with tab_my:
        render_my_challenges(manager)

    with tab_create:
        render_create_challenge(manager)

    with tab_certificates:
        render_certificates(manager)


if __name__ == "__main__":
    main()