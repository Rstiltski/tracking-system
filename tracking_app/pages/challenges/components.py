"""
UI components for the Challenges page.

Contains all render functions for the challenges interface.
"""

import streamlit as st
from datetime import date, timedelta

from .constants import (
    DURATION_OPTIONS,
    DEFAULT_MAX_PARTICIPANTS,
    LEADERBOARD_DISPLAY_LIMIT,
    CHECKIN_FEED_LIMIT,
    MEDAL_EMOJIS,
)
from .helpers import get_challenge_manager, calculate_challenge_progress, get_days_remaining


def render_browse_challenges(manager) -> None:
    """Render browse challenges tab."""
    st.markdown("**🌍 Browse Active Challenges**")

    try:
        from brain.models.challenge import ChallengeStatus
        challenges = manager.get_challenges(ChallengeStatus.ACTIVE)
    except ImportError:
        st.info("Challenge system requires the brain module.")
        return

    if not challenges:
        st.info("No active challenges. Be the first to create one!")
        return

    for challenge in challenges:
        with st.container():
            st.markdown(f"### {challenge['name']}")
            st.markdown(f"*{challenge.get('description', '')}*")

            # Challenge info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Type", challenge['challenge_type'].replace('_', ' ').title())
            with col2:
                days_left = get_days_remaining(challenge)
                st.metric("Days Left", days_left)
            with col3:
                st.metric("Participants", "TBD")
            with col4:
                st.metric("Goal", challenge.get('goal_description', 'Complete daily')[:20])

            # Progress bar
            progress = calculate_challenge_progress(challenge)
            st.progress(progress)

            # Join button
            if st.button("🎯 Join Challenge", key=f"join_{challenge['id']}", type="primary"):
                manager.join_challenge(challenge['id'])
                st.success("✅ Joined challenge! Good luck!")
                st.rerun()

            st.divider()


def render_my_challenges(manager) -> None:
    """Render my challenges tab."""
    st.markdown("**📋 My Challenges**")

    # Get user's challenges (in production, filter by user)
    challenges = manager.get_challenges()

    if not challenges:
        st.info("You haven't joined any challenges yet")
        return

    for challenge in challenges:
        with st.expander(f"**{challenge['name']}** - {challenge['challenge_type'].replace('_', ' ').title()}"):
            # Progress
            st.markdown("**Your Progress:**")
            progress = st.slider("Today's progress", 0, 100, 50)
            st.progress(progress / 100)

            # Check-in
            with st.form(f"checkin_{challenge['id']}"):
                completed = st.checkbox("I completed today's goal")
                notes = st.text_area("Notes (optional)")
                submitted = st.form_submit_button("📝 Check In")

                if submitted:
                    manager.check_in(challenge['id'], completed, notes)
                    st.success("✅ Check-in recorded!")
                    st.rerun()

            # View leaderboard
            with st.expander("📊 Challenge Leaderboard"):
                participants = manager.get_challenge_participants(challenge['id'])
                if participants:
                    for i, p in enumerate(participants[:LEADERBOARD_DISPLAY_LIMIT], 1):
                        medal = MEDAL_EMOJIS.get(i, f"{i}.")
                        st.markdown(f"{medal} **{p.get('user_name', 'User')}** - {p['progress']:.0f}% (🔥 {p['streak']} day streak)")
                else:
                    st.caption("No participants yet")

            # View check-in feed
            with st.expander("💬 Check-in Feed"):
                checkins = manager.get_challenge_checkins(challenge['id'], limit=CHECKIN_FEED_LIMIT)
                if checkins:
                    for checkin in checkins[:5]:
                        status = "✅" if checkin.get('completed') else "⏳"
                        st.markdown(f"{status} **{checkin.get('user_name', 'User')}** - {checkin.get('check_in_date', '')}")
                        if checkin.get('notes'):
                            st.caption(f"_{checkin['notes']}_")
                else:
                    st.caption("No check-ins yet")

            st.divider()


def render_create_challenge(manager) -> None:
    """Render create challenge tab."""
    st.markdown("**➕ Create New Challenge**")

    try:
        from brain.models.challenge import CHALLENGE_TEMPLATES
    except ImportError:
        st.info("Challenge creation requires the brain module.")
        return

    with st.form("create_challenge_form"):
        name = st.text_input("Challenge Name", placeholder="e.g., 30-Day Fitness Challenge")

        # Use template
        template = st.selectbox(
            "Choose a template",
            options=list(CHALLENGE_TEMPLATES.keys()),
            format_func=lambda x: CHALLENGE_TEMPLATES[x]['name']
        )

        if template:
            template_data = CHALLENGE_TEMPLATES[template]
            st.info(f"**{template_data['name']}** - {template_data['description']}")
            st.caption(f"Goal: {template_data['goal']}")

        description = st.text_area("Description", value=CHALLENGE_TEMPLATES.get(template, {}).get('description', ''))
        goal = st.text_area("Goal Description", value=CHALLENGE_TEMPLATES.get(template, {}).get('goal', ''))

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today())
        with col2:
            duration = st.selectbox("Duration", options=DURATION_OPTIONS)
            end_date = start_date + timedelta(days=duration)

        max_participants = st.number_input("Max Participants (0 = unlimited)", min_value=0, value=DEFAULT_MAX_PARTICIPANTS)
        is_public = st.checkbox("Public Challenge", value=True)

        submitted = st.form_submit_button("Create Challenge", type="primary")

        if submitted and name:
            manager.create_challenge(
                name=name,
                challenge_type=CHALLENGE_TEMPLATES.get(template, {}).get('type', 'custom').value,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                description=description,
                goal_description=goal,
                max_participants=max_participants,
                is_public=is_public
            )
            st.success(f"✅ Created challenge: {name}")
            st.rerun()


def render_certificates(manager) -> None:
    """Render certificates tab."""
    st.markdown("**🏆 My Certificates**")

    certificates = manager.get_certificates()

    if not certificates:
        st.info("You haven't earned any certificates yet. Complete challenges to earn them!")
        return

    for cert in certificates:
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"### 🎉 {cert.get('challenge_name', 'Challenge Completed')}")
                st.caption(f"Earned on {cert.get('earned_at', '')[:10]}")

            with col2:
                st.markdown("### 📜")

            st.divider()