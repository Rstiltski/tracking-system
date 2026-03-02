"""
Session state management for the Emotional Health page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st

from brain.models.emotional_state import EmotionalStateManager, EmotionAnalyzer


def init_session_state():
    """Initialize session state variables for the Emotional Health page."""
    if 'emotion_manager' not in st.session_state:
        st.session_state.emotion_manager = EmotionalStateManager()
    
    if 'emotion_analyzer' not in st.session_state:
        st.session_state.emotion_analyzer = EmotionAnalyzer(
            st.session_state.emotion_manager
        )
    
    if 'last_emotion_logged' not in st.session_state:
        st.session_state.last_emotion_logged = None