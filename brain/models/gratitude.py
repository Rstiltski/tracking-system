"""
Gratitude & Kindness Logger

Track gratitude and kindness acts to counter loneliness epidemic.

Based on Task 11.2.10 from PHASE_11_INTEGRATION_ROADMAP.md

Addresses loneliness epidemic!
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class GratitudeCategory(Enum):
    """Categories of gratitude."""
    PEOPLE = "people"           # People in your life
    EXPERIENCES = "experiences"  # Life experiences
    THINGS = "things"          # Material things
    ACHIEVEMENTS = "achievements"  # Personal achievements
    NATURE = "nature"          # Nature and environment
    HEALTH = "health"          # Health and body
    OPPORTUNITIES = "opportunities"  # Opportunities


class KindnessCategory(Enum):
    """Categories of kindness acts."""
    SELF = "self"             # Acts of self-kindness
    FAMILY = "family"         # Family members
    FRIENDS = "friends"       # Friends
    STRANGERS = "strangers"   # Strangers/acquaintances
    COMMUNITY = "community"   # Community/society
    ENVIRONMENT = "environment"  # Environment/nature


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class GratitudeEntry:
    """A gratitude entry."""
    id: str
    user_id: str
    date: date
    timestamp: datetime
    category: GratitudeCategory
    text: str
    impact_score: int = 1  # How much this meant (1-5)


@dataclass
class KindnessEntry:
    """A kindness act entry."""
    id: str
    user_id: str
    date: date
    timestamp: datetime
    category: KindnessCategory
    description: str
    recipient: str  # Who was the act for
    impact_score: int = 1  # How meaningful (1-5)


@dataclass
class GratitudeStats:
    """Statistics for gratitude practice."""
    total_entries: int
    streak_days: int
    category_breakdown: Dict[str, int]
    avg_impact: float


# =============================================================================
# GRATITUDE ENGINE
# =============================================================================

class GratitudeEngine:
    """
    Manages gratitude and kindness logging.
    
    Features:
    - Daily gratitude entries
    - Kindness tracking
    - Streak tracking
    - Weekly/monthly summaries
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.gratitude_entries: List[GratitudeEntry] = []
        self.kindness_entries: List[KindnessEntry] = []
    
    def add_gratitude(
        self,
        user_id: str,
        category: GratitudeCategory,
        text: str,
        impact_score: int = 3
    ) -> GratitudeEntry:
        """Add a gratitude entry."""
        import uuid
        
        entry = GratitudeEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            date=date.today(),
            timestamp=datetime.now(),
            category=category,
            text=text,
            impact_score=impact_score
        )
        
        self.gratitude_entries.append(entry)
        return entry
    
    def add_kindness(
        self,
        user_id: str,
        category: KindnessCategory,
        description: str,
        recipient: str,
        impact_score: int = 3
    ) -> KindnessEntry:
        """Add a kindness entry."""
        import uuid
        
        entry = KindnessEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            date=date.today(),
            timestamp=datetime.now(),
            category=category,
            description=description,
            recipient=recipient,
            impact_score=impact_score
        )
        
        self.kindness_entries.append(entry)
        return entry
    
    def get_user_gratitude(
        self, 
        user_id: str, 
        days: int = 7
    ) -> List[GratitudeEntry]:
        """Get recent gratitude entries."""
        from datetime import timedelta
        
        cutoff = date.today() - timedelta(days=days)
        
        return [
            e for e in self.gratitude_entries
            if e.user_id == user_id and e.date >= cutoff
        ]
    
    def get_user_kindness(
        self, 
        user_id: str, 
        days: int = 7
    ) -> List[KindnessEntry]:
        """Get recent kindness entries."""
        from datetime import timedelta
        
        cutoff = date.today() - timedelta(days=days)
        
        return [
            e for e in self.kindness_entries
            if e.user_id == user_id and e.date >= cutoff
        ]
    
    def calculate_streak(self, user_id: str) -> int:
        """Calculate current gratitude streak."""
        # Group entries by date
        dates = set(e.date for e in self.gratitude_entries if e.user_id == user_id)
        
        if not dates:
            return 0
        
        # Count consecutive days ending today
        streak = 0
        current = date.today()
        
        while current in dates or (streak == 0 and current == date.today()):
            if current in dates:
                streak += 1
                current = current - __import__('datetime').timedelta(days=1)
            else:
                break
        
        return streak
    
    def get_stats(self, user_id: str, days: int = 30) -> Dict:
        """Get gratitude statistics."""
        from datetime import timedelta
        
        cutoff = date.today() - timedelta(days=days)
        
        entries = [
            e for e in self.gratitude_entries
            if e.user_id == user_id and e.date >= cutoff
        ]
        
        # Category breakdown
        categories = {}
        for e in entries:
            cat = e.category.value
            categories[cat] = categories.get(cat, 0) + 1
        
        # Average impact
        avg_impact = sum(e.impact_score for e in entries) / len(entries) if entries else 0
        
        return {
            "total_entries": len(entries),
            "streak": self.calculate_streak(user_id),
            "category_breakdown": categories,
            "avg_impact": avg_impact,
            "kindness_count": len([
                e for e in self.kindness_entries
                if e.user_id == user_id and e.date >= cutoff
            ])
        }


def create_engine() -> GratitudeEngine:
    """Factory function."""
    return GratitudeEngine()
