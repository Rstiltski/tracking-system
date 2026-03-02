"""
Helper functions for the Emotional Health page.

Contains utility functions for emotion display and manipulation.
"""

import streamlit as st

from brain.models.emotional_state import EmotionalState, EmotionPreset

from .constants import (
    COLOR_CIRCLE_SIZE,
    COLOR_CIRCLE_SIZE_PREVIEW,
    COLOR_CIRCLE_SIZE_CARD,
)


def get_preset_emoji(preset: EmotionPreset) -> str:
    """
    Get emoji for a preset emotion.
    
    Args:
        preset: EmotionPreset enum value
        
    Returns:
        Emoji string for the preset
    """
    state = EmotionalState.from_preset(preset)
    return state.get_secondary_emotion()['emoji']


def render_color_circle(hex_color: str, size: int = COLOR_CIRCLE_SIZE) -> None:
    """
    Render a colored circle using HTML/CSS.
    
    Args:
        hex_color: Hex color string (e.g., '#FF0000')
        size: Circle size in pixels
    """
    st.markdown(
        f"""
        <div style="
            width: {size}px;
            height: {size}px;
            background-color: {hex_color};
            border-radius: 50%;
            margin: 0 auto;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        "></div>
        """,
        unsafe_allow_html=True
    )


def render_emotion_card(state: EmotionalState) -> None:
    """
    Render a compact emotion card.
    
    Args:
        state: EmotionalState to display
    """
    emotion = state.get_secondary_emotion()
    
    col1, col2, col3 = st.columns([1, 3, 4])
    
    with col1:
        render_color_circle(state.hex_color, size=COLOR_CIRCLE_SIZE_CARD)
    
    with col2:
        st.write(f"{emotion['emoji']} **{emotion['label']}**")
        st.caption(state.timestamp.strftime("%Y-%m-%d %H:%M"))
    
    with col3:
        if state.notes:
            st.caption(f"📝 {state.notes[:50]}...")