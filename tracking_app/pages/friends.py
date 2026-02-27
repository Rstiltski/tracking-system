"""
Friends Page - Social accountability management.

Usage:
    streamlit run tracking_app/pages/friends.py
"""
import streamlit as st
from datetime import datetime

from brain.social.friend_manager import FriendManager
from brain.models.friend import FriendshipStatus, PrivacyLevel


# Page configuration
st.set_page_config(
    page_title="Friends - Veryfyn",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main friends page."""
    # Initialize
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()

    if 'user_id' not in st.session_state:
        st.session_state.user_id = "user-123"  # Demo user ID

    storage = st.session_state.storage
    user_id = st.session_state.user_id

    # Initialize manager
    manager = FriendManager(storage, user_id)

    # Header
    st.title("👥 Friends & Accountability")
    st.markdown("Connect with friends for mutual support and accountability!")

    # Tabs
    tab_friends, tab_requests, tab_feed, tab_settings = st.tabs([
        "👫 My Friends",
        "📨 Requests",
        "📰 Activity Feed",
        "⚙️ Privacy"
    ])

    with tab_friends:
        render_friends_tab(manager)

    with tab_requests:
        render_requests_tab(manager)

    with tab_feed:
        render_feed_tab(manager)

    with tab_settings:
        render_settings_tab(manager)


def render_friends_tab(manager: FriendManager) -> None:
    """Render friends tab."""
    st.markdown("**👫 Your Friends**")

    friends = manager.get_friends()

    if not friends:
        st.info("No friends yet. Send a friend request to get started!")

        # Add friend form
        with st.form("add_friend_form"):
            friend_username = st.text_input("Friend's username or email")
            submitted = st.form_submit_button("Send Friend Request")

            if submitted and friend_username:
                # In production, look up user by username/email
                manager.send_friend_request(friend_username)
                st.success(f"✅ Friend request sent to {friend_username}!")
                st.rerun()
    else:
        # Show friends list
        for friend in friends:
            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:
                st.markdown(f"**{friend.get('friend_name', 'Friend')}**")
                st.caption(f"Friends since {friend.get('created_at', '')[:10]}")

            with col2:
                if st.button("📊 View Progress", key=f"view_{friend['id']}"):
                    st.info("Progress view would go here")

            with col3:
                if st.button("✕ Remove", key=f"remove_{friend['id']}"):
                    manager.remove_friend(friend['id'])
                    st.success("Friend removed")
                    st.rerun()

            st.divider()

        # Add more friends
        st.divider()
        with st.form("add_friend_form2"):
            friend_username = st.text_input("Add another friend")
            submitted = st.form_submit_button("Send Request")

            if submitted and friend_username:
                manager.send_friend_request(friend_username)
                st.success(f"✅ Request sent to {friend_username}!")
                st.rerun()


def render_requests_tab(manager: FriendManager) -> None:
    """Render requests tab."""
    st.markdown("**📨 Friend Requests**")

    requests = manager.get_pending_requests()

    if not requests:
        st.info("No pending friend requests")
        return

    for request in requests:
        col1, col2, col3 = st.columns([4, 1, 1])

        with col1:
            st.markdown(f"**{request.get('sender_name', 'User')}**")
            st.caption(f"Requested {request.get('created_at', '')[:10]}")

        with col2:
            if st.button("✓ Accept", key=f"accept_{request['id']}", type="primary"):
                manager.accept_friend_request(request['id'])
                st.success("Friend request accepted!")
                st.rerun()

        with col3:
            if st.button("✕ Decline", key=f"decline_{request['id']}"):
                manager.reject_friend_request(request['id'])
                st.success("Request declined")
                st.rerun()

        st.divider()


def render_feed_tab(manager: FriendManager) -> None:
    """Render activity feed tab."""
    st.markdown("**📰 Friend Activity Feed**")

    feed = manager.get_friend_feed(limit=20)

    if not feed:
        st.info("No recent activity from friends")
        return

    for activity in feed:
        user_name = activity.get('user_name', 'Friend')
        activity_type = activity.get('activity_type', '')
        habit_name = activity.get('habit_name', '')

        # Format activity message
        if activity_type == "completion":
            message = f"✅ {user_name} completed **{habit_name}**"
        elif activity_type == "streak":
            days = activity.get('details', {}).get('days', 0)
            message = f"🔥 {user_name} reached a {days}-day streak on **{habit_name}**"
        elif activity_type == "achievement":
            achievement = activity.get('details', {}).get('achievement', '')
            message = f"🏆 {user_name} earned **{achievement}**"
        else:
            message = f"{user_name} shared an activity"

        st.markdown(message)
        st.caption(f"{activity.get('created_at', '')[:16]}")

        # Cheer button
        if st.button("🎉 Cheer", key=f"cheer_{activity['id']}"):
            manager.send_cheer(
                receiver_id=activity['user_id'],
                habit_id=activity.get('habit_id'),
                cheer_type="general"
            )
            st.success("🎉 Cheer sent!")

        st.divider()


def render_settings_tab(manager: FriendManager) -> None:
    """Render privacy settings tab."""
    st.markdown("**⚙️ Privacy Settings**")

    settings = manager.get_privacy_settings()

    with st.form("privacy_form"):
        st.markdown("**What to share with friends:**")

        share_achievements = st.checkbox(
            "Share achievements",
            value=settings.get('share_achievements', True)
        )

        share_streaks = st.checkbox(
            "Share streak milestones",
            value=settings.get('share_streaks', True)
        )

        share_completions = st.checkbox(
            "Share daily completions",
            value=settings.get('share_completions', False)
        )

        allow_cheers = st.checkbox(
            "Allow friends to send cheers",
            value=settings.get('allow_cheers', True)
        )

        st.divider()

        visibility = st.selectbox(
            "Profile visibility",
            options=["private", "friends", "public"],
            index=["private", "friends", "public"].index(
                settings.get('visible_to', 'friends')
            )
        )

        submitted = st.form_submit_button("Save Settings", type="primary")

        if submitted:
            from brain.models.friend import UserPrivacySettings

            new_settings = UserPrivacySettings(
                user_id=st.session_state.user_id,
                share_achievements=share_achievements,
                share_streaks=share_streaks,
                share_completions=share_completions,
                allow_cheers=allow_cheers,
                visible_to=visibility
            )

            manager.update_privacy_settings(new_settings)
            st.success("✅ Privacy settings saved!")
            st.rerun()


if __name__ == "__main__":
    main()
