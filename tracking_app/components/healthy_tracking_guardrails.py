"""
Healthy Tracking Guardrails Component

Streamlit UI for displaying orthorexia safeguards and intervention prompts.

Features:
- Risk level display
- Intervention prompts
- Resource links
- Data fasting reminders
- Rest day encouragement

Based on Task 11.1.1 from PHASE_11_INTEGRATION_ROADMAP.md

Ethical Principles:
- NEVER enable disordered patterns
- ALWAYS provide resources when risk detected
- Frame flexibility as health, not failure
"""

import streamlit as st
from datetime import date, timedelta
from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from brain.models.disordered_patterns import (
    DisorderedPatternDetector,
    OrthorexiaRisk,
    RiskLevel,
    PatternType,
    check_calorie_limit,
    check_daily_entry_limit,
    check_rest_day_required,
    DataFastingProtocol,
    MIN_CALORIE_LIMIT,
    MAX_DAILY_ENTRIES,
)


# =============================================================================
# SESSION STATE
# =============================================================================

@st.cache_data
def get_detector() -> DisorderedPatternDetector:
    """Get or create the pattern detector."""
    return DisorderedPatternDetector()


@st.cache_data
def get_fasting_protocol() -> DataFastingProtocol:
    """Get or create the data fasting protocol."""
    return DataFastingProtocol()


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_risk_banner(risk: OrthorexiaRisk):
    """
    Render a risk level banner.
    
    Args:
        risk: The orthorexia risk assessment
    """
    if not risk.has_risk():
        return
    
    # Choose color based on risk level
    colors = {
        RiskLevel.LOW: "blue",
        RiskLevel.MODERATE: "orange",
        RiskLevel.HIGH: "red",
        RiskLevel.CRITICAL: "red"
    }
    
    icons = {
        RiskLevel.LOW: "💡",
        RiskLevel.MODERATE: "⚠️",
        RiskLevel.HIGH: "🛑",
        RiskLevel.CRITICAL: "🚨"
    }
    
    color = colors.get(risk.overall_risk, "blue")
    icon = icons.get(risk.overall_risk, "💡")
    
    if risk.overall_risk == RiskLevel.CRITICAL:
        st.error(f"{icon} **HEALTH WARNING**: {risk.overall_risk.value.upper()} RISK DETECTED")
    elif risk.overall_risk == RiskLevel.HIGH:
        st.warning(f"{icon} **Attention**: {risk.overall_risk.value.title()} Risk Level")
    else:
        st.info(f"{icon} **Note**: {risk.overall_risk.value.title()} Risk Level")


def render_orthorexia_card(risk: OrthorexiaRisk):
    """
    Render a full orthorexia risk assessment card.
    
    Args:
        risk: The orthorexia risk assessment
    """
    with st.container():
        # Header
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("🛡️ Healthy Tracking Monitor")
        
        with col2:
            # Risk badge
            if risk.has_risk():
                if risk.overall_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    st.error(f"⚠️ {risk.overall_risk.value.title()}")
                elif risk.overall_risk == RiskLevel.MODERATE:
                    st.warning(f"⚠️ {risk.overall_risk.value.title()}")
                else:
                    st.info(f"💡 {risk.overall_risk.value.title()}")
            else:
                st.success("✅ Healthy")
        
        # Show signals if any
        if risk.signals:
            st.markdown("### Detected Patterns")
            for signal in risk.signals:
                with st.expander(f"{signal.pattern_type.value.replace('_', ' ').title()}"):
                    st.markdown(f"**Confidence:** {signal.confidence:.0%}")
                    for evidence in signal.evidence:
                        st.markdown(f"- {evidence}")
        
        # Show recommendations
        if risk.recommended_actions:
            st.markdown("### 💭 Recommendations")
            for action in risk.recommended_actions:
                st.markdown(f"- {action}")
        
        # Show resources if intervention needed
        if risk.resources:
            st.markdown("### 📞 Support Resources")
            st.warning("If you're struggling, please reach out:")
            for resource in risk.resources:
                st.markdown(f"- {resource}")
        
        # Last assessment
        st.caption(f"Last assessed: {risk.assessment_date.strftime('%Y-%m-%d %H:%M')}")


def render_guardrail_warning(
    title: str,
    message: str,
    risk_level: RiskLevel = RiskLevel.MODERATE
):
    """
    Render a guardrail warning.
    
    Args:
        title: Warning title
        message: Warning message
        risk_level: Severity of the warning
    """
    if risk_level == RiskLevel.CRITICAL:
        st.error(f"🚨 **{title}**\n\n{message}")
    elif risk_level == RiskLevel.HIGH:
        st.warning(f"🛑 **{title}**\n\n{message}")
    elif risk_level == RiskLevel.MODERATE:
        st.warning(f"⚠️ **{title}**\n\n{message}")
    else:
        st.info(f"💡 **{title}**\n\n{message}")


def render_calorie_guardrail(calories: int) -> bool:
    """
    Render calorie limit guardrail.
    
    Args:
        calories: Current calorie intake
        
    Returns:
        True if entry should be blocked
    """
    is_allowed, message = check_calorie_limit(calories)
    
    if not is_allowed:
        render_guardrail_warning(
            "Calorie Limit Reached",
            f"{message}\n\nYour health is more important than perfect tracking.",
            RiskLevel.HIGH
        )
    
    return is_allowed


def render_entry_limit_guardrail(entries_today: int) -> bool:
    """
    Render daily entry limit guardrail.
    
    Args:
        entries_today: Number of entries today
        
    Returns:
        True if entry should be blocked
    """
    is_allowed, message = check_daily_entry_limit(entries_today)
    
    if not is_allowed:
        render_guardrail_warning(
            "Daily Entry Limit",
            f"{message}\n\nTaking a break is a sign of healthy habits!",
            RiskLevel.MODERATE
        )
    
    return is_allowed


def render_rest_day_reminder(entries: List[date]) -> Optional[str]:
    """
    Render rest day reminder if needed.
    
    Args:
        entries: List of dates with entries
        
    Returns:
        Reminder message if rest day is due
    """
    is_required, message = check_rest_day_required(entries)
    
    if is_required:
        st.warning(f"📢 **{message}**")
    
    return message if is_required else None


def render_data_fasting_banner():
    """Render data fasting day banner if today is a fasting day."""
    protocol = get_fasting_protocol()
    
    if protocol.is_fasting_day():
        st.info(f"🌿 **{protocol.get_fasting_message()}**")
        with st.expander("What is data fasting?"):
            st.markdown("""
            **Data fasting** means taking a break from tracking:
            
            - Eat when you're hungry
            - Stop when you're full
            - Enjoy food without guilt
            - Listen to your body's cues
            
            This helps build a healthier relationship with food!
            """)


def render_somatic_prompt():
    """Render a somatic/body awareness prompt."""
    prompts = [
        "🌱 How does your body feel right now?",
        "🌿 Are you eating because you're hungry, or for another reason?",
        "🍃 Take a moment to check in with your hunger levels (1-10)",
        "🌸 What does satisfaction feel like in your body?",
        "🌻 Remember: Food is fuel AND enjoyment",
    ]
    
    import random
    selected = random.choice(prompts)
    
    st.caption(f"💭 {selected}")


def render_healthy_tracking_tips():
    """Render general healthy tracking tips."""
    with st.expander("💡 Healthy Tracking Tips"):
        st.markdown("""
        ### Guidelines for Balanced Tracking
        
        1. **Track to learn, not to judge**
           - Use data to understand patterns, not to criticize yourself
        
        2. **Flexibility is healthy**
           - Missing a day doesn't ruin your progress
           - Life happens - be kind to yourself
        
        3. **Listen to your body**
           - Hunger and fullness cues are more accurate than numbers
           - Intuitive eating is a skill worth developing
        
        4. **Take regular breaks**
           - Schedule untracked meals
           - Weekends can be tracking-free
        
        5. **Focus on behaviors, not perfection**
           - Consistency > perfection
           - Small changes compound over time
        
        6. **Seek balance**
           - All foods fit in a healthy relationship with food
           - Progress, not perfection
        """)


# =============================================================================
# MAIN GUARDRAIL CHECK
# =============================================================================

def check_all_guardrails(
    calories: int = None,
    entries_today: int = 0,
    recent_entries: List[date] = None
) -> dict:
    """
    Check all guardrails and return results.
    
    Args:
        calories: Current calorie intake (optional)
        entries_today: Number of entries today
        recent_entries: List of recent entry dates
        
    Returns:
        Dictionary with guardrail results
    """
    results = {
        "blocked": False,
        "calorie_blocked": False,
        "entry_blocked": False,
        "rest_day_warning": False,
        "messages": []
    }
    
    # Check calorie limit
    if calories is not None:
        is_allowed, message = check_calorie_limit(calories)
        if not is_allowed:
            results["blocked"] = True
            results["calorie_blocked"] = True
            results["messages"].append(message)
    
    # Check entry limit
    is_allowed, message = check_daily_entry_limit(entries_today)
    if not is_allowed:
        results["blocked"] = True
        results["entry_blocked"] = True
        results["messages"].append(message)
    
    # Check rest day
    if recent_entries:
        is_required, message = check_rest_day_required(recent_entries)
        if is_required:
            results["rest_day_warning"] = True
            results["messages"].append(message)
    
    return results


# =============================================================================
# DEMO / TEST
# =============================================================================

def render_demo():
    """Render a demo of the guardrails."""
    st.subheader("🧪 Guardrails Demo")
    
    # Demo calorie check
    st.markdown("### Calorie Limit Check")
    demo_calories = st.number_input("Test calories", 0, 5000, 1100)
    render_calorie_guardrail(demo_calories)
    
    # Demo entry limit
    st.markdown("### Entry Limit Check")
    demo_entries = st.number_input("Test entries today", 0, 20, 8)
    render_entry_limit_guardrail(demo_entries)
    
    # Demo fasting
    st.markdown("### Data Fasting")
    render_data_fasting_banner()
    
    # Demo tips
    render_healthy_tracking_tips()
