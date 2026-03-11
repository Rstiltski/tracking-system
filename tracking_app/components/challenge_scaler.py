"""
Challenge Scaler Component

UI for challenge difficulty adjustment based on fixed mindset detection.

Based on Task 11.1.7 from PHASE_11_INTEGRATION_ROADMAP.md

Complements Growth Mindset interventions - automatically scales difficulty
when users show signs of struggle.
"""

import streamlit as st
from typing import Optional


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_difficulty_selector(
    current_level: int,
    on_change=None,
    key: str = "difficulty_selector"
) -> int:
    """
    Render a difficulty level selector.
    
    Args:
        current_level: Current difficulty level (1-6)
        on_change: Callback when level changes
        key: Streamlit component key
        
    Returns:
        Selected difficulty level
    """
    levels = {
        1: "🟢 Very Easy",
        2: "🟢 Easy", 
        3: "🟡 Moderate",
        4: "🟠 Challenging",
        5: "🔴 Very Hard",
        6: "🔴 Extreme"
    }
    
    level_labels = [f"{v} - {k}" for k, v in levels.items()]
    
    selected = st.selectbox(
        "🏋️ Challenge Difficulty",
        options=list(levels.keys()),
        format_func=lambda x: levels[x],
        index=current_level - 1,
        key=key,
        on_change=on_change
    )
    
    return selected


def render_challenge_indicator(
    level: int,
    completion_rate: float = 0.0,
    show_recommendation: bool = False,
    recommended_level: Optional[int] = None
) -> None:
    """
    Render a visual challenge level indicator.
    
    Args:
        level: Current difficulty level (1-6)
        completion_rate: User's completion rate (0.0 to 1.0)
        show_recommendation: Whether to show level recommendation
        recommended_level: Recommended level if struggling
    """
    # Color based on level
    colors = {
        1: "🟢",
        2: "🟢", 
        3: "🟡",
        4: "🟠",
        5: "🔴",
        6: "🔴"
    }
    
    level_names = {
        1: "Very Easy",
        2: "Easy", 
        3: "Moderate",
        4: "Challenging",
        5: "Very Hard",
        6: "Extreme"
    }
    
    # Display current level
    st.markdown(f"### Current Level: {colors.get(level, '⚪')} {level_names.get(level, 'Unknown')}")
    
    # Progress bar
    if completion_rate > 0:
        st.progress(completion_rate)
        st.caption(f"Completion Rate: {completion_rate * 100:.1f}%")
    
    # Show recommendation if applicable
    if show_recommendation and recommended_level:
        if recommended_level < level:
            st.info(f"💡 **Recommendation:** Consider lowering to {level_names.get(recommended_level, 'Unknown')} (Level {recommended_level})")
        elif recommended_level > level:
            st.success(f"🚀 **Ready to level up!** Try {level_names.get(recommended_level, 'Unknown')} (Level {recommended_level})")
        else:
            st.success("✅ **Perfect difficulty!** You're in the sweet spot.")


def render_fixed_mindset_alert(
    triggers: list,
    new_level: Optional[int] = None
) -> None:
    """
    Render an alert when fixed mindset is detected.
    
    Args:
        triggers: List of detected triggers
        new_level: Recommended new difficulty level
    """
    if not triggers:
        return
    
    # Warning message
    st.warning("⚠️ **You're showing signs of struggling.**")
    
    # Explain triggers
    trigger_descriptions = {
        "low_completion": "📉 Low completion rate",
        "consecutive_failures": "❌ Multiple consecutive failures",
        "repeated_skip": "⏭️ Skipped several times",
        "fixed_language": "💭 Self-defeating thoughts detected"
    }
    
    for trigger in triggers:
        desc = trigger_descriptions.get(trigger, trigger)
        st.write(f"- {desc}")
    
    # Show level recommendation
    if new_level:
        level_names = {
            1: "Very Easy",
            2: "Easy", 
            3: "Moderate",
            4: "Challenging"
        }
        
        st.info(f"🔄 **Auto-adjusting:** Difficulty lowered to **{level_names.get(new_level, 'Level ' + str(new_level))}**")


def render_encouragement() -> None:
    """Render an encouragement message."""
    messages = [
        "🌱 Growth takes time. Every step counts!",
        "💪 You're stronger than you think!",
        "🎯 Small progress is still progress!",
        "🏆 Consistency beats intensity!",
        "✨ You're building a better you, one day at a time!",
        "🌟 Mistakes are proof that you're trying!",
        "🚀 Every expert was once a beginner!",
    ]
    
    import random
    message = random.choice(messages)
    
    st.success(message)


def render_level_up_celebration(
    new_level: int
) -> None:
    """
    Render a celebration when user levels up.
    
    Args:
        new_level: The new achieved level
    """
    level_names = {
        2: "Easy",
        3: "Moderate", 
        4: "Challenging",
        5: "Very Hard",
        6: "Extreme"
    }
    
    st.balloons()
    
    st.markdown(f"""
    ### 🎉 Level Up! 🎉
    
    You've reached **{level_names.get(new_level, 'Level ' + str(new_level))}**!
    
    Keep pushing your boundaries! 💪
    """)


# =============================================================================
# MAIN COMPONENT
# =============================================================================

def render_challenge_scaler(
    challenge_id: str,
    current_level: int = 3,
    completion_rate: float = 0.5,
    detected_triggers: Optional[list] = None,
    recommended_level: Optional[int] = None
) -> Optional[int]:
    """
    Main challenge scaler component.
    
    Args:
        challenge_id: ID of the challenge
        current_level: Current difficulty level (1-6)
        completion_rate: User's completion rate (0.0 to 1.0)
        detected_triggers: List of detected fixed mindset triggers
        recommended_level: System recommended level
        
    Returns:
        New level if changed, None otherwise
    """
    st.markdown("### 🎯 Challenge Scaler")
    
    # Show fixed mindset alert if triggers detected
    if detected_triggers:
        render_fixed_mindset_alert(detected_triggers, recommended_level)
    
    # Show difficulty selector
    new_level = render_difficulty_selector(
        current_level=current_level,
        key=f"challenge_scaler_{challenge_id}"
    )
    
    # Show encouragement if struggling
    if completion_rate < 0.4:
        render_encouragement()
    
    # Show celebration if level up
    if new_level > current_level:
        render_level_up_celebration(new_level)
    
    return new_level


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import streamlit as st
    
    st.set_page_config(page_title="Challenge Scaler Test")
    
    st.title("🎯 Challenge Scaler Component Test")
    
    # Test the component
    result = render_challenge_scaler(
        challenge_id="test_habit",
        current_level=3,
        completion_rate=0.35,
        detected_triggers=["low_completion", "repeated_skip"],
        recommended_level=2
    )
    
    if result:
        st.write(f"New level selected: {result}")
