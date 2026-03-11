"""
Social Comparison Safeguards Page

UI for preventing harmful social comparison.

Based on Task 11.2.12 from PHASE_11_INTEGRATION_ROADMAP.md
"""

import streamlit as st


def render_social_page(engine, user_id: str) -> None:
    """
    Render the social comparison safeguards page.
    
    Args:
        engine: SocialSafeguardsEngine instance
        user_id: User ID
    """
    st.markdown("🛡️ Social Comparison Safeguards")
    st.markdown("*Prevent harmful comparison. Focus on YOUR progress.*")
    
    # Stats
    stats = engine.get_stats(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Comparisons", stats["total_events"])
    with col2:
        st.metric("📊 Avg Impact", f"{stats['avg_mood_impact']:.1f}")
    with col3:
        st.metric("🔧 Interventions", stats["interventions_used"])
    with col4:
        st.metric("🏆 Personal Bests", stats["personal_bests"])
    
    st.markdown("---")
    
    # Record comparison
    render_comparison_recorder(engine, user_id)
    
    st.markdown("---")
    
    # Personal bests
    render_personal_bests(engine, user_id)
    
    st.markdown("---")
    
    # Recent events
    render_recent_events(engine, user_id)


def render_comparison_recorder(engine, user_id: str) -> None:
    """Render comparison event recorder."""
    st.markdown("### 🌡️ Check Your Comparison")
    
    from brain.models.social_safeguards import ComparisonType, TriggerSource
    
    col1, col2 = st.columns(2)
    
    with col1:
        comparison_type = st.selectbox(
            "Type of Comparison",
            [c.name for c in ComparisonType]
        )
    
    with col2:
        trigger_source = st.selectbox(
            "Trigger Source",
            [t.name for t in TriggerSource]
        )
    
    trigger_content = st.text_input(
        "What triggered this?",
        placeholder="e.g., Saw friend's vacation photos"
    )
    
    col3, col4 = st.columns(2)
    
    with col3:
        mood_before = st.slider("Mood Before (1-10)", 1, 10, 7)
    
    with col4:
        mood_after = st.slider("Mood After (1-10)", 1, 10, 5)
    
    if st.button("Record Comparison"):
        from brain.models.social_safeguards import ComparisonType, TriggerSource
        
        event = engine.record_comparison(
            user_id=user_id,
            comparison_type=ComparisonType[comparison_type],
            trigger_source=TriggerSource[trigger_source],
            trigger_content=trigger_content,
            mood_before=mood_before,
            mood_after=mood_after
        )
        
        # Show interventions
        interventions = engine.get_interventions(ComparisonType[comparison_type])
        
        st.warning("💡 **Try these interventions:**")
        for i in interventions:
            st.write(f"- {i}")
        
        # Mood impact
        impact = event.impact_score
        if impact < 0:
            st.error(f"Mood dropped by {abs(impact)} points 😔")
        elif impact > 0:
            st.success(f"Mood improved by {impact} points! 🎉")
        else:
            st.info("Mood stayed the same")


def render_personal_bests(engine, user_id: str) -> None:
    """Render personal bests section."""
    st.markdown("### 🏆 Personal Bests")
    st.markdown("*Focus on YOUR progress, not others'*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        metric = st.text_input("Metric (e.g., Running distance)")
    
    with col2:
        value = st.number_input("Value", min_value=0.0)
    
    context = st.text_input("Context", placeholder="e.g., 5k run in under 30 min")
    
    if st.button("Record Personal Best"):
        engine.add_personal_best(
            user_id=user_id,
            metric=metric,
            value=value,
            context=context
        )
        
        st.success(f"New personal best: {value} {metric}! 🏆")


def render_recent_events(engine, user_id: str) -> None:
    """Render recent comparison events."""
    st.markdown("### 📊 Recent Events")
    
    events = engine.get_recent_events(user_id, days=30)
    
    if not events:
        st.info("No comparison events recorded. Great job staying focused!")
        return
    
    for event in reversed(events[-10:]):
        impact_emoji = "📉" if event.impact_score < 0 else "📈" if event.impact_score > 0 else "➡️"
        
        with st.expander(f"{impact_emoji} {event.comparison_type.value} - {event.timestamp.strftime('%m/%d')}"):
            st.write(f"**Trigger:** {event.trigger_content}")
            st.write(f"**Source:** {event.trigger_source.value}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Mood: {event.mood_before} → {event.mood_after}")
            with col2:
                st.write(f"Impact: {event.impact_score:+d}")


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import streamlit as st
    from brain.models.social_safeguards import (
        create_engine, ComparisonType, TriggerSource
    )
    
    st.set_page_config(page_title="Social Safeguards Test")
    
    st.title("🛡️ Social Comparison Test")
    
    engine = create_engine()
    
    # Record comparison
    event = engine.record_comparison(
        user_id="test",
        comparison_type=ComparisonType.UPWARD,
        trigger_source=TriggerSource.SOCIAL_MEDIA,
        trigger_content="Friend got promoted",
        mood_before=7,
        mood_after=4
    )
    print(f"Recorded event: {event.comparison_type.value}")
    print(f"Impact: {event.impact_score}")
    
    # Get interventions
    interventions = engine.get_interventions(ComparisonType.UPWARD)
    print(f"Interventions: {len(interventions)}")
    
    # Add personal best
    pb = engine.add_personal_best(
        user_id="test",
        metric="Running",
        value=5.0,
        context="5k in 25 min"
    )
    print(f"Added PB: {pb.metric}")
    
    # Stats
    stats = engine.get_stats("test")
    print(f"Stats: {stats}")
    
    st.write("Test passed!")
