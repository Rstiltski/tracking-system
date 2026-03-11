"""
Energy Dashboard Page

Track energy, not just time. Schedule tasks to circadian peaks.

Based on Task 11.2.2 from PHASE_11_INTEGRATION_ROADMAP.md
"""

import streamlit as st
from datetime import datetime, time


def render_energy_dashboard(manager, user_id: str) -> None:
    """
    Render the energy dashboard.
    
    Args:
        manager: EnergyManager instance
        user_id: User ID
    """
    st.markdown("⚡ Energy Manager")
    st.markdown("*Track energy, not just time. Schedule tasks to your natural peaks.*")
    
    # Get summary
    summary = manager.get_energy_summary(user_id)
    
    # Current energy display
    st.markdown("### 🔋 Current Energy")
    
    current = summary["current_energy"]
    
    # Color based on energy
    energy_colors = {
        "VERY_LOW": "🔴",
        "LOW": "🟠", 
        "MODERATE": "🟡",
        "HIGH": "🟢",
        "PEAK": "⚡"
    }
    
    emoji = energy_colors.get(current, "⚪")
    st.success(f"{emoji} **{current.replace('_', ' ')}**")
    
    # Energy curve visualization
    render_energy_curve(manager, user_id)
    
    st.markdown("---")
    
    # Log energy section
    render_energy_logger(manager, user_id)
    
    st.markdown("---")
    
    # Task timing suggestions
    render_task_suggester(manager, user_id)
    
    st.markdown("---")
    
    # Profile settings
    render_profile_settings(manager, user_id)


def render_energy_curve(manager, user_id: str) -> None:
    """Render 24-hour energy curve."""
    st.markdown("### 📈 Your Energy Curve")
    
    profile = manager.get_or_create_profile(user_id)
    
    # Create hourly data
    hours = list(range(24))
    energies = []
    
    for h in hours:
        level = profile.get_energy_at(h)
        energies.append(level.value)
    
    # Display as bar chart
    cols = st.columns(24)
    
    for i, (h, e) in enumerate(zip(hours, energies)):
        # Color based on energy
        colors = {
            1: "🔴",
            2: "🟠",
            3: "🟡",
            4: "🟢",
            5: "⚡"
        }
        
        with cols[i]:
            st.write(f"{h}")
            st.write(colors.get(e, "⚪"))
    
    # Peak hours legend
    peak = profile.get_peak_hours()
    st.caption(f"⚡ Peak hours: {peak}")


def render_energy_logger(manager, user_id: str) -> None:
    """Render energy logging form."""
    st.markdown("### 📝 Log Energy")
    
    from brain.models.energy import EnergyType, EnergyLevel
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        energy_type = st.selectbox(
            "Energy Type",
            [e.name for e in EnergyType]
        )
    
    with col2:
        level = st.select_slider(
            "Energy Level",
            options=[e.name for e in EnergyLevel],
            value="MODERATE"
        )
    
    with col3:
        note = st.text_input("Note (optional)", placeholder="e.g., After lunch...")
    
    if st.button("Log Energy"):
        energy_type_enum = EnergyType[energy_type]
        level_enum = EnergyLevel[level]
        
        manager.log_energy(
            user_id=user_id,
            energy_type=energy_type_enum,
            level=level_enum,
            note=note if note else None
        )
        
        st.success("Energy logged! ⚡")


def render_task_suggester(manager, user_id: str) -> None:
    """Render task timing suggestions."""
    st.markdown("### 🎯 Task Timing Suggestions")
    
    from brain.models.energy import EnergyLevel
    
    col1, col2 = st.columns(2)
    
    with col1:
        task_name = st.text_input("Task Name", placeholder="e.g., Deep work session")
    
    with col2:
        required = st.selectbox(
            "Required Energy",
            [e.name for e in EnergyLevel]
        )
    
    if st.button("Get Timing Suggestion") and task_name:
        from brain.models.energy import EnergyLevel
        
        required_level = EnergyLevel[required]
        
        suggestion = manager.suggest_task_timing(
            task_name=task_name,
            required_energy=required_level,
            user_id=user_id
        )
        
        if suggestion.recommended_time:
            st.success(f"🕐 **Best time:** {suggestion.recommended_time.strftime('%H:%M')}")
            st.info(f"💡 {suggestion.reason}")
        else:
            st.warning(f"⚠️ {suggestion.reason}")


def render_profile_settings(manager, user_id: str) -> None:
    """Render circadian profile settings."""
    st.markdown("### ⚙️ Circadian Profile")
    
    profile = manager.get_or_create_profile(user_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        wake = st.time_input("Wake Time", value=profile.wake_time)
    
    with col2:
        sleep = st.time_input("Sleep Time", value=profile.sleep_time)
    
    if st.button("Update Profile"):
        manager.update_profile(
            user_id=user_id,
            wake_time=wake,
            sleep_time=sleep
        )
        
        st.success("Profile updated! ✅")


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import streamlit as st
    from brain.models.energy import create_manager, EnergyType, EnergyLevel
    
    st.set_page_config(page_title="Energy Manager Test")
    
    st.title("⚡ Energy Manager Test")
    
    manager = create_manager()
    
    # Log some energy
    manager.log_energy(
        user_id="test",
        energy_type=EnergyType.PHYSICAL,
        level=EnergyLevel.HIGH,
        note="After coffee"
    )
    
    # Show dashboard
    render_energy_dashboard(manager, "test")
