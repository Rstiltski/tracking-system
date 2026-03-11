"""
Rest Prompts Component - Recovery Interventions

Streamlit UI for ego depletion recovery and rest interventions.

Features:
- Depletion level display
- Rest recommendations
- Recovery suggestions
- Easy return protocol

Based on Task 11.1.6 from PHASE_11_INTEGRATION_ROADMAP.md
"""

import streamlit as st
from datetime import date, timedelta
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from brain.models.ego_depletion import (
    EgoDepletionDetector,
    EgoDepletionAssessment,
    DepletionLevel,
    RestProtocol,
    create_depletion_detector,
)


# =============================================================================
# SESSION STATE
# =============================================================================

@st.cache_data
def get_depletion_detector() -> EgoDepletionDetector:
    """Get or create the depletion detector."""
    return create_depletion_detector()


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_depletion_banner(assessment: EgoDepletionAssessment):
    """
    Render a depletion level banner.
    
    Args:
        assessment: The ego depletion assessment
    """
    if assessment.level == DepletionLevel.NONE:
        return
    
    icons = {
        DepletionLevel.LOW: "💡",
        DepletionLevel.MODERATE: "⚠️",
        DepletionLevel.HIGH: "🛑",
        DepletionLevel.CRITICAL: "🚨"
    }
    
    colors = {
        DepletionLevel.LOW: "blue",
        DepletionLevel.MODERATE: "orange",
        DepletionLevel.HIGH: "red",
        DepletionLevel.CRITICAL: "red"
    }
    
    icon = icons.get(assessment.level, "💡")
    color = colors.get(assessment.level, "blue")
    
    if assessment.is_critical():
        st.error(f"{icon} **{assessment.level.value.upper()}** - Rest recommended")
    elif assessment.level == DepletionLevel.MODERATE:
        st.warning(f"{icon} **{assessment.level.value.title()}** - Consider rest")
    else:
        st.info(f"{icon} **{assessment.level.value.title()}** - Monitor")


def render_rest_card(assessment: EgoDepletionAssessment):
    """
    Render a rest recommendation card.
    
    Args:
        assessment: The ego depletion assessment
    """
    if not assessment.should_intervene():
        st.success("✅ You're doing great! Keep up the good work.")
        return
    
    with st.container():
        # Header
        st.subheader("🛋️ Time for Rest?")
        
        # Rest message
        message = RestProtocol.get_rest_message(assessment.level)
        st.info(f"💭 {message}")
        
        # Show signals
        if assessment.signals:
            with st.expander("What we noticed:"):
                for signal in assessment.signals:
                    st.markdown(f"- **{signal.indicator.value.replace('_', ' ').title()}**: {signal.evidence[0]}")
        
        # Fatigue score
        st.caption(f"Fatigue Score: {assessment.fatigue_score:.0%}")
        
        # Recovery suggestions
        st.markdown("### 🌿 Recovery Suggestions")
        
        suggestions = RestProtocol.get_recovery_suggestions()
        for suggestion in suggestions[:4]:
            st.markdown(f"- {suggestion}")
        
        # Easy return
        st.markdown("---")
        st.markdown("### 🔄 Easy Return")
        st.markdown("""
        When you're ready to come back:
        
        1. **Start small** - Just 1-2 habits
        2. **No pressure** - Missing a day is fine
        3. **Be kind** - Your worth isn't tied to tracking
        """)


def render_fatigue_score(fatigue_score: float):
    """
    Render a fatigue score display.
    
    Args:
        fatigue_score: The fatigue score (0.0 to 1.0)
    """
    col1, col2 = st.columns([1, 2])
    
    with col1:
        level = "🟢" if fatigue_score < 0.3 else "🟡" if fatigue_score < 0.5 else "🟠" if fatigue_score < 0.7 else "🔴"
        st.metric("Fatigue Level", f"{fatigue_score:.0%}", delta=level)
    
    with col2:
        st.progress(fatigue_score)


def render_depletion_dashboard(assessment: EgoDepletionAssessment):
    """
    Render a complete depletion dashboard.
    
    Args:
        assessment: The ego depletion assessment
    """
    st.subheader("🔋 Energy & Recovery Dashboard")
    
    # Banner
    render_depletion_banner(assessment)
    
    st.divider()
    
    # Fatigue score
    st.markdown("### Current Energy Level")
    render_fatigue_score(assessment.fatigue_score)
    
    st.divider()
    
    # Rest card
    render_rest_card(assessment)
    
    st.divider()
    
    # Last assessment
    st.caption(f"Last assessed: {assessment.assessment_date.strftime('%Y-%m-%d %H:%M')}")


def render_preventative_tips():
    """Render tips for preventing depletion."""
    with st.expander("💡 Preventing Burnout"):
        st.markdown("""
        ### Tips to Prevent Tracking Fatigue
        
        1. **Start small**
           - Don't try to track everything at once
           - 1-3 habits is a great starting point
        
        2. **Build gradually**
           - Add new habits only when current ones feel automatic
        
        3. **Take planned breaks**
           - Schedule rest days
           - Weekends can be tracking-free
        
        4. **Simplify when stressed**
           - It's okay to reduce tracking during busy times
           - Quality over quantity
        
        5. **Connect to purpose**
           - Remember why you're tracking
           - Purpose fuels motivation
        
        6. **Celebrate progress**
           - Acknowledge wins, no matter how small
           - Progress > perfection
        """)


def render_easy_return_flow():
    """Render an easy return flow for users coming back."""
    st.subheader("🔄 Welcome Back!")
    
    st.markdown("""
    ### Getting Started Again
    
    Starting fresh? Here's how:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Step 1: Choose 1-2 habits**
        
        Don't try to do everything at once.
        
        **Step 2: Set realistic goals**
        
        Aim for consistency, not perfection.
        
        **Step 3: Be patient**
        
        Your first week doesn't need to be perfect.
        """)
    
    with col2:
        st.markdown("""
        **Step 4: Celebrate small wins**
        
        Every day you show up counts!
        
        **Step 5: Take breaks**
        
        It's okay to miss a day or two.
        
        **Step 6: Be kind to yourself**
        
        Your worth isn't tied to your streak.
        """)
    
    if st.button("I'm Ready to Start! 🎉"):
        st.success("Welcome back! You've got this! 🌟")


# =============================================================================
# DEMO
# =============================================================================

def render_demo():
    """Render a demo of the rest prompts."""
    st.subheader("🧪 Rest Prompts Demo")
    
    # Demo detector
    detector = get_depletion_detector()
    
    # Simulate data
    entry_dates = [
        date.today() - timedelta(days=i) for i in range(5)
    ]
    entry_dates.pop(2)  # Create a gap
    
    logging_times = {
        date.today() - timedelta(days=i): 3.0 for i in range(3)  # Rushed
    }
    
    completions = {
        date.today() - timedelta(days=i): 0.5 - (i * 0.1) for i in range(10)  # Declining
    }
    
    # Assess
    assessment = detector.assess_depletion(
        "demo_user",
        entry_dates=entry_dates,
        logging_times=logging_times,
        habit_completions=completions
    )
    
    # Show dashboard
    render_depletion_dashboard(assessment)
    
    st.markdown("---")
    
    # Preventative tips
    render_preventative_tips()
    
    st.markdown("---")
    
    # Easy return
    render_easy_return_flow()
