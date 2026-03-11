"""
Dopamine Menu Component

UI for displaying and interacting with the personalized dopamine menu.

Based on Task 11.2.6 from PHASE_11_INTEGRATION_ROADMAP.md
"""

import streamlit as st
from typing import Dict, List, Optional


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_category_header(category: str, emoji: str) -> None:
    """Render a category header."""
    st.markdown(f"### {emoji} {category}")


def render_activity_card(
    activity_name: str,
    duration: int,
    intensity: str,
    completed: int = 0
) -> None:
    """
    Render an activity card.
    
    Args:
        activity_name: Name of the activity
        duration: Duration in minutes
        intensity: Intensity level
        completed: Times completed
    """
    # Intensity color coding
    intensity_colors = {
        "calm": "🟢",
        "boost": "🟡",
        "energy": "🟠",
        "accomplishment": "🔵",
        "connection": "🟣",
        "reflection": "⚪",
        "reset": "🔷",
        "flow": "🌈",
        "growth": "🌱",
        "learning": "📚",
        "renewal": "🍃",
        "purpose": "⭐",
    }
    
    emoji = intensity_colors.get(intensity, "⚪")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"**{emoji} {activity_name}**")
        st.caption(f"⏱️ {duration} min | {intensity.title()}")
    
    with col2:
        if completed > 0:
            st.write(f"✅ Done {completed}x")


def render_dopamine_menu(
    user_id: str,
    engine,
    show_craving_form: bool = True
) -> None:
    """
    Render the full dopamine menu.
    
    Args:
        user_id: User ID
        engine: DopamineMenuEngine instance
        show_craving_form: Whether to show craving input form
    """
    st.markdown("## 🧬 Dopamine Menu")
    
    # Craving form
    if show_craving_form:
        with st.expander("😫 Feeling a craving?", expanded=False):
            trigger = st.text_input("What's triggering the craving?", placeholder="e.g., Boredom, Stress, Social media...")
            intensity = st.slider("Craving intensity", 1, 10, 5)
            
            if st.button("Get Activity Suggestion"):
                # Find suitable activity
                suggested = engine.suggest_activity(user_id, available_time=30)
                if suggested:
                    st.success(f"Try this: **{suggested.name}** ({suggested.duration_minutes} min)")
                    
                    # Record craving
                    engine.record_craving(user_id, trigger, intensity, suggested.name)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        satisfaction = st.slider("How satisfied?", 1, 10, 7, key="sat")
                        if st.button("Mark Complete"):
                            engine.complete_activity(user_id, suggested.name, satisfaction)
                            st.balloons()
                            st.success("Great job! 🎉")
    
    st.markdown("---")
    
    # Get menu summary
    summary = engine.get_menu_summary(user_id)
    
    # Display by category
    categories = [
        ("⚡ Quick Hits (0-5 min)", "quick_hits"),
        ("🌊 Medium Boost (5-20 min)", "medium_boost"),
        ("🎯 Deep Satisfaction (20+ min)", "deep_satisfaction"),
    ]
    
    for header, cat_key in categories:
        render_category_header(header, "")
        
        activities = engine.get_activities_by_category(
            user_id, 
            getattr(__import__('brain.models.dopamine_menu', fromlist=['DopamineCategory']).DopamineCategory, cat_key)
        )
        
        for activity in activities:
            render_activity_card(
                activity.name,
                activity.duration_minutes,
                activity.intensity,
                activity.times_completed
            )
        
        st.markdown("")  # Spacing


def render_craving_tracker(
    user_id: str,
    engine
) -> None:
    """
    Render craving history tracker.
    
    Args:
        user_id: User ID
        engine: DopamineMenuEngine instance
    """
    menu = engine.get_or_create_menu(user_id)
    
    if not menu.craving_history:
        st.info("No cravings recorded yet. Use the menu above when you feel a craving!")
        return
    
    st.markdown("### 📊 Craving History")
    
    for craving in reversed(menu.craving_history[-10:]):  # Last 10
        status = "✅ Satisfied" if craving.activity_completed else "❌ Not addressed"
        
        st.write(f"**{craving.timestamp.strftime('%H:%M')}** - {craving.trigger[:30]}")
        st.caption(f"Intensity: {craving.intensity}/10 | {status}")


def render_intensity_filter(
    engine,
    user_id: str,
    current_filter: str = "any"
) -> List:
    """
    Render intensity filter and return filtered activities.
    
    Args:
        engine: DopamineMenuEngine instance
        user_id: User ID
        current_filter: Current filter value
        
    Returns:
        Filtered list of activities
    """
    intensities = ["any", "calm", "boost", "energy", "accomplishment", "connection"]
    
    selected = st.selectbox(
        "🎨 Filter by feeling",
        intensities,
        index=intensities.index(current_filter) if current_filter in intensities else 0
    )
    
    if selected == "any":
        return engine.get_or_create_menu(user_id).activities
    else:
        return engine.get_activities_by_intensity(user_id, selected)


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import streamlit as st
    from brain.models.dopamine_menu import create_engine, DopamineCategory
    
    st.set_page_config(page_title="Dopamine Menu Test")
    
    st.title("🧬 Dopamine Menu Component Test")
    
    # Create engine
    engine = create_engine()
    user_id = "test_user"
    
    # Show menu
    render_dopamine_menu(user_id, engine)
    
    st.markdown("---")
    
    # Show tracker
    render_craving_tracker(user_id, engine)
