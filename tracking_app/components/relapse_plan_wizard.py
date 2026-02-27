"""
Relapse Prevention Plan Wizard - UI for creating and managing plans.

Provides UI components for:
- Creating prevention plans from templates
- Custom plan creation
- Viewing active plans
- Recording plan usage
- Tracking effectiveness

Usage:
    from tracking_app.components.relapse_plan_wizard import render_plan_wizard
    
    render_plan_wizard(storage, habit_id, habit_name)
"""
import streamlit as st
from typing import Dict, Optional, Any, List, Callable
from datetime import date

from brain.models.relapse_plan import (
    PlanCategory,
    PlanTrigger,
    RelapsePreventionPlan,
    PlanTemplate,
    DEFAULT_PLAN_TEMPLATES,
)
from brain.behavioral.relapse_plan_manager import (
    RelapsePlanManager,
    get_plan_recommendations,
)


# Category emojis and descriptions
CATEGORY_INFO = {
    PlanCategory.MISSED_DAY: {
        "emoji": "📅",
        "label": "Missed Day",
        "description": "Plan for getting back on track",
    },
    PlanCategory.TRAVEL: {
        "emoji": "✈️",
        "label": "Travel",
        "description": "Plan for when away from home",
    },
    PlanCategory.LOW_MOTIVATION: {
        "emoji": "😴",
        "label": "Low Motivation",
        "description": "Plan for low willpower days",
    },
    PlanCategory.TIME_CRUNCH: {
        "emoji": "⏰",
        "label": "Time Crunch",
        "description": "Plan for busy days",
    },
    PlanCategory.STRESS: {
        "emoji": "😰",
        "label": "High Stress",
        "description": "Plan for overwhelming periods",
    },
    PlanCategory.SOCIAL: {
        "emoji": "👥",
        "label": "Social",
        "description": "Plan for social conflicts",
    },
    PlanCategory.CUSTOM: {
        "emoji": "📋",
        "label": "Custom",
        "description": "Your own plan",
    },
}


def render_plan_wizard(
    storage: Any,
    habit_id: str,
    habit_name: str,
    on_plan_created: Optional[Callable] = None
) -> None:
    """
    Render the relapse prevention plan wizard.

    Args:
        storage: Storage instance
        habit_id: ID of the habit
        habit_name: Name of the habit
        on_plan_created: Optional callback when plan is created
    """
    # Initialize manager
    manager = RelapsePlanManager(storage, habit_id)

    # Wizard container
    with st.container():
        st.markdown("**🛡️ Relapse Prevention Plans**")
        st.caption("Create if-then plans to protect your habit")

        # Check if user has any plans
        existing_plans = manager.get_active_plans()

        if not existing_plans:
            # Show getting started
            _render_plan_intro(manager, habit_name, on_plan_created, habit_id)
        else:
            # Show existing plans with option to add more
            _render_existing_plans(manager, on_plan_created, habit_id)

        # Show plan usage history
        st.divider()
        _render_plan_usage_history(manager)


def _render_plan_intro(
    manager: RelapsePlanManager,
    habit_name: str,
    on_plan_created: Optional[Callable] = None,
    habit_id: Optional[str] = None
) -> None:
    """
    Render introduction for new users.

    Args:
        manager: RelapsePlanManager instance
        habit_name: Name of the habit
        on_plan_created: Optional callback
        habit_id: Optional habit ID for unique keys
    """
    st.info(
        f"""
        **Why create a prevention plan?**

        Research shows that people who create "if-then" plans are **2-3x more likely**
        to stick with their habits, especially during challenging times.

        Your plan will help you stay on track when:
        - You miss a day
        - You're traveling or busy
        - Your motivation is low
        - Life gets stressful
        """
    )

    # Get personalized recommendations
    recommendations = manager.get_suggested_plans()

    if recommendations:
        st.markdown("**💡 Recommended Plans for You:**")
        for template in recommendations[:3]:
            _render_template_card(manager, template, on_plan_created, habit_id)

    # Option to create custom plan
    with st.expander("✏️ Create Custom Plan"):
        _render_custom_plan_form(manager, on_plan_created)


def _render_template_card(
    manager: RelapsePlanManager,
    template: PlanTemplate,
    on_plan_created: Optional[Callable] = None,
    habit_id: Optional[str] = None
) -> None:
    """
    Render a plan template card.

    Args:
        manager: RelapsePlanManager instance
        template: Template to display
        on_plan_created: Optional callback
        habit_id: Optional habit ID for unique keys
    """
    category_info = CATEGORY_INFO.get(
        template.category,
        CATEGORY_INFO[PlanCategory.CUSTOM]
    )

    # Create unique key prefix with habit_id if provided
    key_prefix = f"{habit_id}_" if habit_id else ""

    with st.container():
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(
                f"**{category_info['emoji']} {template.name}**"
            )
            st.caption(template.description)
            st.markdown(
                f"*If {template.if_condition}, "
                f"then I will {template.then_action}*"
            )

            if template.backup_plan:
                st.caption(f"🔄 Backup: {template.backup_plan}")

            if template.effectiveness_rating > 0:
                stars = "⭐" * round(template.effectiveness_rating)
                st.caption(f"User effectiveness: {stars}")

        with col2:
            if st.button(
                "Use This",
                key=f"{key_prefix}use_template_{template.id}",
                type="primary",
                use_container_width=True
            ):
                # Create plan from template
                plan = manager.create_plan_from_template(template)
                st.success(f"✅ Plan created: {template.name}")
                if on_plan_created:
                    on_plan_created(plan)
                st.rerun()


def _render_custom_plan_form(
    manager: RelapsePlanManager,
    on_plan_created: Optional[Callable] = None
) -> None:
    """
    Render custom plan creation form.

    Args:
        manager: RelapsePlanManager instance
        on_plan_created: Optional callback
    """
    with st.form("custom_plan_form"):
        # Category selection
        category = st.selectbox(
            "Plan Category",
            options=[c.value for c in PlanCategory],
            format_func=lambda x: CATEGORY_INFO.get(
                PlanCategory(x),
                CATEGORY_INFO[PlanCategory.CUSTOM]
            )["label"]
        )

        # If condition
        st.markdown("**The IF part:**")
        if_condition = st.text_input(
            "When will you use this plan?",
            placeholder="e.g., I miss a day, I'm traveling, I'm too busy..."
        )

        # Then action
        st.markdown("**The THEN part:**")
        then_action = st.text_area(
            "What will you do?",
            placeholder="e.g., do a 2-minute version, reschedule for tomorrow...",
            height=80
        )

        # Action type
        action_type = st.selectbox(
            "Type of Action",
            options=["reduce", "reschedule", "substitute", "skip"],
            format_func=lambda x: x.title()
        )

        # Backup plan
        backup_plan = st.text_input(
            "Backup Plan (optional)",
            placeholder="What if the primary plan fails?"
        )

        submitted = st.form_submit_button("Create Plan", type="primary")

        if submitted and if_condition and then_action:
            plan = manager.create_plan(
                category=PlanCategory(category),
                if_condition=if_condition,
                then_action=then_action,
                action_type=action_type,
                backup_plan=backup_plan
            )
            st.success(f"✅ Plan created!")
            if on_plan_created:
                on_plan_created(plan)
            st.rerun()
        elif submitted:
            st.error("Please fill in both the IF and THEN parts")


def _render_existing_plans(
    manager: RelapsePlanManager,
    on_plan_created: Optional[Callable] = None,
    habit_id: Optional[str] = None
) -> None:
    """
    Render existing plans section.

    Args:
        manager: RelapsePlanManager instance
        on_plan_created: Optional callback
        habit_id: Optional habit ID for unique keys
    """
    plans = manager.get_plans(active_only=False)

    # Show active plans
    active_plans = [p for p in plans if p.is_active]
    if active_plans:
        st.markdown(f"**✅ {len(active_plans)} Active Plan(s)**")

        for plan in active_plans:
            _render_plan_card(manager, plan)

    # Show inactive plans in expander
    inactive_plans = [p for p in plans if not p.is_active]
    if inactive_plans:
        with st.expander(f"⏸️ {len(inactive_plans)} Inactive Plan(s)"):
            for plan in inactive_plans:
                _render_plan_card(manager, plan, show_activate=True)

    st.divider()

    # Add new plan button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add New Plan", use_container_width=True):
            st.session_state.show_new_plan_form = True
            st.rerun()

    with col2:
        if st.button("📋 Use Template", use_container_width=True):
            st.session_state.show_template_browser = True
            st.rerun()

    # Show new plan form if requested
    if st.session_state.get("show_new_plan_form", False):
        with st.form("new_plan_form"):
            _render_quick_plan_form(manager, on_plan_created)

    # Show template browser if requested
    if st.session_state.get("show_template_browser", False):
        with st.container():
            st.markdown("**📋 Browse Templates**")
            for template in DEFAULT_PLAN_TEMPLATES:
                _render_template_card(manager, template, on_plan_created, habit_id)

            if st.button("Close Templates"):
                st.session_state.show_template_browser = False
                st.rerun()


def _render_plan_card(
    manager: RelapsePlanManager,
    plan: RelapsePreventionPlan,
    show_activate: bool = False
) -> None:
    """
    Render a single plan card.

    Args:
        manager: RelapsePlanManager instance
        plan: Plan to display
        show_activate: Whether to show activate button
    """
    category_info = CATEGORY_INFO.get(
        plan.category,
        CATEGORY_INFO[PlanCategory.CUSTOM]
    )

    with st.expander(
        f"{category_info['emoji']} {plan.get_if_then_text()}",
        expanded=False
    ):
        # Plan details
        st.caption(f"**Category:** {category_info['label']}")
        st.caption(f"**Action Type:** {plan.action_type.title()}")

        if plan.backup_plan:
            st.caption(f"🔄 **Backup:** {plan.backup_plan}")

        # Usage stats
        if plan.usage_count > 0:
            st.caption(f"📊 Used {plan.usage_count} time(s)")
            if plan.effectiveness:
                stars = "⭐" * plan.effectiveness
                st.caption(f"Effectiveness: {stars}")

        # Action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                "📝 Record Usage",
                key=f"record_usage_{plan.id}",
                use_container_width=True
            ):
                st.session_state[f"record_usage_{plan.id}"] = True
                st.rerun()

        with col2:
            if show_activate:
                if st.button(
                    "✅ Activate",
                    key=f"activate_{plan.id}",
                    use_container_width=True
                ):
                    manager.activate_plan(plan.id)
                    st.success("Plan activated!")
                    st.rerun()
            else:
                if st.button(
                    "⏸️ Deactivate",
                    key=f"deactivate_{plan.id}",
                    use_container_width=True
                ):
                    manager.deactivate_plan(plan.id)
                    st.success("Plan deactivated")
                    st.rerun()

        with col3:
            if st.button(
                "🗑️ Delete",
                key=f"delete_{plan.id}",
                use_container_width=True
            ):
                # Confirm deletion
                if "confirm_delete" not in st.session_state:
                    st.session_state.confirm_delete = plan.id
                    st.rerun()
                elif st.session_state.confirm_delete == plan.id:
                    manager.delete_plan(plan.id)
                    st.success("Plan deleted")
                    st.session_state.confirm_delete = None
                    st.rerun()
                else:
                    st.warning("Click delete again to confirm")

        # Show usage recording form if requested
        if st.session_state.get(f"record_usage_{plan.id}", False):
            _render_usage_form(manager, plan)


def _render_quick_plan_form(
    manager: RelapsePlanManager,
    on_plan_created: Optional[Callable] = None
) -> None:
    """
    Render quick plan creation form.

    Args:
        manager: RelapsePlanManager instance
        on_plan_created: Optional callback
    """
    st.markdown("**Create a Quick Plan**")

    category = st.selectbox(
        "Category",
        options=[c.value for c in PlanCategory],
        format_func=lambda x: CATEGORY_INFO.get(
            PlanCategory(x),
            CATEGORY_INFO[PlanCategory.CUSTOM]
        )["label"]
    )

    col1, col2 = st.columns(2)
    with col1:
        if_condition = st.text_input(
            "IF...",
            placeholder="When will you use this?"
        )
    with col2:
        then_action = st.text_input(
            "THEN...",
            placeholder="What will you do?"
        )

    action_type = st.selectbox(
        "Action Type",
        options=["reduce", "reschedule", "substitute", "skip"]
    )

    backup_plan = st.text_input("Backup Plan (optional)")

    col_create, col_cancel = st.columns(2)
    with col_create:
        submitted = st.form_submit_button("Create Plan", type="primary")
        if submitted and if_condition and then_action:
            plan = manager.create_plan(
                category=PlanCategory(category),
                if_condition=if_condition,
                then_action=then_action,
                action_type=action_type,
                backup_plan=backup_plan
            )
            st.success("✅ Plan created!")
            st.session_state.show_new_plan_form = False
            if on_plan_created:
                on_plan_created(plan)
            st.rerun()

    with col_cancel:
        if st.form_submit_button("Cancel"):
            st.session_state.show_new_plan_form = False
            st.rerun()


def _render_usage_form(
    manager: RelapsePlanManager,
    plan: RelapsePreventionPlan
) -> None:
    """
    Render plan usage recording form.

    Args:
        manager: RelapsePlanManager instance
        plan: Plan to record usage for
    """
    st.markdown("**📝 Record Plan Usage**")

    with st.form(f"usage_form_{plan.id}"):
        situation = st.text_input(
            "What situation triggered this plan?",
            value=plan.if_condition
        )

        action_taken = st.text_input(
            "What action did you take?",
            value=plan.then_action
        )

        effectiveness = st.slider(
            "How effective was this plan?",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Not effective, 5 = Very effective"
        )

        notes = st.text_area("Additional notes (optional)")

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Save Usage", type="primary")
            if submitted:
                manager.record_plan_usage(
                    plan.id,
                    situation=situation,
                    action_taken=action_taken,
                    effectiveness=effectiveness,
                    notes=notes
                )
                st.success("✅ Usage recorded!")
                st.session_state[f"record_usage_{plan.id}"] = False
                st.rerun()

        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state[f"record_usage_{plan.id}"] = False
                st.rerun()


def _render_plan_usage_history(
    manager: RelapsePlanManager
) -> None:
    """
    Render plan usage history section.

    Args:
        manager: RelapsePlanManager instance
    """
    usage_history = manager.get_plan_usage_history(limit=10)

    if not usage_history:
        st.caption("📝 No plan usage recorded yet")
        return

    st.markdown("**📜 Recent Plan Usage**")

    for usage in usage_history[:5]:
        used_date = usage.used_at[:10] if hasattr(usage.used_at, '__str__') else str(usage.used_at)[:10]

        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.caption(
                    f"**{used_date}:** {usage.situation[:50]}..."
                )
            with col2:
                if usage.effectiveness:
                    stars = "⭐" * usage.effectiveness
                    st.caption(stars)


def render_plan_quick_actions(
    storage: Any,
    habit_id: str
) -> None:
    """
    Render quick action buttons for plans.

    Args:
        storage: Storage instance
        habit_id: ID of the habit
    """
    manager = RelapsePlanManager(storage, habit_id)

    # Check for triggered plans
    triggered = manager.check_triggers()

    if triggered:
        st.warning(
            f"⚠️ **{len(triggered)} plan(s) triggered!** "
            f"Review your prevention plans."
        )

        for plan in triggered:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{plan.get_if_then_text()}**")
            with col2:
                if st.button(
                    "Review",
                    key=f"review_triggered_{plan.id}",
                    use_container_width=True
                ):
                    st.session_state[f"review_plan_{plan.id}"] = True


__all__ = [
    "render_plan_wizard",
    "render_plan_quick_actions",
]
