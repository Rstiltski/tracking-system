"""
Competition Model - Streak competitions and leaderboards.

Enables users to:
- Compete for longest streak
- Compete for highest score
- Compete for most improved
- Join weekly/monthly challenges

Based on research showing friendly competition increases motivation by 40%.
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any, List
import uuid


class CompetitionType(str, Enum):
    """Types of competitions."""
    LONGEST_STREAK = "longest_streak"
    HIGHEST_SCORE = "highest_score"
    MOST_IMPROVED = "most_improved"
    PERFECT_WEEK = "perfect_week"
    CUSTOM = "custom"


class CompetitionStatus(str, Enum):
    """Status of a competition."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Competition:
    """
    A streak competition.

    Attributes:
        id: Unique identifier
        name: Competition name
        competition_type: Type of competition
        status: Competition status
        start_date: When competition starts
        end_date: When competition ends
        creator_id: User who created it
        max_participants: Maximum participants (0 = unlimited)
        is_public: Whether anyone can join
        prize: Optional prize description
        created_at: When created
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    competition_type: CompetitionType = CompetitionType.LONGEST_STREAK
    status: CompetitionStatus = CompetitionStatus.DRAFT
    start_date: date = field(default_factory=date.today)
    end_date: date = field(default_factory=lambda: date.today() + timedelta(days=7))
    creator_id: str = ""
    max_participants: int = 0
    is_public: bool = True
    prize: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "competition_type": self.competition_type.value,
            "status": self.status.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "creator_id": self.creator_id,
            "max_participants": self.max_participants,
            "is_public": self.is_public,
            "prize": self.prize,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Competition":
        """Create from dictionary."""
        from datetime import timedelta
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", ""),
            competition_type=CompetitionType(data.get("competition_type", "longest_streak")),
            status=CompetitionStatus(data.get("status", "draft")),
            start_date=date.fromisoformat(data["start_date"]) if data.get("start_date") else date.today(),
            end_date=date.fromisoformat(data["end_date"]) if data.get("end_date") else date.today() + timedelta(days=7),
            creator_id=data.get("creator_id", ""),
            max_participants=data.get("max_participants", 0),
            is_public=data.get("is_public", True),
            prize=data.get("prize", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        )


@dataclass
class CompetitionParticipant:
    """
    A participant in a competition.

    Attributes:
        id: Unique identifier
        competition_id: Competition ID
        user_id: User ID
        score: Current score
        rank: Current rank
        joined_at: When joined
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    competition_id: str = ""
    user_id: str = ""
    score: float = 0.0
    rank: int = 0
    joined_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "competition_id": self.competition_id,
            "user_id": self.user_id,
            "score": self.score,
            "rank": self.rank,
            "joined_at": self.joined_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompetitionParticipant":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            competition_id=data.get("competition_id", ""),
            user_id=data.get("user_id", ""),
            score=data.get("score", 0.0),
            rank=data.get("rank", 0),
            joined_at=datetime.fromisoformat(data["joined_at"]) if data.get("joined_at") else datetime.now()
        )


@dataclass
class LeaderboardEntry:
    """
    An entry in the leaderboard.

    Attributes:
        id: Unique identifier
        competition_id: Competition ID
        user_id: User ID
        user_name: User name
        score: Score value
        rank: Rank position
        change: Rank change from last period
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    competition_id: str = ""
    user_id: str = ""
    user_name: str = ""
    score: float = 0.0
    rank: int = 0
    change: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "competition_id": self.competition_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "score": self.score,
            "rank": self.rank,
            "change": self.change
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LeaderboardEntry":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            competition_id=data.get("competition_id", ""),
            user_id=data.get("user_id", ""),
            user_name=data.get("user_name", ""),
            score=data.get("score", 0.0),
            rank=data.get("rank", 0),
            change=data.get("change", 0)
        )


# Import timedelta for default values
from datetime import timedelta


__all__ = [
    "CompetitionType",
    "CompetitionStatus",
    "Competition",
    "CompetitionParticipant",
    "LeaderboardEntry",
]
