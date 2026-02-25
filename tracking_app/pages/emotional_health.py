"""
Emotional Health Page - RGB Neurotransmitter-Based Emotion Tracking

Streamlit page for tracking emotions using the RGB neurotransmitter model.
Allows users to log emotional states using sliders or presets, view history,
and see pattern analysis.

Usage:
    streamlit run tracking_app/pages/emotional_health.py

Integration:
    - Uses brain.models.emotional_state for data models
    - Saves to SQLite database (emotional_states table)
    - Can be accessed from main navigation
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, List
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brain.models.emotional_state import (
    EmotionalState,
    NeurotransmitterLevels,
    EmotionalModifiers,
    EmotionPreset,
    EmotionalStateManager,
    EmotionAnalyzer
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Emotional Health - Veryfyn",
    page_icon="🌈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# SESSION STATE MANAGEMENT
# =============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'emotion_manager' not in st.session_state:
        st.session_state.emotion_manager = EmotionalStateManager()
    
    if 'emotion_analyzer' not in st.session_state:
        st.session_state.emotion_analyzer = EmotionAnalyzer(
            st.session_state.emotion_manager
        )
    
    if 'last_emotion_logged' not in st.session_state:
        st.session_state.last_emotion_logged = None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_preset_emoji(preset: EmotionPreset) -> str:
    """Get emoji for a preset emotion."""
    state = EmotionalState.from_preset(preset)
    return state.get_secondary_emotion()['emoji']


def render_color_circle(hex_color: str, size: int = 60):
    """Render a colored circle using HTML/CSS."""
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


def render_emotion_card(state: EmotionalState):
    """Render a compact emotion card."""
    emotion = state.get_secondary_emotion()
    
    col1, col2, col3 = st.columns([1, 3, 4])
    
    with col1:
        render_color_circle(state.hex_color, size=40)
    
    with col2:
        st.write(f"{emotion['emoji']} **{emotion['label']}**")
        st.caption(state.timestamp.strftime("%Y-%m-%d %H:%M"))
    
    with col3:
        if state.notes:
            st.caption(f"📝 {state.notes[:50]}...")


# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

def render_header():
    """Render page header with explanation."""
    st.title("🌈 Emotional Health")
    st.markdown("""
    Track your emotions using the **RGB Neurotransmitter Model** - a scientifically-grounded 
    approach where three primary neurotransmitters combine like colors to produce the full 
    spectrum of human emotions.
    """)
    
    # Quick explanation
    with st.expander("ℹ️ How it works"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🔴 Dopamine**
            
            Joy • Reward • Pleasure
            
            High: Achievement, excitement
            Low: Lack of motivation
            """)
        
        with col2:
            st.markdown("""
            **🔵 Norepinephrine**
            
            Stress • Energy • Focus
            
            High: Alertness, anxiety
            Low: Fatigue, low focus
            """)
        
        with col3:
            st.markdown("""
            **🟢 Serotonin**
            
            Satisfaction • Stability
            
            High: Contentment, calm
            Low: Sadness, irritability
            """)


def render_quick_log():
    """Render quick preset selection for logging."""
    st.subheader("⚡ Quick Log")
    
    # Create preset buttons in a grid
    presets = list(EmotionPreset)
    
    # Group presets into rows of 5
    for i in range(0, len(presets), 5):
        cols = st.columns(5)
        for j, col in enumerate(cols):
            if i + j < len(presets):
                preset = presets[i + j]
                emoji = get_preset_emoji(preset)
                
                with col:
                    if st.button(
                        f"{emoji} {preset.value.title()}",
                        key=f"preset_{preset.value}",
                        use_container_width=True
                    ):
                        # Create and save state
                        state = EmotionalState.from_preset(preset)
                        state.timestamp = datetime.now()  # Update timestamp
                        st.session_state.emotion_manager.save(state)
                        st.session_state.last_emotion_logged = state
                        
                        st.success(f"Logged: {state}")
                        st.rerun()


def render_advanced_log():
    """Render advanced neurotransmitter sliders."""
    with st.expander("🎛️ Advanced: Custom Neurotransmitters"):
        st.markdown("Fine-tune your emotional state using the sliders below:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dopamine = st.slider(
                "Dopamine (Joy/Reward)",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.05,
                help="Controls feelings of pleasure, motivation, and reward"
            )
        
        with col2:
            norepinephrine = st.slider(
                "Norepinephrine (Stress/Energy)",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.05,
                help="Controls alertness, focus, and stress response"
            )
        
        with col3:
            serotonin = st.slider(
                "Serotonin (Satisfaction)",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.05,
                help="Controls mood stability, satisfaction, and contentment"
            )
        
        # Optional modifiers
        st.markdown("**Optional Modifiers:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            oxytocin = st.slider(
                "Oxytocin (Bonding)",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.05,
                help="Controls feelings of trust, bonding, and empathy"
            )
        
        with col2:
            endorphins = st.slider(
                "Endorphins (Euphoria)",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.05,
                help="Controls feelings of euphoria and pain relief"
            )
        
        with col3:
            gaba = st.slider(
                "GABA (Calm)",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.05,
                help="Controls feelings of calm and relaxation"
            )
        
        # Notes
        notes = st.text_area("Notes (optional)", placeholder="What's happening?")
        
        # Preview and save
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Create preview state
            preview_state = EmotionalState.create(
                dopamine=dopamine,
                norepinephrine=norepinephrine,
                serotonin=serotonin,
                oxytocin=oxytocin,
                endorphins=endorphins,
                gaba=gaba
            )
            
            st.markdown("**Preview:**")
            render_color_circle(preview_state.hex_color, size=80)
            emotion = preview_state.get_secondary_emotion()
            st.markdown(f"<center>{emotion['emoji']} {emotion['label']}</center>", unsafe_allow_html=True)
        
        with col2:
            if st.button("💾 Save Custom State", use_container_width=True, type="primary"):
                state = EmotionalState.create(
                    dopamine=dopamine,
                    norepinephrine=norepinephrine,
                    serotonin=serotonin,
                    oxytocin=oxytocin,
                    endorphins=endorphins,
                    gaba=gaba,
                    notes=notes
                )
                st.session_state.emotion_manager.save(state)
                st.session_state.last_emotion_logged = state
                st.success(f"Saved: {state}")
                st.rerun()


def render_current_state():
    """Render the last logged emotion."""
    if st.session_state.last_emotion_logged:
        st.subheader("📍 Last Logged")
        state = st.session_state.last_emotion_logged
        emotion = state.get_secondary_emotion()
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            render_color_circle(state.hex_color, size=80)
        
        with col2:
            st.markdown(f"### {emotion['emoji']} {emotion['label']}")
            st.caption(emotion['description'])
            st.caption(f"Logged: {state.timestamp.strftime('%Y-%m-%d %H:%M')}")
            if state.notes:
                st.write(f"📝 {state.notes}")


def render_history():
    """Render emotion history."""
    st.subheader("📜 Recent History")
    
    # Get recent states
    recent = st.session_state.emotion_manager.get_recent(days=14)
    
    if not recent:
        st.info("No emotions logged yet. Start by logging how you feel!")
        return
    
    # Display as a list
    for state in recent[:10]:
        render_emotion_card(state)
        st.divider()


def render_analytics():
    """Render analytics and patterns."""
    st.subheader("📊 Analytics")
    
    analyzer = st.session_state.emotion_analyzer
    
    # Get weekly summary
    summary = analyzer.get_weekly_summary()
    
    if summary['total_entries'] == 0:
        st.info("Log some emotions to see analytics!")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Entries This Week", summary['total_entries'])
    
    with col2:
        dominant = summary['dominant_emotion']
        st.metric("Dominant Emotion", dominant['label'])
    
    with col3:
        avg_levels = NeurotransmitterLevels.from_dict(summary['average_levels'])
        st.metric("Average Color", avg_levels.hex_color)
    
    with col4:
        # Overall brightness
        brightness = (avg_levels.dopamine + avg_levels.norepinephrine + avg_levels.serotonin) / 3
        st.metric("Avg Brightness", f"{brightness:.0%}")
    
    # Average levels display
    st.markdown("#### Average Neurotransmitter Levels")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Dopamine", f"{avg_levels.dopamine:.0%}")
        st.progress(avg_levels.dopamine)
    
    with col2:
        st.metric("Norepinephrine", f"{avg_levels.norepinephrine:.0%}")
        st.progress(avg_levels.norepinephrine)
    
    with col3:
        st.metric("Serotonin", f"{avg_levels.serotonin:.0%}")
        st.progress(avg_levels.serotonin)
    
    # Color trend
    if summary['color_trend']:
        st.markdown("#### Color Trend (Last 7 entries)")
        
        cols = st.columns(len(summary['color_trend']))
        for i, color in enumerate(summary['color_trend']):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="
                        width: 100%;
                        height: 40px;
                        background-color: {color};
                        border-radius: 8px;
                    "></div>
                    """,
                    unsafe_allow_html=True
                )
    
    # Patterns and insights
    patterns = summary.get('patterns', [])
    
    if patterns:
        st.markdown("#### 🔍 Insights")
        
        for pattern in patterns:
            if pattern['type'] == 'warning':
                st.warning(f"**{pattern['label']}**: {pattern['description']}")
                st.info(f"💡 {pattern['recommendation']}")
            elif pattern['type'] == 'positive':
                st.success(f"**{pattern['label']}**: {pattern['description']}")


def render_sidebar():
    """Render sidebar with navigation and info."""
    with st.sidebar:
        st.title("🌈 Emotional Health")
        st.caption("RGB Neurotransmitter Model")
        
        st.divider()
        
        # Quick stats
        analyzer = st.session_state.emotion_analyzer
        summary = analyzer.get_weekly_summary()
        
        st.metric("This Week", summary['total_entries'])
        
        if summary['total_entries'] > 0:
            dominant = summary['dominant_emotion']
            st.metric("Most Common", f"{dominant['label']}")
        
        st.divider()
        
        # Navigation links
        st.subheader("Navigation")
        st.page_link("app.py", label="🏠 Dashboard", icon="🏠")
        st.page_link("pages/health.py", label="❤️ Health", icon="❤️")
        
        st.divider()
        
        # Color legend
        st.subheader("Color Legend")
        st.markdown("""
        - 🔴 **Red tones**: High dopamine (joy)
        - 🔵 **Blue tones**: High stress/energy
        - 🟢 **Green tones**: High satisfaction
        - 🟡 **Yellow tones**: Joy + satisfaction
        - 🟣 **Purple tones**: Joy + stress
        """)


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main page entry point."""
    # Initialize
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main content
    render_header()
    
    st.divider()
    
    # Quick log section
    render_quick_log()
    
    # Advanced log section
    render_advanced_log()
    
    st.divider()
    
    # Show last logged
    render_current_state()
    
    st.divider()
    
    # Two-column layout for history and analytics
    col1, col2 = st.columns(2)
    
    with col1:
        render_history()
    
    with col2:
        render_analytics()


if __name__ == "__main__":
    main()