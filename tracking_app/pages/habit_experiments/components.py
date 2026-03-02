"""
UI components for the Habit Experiments page.

Contains all render functions for the experiments interface.
"""

from typing import Dict, Any, List
from datetime import date

import streamlit as st

from brain.models.experiment import (
    ExperimentStatus,
    ExperimentType,
    EXPERIMENT_TEMPLATES,
)
from brain.models.experiment import create_experiment_from_template

from .constants import (
    MIN_DURATION_DAYS,
    MAX_DURATION_DAYS,
    DEFAULT_DURATION_DAYS,
    DEFAULT_VARIANT_A_NAME,
    DEFAULT_VARIANT_B_NAME,
)
from .helpers import (
    get_habit_options,
    calculate_experiment_progress,
    get_days_running,
    determine_winner,
    format_rate_as_percentage,
)


def render_template_browser(tracker) -> None:
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
            habit_options = get_habit_options(st.session_state.storage)
            
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


def render_active_experiments(tracker) -> None:
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
                days_running = get_days_running(exp.start_date)
                progress = calculate_experiment_progress(exp.start_date, exp.duration_days)
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


def render_custom_experiment(tracker) -> None:
    """
    Render custom experiment creator.
    
    Args:
        tracker: ExperimentTracker instance
    """
    st.markdown("**➕ Create Custom Experiment**")
    
    with st.form("custom_experiment_form"):
        # Get habits
        habit_options = get_habit_options(st.session_state.storage)
        
        selected_habit = st.selectbox("Select habit", list(habit_options.keys()))
        
        name = st.text_input("Experiment Name", placeholder="e.g., Morning vs Evening")
        hypothesis = st.text_area("Hypothesis", placeholder="I will be more consistent when...")
        
        col1, col2 = st.columns(2)
        with col1:
            variant_a_name = st.text_input("Variant A Name", value=DEFAULT_VARIANT_A_NAME)
            variant_a_desc = st.text_area("Variant A Description")
        with col2:
            variant_b_name = st.text_input("Variant B Name", value=DEFAULT_VARIANT_B_NAME)
            variant_b_desc = st.text_area("Variant B Description")
        
        duration = st.slider(
            "Duration (days)",
            MIN_DURATION_DAYS,
            MAX_DURATION_DAYS,
            DEFAULT_DURATION_DAYS
        )
        
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


def render_experiment_history(tracker) -> None:
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
                a_rate = results.get("variant_a_rate", 0)
                b_rate = results.get("variant_b_rate", 0)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Variant A", format_rate_as_percentage(a_rate))
                with col2:
                    st.metric("Variant B", format_rate_as_percentage(b_rate))
                
                winner = determine_winner(results)
                st.success(f"🏆 Winner: {winner}")
            else:
                st.caption("No results data")