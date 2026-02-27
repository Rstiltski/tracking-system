"""
Friend/Connection Model - Social accountability system.

Enables users to:
- Connect with friends
- Share progress
- Cheer each other on
- Hold each other accountable

Based on research showing social accountability increases habit success by 65%.

References:
- Dominican University study on goal accountability
- Social support in behavior change research
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


class FriendshipStatus(str, Enum):
    """Status of a friendship connection."""
    PENDING = "pending"  # Request sent, awaiting acceptance
    ACCEPTED = "accepted"  # Friends connected
    BLOCKED = "blocked"  # User blocked
    REJECTED = "rejected"  # Request rejected


class PrivacyLevel(str, Enum):
    """Privacy levels for sharing."""
    PRIVATE = "private"  # Share nothing
    FRIENDS = "friends"  # Share with friends only
    PUBLIC = "public"  # Share publicly


@dataclass
class Friendship:
    """
    A friendship connection between two users.

    Attributes:
        id: Unique identifier
        user_id: User who initiated the friendship
        friend_id: User who received the request
        status: Friendship status
        created_at: When friendship was created
        updated_at: Last update
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str = ""
    friend_id: str = ""
    status: FriendshipStatus = FriendshipStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "friend_id": self.friend_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Friendship":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            user_id=data.get("user_id", ""),
            friend_id=data.get("friend_id", ""),
            status=FriendshipStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now()
        )


@dataclass
class UserPrivacySettings:
    """
    User's privacy settings for social features.

    Attributes:
        user_id: User ID
        share_achievements: Share achievements with friends
        share_streaks: Share streak milestones
        share_completions: Share daily completions
        allow_cheers: Allow friends to send cheers
        visible_to: Privacy level
    """
    user_id: str = ""
    share_achievements: bool = True
    share_streaks: bool = True
    share_completions: bool = False
    allow_cheers: bool = True
    visible_to: PrivacyLevel = PrivacyLevel.FRIENDS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "share_achievements": self.share_achievements,
            "share_streaks": self.share_streaks,
            "share_completions": self.share_completions,
            "allow_cheers": self.allow_cheers,
            "visible_to": self.visible_to.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPrivacySettings":
        """Create from dictionary."""
        return cls(
            user_id=data.get("user_id", ""),
            share_achievements=data.get("share_achievements", True),
            share_streaks=data.get("share_streaks", True),
            share_completions=data.get("share_completions", False),
            allow_cheers=data.get("allow_cheers", True),
            visible_to=PrivacyLevel(data.get("visible_to", "friends"))
        )


@dataclass
class Cheer:
    """
    A cheer/encouragement sent between friends.

    Attributes:
        id: Unique identifier
        sender_id: User who sent the cheer
        receiver_id: User who received the cheer
        habit_id: Optional habit being cheered for
        message: Optional custom message
        cheer_type: Type of cheer
        created_at: When sent
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    sender_id: str = ""
    receiver_id: str = ""
    habit_id: Optional[str] = None
    message: str = "🎉 Keep it up!"
    cheer_type: str = "general"
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "habit_id": self.habit_id,
            "message": self.message,
            "cheer_type": self.cheer_type,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cheer":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            sender_id=data.get("sender_id", ""),
            receiver_id=data.get("receiver_id", ""),
            habit_id=data.get("habit_id"),
            message=data.get("message", "🎉 Keep it up!"),
            cheer_type=data.get("cheer_type", "general"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        )


@dataclass
class ActivityShare:
    """
    A shared activity post for friends to see.

    Attributes:
        id: Unique identifier
        user_id: User who shared
        activity_type: Type of activity
        habit_id: Optional related habit
        habit_name: Optional habit name
        details: Activity details
        created_at: When shared
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str = ""
    activity_type: str = "completion"  # completion, streak, achievement
    habit_id: Optional[str] = None
    habit_name: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_type": self.activity_type,
            "habit_id": self.habit_id,
            "habit_name": self.habit_name,
            "details": self.details,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActivityShare":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            user_id=data.get("user_id", ""),
            activity_type=data.get("activity_type", "completion"),
            habit_id=data.get("habit_id"),
            habit_name=data.get("habit_name"),
            details=data.get("details", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        )


# Cheer message templates
CHEER_TEMPLATES = {
    "streak_7": "🔥 {days} days strong! Amazing!",
    "streak_30": "🏆 {days} days! You're on fire!",
    "streak_100": "💯 {days} days! Legendary!",
    "achievement": "🎉 Congrats on {achievement}!",
    "comeback": "💪 Welcome back! You got this!",
    "general": "🎉 Keep it up!",
}


def get_cheer_message(cheer_type: str, **kwargs) -> str:
    """
    Get cheer message from template.

    Args:
        cheer_type: Type of cheer
        **kwargs: Template variables

    Returns:
        Formatted cheer message
    """
    template = CHEER_TEMPLATES.get(cheer_type, CHEER_TEMPLATES["general"])
    return template.format(**kwargs)


__all__ = [
    "FriendshipStatus",
    "PrivacyLevel",
    "Friendship",
    "UserPrivacySettings",
    "Cheer",
    "ActivityShare",
    "CHEER_TEMPLATES",
    "get_cheer_message",
]
