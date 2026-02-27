"""
Burnout Risk Card Component

Displays burnout risk assessment with intervention suggestions.

Usage:
    from tracking_app.components.burnout_card import render_burnout_risk_card
    
    render_burnout_risk_card(risk, storage, habit_id)
"""
import streamlit as st
from typing import Dict, Optional, Any
from datetime import date

from brain.models.burnout import BurnoutRisk, BurnoutRiskLevel, ContributingFactor


# Risk level colors
RISK_COLORS = {
    BurnoutRiskLevel.LOW: "#4CAF50",  # Green
    BurnoutRiskLevel.MODERATE: "#FFC107",  # Yellow
    BurnoutRiskLevel.HIGH: "#FF9800",  # Orange
    BurnoutRiskLevel.CRITICAL: "#F44336",  # Red
}

# Risk level emojis
RISK_EMOJIS = {
    BurnoutRiskLevel.LOW: "🟢",
    BurnoutRiskLevel.MODERATE: "🟡",
    BurnoutRiskLevel.HIGH: "🟠",
    BurnoutRiskLevel.CRITICAL: "🔴",
}

# Trend indicators
TREND_ICONS = {
    "increasing": "📈",
    "stable": "➡️",
    "decreasing": "📉",
}


def render_burnout_risk_card(
    risk: BurnoutRisk,
    storage: Any,
    habit_id: str,
    show_dismiss: bool = True
) -> bool:
    """
    Render a burnout risk card.

    Args:
        risk: BurnoutRisk assessment to display
        storage: Storage instance for data access
        habit_id: ID of the habit
        show_dismiss: Whether to show dismiss button

    Returns:
        True if dismissed, False otherwise
    """
    # Don't show low risk cards
    if risk.risk_level == BurnoutRiskLevel.LOW:
        return False

    # Get intervention suggestion
    intervention = risk.get_intervention_suggestion()

    # Get top contributing factors
    top_factors = risk.get_top_factors(limit=3)

    # Color based on risk level
    color = RISK_COLORS.get(risk.risk_level, "#808080")
    emoji = RISK_EMOJIS.get(risk.risk_level, "⚪")
    trend_icon = TREND_ICONS.get(risk.trend, "➡️")

    # Create card with border color
    with st.container():
        # Header with risk level
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(
                f"""
                <div style="
                    padding: 0.75rem;
                    border-radius: 0.5rem;
                    border-left: 5px solid {color};
                    background: rgba(255,255,255,0.05);
                    margin-bottom: 0.5rem;
                ">
                    <div style="font-size: 1.1rem; font-weight: bold;">
                        {emoji} Burnout Risk: {risk.risk_level.value.upper()}
                        <span style="font-size: 0.9rem; margin-left: 0.5rem;">
                            {trend_icon} {risk.trend}
                        </span>
                    </div>
                    <div style="font-size: 0.85rem; color: gray; margin-top: 0.25rem;">
                        Score: {risk.risk_score:.1f}% · {intervention['title']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            # Dismiss button
            if show_dismiss:
                dismiss_key = f"dismiss_burnout_{habit_id}_{risk.assessment_date}"
                if st.button("✕", key=dismiss_key, help="Dismiss this warning"):
                    # Mark as acknowledged in session state
                    if "dismissed_burnout_warnings" not in st.session_state:
                        st.session_state.dismissed_burnout_warnings = set()
                    st.session_state.dismissed_burnout_warnings.add(f"{habit_id}_{risk.assessment_date}")
                    return True

        # Show intervention description
        st.markdown(f"**{intervention['description']}**")

        # Show contributing factors
        if top_factors:
            st.markdown("**Top Risk Factors:**")
            factor_cols = st.columns(min(len(top_factors), 3))
            for i, factor_data in enumerate(top_factors):
                with factor_cols[i]:
                    factor_name = _format_factor_name(factor_data["factor"])
                    weight_bar = "█" * int(factor_data["weight"] * 5)
                    st.markdown(
                        f"""
                        <div style="
                            font-size: 0.8rem;
                            padding: 0.25rem;
                            background: rgba(0,0,0,0.1);
                            border-radius: 0.25rem;
                            margin-bottom: 0.25rem;
                        ">
                            <div style="color: {color}; font-weight: bold;">
                                {weight_bar}
                            </div>
                            <div>{factor_name}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # Show action buttons based on intervention type
        _render_intervention_actions(intervention, habit_id, storage)

        return False


def _format_factor_name(factor_value: str) -> str:
    """
    Format factor name for display.

    Args:
        factor_value: Factor value (e.g., "declining_score_trend")

    Returns:
        Formatted name (e.g., "Declining Score Trend")
    """
    return factor_value.replace("_", " ").title()


def _render_intervention_actions(
    intervention: Dict[str, str],
    habit_id: str,
    storage: Any
) -> None:
    """
    Render action buttons based on intervention type.

    Args:
        intervention: Intervention suggestion dict
        habit_id: ID of the habit
        storage: Storage instance
    """
    action_type = intervention.get("action", "maintain")

    if action_type == "maintain":
        # No action needed for low risk
        return

    st.markdown("**Suggested Action:**")

    if action_type == "rest_day":
        # Suggest taking a rest day
        if st.button(
            "🛌 Take Rest Day",
            key=f"rest_day_{habit_id}",
            help="Skip today without breaking your streak",
            use_container_width=True
        ):
            # Mark habit as skipped for today
            from datetime import date
            storage.skip_habit(habit_id, date.today(), "Rest day - burnout prevention")
            st.success("✅ Rest day recorded! Your streak is preserved.")

    elif action_type == "modify_habit":
        # Suggest modifying the habit
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "✏️ Make It Easier",
                key=f"modify_easier_{habit_id}",
                help="Reduce the habit scope",
                use_container_width=True
            ):
                # Open edit form with suggestion to reduce scope
                if "editing_habit" not in st.session_state:
                    st.session_state.editing_habit = habit_id
                st.info("💡 Consider reducing the habit target by 50%")

        with col2:
            if st.button(
                "📝 Edit Habit",
                key=f"modify_edit_{habit_id}",
                help="Edit habit details",
                use_container_width=True
            ):
                if "editing_habit" not in st.session_state:
                    st.session_state.editing_habit = habit_id

    elif action_type == "create_plan":
        # Suggest creating a relapse prevention plan
        if st.button(
            "📋 Create Prevention Plan",
            key=f"create_plan_{habit_id}",
            help="Create a plan to prevent relapse",
            use_container_width=True
        ):
            # Show plan creation UI
            st.info("📝 Plan creation would go here (see Phase 1.3)")
            # TODO: Implement relapse prevention plan creation


def render_burnout_summary_card(
    at_risk_count: int,
    total_habits: int,
    highest_risk_level: Optional[BurnoutRiskLevel] = None
) -> None:
    """
    Render a burnout summary card for the dashboard.

    Args:
        at_risk_count: Number of habits with elevated risk
        total_habits: Total number of active habits
        highest_risk_level: Highest risk level among all habits
    """
    if at_risk_count == 0:
        # All clear
        st.success(
            f"🎉 All {total_habits} habits are healthy! "
            "Keep up the great work!"
        )
        return

    # Determine overall status
    if highest_risk_level == BurnoutRiskLevel.CRITICAL:
        status_emoji = "🚨"
        status_color = "#F44336"
        status_text = "Critical attention needed"
    elif highest_risk_level == BurnoutRiskLevel.HIGH:
        status_emoji = "⚠️"
        status_color = "#FF9800"
        status_text = "Intervention recommended"
    else:
        status_emoji = "👀"
        status_color = "#FFC107"
        status_text = "Monitor closely"

    st.markdown(
        f"""
        <div style="
            padding: 1rem;
            border-radius: 0.5rem;
            border: 2px solid {status_color};
            background: rgba(255,255,255,0.05);
        ">
            <div style="font-size: 1.2rem; font-weight: bold;">
                {status_emoji} {at_risk_count}/{total_habits} habits at risk
            </div>
            <div style="font-size: 0.9rem; color: gray; margin-top: 0.25rem;">
                {status_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def is_warning_dismissed(habit_id: str, assessment_date: date) -> bool:
    """
    Check if a burnout warning has been dismissed.

    Args:
        habit_id: ID of the habit
        assessment_date: Date of the risk assessment

    Returns:
        True if dismissed, False otherwise
    """
    if "dismissed_burnout_warnings" not in st.session_state:
        return False

    key = f"{habit_id}_{assessment_date}"
    return key in st.session_state.dismissed_burnout_warnings


__all__ = [
    "render_burnout_risk_card",
    "render_burnout_summary_card",
    "is_warning_dismissed",
]
