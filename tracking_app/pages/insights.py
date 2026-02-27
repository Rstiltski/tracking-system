"""
Insights Page - Intelligence Dashboard

Streamlit page for displaying AI-powered insights about habits, health, and behavior.

Features:
- Burnout Risk Assessment with recommendations
- Habit Correlations (sleep ↔ mood, exercise ↔ energy)
- PCS Fragility Scores (habit predictability)
- Personalized recommendations

Usage:
    streamlit run tracking_app/pages/insights.py
"""
import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage
from tracking_app.models import Habit, HealthEntry

# Import brain analysis modules
from brain.analysis.burnout import BurnoutPredictor, BurnoutIndicators, BurnoutRisk
from brain.analysis.correlation import CorrelationEngine, InsightGenerator
from brain.analysis.prediction import PCSEngine, PCSScore, ContextVariables

# Import UI components
from tracking_app.components.metrics import render_burnout_risk_card


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Insights - Veryfyn",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# SESSION STATE
# =============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    if 'user_xp' not in st.session_state:
        st.session_state.user_xp = st.session_state.storage.get_xp()
    
    if 'user_level' not in st.session_state:
        st.session_state.user_level = st.session_state.storage.get_level()


# =============================================================================
# DATA GATHERING FUNCTIONS
# =============================================================================

def gather_burnout_indicators(storage: Storage) -> BurnoutIndicators:
    """
    Gather data for burnout prediction from storage.
    
    Returns:
        BurnoutIndicators with current metrics
    """
    today = date.today()
    
    # Get habits
    habits = storage.get_habits()
    active_habits = [h for h in habits if not h.archived]
    
    # Calculate completion rate trend (last 14 days vs previous 14 days)
    completion_trend = calculate_completion_trend(storage, active_habits, days=14)
    
    # Get sleep data from health entries
    sleep_deviation = calculate_sleep_deviation(storage, days=14)
    
    # Get mood trend
    mood_trend = calculate_mood_trend(storage, days=14)
    
    # Count streak breaks in last 7 days
    streak_breaks = count_recent_streak_breaks(storage, active_habits, days=7)
    
    # Count missed days
    missed_days = count_consecutive_missed_days(storage, active_habits)
    
    # Task overload (mock - would need task data)
    task_overload = 0.0  # TODO: Calculate from task data
    
    return BurnoutIndicators(
        completion_rate_trend=completion_trend,
        sleep_deviation=sleep_deviation,
        stress_level=5,  # Default - would come from health data
        days_since_checkin=0,  # User is here now
        streak_breaks=streak_breaks,
        mood_trend=mood_trend,
        task_overload=task_overload,
        habit_load=len(active_habits),
        missed_days=missed_days
    )


def calculate_completion_trend(storage: Storage, habits: List[Habit], days: int = 14) -> float:
    """Calculate trend in completion rate."""
    if not habits:
        return 0.0
    
    today = date.today()
    
    # First half
    first_half_completions = 0
    first_half_total = 0
    for i in range(days // 2, days):
        check_date = today - timedelta(days=i)
        for habit in habits:
            entry = storage.get_habit_entry(habit.id, check_date)
            first_half_total += 1
            if entry and not entry.skipped and entry.value > 0:
                first_half_completions += 1
    
    # Second half
    second_half_completions = 0
    second_half_total = 0
    for i in range(0, days // 2):
        check_date = today - timedelta(days=i)
        for habit in habits:
            entry = storage.get_habit_entry(habit.id, check_date)
            second_half_total += 1
            if entry and not entry.skipped and entry.value > 0:
                second_half_completions += 1
    
    if first_half_total == 0 or second_half_total == 0:
        return 0.0
    
    first_rate = first_half_completions / first_half_total
    second_rate = second_half_completions / second_half_total
    
    # Normalize to -1 to 1
    diff = second_rate - first_rate
    return max(-1.0, min(1.0, diff * 5))  # Scale for interpretability


def calculate_sleep_deviation(storage: Storage, days: int = 14) -> float:
    """Calculate deviation from average sleep hours."""
    health_entries = storage.get_health_entries(
        start_date=date.today() - timedelta(days=days)
    )
    
    if not health_entries or len(health_entries) < 3:
        return 0.0
    
    # Get sleep hours
    sleep_hours = [e.sleep_hours for e in health_entries if e.sleep_hours]
    
    if len(sleep_hours) < 3:
        return 0.0
    
    # Calculate average and recent deviation
    avg_sleep = sum(sleep_hours[:-3]) / len(sleep_hours[:-3]) if len(sleep_hours) > 3 else sum(sleep_hours) / len(sleep_hours)
    recent_sleep = sum(sleep_hours[-3:]) / 3
    
    return recent_sleep - avg_sleep


def calculate_mood_trend(storage: Storage, days: int = 14) -> float:
    """Calculate trend in mood scores."""
    health_entries = storage.get_health_entries(
        start_date=date.today() - timedelta(days=days)
    )
    
    if not health_entries or len(health_entries) < 3:
        return 0.0
    
    # Map mood to numeric
    mood_map = {"great": 1.0, "good": 0.75, "okay": 0.5, "bad": 0.25}
    
    scores = [mood_map.get(e.mood, 0.5) for e in health_entries if e.mood]
    
    if len(scores) < 3:
        return 0.0
    
    # Simple trend: compare first half to second half
    mid = len(scores) // 2
    first_avg = sum(scores[:mid]) / mid if mid > 0 else 0.5
    second_avg = sum(scores[mid:]) / (len(scores) - mid) if len(scores) > mid else 0.5
    
    return max(-1.0, min(1.0, (second_avg - first_avg) * 4))


def count_recent_streak_breaks(storage: Storage, habits: List[Habit], days: int = 7) -> int:
    """Count streak breaks in the last N days."""
    today = date.today()
    breaks = 0
    
    for habit in habits:
        # Check if there was a completion before the window
        had_completion_before = False
        for i in range(days + 1, days + 7):
            check_date = today - timedelta(days=i)
            entry = storage.get_habit_entry(habit.id, check_date)
            if entry and not entry.skipped and entry.value > 0:
                had_completion_before = True
                break
        
        if not had_completion_before:
            continue
        
        # Count missed days in window
        for i in range(days):
            check_date = today - timedelta(days=i)
            entry = storage.get_habit_entry(habit.id, check_date)
            if not entry or (not entry.skipped and entry.value == 0):
                breaks += 1
                break  # Only count once per habit
    
    return breaks


def count_consecutive_missed_days(storage: Storage, habits: List[Habit]) -> int:
    """Count consecutive days with no completions."""
    if not habits:
        return 0
    
    today = date.today()
    missed = 0
    
    for i in range(30):  # Max 30 days
        check_date = today - timedelta(days=i)
        any_completed = False
        
        for habit in habits:
            entry = storage.get_habit_entry(habit.id, check_date)
            if entry and not entry.skipped and entry.value > 0:
                any_completed = True
                break
        
        if any_completed:
            break
        missed += 1
    
    return missed


def gather_habit_data_for_pcs(
    storage: Storage, 
    habit: Habit, 
    days: int = 30
) -> Tuple[List[bool], List[ContextVariables]]:
    """
    Gather completion and context data for PCS calculation.
    
    Returns:
        Tuple of (completion_history, context_history)
    """
    today = date.today()
    completions = []
    contexts = []
    
    # Get health entries for context
    health_entries = storage.get_health_entries(
        start_date=today - timedelta(days=days)
    )
    health_by_date = {e.entry_date: e for e in health_entries if e.entry_date}
    
    for i in range(days):
        check_date = today - timedelta(days=i)
        
        # Get completion status
        entry = storage.get_habit_entry(habit.id, check_date)
        completed = entry is not None and not entry.skipped and entry.value > 0
        completions.append(completed)
        
        # Get context for this date
        health = health_by_date.get(check_date)
        
        if health:
            context = ContextVariables(
                date=check_date.isoformat(),
                sleep_hours=health.sleep_hours,
                mood_score={"great": 1.0, "good": 0.75, "okay": 0.5, "bad": 0.25}.get(health.mood, 0.5),
                day_of_week=check_date.weekday()
            )
        else:
            # Default context
            context = ContextVariables(
                date=check_date.isoformat(),
                day_of_week=check_date.weekday()
            )
        
        contexts.append(context)
    
    # Reverse to get chronological order (oldest first)
    completions.reverse()
    contexts.reverse()
    
    return completions, contexts


def calculate_habit_correlations(
    storage: Storage,
    habits: List[Habit],
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Calculate correlations between habits.
    
    Returns:
        List of correlation results
    """
    if len(habits) < 2:
        return []
    
    today = date.today()
    habit_data = {}
    
    # Gather completion data for each habit
    for habit in habits:
        completions = []
        for i in range(days):
            check_date = today - timedelta(days=i)
            entry = storage.get_habit_entry(habit.id, check_date)
            completed = 1.0 if (entry and not entry.skipped and entry.value > 0) else 0.0
            completions.append(completed)
        habit_data[habit.name] = completions
    
    # Calculate correlations
    engine = CorrelationEngine()
    correlations = engine.analyze_habit_correlations(habit_data, min_samples=7)
    
    return [c.to_dict() for c in correlations]


# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

def render_sidebar():
    """Render sidebar with navigation."""
    with st.sidebar:
        st.title("🎯 Veryfyn")
        st.caption("Personal Tracking System")
        st.divider()
        
        # User Stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Level", st.session_state.user_level)
        with col2:
            st.metric("XP", st.session_state.user_xp)
        
        st.divider()
        
        # Navigation
        st.subheader("📊 Tracking")
        st.page_link("pages/dashboard.py", label="🏠 Dashboard", icon="🏠")
        st.page_link("pages/habits.py", label="✅ Habits", icon="✅")
        st.page_link("pages/tasks.py", label="📋 Tasks", icon="📋")
        st.page_link("pages/finances.py", label="💰 Finances", icon="💰")
        st.page_link("pages/health.py", label="❤️ Health", icon="❤️")
        st.page_link("pages/emotional_health.py", label="🌈 Emotional Health", icon="🌈")
        st.page_link("pages/time.py", label="⏱️ Time", icon="⏱️")
        st.page_link("pages/goals.py", label="🎯 Goals", icon="🎯")
        st.page_link("pages/achievements.py", label="🏆 Achievements", icon="🏆")
        
        st.divider()
        st.page_link("pages/insights.py", label="🧠 Insights", icon="🧠")


def render_header():
    """Render page header."""
    st.title("🧠 Intelligence Dashboard")
    st.markdown("AI-powered insights about your habits, health, and behavior.")


def render_burnout_section(storage: Storage):
    """Render burnout risk assessment section."""
    st.subheader("⚠️ Burnout Risk Assessment")
    
    # Gather indicators
    indicators = gather_burnout_indicators(storage)
    
    # Calculate risk
    predictor = BurnoutPredictor()
    risk = predictor.assess_risk(indicators)
    
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
    for corr in correlations[:5]:  # Top 5
        col1, col2, col3 = st.columns([2, 1, 3])
        
        with col1:
            st.markdown(f"**{corr['variable_x']}** ↔ **{corr['variable_y']}**")
        
        with col2:
            strength = corr['strength'].title()
            direction = "↗️" if corr['direction'] == "positive" else "↘️"
            color = "green" if corr['direction'] == "positive" else "red"
            st.markdown(f"r = **{corr['coefficient']:.2f}** {direction}")
        
        with col3:
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
    
    # Calculate PCS for each habit
    pcs_engine = PCSEngine()
    scores = []
    
    for habit in active_habits:
        completions, contexts = gather_habit_data_for_pcs(storage, habit)
        if len(completions) >= 14:  # Need at least 14 days
            score = pcs_engine.calculate_pcs(habit.id, habit.name, completions, contexts)
            scores.append(score)
    
    if not scores:
        st.info("Need at least 14 days of tracking data for PCS analysis.")
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
    predictor = BurnoutPredictor()
    risk = predictor.assess_risk(indicators)
    
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


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main page entry point."""
    # Initialize
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    render_header()
    st.divider()
    
    storage = st.session_state.storage
    
    # Render sections
    render_insights_summary(storage)
    st.divider()
    
    # Tabs for different insights
    tab1, tab2, tab3 = st.tabs(["Burnout Risk", "Correlations", "Habit Fragility"])
    
    with tab1:
        render_burnout_section(storage)
    
    with tab2:
        render_correlations_section(storage)
    
    with tab3:
        render_pcs_section(storage)


if __name__ == "__main__":
    main()
