"""
UI components for the Leaderboards page.

Contains all render functions for the competitions interface.
"""

from datetime import date, timedelta
from typing import Dict, Any, List

import streamlit as st

from brain.models.competition import CompetitionType, CompetitionStatus

from .constants import (
    DEFAULT_MAX_PARTICIPANTS,
    DEFAULT_IS_PUBLIC,
    LEADERBOARD_TOP_DISPLAY_COUNT,
)
from .helpers import (
    calculate_days_remaining,
    calculate_progress,
    format_competition_type,
    get_medal_for_position,
    get_default_end_date,
)


def render_active_competitions(manager) -> None:
    """
    Render active competitions tab.
    
    Args:
        manager: LeaderboardManager instance
    """
    st.markdown("**🔥 Active Competitions**")
    
    competitions = manager.get_competitions(CompetitionStatus.ACTIVE)
    
    if not competitions:
        st.info("No active competitions. Create one or join a friend's competition!")
        return
    
    for comp in competitions:
        with st.container():
            st.markdown(f"### {comp['name']}")
            
            # Competition info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Type", format_competition_type(comp['competition_type']))
            with col2:
                days_left = calculate_days_remaining(comp['end_date'])
                st.metric("Ends In", f"{days_left} days")
            with col3:
                st.metric("Participants", "TBD")
            
            # Progress bar
            progress = calculate_progress(comp['start_date'], comp['end_date'])
            st.progress(progress)
            
            # Join button
            if st.button("🎯 Join Competition", key=f"join_{comp['id']}"):
                manager.join_competition(comp['id'])
                st.success("✅ Joined competition!")
                st.rerun()
            
            # Show leaderboard
            with st.expander("📊 View Leaderboard"):
                _render_leaderboard(manager, comp['id'])
            
            st.divider()


def render_create_competition(manager) -> None:
    """
    Render create competition tab.
    
    Args:
        manager: LeaderboardManager instance
    """
    st.markdown("**➕ Create New Competition**")
    
    with st.form("create_competition_form"):
        name = st.text_input("Competition Name", placeholder="e.g., Week Long Streak Challenge")
        
        comp_type = st.selectbox(
            "Competition Type",
            options=[t.value for t in CompetitionType],
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today())
        with col2:
            end_date = st.date_input("End Date", value=get_default_end_date())
        
        max_participants = st.number_input(
            "Max Participants (0 = unlimited)",
            min_value=0,
            value=DEFAULT_MAX_PARTICIPANTS
        )
        
        is_public = st.checkbox("Public Competition", value=DEFAULT_IS_PUBLIC)
        
        prize = st.text_input("Prize (optional)", placeholder="e.g., Bragging rights!")
        
        submitted = st.form_submit_button("Create Competition", type="primary")
        
        if submitted and name:
            manager.create_competition(
                name=name,
                competition_type=comp_type,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                max_participants=max_participants,
                is_public=is_public,
                prize=prize
            )
            st.success(f"✅ Created competition: {name}")
            st.rerun()


def render_archive(manager) -> None:
    """
    Render archive tab.
    
    Args:
        manager: LeaderboardManager instance
    """
    st.markdown("**📜 Past Competitions**")
    
    competitions = manager.get_competitions(CompetitionStatus.COMPLETED)
    
    if not competitions:
        st.info("No completed competitions yet")
        return
    
    for comp in competitions:
        with st.expander(f"🏆 {comp['name']} - {format_competition_type(comp['competition_type'])}"):
            st.markdown(f"**Ended:** {comp['end_date']}")
            
            if comp.get('prize'):
                st.markdown(f"**Prize:** {comp['prize']}")
            
            # Show final leaderboard
            st.markdown("**Final Standings:**")
            _render_leaderboard(manager, comp['id'])
            
            st.divider()


def _render_leaderboard(manager, competition_id: str) -> None:
    """
    Render a leaderboard for a competition.
    
    Args:
        manager: LeaderboardManager instance
        competition_id: Competition ID
    """
    leaderboard = manager.get_leaderboard(competition_id)
    
    if leaderboard:
        for i, entry in enumerate(leaderboard[:LEADERBOARD_TOP_DISPLAY_COUNT], 1):
            medal = get_medal_for_position(i)
            st.markdown(f"{medal} **{entry.get('user_name', 'User')}** - Score: {entry['score']}")
    else:
        st.caption("No entries yet")