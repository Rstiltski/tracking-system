"""
Dyadic/Couples Tracking Model

Track habits together. Shared goals and accountability.

Based on Task 11.2.9 from PHASE_11_INTEGRATION_ROADMAP.md

Relationship market - significant untapped potential!
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class RelationshipType(Enum):
    """Types of relationships."""
    PARTNER = "partner"       # Romantic partner
    FRIEND = "friend"        # Close friend
    FAMILY = "family"        # Family member
    MENTOR = "mentor"        # Mentor/mentee
    COWORKER = "coworker"    # Work buddy


class ActivityCategory(Enum):
    """Categories of couple activities."""
    HEALTH = "health"           # Exercise, wellness
    LEARNING = "learning"       # Reading, courses
    CREATIVE = "creative"       # Art, music, projects
    SOCIAL = "social"          # Friends, family
    ADVENTURE = "adventure"    # Travel, exploration
    ROUTINE = "routine"        # Chores, daily life
    ROMANCE = "romance"        # Date night, intimacy
    GROWTH = "growth"          # Personal development


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class Partner:
    """A partner in tracking."""
    id: str
    name: str
    relationship_type: RelationshipType
    user_id: str  # Who added this partner


@dataclass
class SharedActivity:
    """A shared activity between partners."""
    id: str
    partners: List[str]  # Partner IDs
    activity_name: str
    category: ActivityCategory
    frequency: str  # daily, weekly, etc.
    created_at: datetime
    
    # Tracking
    completed_dates: List[date] = field(default_factory=list)
    last_completed: Optional[date] = None
    
    # Stats
    total_completions: int = 0
    streak: int = 0


@dataclass
class CheckIn:
    """A check-in from a partner."""
    id: str
    activity_id: str
    partner_id: str
    timestamp: datetime
    completed: bool
    note: str


# =============================================================================
# DYADIC TRACKING ENGINE
# =============================================================================

class DyadicEngine:
    """
    Manages dyadic/couples tracking.
    
    Features:
    - Partner management
    - Shared activities
    - Joint progress tracking
    - Accountability between partners
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.partners: Dict[str, Partner] = {}
        self.activities: Dict[str, SharedActivity] = {}
        self.check_ins: List[CheckIn] = []
    
    def add_partner(
        self,
        user_id: str,
        name: str,
        relationship_type: RelationshipType
    ) -> Partner:
        """Add a partner."""
        import uuid
        
        partner = Partner(
            id=str(uuid.uuid4()),
            name=name,
            relationship_type=relationship_type,
            user_id=user_id
        )
        
        self.partners[partner.id] = partner
        return partner
    
    def create_shared_activity(
        self,
        partner_ids: List[str],
        activity_name: str,
        category: ActivityCategory,
        frequency: str
    ) -> SharedActivity:
        """Create a shared activity."""
        import uuid
        
        activity = SharedActivity(
            id=str(uuid.uuid4()),
            partners=partner_ids,
            activity_name=activity_name,
            category=category,
            frequency=frequency,
            created_at=datetime.now()
        )
        
        self.activities[activity.id] = activity
        return activity
    
    def log_completion(
        self,
        activity_id: str,
        partner_id: str,
        note: str = ""
    ) -> CheckIn:
        """Log activity completion."""
        import uuid
        
        check_in = CheckIn(
            id=str(uuid.uuid4()),
            activity_id=activity_id,
            partner_id=partner_id,
            timestamp=datetime.now(),
            completed=True,
            note=note
        )
        
        self.check_ins.append(check_in)
        
        # Update activity
        activity = self.activities.get(activity_id)
        if activity:
            today = date.today()
            activity.completed_dates.append(today)
            activity.last_completed = today
            activity.total_completions += 1
            
            # Simple streak calculation
            if len(activity.completed_dates) > 1:
                # Check if consecutive
                sorted_dates = sorted(activity.completed_dates)
                activity.streak = 1
                for i in range(1, len(sorted_dates)):
                    if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                        activity.streak += 1
                    else:
                        break
        
        return check_in
    
    def get_user_partners(self, user_id: str) -> List[Partner]:
        """Get all partners for a user."""
        return [p for p in self.partners.values() if p.user_id == user_id]
    
    def get_shared_activities(self, partner_id: str) -> List[SharedActivity]:
        """Get activities shared with a partner."""
        return [
            a for a in self.activities.values()
            if partner_id in a.partners
        ]
    
    def get_partner_stats(self, partner_id: str) -> Dict:
        """Get stats for a partnership."""
        activities = self.get_shared_activities(partner_id)
        
        total_completions = sum(a.total_completions for a in activities)
        avg_streak = sum(a.streak for a in activities) / len(activities) if activities else 0
        
        return {
            "total_activities": len(activities),
            "total_completions": total_completions,
            "avg_streak": avg_streak,
            "categories": list(set(a.category.value for a in activities))
        }


def create_engine() -> DyadicEngine:
    """Factory function."""
    return DyadicEngine()
