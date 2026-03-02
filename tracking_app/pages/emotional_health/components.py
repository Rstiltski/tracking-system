"""
UI components for the Emotional Health page.

Contains all render functions for the emotion tracking interface.
"""

import streamlit as st
from datetime import datetime

from brain.models.emotional_state import (
    EmotionalState,
    NeurotransmitterLevels,
    EmotionPreset,
)

from .constants import (
    NEUROTRANSMITTER_INFO,
    DEFAULT_NEUROTRANSMITTER_VALUE,
    NEUROTRANSMITTER_STEP,
    NEUROTRANSMITTER_MIN,
    NEUROTRANSMITTER_MAX,
    COLOR_CIRCLE_SIZE_PREVIEW,
    HISTORY_DAYS,
    HISTORY_DISPLAY_LIMIT,
    TREND_DISPLAY_COUNT,
)
from .helpers import get_preset_emoji, render_color_circle, render_emotion_card


def render_header() -> None:
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
            info = NEUROTRANSMITTER_INFO['dopamine']
            st.markdown(f"""
            **{info['emoji']} {info['name']}**
            
            {info['role']}
            
            High: {info['high']}
            Low: {info['low']}
            """)
        
        with col2:
            info = NEUROTRANSMITTER_INFO['norepinephrine']
            st.markdown(f"""
            **{info['emoji']} {info['name']}**
            
            {info['role']}
            
            High: {info['high']}
            Low: {info['low']}
            """)
        
        with col3:
            info = NEUROTRANSMITTER_INFO['serotonin']
            st.markdown(f"""
            **{info['emoji']} {info['name']}**
            
            {info['role']}
            
            High: {info['high']}
            Low: {info['low']}
            """)


def render_quick_log() -> None:
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


def render_advanced_log() -> None:
    """Render advanced neurotransmitter sliders."""
    with st.expander("🎛️ Advanced: Custom Neurotransmitters"):
        st.markdown("Fine-tune your emotional state using the sliders below:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dopamine_info = NEUROTRANSMITTER_INFO['dopamine']
            dopamine = st.slider(
                f"{dopamine_info['emoji']} {dopamine_info['name']} (Joy/Reward)",
                min_value=NEUROTRANSMITTER_MIN,
                max_value=NEUROTRANSMITTER_MAX,
                value=DEFAULT_NEUROTRANSMITTER_VALUE,
                step=NEUROTRANSMITTER_STEP,
                help=dopamine_info['help']
            )
        
        with col2:
            norepinephrine_info = NEUROTRANSMITTER_INFO['norepinephrine']
            norepinephrine = st.slider(
                f"{norepinephrine_info['emoji']} {norepinephrine_info['name']} (Stress/Energy)",
                min_value=NEUROTRANSMITTER_MIN,
                max_value=NEUROTRANSMITTER_MAX,
                value=DEFAULT_NEUROTRANSMITTER_VALUE,
                step=NEUROTRANSMITTER_STEP,
                help=norepinephrine_info['help']
            )
        
        with col3:
            serotonin_info = NEUROTRANSMITTER_INFO['serotonin']
            serotonin = st.slider(
                f"{serotonin_info['emoji']} {serotonin_info['name']} (Satisfaction)",
                min_value=NEUROTRANSMITTER_MIN,
                max_value=NEUROTRANSMITTER_MAX,
                value=DEFAULT_NEUROTRANSMITTER_VALUE,
                step=NEUROTRANSMITTER_STEP,
                help=serotonin_info['help']
            )
        
        # Optional modifiers
        st.markdown("**Optional Modifiers:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            oxytocin_info = NEUROTRANSMITTER_INFO['oxytocin']
            oxytocin = st.slider(
                f"{oxytocin_info['emoji']} {oxytocin_info['name']} (Bonding)",
                min_value=NEUROTRANSMITTER_MIN,
                max_value=NEUROTRANSMITTER_MAX,
                value=0.0,
                step=NEUROTRANSMITTER_STEP,
                help=oxytocin_info['help']
            )
        
        with col2:
            endorphins_info = NEUROTRANSMITTER_INFO['endorphins']
            endorphins = st.slider(
                f"{endorphins_info['emoji']} {endorphins_info['name']} (Euphoria)",
                min_value=NEUROTRANSMITTER_MIN,
                max_value=NEUROTRANSMITTER_MAX,
                value=0.0,
                step=NEUROTRANSMITTER_STEP,
                help=endorphins_info['help']
            )
        
        with col3:
            gaba_info = NEUROTRANSMITTER_INFO['gaba']
            gaba = st.slider(
                f"{gaba_info['emoji']} {gaba_info['name']} (Calm)",
                min_value=NEUROTRANSMITTER_MIN,
                max_value=NEUROTRANSMITTER_MAX,
                value=0.0,
                step=NEUROTRANSMITTER_STEP,
                help=gaba_info['help']
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
            render_color_circle(preview_state.hex_color, size=COLOR_CIRCLE_SIZE_PREVIEW)
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


def render_current_state() -> None:
    """Render the last logged emotion."""
    if st.session_state.last_emotion_logged:
        st.subheader("📍 Last Logged")
        state = st.session_state.last_emotion_logged
        emotion = state.get_secondary_emotion()
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            render_color_circle(state.hex_color, size=COLOR_CIRCLE_SIZE_PREVIEW)
        
        with col2:
            st.markdown(f"### {emotion['emoji']} {emotion['label']}")
            st.caption(emotion['description'])
            st.caption(f"Logged: {state.timestamp.strftime('%Y-%m-%d %H:%M')}")
            if state.notes:
                st.write(f"📝 {state.notes}")


def render_history() -> None:
    """Render emotion history."""
    st.subheader("📜 Recent History")
    
    # Get recent states
    recent = st.session_state.emotion_manager.get_recent(days=HISTORY_DAYS)
    
    if not recent:
        st.info("No emotions logged yet. Start by logging how you feel!")
        return
    
    # Display as a list
    for state in recent[:HISTORY_DISPLAY_LIMIT]:
        render_emotion_card(state)
        st.divider()


def render_analytics() -> None:
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
        st.markdown(f"#### Color Trend (Last {TREND_DISPLAY_COUNT} entries)")
        
        cols = st.columns(len(summary['color_trend'][:TREND_DISPLAY_COUNT]))
        for i, color in enumerate(summary['color_trend'][:TREND_DISPLAY_COUNT]):
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