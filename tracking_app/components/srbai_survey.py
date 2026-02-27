"""
SRBAI Survey Component - Habit automaticity measurement.

Provides UI components for:
- SRBAI 4-question survey
- Automaticity badge display
- Survey history tracking

Usage:
    from tracking_app.components.srbai_survey import render_srbai_survey
    
    render_srbai_survey(storage, habit_id, user_id)
"""
import streamlit as st
from typing import Dict, Optional, Any, List
from datetime import date

# SRBAI Questions
SRBAI_QUESTIONS = [
    {
        "id": "q1",
        "text": "I do this automatically",
        "description": "Behavior happens without conscious decision"
    },
    {
        "id": "q2",
        "text": "I do this without thinking",
        "description": "Behavior requires minimal mental effort"
    },
    {
        "id": "q3",
        "text": "I start doing this without realizing",
        "description": "Behavior initiation is unconscious"
    },
    {
        "id": "q4",
        "text": "It would be difficult not to do this",
        "description": "Behavior has become necessary/expected"
    }
]

# Habit strength indicators
HABIT_STRENGTH_INFO = {
    "strong": {
        "emoji": "💪",
        "label": "Strong Habit",
        "color": "#4CAF50",
        "description": "This habit is well-established!"
    },
    "moderate": {
        "emoji": "👍",
        "label": "Moderate Habit",
        "color": "#8BC34A",
        "description": "Good progress, keep going!"
    },
    "developing": {
        "emoji": "🌱",
        "label": "Developing",
        "color": "#FFC107",
        "description": "Building momentum"
    },
    "weak": {
        "emoji": "🔧",
        "label": "Weak",
        "color": "#FF9800",
        "description": "Needs more consistency"
    },
    "not_a_habit": {
        "emoji": "🆕",
        "label": "Not a Habit Yet",
        "color": "#F44336",
        "description": "Keep practicing!"
    }
}


def render_srbai_survey(
    storage: Any,
    habit_id: str,
    user_id: str = "",
    on_submit: Optional[callable] = None
) -> None:
    """
    Render SRBAI survey.

    Args:
        storage: Storage instance
        habit_id: Habit ID
        user_id: User ID
        on_submit: Optional callback on survey submission
    """
    # Check if survey should be shown
    if not storage.should_show_srbai_survey(habit_id):
        return

    # Check if already taken recently
    latest = storage.get_latest_srbai_result(habit_id)
    if latest:
        # Show result instead
        render_automaticity_badge(storage, habit_id)
        return

    # Survey form
    with st.form("srbai_survey_form"):
        st.markdown("**📋 Habit Automaticity Survey**")
        st.caption("Rate how automatic this habit has become")

        # 4 questions with 1-7 scale
        responses = {}
        for q in SRBAI_QUESTIONS:
            responses[q["id"]] = st.slider(
                q["text"],
                min_value=1,
                max_value=7,
                value=4,
                help=q["description"],
                key=f"srbai_{q['id']}_{habit_id}"
            )

        submitted = st.form_submit_button("Submit Survey", type="primary")

        if submitted:
            # Submit survey
            result = storage.submit_srbai_survey(
                habit_id=habit_id,
                user_id=user_id,
                q1=responses["q1"],
                q2=responses["q2"],
                q3=responses["q3"],
                q4=responses["q4"]
            )

            # Show result
            st.success("✅ Survey submitted!")
            _display_survey_result(result)

            if on_submit:
                on_submit(result)


def render_automaticity_badge(
    storage: Any,
    habit_id: str,
    show_history: bool = False
) -> None:
    """
    Render automaticity badge.

    Args:
        storage: Storage instance
        habit_id: Habit ID
        show_history: Whether to show survey history
    """
    latest = storage.get_latest_srbai_result(habit_id)

    if not latest:
        return

    strength = latest["habit_strength"]
    info = HABIT_STRENGTH_INFO.get(strength, HABIT_STRENGTH_INFO["not_a_habit"])

    # Display badge
    score = latest["automaticity_score"]

    st.markdown(
        f"""
        <div style="
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid {info['color']};
            background: rgba(255,255,255,0.05);
            margin: 1rem 0;
        ">
            <div style="font-size: 1.5rem; font-weight: bold;">
                {info['emoji']} {info['label']}
            </div>
            <div style="font-size: 1.2rem; color: {info['color']}; margin: 0.5rem 0;">
                Score: {score:.1f}/7.0
            </div>
            <div style="font-size: 0.9rem; color: gray;">
                {info['description']}
            </div>
            <div style="font-size: 0.8rem; color: gray; margin-top: 0.5rem;">
                📅 Survey date: {latest['survey_date']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Show history if requested
    if show_history:
        _render_survey_history(storage, habit_id)


def _display_survey_result(result: Dict[str, Any]) -> None:
    """
    Display survey result.

    Args:
        result: Survey result dict
    """
    strength = result["habit_strength"]
    info = HABIT_STRENGTH_INFO.get(strength, HABIT_STRENGTH_INFO["not_a_habit"])

    st.success(
        f"""
        **{info['emoji']} {info['label']}**
        
        Automaticity Score: **{result['automaticity_score']:.1f}/7.0**
        
        {info['description']}
        """
    )

    if result["is_habit_formed"]:
        st.balloons()


def _render_survey_history(
    storage: Any,
    habit_id: str
) -> None:
    """
    Render survey history.

    Args:
        storage: Storage instance
        habit_id: Habit ID
    """
    history = storage.get_srbai_history(habit_id, limit=5)

    if not history:
        return

    with st.expander("📜 Survey History"):
        for result in history:
            strength = result["habit_strength"]
            info = HABIT_STRENGTH_INFO.get(strength, HABIT_STRENGTH_INFO["not_a_habit"])

            st.markdown(
                f"**{result['survey_date']}** - "
                f"{info['emoji']} {info['label']} "
                f"({result['automaticity_score']:.1f})"
            )


def render_survey_prompt(
    storage: Any,
    habit_id: str,
    habit_name: str
) -> None:
    """
    Render survey prompt for eligible habits.

    Args:
        storage: Storage instance
        habit_id: Habit ID
        habit_name: Habit name
    """
    if not storage.should_show_srbai_survey(habit_id):
        return

    latest = storage.get_latest_srbai_result(habit_id)
    if latest:
        return

    # Show prompt
    st.info(
        f"""
        **📊 Measure Your Progress!**
        
        You've been tracking **{habit_name}** for a while. 
        Take the 2-minute survey to see how automatic it's become!
        """
    )

    if st.button(
        "📋 Take Survey",
        key=f"take_survey_{habit_id}",
        type="primary"
    ):
        st.session_state[f"show_survey_{habit_id}"] = True


def get_habit_strength_emoji(strength: str) -> str:
    """
    Get emoji for habit strength.

    Args:
        strength: Strength level

    Returns:
        Emoji string
    """
    info = HABIT_STRENGTH_INFO.get(strength, HABIT_STRENGTH_INFO["not_a_habit"])
    return info["emoji"]


def get_habit_strength_color(strength: str) -> str:
    """
    Get color for habit strength.

    Args:
        strength: Strength level

    Returns:
        Color hex code
    """
    info = HABIT_STRENGTH_INFO.get(strength, HABIT_STRENGTH_INFO["not_a_habit"])
    return info["color"]


__all__ = [
    "render_srbai_survey",
    "render_automaticity_badge",
    "render_survey_prompt",
    "get_habit_strength_emoji",
    "get_habit_strength_color",
]
