"""
Spiritual Journaling Page

UI for voice and text spiritual journaling.

Based on Task 11.2.7 from PHASE_11_INTEGRATION_ROADMAP.md
"""

import streamlit as st


def render_spiritual_page(engine, user_id: str) -> None:
    """
    Render the spiritual journaling page.
    
    Args:
        engine: SpiritualEngine instance
        user_id: User ID
    """
    st.markdown("🧘 Spiritual Journal")
    st.markdown("*Voice journaling removes friction. AI-guided spiritual pattern recognition.*")
    
    # Insights
    insights = engine.get_insights(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Entries", insights["total_entries"])
    with col2:
        st.metric("🎙️ Voice", insights["voice_entries"])
    with col3:
        st.metric("🔄 Patterns", insights["patterns_detected"])
    with col4:
        st.metric("⭐ Mood", f"{insights['avg_mood']:.1f}")
    
    st.markdown("---")
    
    # New entry
    render_entry_form(engine, user_id)
    
    st.markdown("---")
    
    # Recent entries
    render_recent_entries(engine, user_id)
    
    st.markdown("---")
    
    # Patterns
    render_patterns(engine, user_id)


def render_entry_form(engine, user_id: str) -> None:
    """Render entry creation form."""
    st.markdown("### ✍️ New Journal Entry")
    
    from brain.models.spiritual import JournalType, SpiritualTheme
    
    col1, col2 = st.columns(2)
    
    with col1:
        journal_type = st.selectbox(
            "Journal Type",
            [j.name for j in JournalType]
        )
    
    with col2:
        theme = st.selectbox(
            "Theme (optional)",
            ["None"] + [t.name for t in SpiritualTheme]
        )
    
    transcript = st.text_area(
        "Your thoughts...",
        placeholder="What's on your mind? What's stirring in your spirit?",
        height=150
    )
    
    # Voice recording placeholder
    with st.expander("🎙️ Voice Recording (Beta)"):
        st.info("Voice recording coming soon! For now, type or paste your transcript.")
    
    if st.button("Save Entry"):
        from brain.models.spiritual import JournalType, SpiritualTheme
        
        theme_enum = None if theme == "None" else SpiritualTheme[theme]
        
        engine.add_entry(
            user_id=user_id,
            journal_type=JournalType[journal_type],
            transcript=transcript,
            theme=theme_enum
        )
        
        st.success("Entry saved! 🧘")


def render_recent_entries(engine, user_id: str) -> None:
    """Render recent entries."""
    st.markdown("### 📖 Recent Entries")
    
    entries = engine.get_entries(user_id, days=30)
    
    if not entries:
        st.info("No journal entries yet. Start your spiritual journey today!")
        return
    
    for entry in reversed(entries[-10:]):
        with st.expander(f"{entry.journal_type.value.title()} - {entry.date}"):
            st.write(entry.transcript)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if entry.sentiment:
                    emoji = "😊" if entry.sentiment == "positive" else "😔" if entry.sentiment == "challenging" else "😐"
                    st.write(f"{emoji} {entry.sentiment}")
            
            with col2:
                if entry.mood_score:
                    st.write(f"⭐ Mood: {entry.mood_score}/10")
            
            with col3:
                if entry.themes_detected:
                    st.write(f"🏷️ {', '.join(entry.themes_detected[:3])}")


def render_patterns(engine, user_id: str) -> None:
    """Render spiritual patterns."""
    st.markdown("### 🔄 Spiritual Patterns")
    
    patterns = engine.detect_patterns(user_id)
    
    if not patterns:
        st.info("Need at least 3 entries to detect patterns. Keep journaling!")
        return
    
    for pattern in patterns:
        trend_emoji = "📈" if pattern.trend == "increasing" else "📉" if pattern.trend == "decreasing" else "➡️"
        
        st.write(f"**{pattern.theme.value.title()}** {trend_emoji}")
        st.caption(f"{pattern.description}")


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import streamlit as st
    from brain.models.spiritual import create_engine, JournalType, SpiritualTheme
    
    st.set_page_config(page_title="Spiritual Journal Test")
    
    st.title("🧘 Spiritual Journal Test")
    
    engine = create_engine()
    
    # Add entries
    engine.add_entry(
        user_id="test",
        journal_type=JournalType.VOICE,
        transcript="I feel so grateful for my life today. The peace I feel is amazing.",
        theme=SpiritualTheme.GRATITUDE
    )
    
    engine.add_entry(
        user_id="test",
        journal_type=JournalType.TEXT,
        transcript="I'm searching for my purpose. What is my calling in life?",
        theme=SpiritualTheme.PURPOSE
    )
    
    # Insights
    insights = engine.get_insights("test")
    print(f"Insights: {insights}")
    
    # Patterns
    patterns = engine.detect_patterns("test")
    print(f"Patterns: {len(patterns)}")
    
    st.write("Test passed!")
