"""
Header component for the Habits page.

Renders the page title and description.
"""

import streamlit as st


def render_header():
    """
    Render page header.
    
    Displays the main title and description for the habits page.
    """
    st.title("✅ Habits")
    st.markdown("Track your daily habits and build streaks!")