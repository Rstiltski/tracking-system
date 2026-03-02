"""
UI components for the Insights page.

Contains all render functions for the intelligence dashboard.
"""

import streamlit as st
from typing import Any, Dict

from tracking_app.components.metrics import render_burnout_risk_card
from tracking_app.storage import Storage

from .constants import MAX_CORRELATIONS_DISPLAY, PCS_MINIMUM_DAYS
from .helpers import (
    gather_burnout_indicators,
    gather_habit_data_for_pcs,
    calculate_habit_correlations,
)


def render_header():
    """Render page header."""
    st.title("🧠 Intelligence Dashboard")
    st.markdown("AI-powered insights about your habits, health, and behavior.")


def render_burnout_section(storage: Storage):
    """Render burnout risk assessment section."""
    st.subheader("⚠️ Burnout Risk Assessment")
    
    # Gather indicators
    indicators = gather_burnout_indicators(storage)
    
    if indicators is None:
        st.info("Burnout analysis requires the brain module. Using simple calculation.")
        render_simple_burnout_section(storage)
        return
    
    # Calculate risk
    try:
        from brain.analysis.burnout import BurnoutPredictor
        predictor = BurnoutPredictor()
        risk = predictor.assess_risk(indicators)
    except ImportError:
        st.info("Burnout analysis requires the brain module.")
        return
    
    # Display risk card
    col1, col2 = st.columns([1, 2])
    
    with col1:
        render_burnout_risk_card(
            risk_score=risk.risk_score,
            risk_level=risk.risk_level,
            contributing_factors=risk.contributing_factors
        )
    
    with col2:
        st.markdown("### Contributing Factors")
        for factor, impact in risk.contributing_factors.items():
            factor_name = factor.replace("_", " ").title()
            impact_pct = impact * 100
            
            # Color based on impact
            if impact > 0.6:
                color = "🔴"
            elif impact > 0.3:
                color = "🟡"
            else:
                color = "🟢"
            
            st.markdown(f"{color} **{factor_name}**: {impact_pct:.0f}%")
    
    # Display interventions
    if risk.interventions:
        st.markdown("### 📋 Recommendations")
        for intervention in risk.interventions:
            st.info(intervention)


def render_simple_burnout_section(storage: Storage):
    """Simple burnout section fallback."""
    habits = storage.get_habits()
    active_habits = [h for h in habits if not h.archived]
    
    # Simple risk calculation
    risk_score = min(100, len(active_habits) * 5)
    risk_level = "low" if risk_score < 30 else "moderate" if risk_score < 60 else "high"
    
    render_burnout_risk_card(
        risk_score=risk_score,
        risk_level=risk_level,
        contributing_factors={"habit_count": len(active_habits) / 10}
    )


def render_correlations_section(storage: Storage):
    """Render habit correlations section."""
    st.subheader("🔗 Habit Correlations")
    st.markdown("Discover patterns between your habits and health metrics.")
    
    habits = storage.get_habits()
    active_habits = [h for h in habits if not h.archived]
    
    if len(active_habits) < 2:
        st.info("Need at least 2 active habits to calculate correlations.")
        return
    
    # Calculate correlations
    correlations = calculate_habit_correlations(storage, active_habits)
    
    if not correlations:
        st.info("No significant correlations found. Keep tracking your habits!")
        return
    
    # Display correlations
    for corr in correlations[:MAX_CORRELATIONS_DISPLAY]:
        col1, col2, col3 = st.columns([2, 1, 3])
        
        with col1:
            st.markdown(f"**{corr['variable_x']}** ↔ **{corr['variable_y']}**")
        
        with col2:
            direction = "↗️" if corr['direction'] == "positive" else "↘️"
            st.markdown(f"r = **{corr['coefficient']:.2f}** {direction}")
        
        with col3:
            strength = corr['strength'].title()
            st.caption(f"{strength} {corr['direction']} correlation")


def render_pcs_section(storage: Storage):
    """Render PCS Fragility Scores section."""
    st.subheader("📊 Habit Predictability (PCS)")
    st.markdown("Fragility Index shows how much your habits depend on external factors.")
    
    habits = storage.get_habits()
    active_habits = [h for h in habits if not h.archived]
    
    if not active_habits:
        st.info("No active habits to analyze.")
        return
    
    try:
        from brain.analysis.prediction import PCSEngine
        pcs_engine = PCSEngine()
    except ImportError:
        st.info("PCS analysis requires the brain module.")
        return
    
    # Calculate PCS for each habit
    scores = []
    
    for habit in active_habits:
        completions, contexts = gather_habit_data_for_pcs(storage, habit)
        if len(completions) >= PCS_MINIMUM_DAYS:
            score = pcs_engine.calculate_pcs(habit.id, habit.name, completions, contexts)
            scores.append(score)
    
    if not scores:
        st.info(f"Need at least {PCS_MINIMUM_DAYS} days of tracking data for PCS analysis.")
        return
    
    # Display scores
    for score in sorted(scores, key=lambda s: s.fragility_index, reverse=True):
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                fragility_emoji = score.fragility_emoji
                st.markdown(f"### {fragility_emoji} {score.habit_name}")
                st.caption(f"Fragility: {score.fragility.title()} ({score.fragility_index:.0f}%)")
            
            with col2:
                st.metric("AUC Score", f"{score.auc_score:.2f}")
                st.caption("Predictability")
            
            with col3:
                st.metric("Habit Strength", score.habit_strength.title())
            
            # Show recommendations for fragile habits
            if score.fragility == "fragile":
                recommendations = pcs_engine.get_protection_recommendations(score)
                with st.expander("View Recommendations"):
                    for rec in recommendations:
                        st.markdown(f"- {rec}")
            
            st.divider()


def render_insights_summary(storage: Storage):
    """Render overall insights summary."""
    st.subheader("💡 Key Insights")
    
    # Gather all data
    indicators = gather_burnout_indicators(storage)
    
    if indicators is None:
        st.info("Insights require the brain analysis module.")
        return
    
    try:
        from brain.analysis.burnout import BurnoutPredictor
        predictor = BurnoutPredictor()
        risk = predictor.assess_risk(indicators)
    except ImportError:
        return
    
    insights = []
    
    # Burnout insight
    if risk.risk_level in ['high', 'critical']:
        insights.append({
            "type": "warning",
            "icon": "⚠️",
            "title": "Burnout Risk Elevated",
            "message": f"Your burnout risk is {risk.risk_level} ({risk.risk_score:.0f}%). Consider reducing your habit load."
        })
    else:
        insights.append({
            "type": "success",
            "icon": "✅",
            "title": "Healthy Burnout Level",
            "message": f"Your burnout risk is {risk.risk_level} ({risk.risk_score:.0f}%). Keep up the good work!"
        })
    
    # Completion trend insight
    if indicators.completion_rate_trend < -0.2:
        insights.append({
            "type": "warning",
            "icon": "📉",
            "title": "Completion Rate Declining",
            "message": "Your habit completion rate has been declining. Focus on your most important habits."
        })
    elif indicators.completion_rate_trend > 0.2:
        insights.append({
            "type": "success",
            "icon": "📈",
            "title": "Completion Rate Improving",
            "message": "Great progress! Your habit completion rate is trending upward."
        })
    
    # Sleep insight
    if indicators.sleep_deviation < -0.5:
        insights.append({
            "type": "info",
            "icon": "😴",
            "title": "Sleep Deficit Detected",
            "message": f"You're sleeping {abs(indicators.sleep_deviation):.1f} hours less than your baseline. Rest is important for habit success."
        })
    
    # Display insights
    for insight in insights:
        if insight["type"] == "warning":
            st.warning(f"{insight['icon']} **{insight['title']}**: {insight['message']}")
        elif insight["type"] == "success":
            st.success(f"{insight['icon']} **{insight['title']}**: {insight['message']}")
        else:
            st.info(f"{insight['icon']} **{insight['title']}**: {insight['message']}")