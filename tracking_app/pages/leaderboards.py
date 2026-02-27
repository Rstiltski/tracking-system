"""
Leaderboards Page - Streak competitions.

Usage:
    streamlit run tracking_app/pages/leaderboards.py
"""
import streamlit as st
from datetime import date, timedelta

from brain.social.leaderboard_manager import LeaderboardManager
from brain.models.competition import CompetitionType, CompetitionStatus


# Page configuration
st.set_page_config(
    page_title="Leaderboards - Veryfyn",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main leaderboards page."""
    # Initialize
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()

    if 'user_id' not in st.session_state:
        st.session_state.user_id = "user-123"  # Demo user ID

    storage = st.session_state.storage
    user_id = st.session_state.user_id

    # Initialize manager
    manager = LeaderboardManager(storage, user_id)

    # Header
    st.title("🏆 Leaderboards & Competitions")
    st.markdown("Compete with friends and climb the ranks!")

    # Tabs
    tab_active, tab_create, tab_archive = st.tabs([
        "🔥 Active Competitions",
        "➕ Create Competition",
        "📜 Archive"
    ])

    with tab_active:
        render_active_competitions(manager)

    with tab_create:
        render_create_competition(manager)

    with tab_archive:
        render_archive(manager)


def render_active_competitions(manager: LeaderboardManager) -> None:
    """Render active competitions tab."""
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
                st.metric("Type", comp['competition_type'].replace('_', ' ').title())
            with col2:
                st.metric("Ends In", f"{(date.fromisoformat(comp['end_date']) - date.today()).days} days")
            with col3:
                st.metric("Participants", "TBD")

            # Progress bar
            start = date.fromisoformat(comp['start_date'])
            end = date.fromisoformat(comp['end_date'])
            total_days = (end - start).days
            days_elapsed = (date.today() - start).days
            progress = min(1.0, days_elapsed / total_days) if total_days > 0 else 0
            st.progress(progress)

            # Join button
            if st.button("🎯 Join Competition", key=f"join_{comp['id']}"):
                manager.join_competition(comp['id'])
                st.success("✅ Joined competition!")
                st.rerun()

            # Show leaderboard
            with st.expander("📊 View Leaderboard"):
                leaderboard = manager.get_leaderboard(comp['id'])
                if leaderboard:
                    for i, entry in enumerate(leaderboard[:10], 1):
                        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                        st.markdown(f"{medal} **{entry.get('user_name', 'User')}** - Score: {entry['score']}")
                else:
                    st.caption("No entries yet")

            st.divider()


def render_create_competition(manager: LeaderboardManager) -> None:
    """Render create competition tab."""
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
            end_date = st.date_input("End Date", value=date.today() + timedelta(days=7))

        max_participants = st.number_input("Max Participants (0 = unlimited)", min_value=0, value=0)

        is_public = st.checkbox("Public Competition", value=True)

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


def render_archive(manager: LeaderboardManager) -> None:
    """Render archive tab."""
    st.markdown("**📜 Past Competitions**")

    competitions = manager.get_competitions(CompetitionStatus.COMPLETED)

    if not competitions:
        st.info("No completed competitions yet")
        return

    for comp in competitions:
        with st.expander(f"🏆 {comp['name']} - {comp['competition_type'].replace('_', ' ').title()}"):
            st.markdown(f"**Ended:** {comp['end_date']}")

            if comp.get('prize'):
                st.markdown(f"**Prize:** {comp['prize']}")

            # Show final leaderboard
            leaderboard = manager.get_leaderboard(comp['id'])
            if leaderboard:
                st.markdown("**Final Standings:**")
                for i, entry in enumerate(leaderboard[:10], 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    st.markdown(f"{medal} **{entry.get('user_name', 'User')}** - Score: {entry['score']}")

            st.divider()


if __name__ == "__main__":
    main()
