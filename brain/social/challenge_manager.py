"""
Challenge Manager - Manage group challenges.

Usage:
    from brain.social.challenge_manager import ChallengeManager
    
    manager = ChallengeManager(storage, user_id)
"""
from typing import List, Dict, Any, Optional
from brain.models.challenge import (
    GroupChallenge,
    ChallengeType,
    ChallengeStatus,
    ChallengeParticipant,
    ChallengeCheckIn,
    CHALLENGE_TEMPLATES,
)


class ChallengeManager:
    """
    Manages group challenges.

    Usage:
        manager = ChallengeManager(storage, user_id)
    """

    def __init__(self, storage: Any, user_id: str = ""):
        """
        Initialize challenge manager.

        Args:
            storage: Storage instance
            user_id: User ID
        """
        self.storage = storage
        self.user_id = user_id

    # ==================== CHALLENGES ====================

    def create_challenge(
        self,
        name: str,
        challenge_type: str,
        start_date: str,
        end_date: str,
        description: str = "",
        goal_description: str = "",
        max_participants: int = 0,
        is_public: bool = True
    ) -> GroupChallenge:
        """Create a new challenge."""
        challenge = GroupChallenge(
            name=name,
            challenge_type=ChallengeType(challenge_type),
            start_date=__import__('datetime').date.fromisoformat(start_date),
            end_date=__import__('datetime').date.fromisoformat(end_date),
            creator_id=self.user_id,
            description=description,
            goal_description=goal_description,
            max_participants=max_participants,
            is_public=is_public
        )

        if hasattr(self.storage, 'save_challenge'):
            self.storage.save_challenge(challenge.to_dict())

        return challenge

    def get_challenges(
        self,
        status: Optional[ChallengeStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get challenges."""
        if hasattr(self.storage, 'get_challenges'):
            return self.storage.get_challenges(
                self.user_id,
                status.value if status else None
            )
        return []

    def join_challenge(self, challenge_id: str) -> bool:
        """Join a challenge."""
        if hasattr(self.storage, 'join_challenge'):
            return self.storage.join_challenge(challenge_id, self.user_id)
        return False

    def get_challenge_participants(
        self,
        challenge_id: str
    ) -> List[Dict[str, Any]]:
        """Get challenge participants."""
        if hasattr(self.storage, 'get_challenge_participants'):
            return self.storage.get_challenge_participants(challenge_id)
        return []

    # ==================== CHECK-INS ====================

    def check_in(
        self,
        challenge_id: str,
        completed: bool = True,
        notes: str = ""
    ) -> ChallengeCheckIn:
        """Daily check-in for challenge."""
        check_in = ChallengeCheckIn(
            challenge_id=challenge_id,
            user_id=self.user_id,
            completed=completed,
            notes=notes
        )

        if hasattr(self.storage, 'save_challenge_checkin'):
            self.storage.save_challenge_checkin(check_in.to_dict())

        return check_in

    def get_checkin_feed(
        self,
        challenge_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get check-in feed for challenge."""
        if hasattr(self.storage, 'get_challenge_checkins'):
            return self.storage.get_challenge_checkins(challenge_id, limit)
        return []

    # ==================== CERTIFICATES ====================

    def earn_certificate(self, challenge_id: str) -> bool:
        """Earn completion certificate."""
        if hasattr(self.storage, 'earn_certificate'):
            return self.storage.earn_certificate(challenge_id, self.user_id)
        return False

    def get_certificates(self) -> List[Dict[str, Any]]:
        """Get user's earned certificates."""
        if hasattr(self.storage, 'get_certificates'):
            return self.storage.get_certificates(self.user_id)
        return []


__all__ = [
    "ChallengeManager",
]
