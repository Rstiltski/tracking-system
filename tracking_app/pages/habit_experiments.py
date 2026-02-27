"""
Habit Experiments Page - A/B testing for habits.

Usage:
    streamlit run tracking_app/pages/habit_experiments.py
"""
import streamlit as st
from datetime import date, timedelta
from typing import Dict, Any

from brain.models.experiment import (
    ExperimentStatus,
    ExperimentType,
    EXPERIMENT_TEMPLATES,
)
from brain.analytics.experiment_tracker import ExperimentTracker


# Page configuration
st.set_page_config(
    page_title="Habit Experiments - Veryfyn",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main experiments page."""
    # Initialize
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()

    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""

    storage = st.session_state.storage
    user_id = st.session_state.user_id

    # Header
    st.title("🧪 Habit Experiments")
    st.markdown("Test different approaches to find what works best for you!")

    # Initialize tracker
    tracker = ExperimentTracker(storage, user_id)

    # Tabs
    tab_browse, tab_active, tab_create, tab_history = st.tabs([
        "📋 Browse Templates",
        "🔄 Active Experiments",
        "➕ Create Custom",
        "📜 History"
    ])

    with tab_browse:
        render_template_browser(tracker)

    with tab_active:
        render_active_experiments(tracker)

    with tab_create:
        render_custom_experiment(tracker)

    with tab_history:
        render_experiment_history(tracker)


def render_template_browser(tracker: ExperimentTracker) -> None:
    """
    Render experiment template browser.

    Args:
        tracker: ExperimentTracker instance
    """
    st.markdown("**📋 Pre-built Experiment Templates**")

    for key, template in EXPERIMENT_TEMPLATES.items():
        with st.expander(
            f"**{template['name']}** - {template['duration_days']} days"
        ):
            st.markdown(f"*{template['hypothesis']}*")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Variant A:** {template['variant_a']['name']}")
                st.caption(template['variant_a']['description'])
            with col2:
                st.info(f"**Variant B:** {template['variant_b']['name']}")
                st.caption(template['variant_b']['description'])

            # Get habits for experiment
            habits = st.session_state.storage.get_habits(include_archived=False)
            habit_options = {f"{h.icon if hasattr(h, 'icon') else '🎯'} {h.name}": h.id for h in habits}
            
            selected_habit = st.selectbox(
                "Select habit to test",
                options=list(habit_options.keys()),
                key=f"template_{key}"
            )

            if st.button(
                "Start Experiment",
                key=f"start_{key}",
                type="primary"
            ):
                from brain.models.experiment import create_experiment_from_template
                try:
                    experiment = create_experiment_from_template(
                        key,
                        habit_options[selected_habit],
                        st.session_state.user_id
                    )
                    experiment.status = ExperimentStatus.ACTIVE
                    experiment.start_date = date.today()
                    tracker.storage.save_experiment(experiment.to_dict())
                    st.success(f"✅ Started experiment: {template['name']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")


def render_active_experiments(tracker: ExperimentTracker) -> None:
    """
    Render active experiments.

    Args:
        tracker: ExperimentTracker instance
    """
    st.markdown("**🔄 Active Experiments**")

    experiments = tracker.get_experiments(ExperimentStatus.ACTIVE)

    if not experiments:
        st.info("No active experiments. Start one from the templates!")
        return

    for exp in experiments:
        with st.container():
            st.markdown(f"**{exp.name}**")
            st.caption(f"Hypothesis: {exp.hypothesis}")

            # Progress
            if exp.start_date:
                days_running = (date.today() - exp.start_date).days
                progress = min(1.0, days_running / exp.duration_days)
                st.progress(progress)
                st.caption(f"Day {days_running} of {exp.duration_days}")

            # Record result
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✓ A Complete", key=f"complete_a_{exp.id}"):
                    tracker.record_result(exp.id, "A", True)
                    st.success("Recorded!")
                    st.rerun()
            with col2:
                if st.button("✓ B Complete", key=f"complete_b_{exp.id}"):
                    tracker.record_result(exp.id, "B", True)
                    st.success("Recorded!")
                    st.rerun()
            with col3:
                if st.button("End Experiment", key=f"end_{exp.id}"):
                    results = tracker.calculate_results(exp.id)
                    tracker.end_experiment(exp.id, results)
                    st.success("Experiment completed!")
                    st.rerun()

            st.divider()


def render_custom_experiment(tracker: ExperimentTracker) -> None:
    """
    Render custom experiment creator.

    Args:
        tracker: ExperimentTracker instance
    """
    st.markdown("**➕ Create Custom Experiment**")

    with st.form("custom_experiment_form"):
        # Get habits
        habits = st.session_state.storage.get_habits(include_archived=False)
        habit_options = {f"{h.icon if hasattr(h, 'icon') else '🎯'} {h.name}": h.id for h in habits}
        
        selected_habit = st.selectbox("Select habit", list(habit_options.keys()))

        name = st.text_input("Experiment Name", placeholder="e.g., Morning vs Evening")
        hypothesis = st.text_area("Hypothesis", placeholder="I will be more consistent when...")

        col1, col2 = st.columns(2)
        with col1:
            variant_a_name = st.text_input("Variant A Name", value="A")
            variant_a_desc = st.text_area("Variant A Description")
        with col2:
            variant_b_name = st.text_input("Variant B Name", value="B")
            variant_b_desc = st.text_area("Variant B Description")

        duration = st.slider("Duration (days)", 7, 30, 14)

        submitted = st.form_submit_button("Create Experiment", type="primary")

        if submitted and name and hypothesis:
            experiment = tracker.create_experiment(
                habit_id=habit_options[selected_habit],
                name=name,
                hypothesis=hypothesis,
                variant_a={"name": variant_a_name, "description": variant_a_desc},
                variant_b={"name": variant_b_name, "description": variant_b_desc},
                duration_days=duration
            )
            experiment.status = ExperimentStatus.ACTIVE
            experiment.start_date = date.today()
            tracker.storage.save_experiment(experiment.to_dict())
            st.success(f"✅ Created experiment: {name}")
            st.rerun()


def render_experiment_history(tracker: ExperimentTracker) -> None:
    """
    Render experiment history.

    Args:
        tracker: ExperimentTracker instance
    """
    st.markdown("**📜 Experiment History**")

    experiments = tracker.get_experiments(ExperimentStatus.COMPLETED)

    if not experiments:
        st.info("No completed experiments yet")
        return

    for exp in experiments:
        with st.expander(f"**{exp.name}** - {exp.hypothesis}"):
            results = exp.results
            
            if results:
                a_rate = results.get("variant_a_rate", 0) * 100
                b_rate = results.get("variant_b_rate", 0) * 100

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Variant A", f"{a_rate:.0f}%")
                with col2:
                    st.metric("Variant B", f"{b_rate:.0f}%")

                winner = "B" if b_rate > a_rate else "A" if a_rate > b_rate else "Tie"
                st.success(f"🏆 Winner: {winner}")
            else:
                st.caption("No results data")


if __name__ == "__main__":
    main()
