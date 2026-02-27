"""
Leaderboard Manager - Manage competitions and leaderboards.

Usage:
    from brain.social.leaderboard_manager import LeaderboardManager
    
    manager = LeaderboardManager(storage, user_id)
"""
from typing import List, Dict, Any, Optional
from brain.models.competition import (
    Competition,
    CompetitionType,
    CompetitionStatus,
    CompetitionParticipant,
    LeaderboardEntry,
)


class LeaderboardManager:
    """
    Manages competitions and leaderboards.

    Usage:
        manager = LeaderboardManager(storage, user_id)
    """

    def __init__(self, storage: Any, user_id: str = ""):
        """
        Initialize leaderboard manager.

        Args:
            storage: Storage instance
            user_id: User ID
        """
        self.storage = storage
        self.user_id = user_id

    # ==================== COMPETITIONS ====================

    def create_competition(
        self,
        name: str,
        competition_type: str,
        start_date: str,
        end_date: str,
        max_participants: int = 0,
        is_public: bool = True,
        prize: str = ""
    ) -> Competition:
        """Create a new competition."""
        competition = Competition(
            name=name,
            competition_type=CompetitionType(competition_type),
            start_date=__import__('datetime').date.fromisoformat(start_date),
            end_date=__import__('datetime').date.fromisoformat(end_date),
            creator_id=self.user_id,
            max_participants=max_participants,
            is_public=is_public,
            prize=prize
        )

        if hasattr(self.storage, 'save_competition'):
            self.storage.save_competition(competition.to_dict())

        return competition

    def get_competitions(
        self,
        status: Optional[CompetitionStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get competitions."""
        if hasattr(self.storage, 'get_competitions'):
            return self.storage.get_competitions(
                self.user_id,
                status.value if status else None
            )
        return []

    def join_competition(self, competition_id: str) -> bool:
        """Join a competition."""
        if hasattr(self.storage, 'join_competition'):
            return self.storage.join_competition(competition_id, self.user_id)
        return False

    def get_leaderboard(self, competition_id: str) -> List[Dict[str, Any]]:
        """Get competition leaderboard."""
        if hasattr(self.storage, 'get_leaderboard'):
            return self.storage.get_leaderboard(competition_id)
        return []

    def update_participant_score(
        self,
        competition_id: str,
        user_id: str,
        score: float
    ) -> bool:
        """Update participant score."""
        if hasattr(self.storage, 'update_participant_score'):
            return self.storage.update_participant_score(
                competition_id,
                user_id,
                score
            )
        return False

    # ==================== TEMPLATE SHARING ====================

    def share_template(
        self,
        template_id: str,
        title: str,
        description: str,
        is_public: bool = True
    ) -> str:
        """Share a template publicly."""
        if hasattr(self.storage, 'save_shared_template'):
            return self.storage.save_shared_template({
                "template_id": template_id,
                "user_id": self.user_id,
                "title": title,
                "description": description,
                "is_public": is_public
            })
        return ""

    def get_shared_templates(
        self,
        search: str = "",
        category: str = ""
    ) -> List[Dict[str, Any]]:
        """Get shared templates."""
        if hasattr(self.storage, 'get_shared_templates'):
            return self.storage.get_shared_templates(search, category)
        return []

    def clone_template(self, shared_template_id: str) -> bool:
        """Clone a shared template."""
        if hasattr(self.storage, 'clone_shared_template'):
            return self.storage.clone_shared_template(
                shared_template_id,
                self.user_id
            )
        return False

    def rate_template(
        self,
        shared_template_id: str,
        rating: int,
        review: str = ""
    ) -> bool:
        """Rate a shared template."""
        if hasattr(self.storage, 'save_template_rating'):
            return self.storage.save_template_rating({
                "shared_template_id": shared_template_id,
                "user_id": self.user_id,
                "rating": rating,
                "review": review
            })
        return False


__all__ = [
    "LeaderboardManager",
]
