"""
Achievement Model - Gamification achievement system.

Based on gamification research for habit formation:

1. Achievement Types:
   - Streak milestones (7, 30, 90, 365 days)
   - Score achievements (90%+ for 30 days)
   - Comeback stories (rebuilt broken streak)
   - Consistency awards (perfect week/month)
   - Mastery badges (automaticity score 6+)

2. XP Multipliers:
   - 7-day streak: 1.1x XP
   - 30-day streak: 1.25x XP
   - 90-day streak: 1.5x XP

3. Research Basis:
   - Immediate feedback increases engagement
   - Visible progress motivates continuation
   - Social recognition amplifies effect

References:
- Hamari, J. (2017). "Do badges increase user activity?"
- Mekler, E.D., et al. (2017). "Gamification and motivation"
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, Any, List
import uuid


class AchievementCategory(str, Enum):
    """Categories of achievements."""
    STREAK = "streak"  # Streak milestones
    SCORE = "score"  # Score achievements
    COMEBACK = "comeback"  # Rebuilding streaks
    CONSISTENCY = "consistency"  # Perfect weeks/months
    MASTERY = "mastery"  # Habit mastery
    SPECIAL = "special"  # Special events


class AchievementTier(str, Enum):
    """Achievement tiers (difficulty levels)."""
    BRONZE = "bronze"  # Easy achievements
    SILVER = "silver"  # Medium achievements
    GOLD = "gold"  # Hard achievements
    PLATINUM = "platinum"  # Very hard achievements
    DIAMOND = "diamond"  # Elite achievements


@dataclass
class Achievement:
    """
    An achievement badge.

    Attributes:
        id: Unique identifier
        name: Achievement name
        description: What you did to earn it
        category: Achievement category
        tier: Difficulty tier
        icon: Emoji icon for display
        xp_reward: XP awarded when unlocked
        requirement: Requirement description
        requirement_data: Structured requirement data
        is_hidden: Whether achievement is secret
        unlocked: Whether user has unlocked it
        unlocked_at: When it was unlocked
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    category: AchievementCategory = AchievementCategory.STREAK
    tier: AchievementTier = AchievementTier.BRONZE
    icon: str = "🏆"
    xp_reward: int = 50
    requirement: str = ""
    requirement_data: Dict[str, Any] = field(default_factory=dict)
    is_hidden: bool = False
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "tier": self.tier.value,
            "icon": self.icon,
            "xp_reward": self.xp_reward,
            "requirement": self.requirement,
            "requirement_data": self.requirement_data,
            "is_hidden": self.is_hidden,
            "unlocked": self.unlocked,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Achievement":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=AchievementCategory(data.get("category", "streak")),
            tier=AchievementTier(data.get("tier", "bronze")),
            icon=data.get("icon", "🏆"),
            xp_reward=data.get("xp_reward", 50),
            requirement=data.get("requirement", ""),
            requirement_data=data.get("requirement_data", {}),
            is_hidden=data.get("is_hidden", False),
            unlocked=data.get("unlocked", False),
            unlocked_at=datetime.fromisoformat(data["unlocked_at"]) if data.get("unlocked_at") else None
        )

    def check_requirement(self, user_data: Dict[str, Any]) -> bool:
        """
        Check if user meets the achievement requirement.

        Args:
            user_data: User's current data (streaks, scores, etc.)

        Returns:
            True if requirement is met
        """
        req_type = self.requirement_data.get("type")
        req_value = self.requirement_data.get("value", 0)

        if req_type == "streak_days":
            return user_data.get("streak", 0) >= req_value
        elif req_type == "completion_rate":
            return user_data.get("completion_rate", 0) >= req_value
        elif req_type == "score_average":
            return user_data.get("score_average", 0) >= req_value
        elif req_type == "perfect_weeks":
            return user_data.get("perfect_weeks", 0) >= req_value
        elif req_type == "total_completions":
            return user_data.get("total_completions", 0) >= req_value

        return False

    def __str__(self) -> str:
        """String representation."""
        tier_emoji = {
            AchievementTier.BRONZE: "🥉",
            AchievementTier.SILVER: "🥈",
            AchievementTier.GOLD: "🥇",
            AchievementTier.PLATINUM: "💎",
            AchievementTier.DIAMOND: "💠",
        }.get(self.tier, "🏆")

        status = "🔓" if self.unlocked else "🔒"
        return f"{status} {tier_emoji} {self.name}"


@dataclass
class UserAchievement:
    """
    A user's unlocked achievement.

    Attributes:
        id: Unique identifier
        achievement_id: ID of the achievement
        user_id: ID of the user
        unlocked_at: When it was unlocked
        xp_awarded: XP awarded for this achievement
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    achievement_id: str = ""
    user_id: str = ""
    unlocked_at: datetime = field(default_factory=datetime.now)
    xp_awarded: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "achievement_id": self.achievement_id,
            "user_id": self.user_id,
            "unlocked_at": self.unlocked_at.isoformat(),
            "xp_awarded": self.xp_awarded
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserAchievement":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            achievement_id=data.get("achievement_id", ""),
            user_id=data.get("user_id", ""),
            unlocked_at=datetime.fromisoformat(data["unlocked_at"]) if data.get("unlocked_at") else datetime.now(),
            xp_awarded=data.get("xp_awarded", 0)
        )


# Pre-defined achievements
DEFAULT_ACHIEVEMENTS: List[Achievement] = [
    # Streak achievements
    Achievement(
        id="achieve_streak_7",
        name="Week Warrior",
        description="Maintain a 7-day streak",
        category=AchievementCategory.STREAK,
        tier=AchievementTier.BRONZE,
        icon="🔥",
        xp_reward=50,
        requirement="7-day streak",
        requirement_data={"type": "streak_days", "value": 7}
    ),
    Achievement(
        id="achieve_streak_30",
        name="Month Master",
        description="Maintain a 30-day streak",
        category=AchievementCategory.STREAK,
        tier=AchievementTier.SILVER,
        icon="🌟",
        xp_reward=150,
        requirement="30-day streak",
        requirement_data={"type": "streak_days", "value": 30}
    ),
    Achievement(
        id="achieve_streak_90",
        name="Quarter Queen/King",
        description="Maintain a 90-day streak",
        category=AchievementCategory.STREAK,
        tier=AchievementTier.GOLD,
        icon="👑",
        xp_reward=400,
        requirement="90-day streak",
        requirement_data={"type": "streak_days", "value": 90}
    ),
    Achievement(
        id="achieve_streak_365",
        name="Yearly Legend",
        description="Maintain a 365-day streak",
        category=AchievementCategory.STREAK,
        tier=AchievementTier.DIAMOND,
        icon="🏆",
        xp_reward=1000,
        requirement="365-day streak",
        requirement_data={"type": "streak_days", "value": 365}
    ),

    # Score achievements
    Achievement(
        id="achieve_score_90",
        name="High Achiever",
        description="Maintain 90%+ score for 7 days",
        category=AchievementCategory.SCORE,
        tier=AchievementTier.SILVER,
        icon="📈",
        xp_reward=100,
        requirement="90%+ score for 7 days",
        requirement_data={"type": "score_average", "value": 0.90}
    ),

    # Consistency achievements
    Achievement(
        id="achieve_perfect_week",
        name="Perfect Week",
        description="Complete all habits for 7 days",
        category=AchievementCategory.CONSISTENCY,
        tier=AchievementTier.GOLD,
        icon="✨",
        xp_reward=300,
        requirement="Perfect week",
        requirement_data={"type": "perfect_weeks", "value": 1}
    ),

    # Comeback achievements
    Achievement(
        id="achieve_comeback",
        name="Phoenix Rising",
        description="Rebuild a streak after breaking it",
        category=AchievementCategory.COMEBACK,
        tier=AchievementTier.SILVER,
        icon="🦅",
        xp_reward=200,
        requirement="Rebuild streak after break",
        requirement_data={"type": "comeback", "value": 1}
    ),

    # Mastery achievements
    Achievement(
        id="achieve_mastery",
        name="Habit Master",
        description="Reach automaticity score of 6+",
        category=AchievementCategory.MASTERY,
        tier=AchievementTier.PLATINUM,
        icon="🧘",
        xp_reward=500,
        requirement="Automaticity 6+",
        requirement_data={"type": "automaticity", "value": 6.0}
    ),

    # Special achievements
    Achievement(
        id="achieve_first_habit",
        name="First Step",
        description="Create your first habit",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.BRONZE,
        icon="🌱",
        xp_reward=25,
        requirement="Create first habit",
        requirement_data={"type": "first_habit", "value": 1},
        is_hidden=False
    ),
    Achievement(
        id="achieve_early_adopter",
        name="Early Bird",
        description="Complete a habit before 7 AM",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.BRONZE,
        icon="🌅",
        xp_reward=50,
        requirement="Early completion",
        requirement_data={"type": "early_bird", "value": 7}
    ),
    
    # Phase 7.2: New Achievements
    
    # Consistency achievements (Unbreakable series)
    Achievement(
        id="achieve_unbreakable_7",
        name="Unbreakable Week",
        description="Don't miss a single day for 7 days straight",
        category=AchievementCategory.CONSISTENCY,
        tier=AchievementTier.BRONZE,
        icon="🛡️",
        xp_reward=75,
        requirement="7 days without missing",
        requirement_data={"type": "streak_days", "value": 7}
    ),
    Achievement(
        id="achieve_unbreakable_14",
        name="Unbreakable Fortnight",
        description="Don't miss a single day for 14 days straight",
        category=AchievementCategory.CONSISTENCY,
        tier=AchievementTier.SILVER,
        icon="🏰",
        xp_reward=150,
        requirement="14 days without missing",
        requirement_data={"type": "streak_days", "value": 14}
    ),
    Achievement(
        id="achieve_unbreakable_30",
        name="Unbreakable Month",
        description="Don't miss a single day for 30 days straight",
        category=AchievementCategory.CONSISTENCY,
        tier=AchievementTier.GOLD,
        icon="🏯",
        xp_reward=350,
        requirement="30 days without missing",
        requirement_data={"type": "streak_days", "value": 30}
    ),
    
    # Variety achievements (Renaissance)
    Achievement(
        id="achieve_variety_5",
        name="Renaissance Beginner",
        description="Track 5 different habits simultaneously",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.BRONZE,
        icon="🎨",
        xp_reward=100,
        requirement="Track 5 habits",
        requirement_data={"type": "total_habits", "value": 5}
    ),
    Achievement(
        id="achieve_variety_10",
        name="Renaissance Enthusiast",
        description="Track 10 different habits simultaneously",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.SILVER,
        icon="🎭",
        xp_reward=250,
        requirement="Track 10 habits",
        requirement_data={"type": "total_habits", "value": 10}
    ),
    Achievement(
        id="achieve_variety_15",
        name="Renaissance Master",
        description="Track 15 different habits simultaneously",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.GOLD,
        icon="🎪",
        xp_reward=500,
        requirement="Track 15 habits",
        requirement_data={"type": "total_habits", "value": 15}
    ),
    
    # Dawn Patrol series (Early Bird expanded)
    Achievement(
        id="achieve_dawn_patrol_10",
        name="Dawn Patrol",
        description="Complete habits before 6 AM 10 times",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.BRONZE,
        icon="🌤️",
        xp_reward=75,
        requirement="10 early completions",
        requirement_data={"type": "early_completions", "value": 10}
    ),
    Achievement(
        id="achieve_dawn_patrol_25",
        name="Early Riser",
        description="Complete habits before 6 AM 25 times",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.SILVER,
        icon="🌄",
        xp_reward=175,
        requirement="25 early completions",
        requirement_data={"type": "early_completions", "value": 25}
    ),
    Achievement(
        id="achieve_dawn_patrol_50",
        name="Morning Champion",
        description="Complete habits before 6 AM 50 times",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.GOLD,
        icon="☀️",
        xp_reward=400,
        requirement="50 early completions",
        requirement_data={"type": "early_completions", "value": 50}
    ),
    
    # Midnight Oil series (Night Owl)
    Achievement(
        id="achieve_night_owl_10",
        name="Night Owl",
        description="Complete habits after 10 PM 10 times",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.BRONZE,
        icon="🌙",
        xp_reward=75,
        requirement="10 late completions",
        requirement_data={"type": "late_completions", "value": 10}
    ),
    Achievement(
        id="achieve_night_owl_25",
        name="Midnight Worker",
        description="Complete habits after 10 PM 25 times",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.SILVER,
        icon="🦉",
        xp_reward=175,
        requirement="25 late completions",
        requirement_data={"type": "late_completions", "value": 25}
    ),
    Achievement(
        id="achieve_night_owl_50",
        name="Nocturnal Legend",
        description="Complete habits after 10 PM 50 times",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.GOLD,
        icon="🌟",
        xp_reward=400,
        requirement="50 late completions",
        requirement_data={"type": "late_completions", "value": 50}
    ),
    
    # Flawless series (Perfectionist)
    Achievement(
        id="achieve_flawless_week",
        name="Flawless Week",
        description="100% completion rate for a week",
        category=AchievementCategory.CONSISTENCY,
        tier=AchievementTier.SILVER,
        icon="💎",
        xp_reward=200,
        requirement="100% weekly completion",
        requirement_data={"type": "perfect_weeks", "value": 1}
    ),
    Achievement(
        id="achieve_flawless_month",
        name="Flawless Month",
        description="100% completion rate for a month",
        category=AchievementCategory.CONSISTENCY,
        tier=AchievementTier.PLATINUM,
        icon="💫",
        xp_reward=750,
        requirement="100% monthly completion",
        requirement_data={"type": "perfect_months", "value": 1}
    ),
    
    # Resilient series (Comeback expanded)
    Achievement(
        id="achieve_resilient",
        name="Resilient Soul",
        description="Recover from 0% to 80% score",
        category=AchievementCategory.COMEBACK,
        tier=AchievementTier.SILVER,
        icon="💪",
        xp_reward=200,
        requirement="Score recovery 0% to 80%",
        requirement_data={"type": "comeback", "value": 80}
    ),
    
    # Quantified Self series (Data Enthusiast)
    Achievement(
        id="achieve_data_100",
        name="Data Enthusiast",
        description="Log 100 habit entries",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.BRONZE,
        icon="📊",
        xp_reward=100,
        requirement="100 entries logged",
        requirement_data={"type": "total_completions", "value": 100}
    ),
    Achievement(
        id="achieve_data_500",
        name="Data Scientist",
        description="Log 500 habit entries",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.SILVER,
        icon="📈",
        xp_reward=300,
        requirement="500 entries logged",
        requirement_data={"type": "total_completions", "value": 500}
    ),
    Achievement(
        id="achieve_data_1000",
        name="Quantified Self Master",
        description="Log 1000 habit entries",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.GOLD,
        icon="🏆",
        xp_reward=600,
        requirement="1000 entries logged",
        requirement_data={"type": "total_completions", "value": 1000}
    ),
    
    # Hidden/Secret achievements
    Achievement(
        id="achieve_streak_freeze",
        name="Frozen in Time",
        description="Use a streak freeze to save your streak",
        category=AchievementCategory.SPECIAL,
        tier=AchievementTier.BRONZE,
        icon="🧊",
        xp_reward=50,
        requirement="Use streak freeze",
        requirement_data={"type": "streak_freeze_used", "value": 1},
        is_hidden=True
    ),
    Achievement(
        id="achieve_weekend_warrior",
        name="Weekend Warrior",
        description="Complete all habits on both Saturday and Sunday for 4 weekends",
        category=AchievementCategory.CONSISTENCY,
        tier=AchievementTier.SILVER,
        icon="🎊",
        xp_reward=200,
        requirement="4 perfect weekends",
        requirement_data={"type": "perfect_weekends", "value": 4},
        is_hidden=True
    ),
]


# XP multiplier tiers
XP_MULTIPLIERS = {
    7: 1.10,    # 7-day streak: +10% XP
    30: 1.25,   # 30-day streak: +25% XP
    90: 1.50,   # 90-day streak: +50% XP
    180: 1.75,  # 180-day streak: +75% XP
    365: 2.00,  # 365-day streak: +100% XP (double XP)
}


def get_xp_multiplier(streak_days: int) -> float:
    """
    Get XP multiplier based on streak length.

    Args:
        streak_days: Current streak length

    Returns:
        XP multiplier (1.0 = no bonus)
    """
    multiplier = 1.0
    for threshold, mult in sorted(XP_MULTIPLIERS.items()):
        if streak_days >= threshold:
            multiplier = mult
    return multiplier


__all__ = [
    "Achievement",
    "AchievementCategory",
    "AchievementTier",
    "UserAchievement",
    "DEFAULT_ACHIEVEMENTS",
    "XP_MULTIPLIERS",
    "get_xp_multiplier",
]
