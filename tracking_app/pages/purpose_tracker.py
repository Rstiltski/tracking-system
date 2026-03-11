"""
Purpose Tracker Page - Eudaemonic Motivation Tracking

Streamlit page for tracking and reinforcing meaning-driven motivation.

Features:
- Motivation type assessment
- Values-habit alignment scoring
- Purpose connection prompts
- Motivation drift detection

Based on Task 11.1.5 from PHASE_11_INTEGRATION_ROADMAP.md

Research: Eudaemonic motivation is the strongest predictor of habit retention.
"""

import streamlit as st
from datetime import datetime
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from brain.models.motivation import (
    MotivationAssessor,
    MotivationProfile,
    MotivationType,
    MotivationDrift,
    MotivationDriftDetection,
    CORE_VALUES,
    SAMPLE_PURPOSES,
    PURPOSE_PROMPTS,
    create_motivation_assessor,
    get_purpose_prompt,
)


# =============================================================================
# SESSION STATE
# =============================================================================

@st.cache_data
def get_assessor() -> MotivationAssessor:
    """Get or create the motivation assessor."""
    return create_motivation_assessor()


# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Purpose & Motivation",
    page_icon="🌟",
    layout="wide"
)


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_header():
    """Render the page header."""
    st.title("🌟 Purpose & Motivation")
    st.markdown("""
    Connect your daily habits to your deeper purpose. Research shows that 
    **meaning-driven motivation** is the strongest predictor of long-term habit retention.
    """)


def render_motivation_type_card(profile: MotivationProfile):
    """Render the user's motivation type."""
    type_icons = {
        MotivationType.EUDAEMONIC: "🌟",
        MotivationType.HEDONIC: "😊",
        MotivationType.UTILITARIAN: "⚡",
        MotivationType.MIXED: "🌈",
    }
    
    type_descriptions = {
        MotivationType.EUDAEMONIC: "You're motivated by meaning and purpose. You want your habits to connect to something bigger than yourself.",
        MotivationType.HEDONIC: "You're motivated by pleasure and positive feelings. You want habits that make you feel good.",
        MotivationType.UTILITARIAN: "You're motivated by utility and achievement. You want habits that produce tangible results.",
        MotivationType.MIXED: "You have a mix of motivations. Different habits may serve different purposes for you.",
    }
    
    icon = type_icons.get(profile.primary_type, "🌟")
    
    st.subheader(f"{icon} Your Motivation Type")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**{profile.primary_type.value.title()} Motivation**")
        st.caption(type_descriptions.get(profile.primary_type, ""))
    
    with col2:
        alignment = profile.get_alignment_score()
        st.metric("Values Alignment", f"{alignment:.0%}")


def render_values_selection() -> List[str]:
    """Render values selection widget."""
    st.subheader("💎 Your Core Values")
    st.markdown("Select 3-5 values that matter most to you:")
    
    selected = st.multiselect(
        "Core Values",
        options=CORE_VALUES,
        default=[],
        help="These values will guide your habit recommendations"
    )
    
    return selected


def render_why_assessment() -> List[str]:
    """Render 'why' assessment questions."""
    st.subheader("🎯 Your 'Why' Assessment")
    
    questions = [
        "Why do you want to build habits?",
        "What do you hope to gain from tracking?",
        "What would your ideal future self look like?",
    ]
    
    answers = []
    
    for q in questions:
        answer = st.text_area(q, key=q)
        if answer:
            answers.append(answer)
    
    return answers


def render_onboarding():
    """Render the onboarding flow for new users."""
    st.subheader("🌱 Discover Your Motivation")
    
    # Step 1: Values
    st.markdown("### Step 1: Your Values")
    selected_values = render_values_selection()
    
    # Step 2: Why
    st.markdown("---")
    st.markdown("### Step 2: Your Why")
    why_answers = render_why_assessment()
    
    # Step 3: Get Results
    if st.button("Discover My Motivation Type", type="primary"):
        if selected_values or why_answers:
            assessor = get_assessor()
            profile = assessor.assess_from_responses(why_answers, selected_values)
            
            st.success("🌟 Your motivation profile has been created!")
            render_motivation_type_card(profile)
            
            return profile
        else:
            st.warning("Please answer at least one question or select values.")
    
    return None


def render_purpose_prompt(motivation_type: MotivationType):
    """Render a purpose connection prompt."""
    prompt = get_purpose_prompt(motivation_type)
    st.info(f"💭 {prompt}")


def render_values_alignment(profile: MotivationProfile):
    """Render value-habit alignment scores."""
    st.subheader("📊 Values-Habit Alignment")
    
    if not profile.alignment_scores:
        st.info("Complete your assessment to see alignment scores.")
        return
    
    for alignment in profile.alignment_scores:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**{alignment.value.title()}**")
        
        with col2:
            st.progress(alignment.alignment_score)
            st.caption(f"{alignment.alignment_score:.0%} alignment")
    
    # Overall score
    overall = profile.get_alignment_score()
    st.divider()
    st.metric("Overall Alignment", f"{overall:.0%}")


def render_motivation_drift(detection: MotivationDriftDetection):
    """Render motivation drift detection."""
    if detection.drift_type == MotivationDrift.NONE:
        return
    
    st.subheader("⚠️ Motivation Drift Detected")
    
    if detection.severity > 0.5:
        st.error(f"**{detection.drift_type.value.title()}** - {detection.severity:.0%} severity")
    else:
        st.warning(f"**{detection.drift_type.value.title()}** - {detection.severity:.0%} severity")
    
    # Show indicators
    if detection.indicators:
        st.markdown("### Indicators")
        for indicator in detection.indicators:
            st.markdown(f"- {indicator}")
    
    # Show recommendations
    if detection.recommendations:
        st.markdown("### Recommendations")
        for rec in detection.recommendations:
            st.markdown(f"- {rec}")
    
    # Show reconnection prompts
    st.markdown("### Let's Reconnect")
    if st.button("Refresh My Why"):
        st.info("Take a moment to remember why you started. Your purpose is still there!")


def render_dashboard(profile: MotivationProfile):
    """Render the main dashboard for existing users."""
    # Motivation type
    render_motivation_type_card(profile)
    
    st.divider()
    
    # Purpose prompt
    render_purpose_prompt(profile.primary_type)
    
    st.divider()
    
    # Values alignment
    render_values_alignment(profile)
    
    st.divider()
    
    # Drift detection
    st.subheader("🔄 Motivation Health")
    
    # Demo drift detection
    detection = MotivationDriftDetection(
        drift_type=MotivationDrift.NONE,
        severity=0.0,
        indicators=[],
        recommendations=[]
    )
    render_motivation_drift(detection)


def render_sample_purposes():
    """Render sample purposes for each motivation type."""
    with st.expander("💡 See examples of different motivation types"):
        st.markdown("""
        ### Eudaemonic (Meaning-Driven)
        """)
        for purpose in SAMPLE_PURPOSES[MotivationType.EUDAEMONIC]:
            st.markdown(f"- {purpose}")
        
        st.markdown("""
        ### Hedonic (Pleasure-Driven)
        """)
        for purpose in SAMPLE_PURPOSES[MotivationType.HEDONIC]:
            st.markdown(f"- {purpose}")
        
        st.markdown("""
        ### Utilitarian (Achievement-Driven)
        """)
        for purpose in SAMPLE_PURPOSES[MotivationType.UTILITARIAN]:
            st.markdown(f"- {purpose}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main purpose tracker page."""
    render_header()
    
    # Check if user has completed assessment
    if "motivation_profile" not in st.session_state:
        st.session_state.motivation_profile = None
    
    # Show onboarding or dashboard
    if st.session_state.motivation_profile is None:
        profile = render_onboarding()
        if profile:
            st.session_state.motivation_profile = profile
    else:
        # Show dashboard
        render_dashboard(st.session_state.motivation_profile)
        
        # Option to retake assessment
        if st.button("Retake Assessment"):
            st.session_state.motivation_profile = None
            st.rerun()
    
    # Show sample purposes
    render_sample_purposes()


if __name__ == "__main__":
    main()
