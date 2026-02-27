"""
Group Challenge Model - Time-bound group habit challenges.

Enables users to:
- Join 7/30/90-day challenges
- Track progress with group
- Earn completion certificates
- Participate in group check-ins

Based on research showing group challenges increase completion rates by 60%.
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
import uuid


class ChallengeType(str, Enum):
    """Types of challenges."""
    SEVEN_DAY = "7_day"
    THIRTY_DAY = "30_day"
    NINETY_DAY = "90_day"
    CUSTOM = "custom"


class ChallengeStatus(str, Enum):
    """Status of a challenge."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class GroupChallenge:
    """
    A group challenge.

    Attributes:
        id: Unique identifier
        name: Challenge name
        challenge_type: Type/duration
        description: Challenge description
        status: Challenge status
        start_date: When challenge starts
        end_date: When challenge ends
        creator_id: User who created it
        max_participants: Maximum participants
        is_public: Whether anyone can join
        goal_description: What participants need to do
        certificate_template: Certificate template
        created_at: When created
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    challenge_type: ChallengeType = ChallengeType.SEVEN_DAY
    description: str = ""
    status: ChallengeStatus = ChallengeStatus.DRAFT
    start_date: date = field(default_factory=date.today)
    end_date: date = field(default_factory=lambda: date.today() + timedelta(days=7))
    creator_id: str = ""
    max_participants: int = 0
    is_public: bool = True
    goal_description: str = ""
    certificate_template: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "challenge_type": self.challenge_type.value,
            "description": self.description,
            "status": self.status.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "creator_id": self.creator_id,
            "max_participants": self.max_participants,
            "is_public": self.is_public,
            "goal_description": self.goal_description,
            "certificate_template": self.certificate_template,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GroupChallenge":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", ""),
            challenge_type=ChallengeType(data.get("challenge_type", "7_day")),
            description=data.get("description", ""),
            status=ChallengeStatus(data.get("status", "draft")),
            start_date=date.fromisoformat(data["start_date"]) if data.get("start_date") else date.today(),
            end_date=date.fromisoformat(data["end_date"]) if data.get("end_date") else date.today() + timedelta(days=7),
            creator_id=data.get("creator_id", ""),
            max_participants=data.get("max_participants", 0),
            is_public=data.get("is_public", True),
            goal_description=data.get("goal_description", ""),
            certificate_template=data.get("certificate_template", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        )


@dataclass
class ChallengeParticipant:
    """
    A participant in a challenge.

    Attributes:
        id: Unique identifier
        challenge_id: Challenge ID
        user_id: User ID
        progress: Progress percentage
        completions: Number of completions
        streak: Current streak
        completed: Whether challenge completed
        certificate_earned: Whether certificate earned
        joined_at: When joined
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    challenge_id: str = ""
    user_id: str = ""
    progress: float = 0.0
    completions: int = 0
    streak: int = 0
    completed: bool = False
    certificate_earned: bool = False
    joined_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "challenge_id": self.challenge_id,
            "user_id": self.user_id,
            "progress": self.progress,
            "completions": self.completions,
            "streak": self.streak,
            "completed": self.completed,
            "certificate_earned": self.certificate_earned,
            "joined_at": self.joined_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChallengeParticipant":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            challenge_id=data.get("challenge_id", ""),
            user_id=data.get("user_id", ""),
            progress=data.get("progress", 0.0),
            completions=data.get("completions", 0),
            streak=data.get("streak", 0),
            completed=data.get("completed", False),
            certificate_earned=data.get("certificate_earned", False),
            joined_at=datetime.fromisoformat(data["joined_at"]) if data.get("joined_at") else datetime.now()
        )


@dataclass
class ChallengeCheckIn:
    """
    A daily check-in for a challenge.

    Attributes:
        id: Unique identifier
        challenge_id: Challenge ID
        participant_id: Participant ID
        user_id: User ID
        check_in_date: Date of check-in
        completed: Whether completed today
        notes: Optional notes
        created_at: When checked in
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    challenge_id: str = ""
    participant_id: str = ""
    user_id: str = ""
    check_in_date: date = field(default_factory=date.today)
    completed: bool = False
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "challenge_id": self.challenge_id,
            "participant_id": self.participant_id,
            "user_id": self.user_id,
            "check_in_date": self.check_in_date.isoformat(),
            "completed": self.completed,
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChallengeCheckIn":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            challenge_id=data.get("challenge_id", ""),
            participant_id=data.get("participant_id", ""),
            user_id=data.get("user_id", ""),
            check_in_date=date.fromisoformat(data["check_in_date"]) if data.get("check_in_date") else date.today(),
            completed=data.get("completed", False),
            notes=data.get("notes", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        )


# Pre-defined challenge templates
CHALLENGE_TEMPLATES = {
    "7_day_streak": {
        "name": "7-Day Streak Challenge",
        "type": ChallengeType.SEVEN_DAY,
        "duration_days": 7,
        "description": "Build consistency with a 7-day streak",
        "goal": "Complete your habit every day for 7 days"
    },
    "30_day_transformation": {
        "name": "30-Day Transformation",
        "type": ChallengeType.THIRTY_DAY,
        "duration_days": 30,
        "description": "Transform your life in 30 days",
        "goal": "Complete your habit daily for 30 days"
    },
    "90_day_mastery": {
        "name": "90-Day Mastery Challenge",
        "type": ChallengeType.NINETY_DAY,
        "duration_days": 90,
        "description": "Master a habit in 90 days",
        "goal": "Achieve 90%+ completion rate over 90 days"
    }
}


__all__ = [
    "ChallengeType",
    "ChallengeStatus",
    "GroupChallenge",
    "ChallengeParticipant",
    "ChallengeCheckIn",
    "CHALLENGE_TEMPLATES",
]
