"""
Gratitude & Kindness Page

UI for gratitude and kindness logging.

Based on Task 11.2.10 from PHASE_11_INTEGRATION_ROADMAP.md
"""

import streamlit as st


def render_gratitude_page(engine, user_id: str) -> None:
    """
    Render the gratitude page.
    
    Args:
        engine: GratitudeEngine instance
        user_id: User ID
    """
    st.markdown("🙏 Gratitude & Kindness")
    st.markdown("*Cultivate gratitude and spread kindness to beat the loneliness epidemic.*")
    
    # Stats
    stats = engine.get_stats(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Gratitude Entries", stats["total_entries"])
    with col2:
        st.metric("🔥 Streak", f"{stats['streak']} days")
    with col3:
        st.metric("💚 Kindness Acts", stats["kindness_count"])
    with col4:
        st.metric("⭐ Avg Impact", f"{stats['avg_impact']:.1f}")
    
    st.markdown("---")
    
    # Two columns: Gratitude and Kindness
    col1, col2 = st.columns(2)
    
    with col1:
        render_gratitude_logger(engine, user_id)
    
    with col2:
        render_kindness_logger(engine, user_id)
    
    st.markdown("---")
    
    # Recent entries
    render_recent_entries(engine, user_id)


def render_gratitude_logger(engine, user_id: str) -> None:
    """Render gratitude logging form."""
    st.markdown("### 🙏 What are you grateful for?")
    
    from brain.models.gratitude import GratitudeCategory
    
    category = st.selectbox(
        "Category",
        [c.name for c in GratitudeCategory]
    )
    
    text = st.text_area(
        "I am grateful for...",
        placeholder="Today I'm grateful for..."
    )
    
    impact = st.slider("How much does this mean to you?", 1, 5, 3)
    
    if st.button("Log Gratitude"):
        from brain.models.gratitude import GratitudeCategory
        
        engine.add_gratitude(
            user_id=user_id,
            category=GratitudeCategory[category],
            text=text,
            impact_score=impact
        )
        
        st.success("Gratitude logged! 💫")


def render_kindness_logger(engine, user_id: str) -> None:
    """Render kindness logging form."""
    st.markdown("### 💚 What kindness did you show?")
    
    from brain.models.gratitude import KindnessCategory
    
    category = st.selectbox(
        "Who did you show kindness to?",
        [c.name for c in KindnessCategory],
        key="kindness_cat"
    )
    
    description = st.text_area(
        "Kindness act...",
        placeholder="I helped someone by...",
        key="kindness_desc"
    )
    
    recipient = st.text_input("Recipient (optional)", placeholder="e.g., My friend, A stranger")
    
    impact = st.slider("How meaningful was it?", 1, 5, 3, key="kindness_impact")
    
    if st.button("Log Kindness"):
        from brain.models.gratitude import KindnessCategory
        
        engine.add_kindness(
            user_id=user_id,
            category=KindnessCategory[category],
            description=description,
            recipient=recipient if recipient else "Self",
            impact_score=impact
        )
        
        st.success("Kindness logged! 🌟")


def render_recent_entries(engine, user_id: str) -> None:
    """Render recent entries."""
    st.markdown("### 📝 Recent Entries")
    
    tab1, tab2 = st.tabs(["🙏 Gratitude", "💚 Kindness"])
    
    with tab1:
        entries = engine.get_user_gratitude(user_id, days=7)
        
        if not entries:
            st.info("No gratitude entries this week. Start today!")
        else:
            for e in reversed(entries):
                st.write(f"**{e.category.value}:** {e.text}")
                st.caption(f"{e.date} | Impact: {e.impact_score}⭐")
                st.markdown("")
    
    with tab2:
        entries = engine.get_user_kindness(user_id, days=7)
        
        if not entries:
            st.info("No kindness acts this week. Spread some love!")
        else:
            for e in reversed(entries):
                st.write(f"**{e.category.value}** for {e.recipient}: {e.description}")
                st.caption(f"{e.date} | Impact: {e.impact_score}⭐")
                st.markdown("")


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import streamlit as st
    from brain.models.gratitude import create_engine, GratitudeCategory, KindnessCategory
    
    st.set_page_config(page_title="Gratitude Test")
    
    st.title("🙏 Gratitude & Kindness Test")
    
    engine = create_engine()
    
    # Add entries
    engine.add_gratitude(
        user_id="test",
        category=GratitudeCategory.PEOPLE,
        text="Grateful for my supportive friends",
        impact_score=5
    )
    
    engine.add_kindness(
        user_id="test",
        category=KindnessCategory.FRIENDS,
        description="Helped friend move",
        recipient="John",
        impact_score=4
    )
    
    # Stats
    stats = engine.get_stats("test")
    print(f"Stats: {stats}")
    
    st.write("Test passed!")
