"""
Digital Coach Page - Streamlit UI

Provides the user interface for the Digital Coach feature.
Allows users to view interventions, configure personality, and track history.

Usage:
    streamlit run tracking_app/pages/digital_coach.py
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Import coach components
from brain.ai.coach import (
    DigitalCoach,
    CoachPersonality,
    PersonalityConfig,
    UserState,
    Intervention,
    RecoveryMode,
    RecoveryModeManager
)
from brain.ai.coach.personality import (
    InterventionFrequency,
    ToneStyle,
    get_default_config
)


def init_session_state():
    """Initialize session state variables."""
    if 'coach' not in st.session_state:
        st.session_state.coach = None
    
    if 'coach_enabled' not in st.session_state:
        st.session_state.coach_enabled = True
    
    if 'personality_config' not in st.session_state:
        st.session_state.personality_config = get_default_config("balanced")
    
    if 'active_interventions' not in st.session_state:
        st.session_state.active_interventions = []
    
    if 'current_state' not in st.session_state:
        st.session_state.current_state = None
    
    if 'recovery_mode_manager' not in st.session_state:
        st.session_state.recovery_mode_manager = RecoveryModeManager()


def get_mock_user_data() -> Dict[str, Any]:
    """
    Get mock user data for demonstration.
    
    In production, this would fetch real data from the database.
    """
    return {
        "habits": [
            {
                "id": "habit_1",
                "name": "Morning Exercise",
                "streak": 12,
                "best_streak": 30,
                "completion_rate": 0.85,
                "streak_broken_recently": False
            },
            {
                "id": "habit_2",
                "name": "Meditation",
                "streak": 5,
                "best_streak": 21,
                "completion_rate": 0.70,
                "streak_broken_recently": True
            },
            {
                "id": "habit_3",
                "name": "Reading",
                "streak": 0,
                "best_streak": 14,
                "completion_rate": 0.40,
                "streak_broken_recently": True
            }
        ],
        "tasks": [
            {"id": "task_1", "title": "Complete project", "completed": True},
            {"id": "task_2", "title": "Review code", "completed": False},
            {"id": "task_3", "title": "Write docs", "completed": False}
        ],
        "health": {
            "sleep": [7.5, 6.0, 7.0, 5.5, 6.5, 7.0, 6.0],
            "mood": [4, 3, 4, 3, 3, 4, 3]
        },
        "goals": [
            {"id": "goal_1", "name": "Run 100km", "progress": 75, "recently_completed": False},
            {"id": "goal_2", "name": "Read 12 books", "progress": 40, "recently_completed": False}
        ],
        "activity_log": [
            {"timestamp": (datetime.now() - timedelta(hours=i)).isoformat()}
            for i in range(10)
        ]
    }


def render_sidebar():
    """Render the sidebar with coach settings."""
    with st.sidebar:
        st.header("⚙️ Coach Settings")
        
        # Enable/Disable toggle
        enabled = st.toggle(
            "Coach Enabled",
            value=st.session_state.coach_enabled,
            help="Turn the Digital Coach on or off"
        )
        st.session_state.coach_enabled = enabled
        
        if not enabled:
            st.info("Coach is paused. Your data is still being tracked.")
            return
        
        st.divider()
        
        # Personality preset
        st.subheader("Personality Preset")
        preset = st.selectbox(
            "Choose a style",
            options=["balanced", "intensive", "minimal", "gentle", "gamer"],
            index=0,
            help="Select a pre-configured coaching style"
        )
        
        if st.button("Apply Preset"):
            st.session_state.personality_config = get_default_config(preset)
            st.success(f"Applied '{preset}' personality!")
        
        st.divider()
        
        # Custom personality settings
        st.subheader("Custom Settings")
        
        personality_type = st.select_slider(
            "Coaching Style",
            options=["encouraging", "gentle", "analytical", "direct", "stern", "playful"],
            value=st.session_state.personality_config.personality.value
        )
        
        tone = st.select_slider(
            "Tone",
            options=["casual", "warm", "neutral", "formal", "motivational"],
            value=st.session_state.personality_config.tone.value
        )
        
        frequency = st.select_slider(
            "Intervention Frequency",
            options=["minimal", "low", "normal", "high", "intensive"],
            value=st.session_state.personality_config.intervention_frequency.value
        )
        
        use_emojis = st.checkbox("Use Emojis", value=st.session_state.personality_config.use_emojis)
        use_gamification = st.checkbox("Gamification Language", value=st.session_state.personality_config.use_gamification)
        
        if st.button("Save Settings"):
            config = PersonalityConfig(
                personality=CoachPersonality(personality_type),
                tone=ToneStyle(tone),
                intervention_frequency=InterventionFrequency(frequency),
                use_emojis=use_emojis,
                use_gamification=use_gamification
            )
            st.session_state.personality_config = config
            st.success("Settings saved!")


def render_status_dashboard():
    """Render the main status dashboard."""
    st.header("📊 Coach Status")
    
    # Get current state
    user_data = get_mock_user_data()
    
    if st.session_state.coach is None:
        st.session_state.coach = DigitalCoach(st.session_state.personality_config)
    
    state = st.session_state.coach.get_state(user_data)
    st.session_state.current_state = state
    
    # Status metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        burnout_color = "🟢" if state.burnout_risk < 31 else "🟡" if state.burnout_risk < 51 else "🔴"
        st.metric(
            "Burnout Risk",
            f"{burnout_color} {state.burnout_risk}%",
            delta=None
        )
    
    with col2:
        streak_color = "🟢" if state.streak_health >= 70 else "🟡" if state.streak_health >= 50 else "🔴"
        st.metric(
            "Streak Health",
            f"{streak_color} {state.streak_health}%",
            delta=None
        )
    
    with col3:
        engagement_emoji = {
            "dormant": "😴",
            "low": "😐",
            "normal": "🙂",
            "high": "😊",
            "intensive": "🤩"
        }
        emoji = engagement_emoji.get(state.engagement_level.value, "❓")
        st.metric(
            "Engagement",
            f"{emoji} {state.engagement_level.value.title()}"
        )
    
    with col4:
        mode_manager = st.session_state.recovery_mode_manager
        current_mode = mode_manager.determine_mode(state)
        mode_emoji = {
            "push": "🚀",
            "maintenance": "⚡",
            "recovery": "🧘",
            "crisis": "🚨"
        }
        emoji = mode_emoji.get(current_mode.value, "❓")
        st.metric(
            "Coaching Mode",
            f"{emoji} {current_mode.value.title()}"
        )
    
    # Trends
    st.subheader("📈 Trends")
    
    trend_col1, trend_col2 = st.columns(2)
    
    with trend_col1:
        mood_trend = state.mood_trend
        mood_icon = "📈" if mood_trend == "improving" else "📉" if mood_trend == "declining" else "➡️"
        st.info(f"{mood_icon} **Mood:** {mood_trend.title()}")
    
    with trend_col2:
        sleep_trend = state.sleep_trend
        sleep_icon = "📈" if sleep_trend == "improving" else "📉" if sleep_trend == "declining" else "➡️"
        st.info(f"{sleep_icon} **Sleep:** {sleep_trend.title()}")


def render_interventions():
    """Render active interventions."""
    st.header("🎯 Active Interventions")
    
    if not st.session_state.coach_enabled:
        st.info("Coach is paused. Enable in settings to receive interventions.")
        return
    
    # Check for new interventions
    if st.button("🔄 Check for Interventions", type="primary"):
        user_data = get_mock_user_data()
        interventions = st.session_state.coach.check(user_data)
        st.session_state.active_interventions = interventions
        
        if interventions:
            st.success(f"Found {len(interventions)} intervention(s)!")
        else:
            st.info("No new interventions needed. Keep up the good work!")
    
    # Display active interventions
    interventions = st.session_state.active_interventions
    
    if not interventions:
        st.info("No active interventions. Click 'Check for Interventions' to analyze your state.")
        return
    
    for i, intervention in enumerate(interventions):
        suggestion = intervention.suggestion
        
        # Determine container style based on priority
        priority_colors = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢", 5: "🔵"}
        priority_icon = priority_colors.get(suggestion.priority, "⚪")
        
        with st.container():
            st.markdown(f"### {priority_icon} {suggestion.title}")
            st.write(suggestion.message)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if suggestion.actionable:
                    if st.button(f"✓ {suggestion.action_text}", key=f"action_{i}"):
                        st.session_state.coach.acknowledge(intervention.id, action_taken=True)
                        st.success("Action recorded!")
            
            with col2:
                if st.button("Dismiss", key=f"dismiss_{i}"):
                    st.session_state.coach.dismiss(intervention.id)
                    st.rerun()
            
            with col3:
                st.caption(f"Type: {suggestion.action_type}")
            
            st.divider()


def render_habits_assessment():
    """Render habits assessment breakdown."""
    st.header("📋 Habits Assessment")
    
    state = st.session_state.current_state
    if not state or not state.habits_assessment:
        st.info("Check for interventions to see habits assessment.")
        return
    
    habits = state.habits_assessment
    
    for habit_id, habit_data in habits.items():
        health = habit_data.get("health", "unknown")
        streak = habit_data.get("streak", 0)
        
        health_colors = {
            "established": "🟢",
            "developing": "🟡",
            "building": "🟠",
            "needs_attention": "🔴"
        }
        
        icon = health_colors.get(health, "⚪")
        
        with st.expander(f"{icon} {habit_data.get('name', 'Unknown')} - Streak: {streak} days"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Current Streak", streak)
                st.metric("Best Streak", habit_data.get("best_streak", 0))
            
            with col2:
                completion = habit_data.get("completion_rate", 0) * 100
                st.metric("Completion Rate", f"{completion:.0f}%")
                st.metric("Status", health.replace("_", " ").title())


def render_mode_info():
    """Render recovery mode information."""
    st.header("🧘 Coaching Mode")
    
    state = st.session_state.current_state
    if not state:
        st.info("Check for interventions to see coaching mode.")
        return
    
    mode_manager = st.session_state.recovery_mode_manager
    current_mode = mode_manager.current_mode
    mode_config = mode_manager.get_mode_config()
    
    # Mode description
    mode_message = mode_manager.get_mode_message(current_mode)
    st.info(mode_message)
    
    # Mode details
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Target Multiplier", f"{mode_config.habit_target_multiplier * 100:.0f}%")
        st.metric("Max Daily Interventions", mode_config.max_daily_interventions)
    
    with col2:
        st.metric("Celebrations", "On" if mode_config.show_celebrations else "Off")
        st.metric("New Habits", "Allowed" if mode_config.allow_new_habits else "Paused")
    
    # Focus areas
    st.subheader("Focus Areas")
    for area in mode_config.focus_areas:
        st.markdown(f"- {area.title()}")


def render_history():
    """Render intervention history."""
    st.header("📜 History")
    
    if st.session_state.coach is None:
        st.info("No history available yet.")
        return
    
    history = st.session_state.coach.get_history(limit=10)
    
    if not history:
        st.info("No intervention history yet.")
        return
    
    for record in history:
        suggestion = record.suggestion
        
        with st.expander(f"{suggestion.title} - {record.created_at.strftime('%Y-%m-%d %H:%M')}"):
            st.write(suggestion.message)
            
            status = "✓ Completed" if record.action_taken else "⏸ Dismissed" if record.dismissed else "⏳ Pending"
            st.caption(f"Status: {status}")


def main():
    """Main page entry point."""
    st.set_page_config(
        page_title="Digital Coach - Veryfyn",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 Digital Coach")
    st.markdown("Your personal AI coach that monitors your progress and provides proactive guidance.")
    
    # Initialize
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Interventions", "Habits", "Mode"])
    
    with tab1:
        render_status_dashboard()
    
    with tab2:
        render_interventions()
    
    with tab3:
        render_habits_assessment()
    
    with tab4:
        render_mode_info()
    
    # Footer
    st.divider()
    st.caption("Digital Coach uses your tracking data to provide personalized guidance. All analysis happens locally.")


if __name__ == "__main__":
    main()