"""
Friend Manager - Manage social connections and accountability.

Usage:
    from brain.social.friend_manager import FriendManager
    
    manager = FriendManager(storage, user_id)
    manager.send_friend_request(friend_user_id)
"""
from typing import List, Dict, Any, Optional
from brain.models.friend import (
    Friendship,
    FriendshipStatus,
    UserPrivacySettings,
    Cheer,
    ActivityShare,
    PrivacyLevel,
)


class FriendManager:
    """
    Manages friend connections and social features.

    Usage:
        manager = FriendManager(storage, user_id)
    """

    def __init__(self, storage: Any, user_id: str = ""):
        """
        Initialize friend manager.

        Args:
            storage: Storage instance
            user_id: User ID
        """
        self.storage = storage
        self.user_id = user_id

    # ==================== FRIEND MANAGEMENT ====================

    def send_friend_request(self, friend_user_id: str) -> Friendship:
        """
        Send a friend request.

        Args:
            friend_user_id: User to send request to

        Returns:
            Created friendship
        """
        friendship = Friendship(
            user_id=self.user_id,
            friend_id=friend_user_id,
            status=FriendshipStatus.PENDING
        )

        if hasattr(self.storage, 'save_friendship'):
            self.storage.save_friendship(friendship.to_dict())

        return friendship

    def accept_friend_request(self, friendship_id: str) -> bool:
        """
        Accept a friend request.

        Args:
            friendship_id: Friendship ID

        Returns:
            True if accepted
        """
        if hasattr(self.storage, 'update_friendship_status'):
            return self.storage.update_friendship_status(
                friendship_id,
                FriendshipStatus.ACCEPTED.value
            )
        return False

    def reject_friend_request(self, friendship_id: str) -> bool:
        """
        Reject a friend request.

        Args:
            friendship_id: Friendship ID

        Returns:
            True if rejected
        """
        if hasattr(self.storage, 'update_friendship_status'):
            return self.storage.update_friendship_status(
                friendship_id,
                FriendshipStatus.REJECTED.value
            )
        return False

    def get_friends(self) -> List[Dict[str, Any]]:
        """
        Get user's accepted friends.

        Returns:
            List of friend data
        """
        if hasattr(self.storage, 'get_friends'):
            return self.storage.get_friends(self.user_id)
        return []

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """
        Get pending friend requests.

        Returns:
            List of pending requests
        """
        if hasattr(self.storage, 'get_pending_friend_requests'):
            return self.storage.get_pending_friend_requests(self.user_id)
        return []

    def remove_friend(self, friendship_id: str) -> bool:
        """
        Remove a friend connection.

        Args:
            friendship_id: Friendship ID

        Returns:
            True if removed
        """
        if hasattr(self.storage, 'delete_friendship'):
            return self.storage.delete_friendship(friendship_id)
        return False

    # ==================== CHEERS ====================

    def send_cheer(
        self,
        receiver_id: str,
        habit_id: Optional[str] = None,
        message: str = "🎉 Keep it up!",
        cheer_type: str = "general"
    ) -> Cheer:
        """
        Send a cheer to a friend.

        Args:
            receiver_id: User to cheer for
            habit_id: Optional habit ID
            message: Custom message
            cheer_type: Type of cheer

        Returns:
            Created cheer
        """
        cheer = Cheer(
            sender_id=self.user_id,
            receiver_id=receiver_id,
            habit_id=habit_id,
            message=message,
            cheer_type=cheer_type
        )

        if hasattr(self.storage, 'save_cheer'):
            self.storage.save_cheer(cheer.to_dict())

        return cheer

    def get_cheers(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get cheers received by user.

        Args:
            limit: Maximum cheers to return

        Returns:
            List of cheers
        """
        if hasattr(self.storage, 'get_cheers'):
            return self.storage.get_cheers(self.user_id, limit)
        return []

    # ==================== ACTIVITY SHARING ====================

    def share_activity(
        self,
        activity_type: str,
        habit_id: Optional[str] = None,
        habit_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> ActivityShare:
        """
        Share an activity with friends.

        Args:
            activity_type: Type of activity
            habit_id: Optional habit ID
            habit_name: Optional habit name
            details: Activity details

        Returns:
            Created activity share
        """
        share = ActivityShare(
            user_id=self.user_id,
            activity_type=activity_type,
            habit_id=habit_id,
            habit_name=habit_name,
            details=details or {}
        )

        if hasattr(self.storage, 'save_activity_share'):
            self.storage.save_activity_share(share.to_dict())

        return share

    def get_friend_feed(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get activity feed from friends.

        Args:
            limit: Maximum activities to return

        Returns:
            List of friend activities
        """
        if hasattr(self.storage, 'get_friend_feed'):
            return self.storage.get_friend_feed(self.user_id, limit)
        return []

    # ==================== PRIVACY ====================

    def get_privacy_settings(self) -> UserPrivacySettings:
        """
        Get user's privacy settings.

        Returns:
            UserPrivacySettings object
        """
        if hasattr(self.storage, 'get_privacy_settings'):
            settings_data = self.storage.get_privacy_settings(self.user_id)
            return UserPrivacySettings.from_dict(settings_data)
        
        # Default settings
        return UserPrivacySettings(user_id=self.user_id)

    def update_privacy_settings(
        self,
        settings: UserPrivacySettings
    ) -> bool:
        """
        Update user's privacy settings.

        Args:
            settings: New privacy settings

        Returns:
            True if updated
        """
        if hasattr(self.storage, 'save_privacy_settings'):
            return self.storage.save_privacy_settings(
                self.user_id,
                settings.to_dict()
            )
        return False

    def can_share_with_friend(
        self,
        friend_id: str,
        activity_type: str
    ) -> bool:
        """
        Check if user can share activity with friend.

        Args:
            friend_id: Friend user ID
            activity_type: Type of activity

        Returns:
            True if sharing allowed
        """
        settings = self.get_privacy_settings()

        if settings.visible_to == PrivacyLevel.PRIVATE:
            return False

        if activity_type == "achievement":
            return settings.share_achievements
        elif activity_type == "streak":
            return settings.share_streaks
        elif activity_type == "completion":
            return settings.share_completions

        return True


__all__ = [
    "FriendManager",
]
