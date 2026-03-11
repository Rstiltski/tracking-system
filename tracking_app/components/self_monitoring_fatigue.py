"""
Self-Monitoring Fatigue Component

UI for self-monitoring fatigue detection and recovery.

Based on Task 11.2.11 from PHASE_11_INTEGRATION_ROADMAP.md
"""

import streamlit as st
from typing import List


def render_fatigue_check(
    engine,
    user_id: str,
    completion_history: List[float]
) -> None:
    """
    Render the fatigue check component.
    
    Args:
        engine: SelfMonitoringFatigueEngine instance
        user_id: User ID
        completion_history: List of daily completion rates
    """
    st.markdown("### 🌊 Self-Monitoring Fatigue Check")
    
    # Calculate fatigue level
    fatigue_level = engine.calculate_fatigue_level(user_id, completion_history)
    
    # Display fatigue level
    level_colors = {
        "none": "🟢",
        "mild": "🟡",
        "moderate": "🟠",
        "severe": "🔴",
        "critical": "⛔"
    }
    
    level_descriptions = {
        "none": "You're doing great! Keep up the momentum.",
        "mild": "Some signs of fatigue. Consider simplifying.",
        "moderate": "Moderate fatigue detected. Take it easy.",
        "severe": "High fatigue! Time for a break.",
        "critical": "Critical fatigue! STOP and recover."
    }
    
    emoji = level_colors.get(fatigue_level.value, "⚪")
    
    st.write(f"{emoji} **Fatigue Level:** {fatigue_level.value.title()}")
    st.info(level_descriptions.get(fatigue_level.value, ""))
    
    # Show interventions
    if fatigue_level.value != "none":
        interventions = engine.get_interventions(fatigue_level)
        
        st.warning("💡 **Recommended Interventions:**")
        for i, interv in enumerate(interventions):
            st.write(f"- {interv['desc']}")
            
            if st.button(f"Apply: {interv['desc'][:30]}...", key=f"interv_{i}"):
                from brain.models.self_monitoring_fatigue import InterventionType
                engine.apply_intervention(
                    user_id=user_id,
                    intervention_type=InterventionType[interv['type'].name],
                    description=interv['desc']
                )
                st.success("Intervention applied! ✅")


def render_fatigue_dashboard(engine, user_id: str) -> None:
    """Render the fatigue dashboard."""
    st.markdown("### 📊 Fatigue Dashboard")
    
    recovery = engine.get_recovery_plan(user_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Recent Signals", recovery["recent_signals"])
    
    with col2:
        st.metric("Recent Interventions", recovery["recent_interventions"])
    
    st.info(f"**Recommendation:** {recovery['recommendation']}")


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import streamlit as st
    from brain.models.self_monitoring_fatigue import (
        create_engine, FatigueLevel, InterventionType
    )
    
    st.set_page_config(page_title="Self-Monitoring Fatigue Test")
    
    st.title("🌊 Self-Monitoring Fatigue Test")
    
    engine = create_engine()
    
    # Test with declining completion
    history = [1.0, 1.0, 0.9, 0.8, 0.5, 0.3, 0.0]  # Declining
    
    fatigue_level = engine.calculate_fatigue_level("test", history)
    print(f"Fatigue level: {fatigue_level.value}")
    
    # Get interventions
    interventions = engine.get_interventions(fatigue_level)
    print(f"Interventions: {len(interventions)}")
    
    # Apply intervention
    if interventions:
        engine.apply_intervention(
            user_id="test",
            intervention_type=InterventionType.TAKE_BREAK,
            description="Take a 3-day break"
        )
    
    # Recovery plan
    recovery = engine.get_recovery_plan("test")
    print(f"Recovery: {recovery}")
    
    st.write("Test passed!")
