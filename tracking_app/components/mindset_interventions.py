"""
Mindset Interventions Component

Streamlit UI for growth mindset reframing and interventions.

Features:
- Fixed mindset language detection
- Real-time reframing
- Self-compassion prompts
- Post-setback recovery protocol

Based on Task 11.1.4 from PHASE_11_INTEGRATION_ROADMAP.md

Ethical Principles:
- NEVER shame for fixed mindset language
- ALWAYS offer reframing as invitation
- Validate difficulty before problem-solving
"""

import streamlit as st
from datetime import date, datetime
from typing import Optional, List
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from brain.models.mindset import (
    MindsetDetector,
    MindsetAssessment,
    MindsetType,
    InterventionType,
    Intervention,
    SetbackProtocol,
    FIXED_MINDSET_PATTERNS,
    GROWTH_MINDSET_PATTERNS,
    REFRAME_MESSAGES,
    SELF_COMPASSION_PROMPTS,
    PROCESS_PRAISE_EXAMPLES,
)


# =============================================================================
# SESSION STATE
# =============================================================================

@st.cache_data
def get_mindset_detector() -> MindsetDetector:
    """Get or create the mindset detector."""
    return MindsetDetector()


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_mindset_badge(assessment: MindsetAssessment):
    """
    Render a badge showing the user's current mindset type.
    
    Args:
        assessment: The mindset assessment
    """
    if assessment.overall_type == MindsetType.GROWTH:
        st.success("🌱 Growth Mindset")
    elif assessment.overall_type == MindsetType.FIXED:
        st.info("🌿 Developing Growth Mindset")
    else:
        st.info("🌿 Mixed Mindset")


def render_reframe_prompt(text: str) -> Optional[Intervention]:
    """
    Detect fixed mindset language and offer reframing.
    
    Args:
        text: User's text input
        
    Returns:
        Intervention if fixed mindset detected, None otherwise
    """
    detector = get_mindset_detector()
    signals = detector.detect_from_text(text)
    
    # Check for fixed mindset signals
    fixed_signals = [s for s in signals if s.is_fixed]
    
    if fixed_signals:
        assessment = detector.assess_mindset(signals)
        if assessment.recommended_interventions:
            return assessment.recommended_interventions[0]
    
    return None


def render_fixed_mindset_warning(user_text: str = None):
    """
    Render a fixed mindset detection warning.
    
    Args:
        user_text: Optional text to analyze
    """
    if user_text:
        intervention = render_reframe_prompt(user_text)
        if intervention:
            render_intervention_card(intervention)


def render_intervention_card(intervention: Intervention):
    """
    Render a single intervention card.
    
    Args:
        intervention: The intervention to display
    """
    icon = {
        InterventionType.REFRAME: "🔄",
        InterventionType.SELF_COMPASSION: "💚",
        InterventionType.PROCESS_PRAISE: "🌟",
        InterventionType.YET_PROMPT: "🌱",
        InterventionType.SETBACK_PROTOCOL: "🤗",
        InterventionType.VALIDATION: "💜",
    }.get(intervention.intervention_type, "💭")
    
    st.info(f"{icon} **{intervention.message}**")


def render_self_compassion_prompt():
    """Render a self-compassion prompt."""
    prompt = random.choice(SELF_COMPASSION_PROMPTS)
    st.caption(f"💚 {prompt}")


def render_process_praise():
    """Render a process praise message."""
    praise = random.choice(PROCESS_PRAISE_EXAMPLES)
    st.success(f"🌟 {praise}")


def render_post_setback_card(days_missed: int):
    """
    Render the post-setback recovery card.
    
    Args:
        days_missed: Number of days since last completion
    """
    message = SetbackProtocol.get_post_setback_message(days_missed)
    st.info(message)
    
    # Add compassion reminder
    compassion = SetbackProtocol.get_compassion_reminder()
    st.caption(f"💚 {compassion}")


def render_yet_prompt():
    """Render a 'yet' prompt to reframe fixed mindset."""
    yet_messages = [
        "You can't do it **yet** - that's the exciting part!",
        "Not yet doesn't mean never. It means you're learning!",
        "What would 'I can do this' feel like?",
    ]
    prompt = random.choice(yet_messages)
    st.info(f"🌱 **{prompt}**")


def render_growth_mindset_tips():
    """Render tips for developing a growth mindset."""
    with st.expander("🌱 Developing a Growth Mindset"):
        st.markdown("""
        ### Growth Mindset Tips
        
        1. **Add "Yet" to Your Vocabulary**
           - "I can't do this" → "I can't do this **yet**"
           - "I don't understand" → "I don't understand **yet**"
        
        2. **Focus on Process, Not Just Results**
           - Instead of "Did I succeed?" ask "Did I try?"
           - Celebrate effort, not just outcomes
        
        3. **Learn from Mistakes**
           - Mistakes are data points, not failures
           - Ask "What can I learn from this?"
        
        4. **Embrace Challenges**
           - Challenges are opportunities to grow
           - Easy things don't help us develop
        
        5. **Use "I Can't" as "I Can't... Yet"**
           - This simple word changes everything
           - It acknowledges where you are while believing in where you're going
        
        ### Examples
        
        | Fixed Mindset | Growth Mindset |
        |---------------|----------------|
        | "I'm not good at this" | "I'm not good at this *yet*" |
        | "I gave up" | "I haven't figured out how yet" |
        | "I'm bad at math" | "I'm still learning math" |
        | "I'll never be able to" | "I'm working on being able to" |
        """)


def render_mindset_onboarding():
    """Render the mindset assessment onboarding."""
    st.subheader("🌱 Growth Mindset Assessment")
    
    st.markdown("""
    Let's understand your current mindset. This helps us support you better.
    
    **How do you typically respond to challenges?**
    """)
    
    response = st.radio(
        "Select the statement that sounds most like you:",
        [
            "When something is hard, I think 'I can't do this'",
            "When something is hard, I think 'I can't do this *yet*'",
            "When I fail, I think I'm not good enough",
            "When I fail, I think 'What can I learn from this?'"
        ],
        captions=[
            "Fixed mindset - challenges feel threatening",
            "Growth mindset - challenges are learning opportunities",
            "Fixed mindset - failure defines ability",
            "Growth mindset - failure is feedback"
        ]
    )
    
    if st.button("Continue"):
        if "yet" in response.lower() or "learn" in response.lower():
            st.success("🌱 That's a growth mindset! We'll support your journey of learning and improvement.")
        else:
            st.info("""
            🌿 That's okay! A growth mindset can be developed. 
            
            We'll offer gentle reframing when we notice fixed mindset language, 
            and help you see challenges as opportunities to grow.
            """)


def render_mindset_dashboard():
    """Render a complete mindset dashboard."""
    st.subheader("🧠 Mindset Dashboard")
    
    # Quick intervention
    st.markdown("### 💭 How are you feeling about your progress?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Struggling 😔"):
            render_self_compassion_prompt()
            st.rerun()
    
    with col2:
        if st.button("Feeling stuck 😕"):
            render_yet_prompt()
            st.rerun()
    
    st.markdown("---")
    
    # Post-setback simulation
    st.markdown("### 🔄 Returning After a Break?")
    
    days = st.number_input("How many days have you been away?", 0, 30, 1)
    
    if days > 0:
        render_post_setback_card(days)
    
    st.markdown("---")
    
    # Growth mindset tips
    render_growth_mindset_tips()


def render_real_time_intervention(user_input: str) -> bool:
    """
    Render real-time intervention if fixed mindset detected.
    
    Args:
        user_input: User's text input
        
    Returns:
        True if intervention was shown
    """
    intervention = render_reframe_prompt(user_input)
    
    if intervention:
        with st.expander("💭 A thought to consider:", expanded=True):
            render_intervention_card(intervention)
        return True
    
    return False


# =============================================================================
# DEMO
# =============================================================================

def render_demo():
    """Render a demo of the mindset interventions."""
    st.subheader("🧪 Mindset Interventions Demo")
    
    # Demo text input
    st.markdown("### Test Fixed Mindset Detection")
    test_text = st.text_input("Enter some text to analyze:")
    
    if test_text:
        render_real_time_intervention(test_text)
    
    st.markdown("---")
    
    # Demo buttons
    st.markdown("### Demo Interventions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Self Compassion"):
            render_self_compassion_prompt()
    
    with col2:
        if st.button("Process Praise"):
            render_process_praise()
    
    with col3:
        if st.button("'Yet' Prompt"):
            render_yet_prompt()
    
    st.markdown("---")
    
    # Post-setback demo
    st.markdown("### Post-Setback Protocol Demo")
    demo_days = st.slider("Days since last completion", 0, 14, 3)
    if demo_days > 0:
        render_post_setback_card(demo_days)
