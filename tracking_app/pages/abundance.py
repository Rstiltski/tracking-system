"""
Abundance Mindset Page

UI for countering scarcity thinking and building abundance.

Based on Task 11.2.5 from PHASE_11_INTEGRATION_ROADMAP.md
"""

import streamlit as st


def render_abundance_page(engine, user_id: str) -> None:
    """
    Render the abundance mindset page.
    
    Args:
        engine: ScarcityEngine instance
        user_id: User ID
    """
    st.markdown("� abundance Mindset")
    st.markdown("*Counter scarcity thinking. Build abundance.*")
    
    # Stats
    stats = engine.get_stats(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Scarcity Thoughts", stats["total_thoughts"])
    with col2:
        st.metric("✅ Resolved", stats["resolved"])
    with col3:
        st.metric("📈 Resolution Rate", f"{stats['resolution_rate']*100:.0f}%")
    with col4:
        st.metric("🌟 Practices", stats["practices_completed"])
    
    st.markdown("---")
    
    # Record scarcity thought
    render_thought_recorder(engine, user_id)
    
    st.markdown("---")
    
    # Abundance practice
    render_practice_logger(engine, user_id)
    
    st.markdown("---")
    
    # Recent thoughts
    render_recent_thoughts(engine, user_id)


def render_thought_recorder(engine, user_id: str) -> None:
    """Render scarcity thought recorder."""
    st.markdown("### 🌱 Reframe Scarcity Thought")
    
    from brain.models.scarcity import ScarcityTrigger
    
    col1, col2 = st.columns(2)
    
    with col1:
        trigger = st.selectbox(
            "What's triggering scarcity?",
            [t.name for t in ScarcityTrigger]
        )
    
    with col2:
        intensity = st.slider("Intensity (1-10)", 1, 10, 5)
    
    thought = st.text_input(
        "Your scarcity thought",
        placeholder="e.g., I don't have enough money for this"
    )
    
    if st.button("Record Thought"):
        from brain.models.scarcity import ScarcityTrigger
        
        thought_obj = engine.record_thought(
            user_id=user_id,
            trigger=ScarcityTrigger[trigger],
            thought=thought,
            intensity=intensity
        )
        
        # Show reframe
        if thought_obj.reframe:
            st.success(f"💡 **Reframe:** {thought_obj.reframe}")
        
        # Show suggestions
        suggestions = engine.get_abundance_suggestions(ScarcityTrigger[trigger])
        
        st.markdown("**Try these:**")
        for s in suggestions:
            st.write(f"- {s}")
        
        # Resolution
        with st.expander("Apply reframe?"):
            note = st.text_input("How did you reframe it?")
            if st.button("Mark Resolved"):
                engine.apply_reframe(thought_obj.id, note)
                st.success("Thought resolved! 🌟")


def render_practice_logger(engine, user_id: str) -> None:
    """Render abundance practice logger."""
    st.markdown("### 🌟 Log Abundance Practice")
    
    practice_types = [
        "Gratitude for non-material things",
        "Creative problem-solving",
        "Generosity act",
        "Visualization",
        "Affirmation",
        "Resource finding"
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        ptype = st.selectbox("Practice Type", practice_types)
    
    with col2:
        impact = st.slider("Impact (1-5)", 1, 5, 3)
    
    description = st.text_area(
        "Description",
        placeholder="What did you do?"
    )
    
    if st.button("Log Practice"):
        engine.log_practice(
            user_id=user_id,
            practice_type=ptype,
            description=description,
            impact_score=impact
        )
        
        st.success("Practice logged! 🌟")


def render_recent_thoughts(engine, user_id: str) -> None:
    """Render recent scarcity thoughts."""
    st.markdown("### 📝 Recent Thoughts")
    
    thoughts = engine.get_thoughts(user_id, days=30)
    
    if not thoughts:
        st.info("No scarcity thoughts recorded. Great job!")
        return
    
    for thought in reversed(thoughts[-10:]):
        status = "✅" if thought.resolved else "⏳"
        
        with st.expander(f"{status} {thought.trigger.value} - {thought.timestamp.strftime('%m/%d')}"):
            st.write(f"**Thought:** {thought.thought}")
            st.caption(f"Intensity: {thought.intensity}/10")
            
            if thought.reframe:
                st.write(f"💡 **Reframe:** {thought.reframe}")
            
            if thought.resolved:
                st.success(f"Resolved: {thought.resolution_note}")


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import streamlit as st
    from brain.models.scarcity import create_engine, ScarcityTrigger
    
    st.set_page_config(page_title="Abundance Test")
    
    st.title("🌱 Abundance Mindset Test")
    
    engine = create_engine()
    
    # Record thought
    thought = engine.record_thought(
        user_id="test",
        trigger=ScarcityTrigger.MONEY,
        thought="I can't afford this course",
        intensity=7
    )
    print(f"Recorded: {thought.thought}")
    print(f"Reframe: {thought.reframe}")
    
    # Log practice
    engine.log_practice(
        user_id="test",
        practice_type="Gratitude",
        description="Grateful for my health",
        impact_score=5
    )
    
    # Stats
    stats = engine.get_stats("test")
    print(f"Stats: {stats}")
    
    # Suggestions
    suggestions = engine.get_abundance_suggestions(ScarcityTrigger.MONEY)
    print(f"Suggestions: {suggestions}")
    
    st.write("Test passed!")
