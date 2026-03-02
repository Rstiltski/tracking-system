"""
UI components for the Friends page.

Contains all render functions for the friends interface.
"""

import streamlit as st

from brain.social.friend_manager import FriendManager
from brain.models.friend import UserPrivacySettings

from .constants import (
    FEED_LIMIT,
    VISIBILITY_OPTIONS,
    DEFAULT_PRIVACY_SETTINGS,
)
from .helpers import format_activity_message


def render_friends_tab(manager: FriendManager) -> None:
    """
    Render friends tab.
    
    Args:
        manager: FriendManager instance
    """
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
    """
    Render requests tab.
    
    Args:
        manager: FriendManager instance
    """
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
    """
    Render activity feed tab.
    
    Args:
        manager: FriendManager instance
    """
    st.markdown("**📰 Friend Activity Feed**")
    
    feed = manager.get_friend_feed(limit=FEED_LIMIT)
    
    if not feed:
        st.info("No recent activity from friends")
        return
    
    for activity in feed:
        message = format_activity_message(activity)
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
    """
    Render privacy settings tab.
    
    Args:
        manager: FriendManager instance
    """
    st.markdown("**⚙️ Privacy Settings**")
    
    settings = manager.get_privacy_settings()
    
    with st.form("privacy_form"):
        st.markdown("**What to share with friends:**")
        
        share_achievements = st.checkbox(
            "Share achievements",
            value=settings.get('share_achievements', DEFAULT_PRIVACY_SETTINGS['share_achievements'])
        )
        
        share_streaks = st.checkbox(
            "Share streak milestones",
            value=settings.get('share_streaks', DEFAULT_PRIVACY_SETTINGS['share_streaks'])
        )
        
        share_completions = st.checkbox(
            "Share daily completions",
            value=settings.get('share_completions', DEFAULT_PRIVACY_SETTINGS['share_completions'])
        )
        
        allow_cheers = st.checkbox(
            "Allow friends to send cheers",
            value=settings.get('allow_cheers', DEFAULT_PRIVACY_SETTINGS['allow_cheers'])
        )
        
        st.divider()
        
        current_visibility = settings.get('visible_to', DEFAULT_PRIVACY_SETTINGS['visible_to'])
        visibility_index = VISIBILITY_OPTIONS.index(current_visibility) if current_visibility in VISIBILITY_OPTIONS else 1
        
        visibility = st.selectbox(
            "Profile visibility",
            options=VISIBILITY_OPTIONS,
            index=visibility_index
        )
        
        submitted = st.form_submit_button("Save Settings", type="primary")
        
        if submitted:
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