"""
Dopamine Menu Model

Personalized menu of healthy dopamine activities for craving management.

Based on Task 11.2.6 from PHASE_11_INTEGRATION_ROADMAP.md

QUICK WIN - LOW effort (1 week)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# DOPAMINE CATEGORIES
# =============================================================================

class DopamineCategory(Enum):
    """Categories of dopamine activities based on time/effort."""
    QUICK_HITS = "quick_hits"      # 0-5 min
    MEDIUM_BOOST = "medium_boost"   # 5-20 min
    DEEP_SATISFACTION = "deep_satisfaction"  # 20+ min


# =============================================================================
# PRE-DEFINED DOPAMINE ACTIVITIES
# =============================================================================

DEFAULT_ACTIVITIES = {
    # Quick Hits (0-5 min)
    DopamineCategory.QUICK_HITS: [
        {"name": "Take 10 deep breaths", "duration": 1, "intensity": "calm"},
        {"name": "Listen to favorite song", "duration": 3, "intensity": "boost"},
        {"name": "Do 10 jumping jacks", "duration": 2, "intensity": "energy"},
        {"name": "Stretch arms and shoulders", "duration": 2, "intensity": "calm"},
        {"name": "Look at nature through window", "duration": 1, "intensity": "calm"},
        {"name": "Drink cold water", "duration": 1, "intensity": "alert"},
        {"name": "Smile at yourself in mirror", "duration": 1, "intensity": "boost"},
        {"name": "Tidy one small area", "duration": 5, "intensity": "accomplishment"},
        {"name": "Text someone you love", "duration": 2, "intensity": "connection"},
        {"name": "Compliment yourself (out loud)", "duration": 1, "intensity": "boost"},
    ],
    
    # Medium Boost (5-20 min)
    DopamineCategory.MEDIUM_BOOST: [
        {"name": "Go for a short walk", "duration": 10, "intensity": "energy"},
        {"name": "Read a few pages of book", "duration": 10, "intensity": "calm"},
        {"name": "Call a friend", "duration": 15, "intensity": "connection"},
        {"name": "Do a 5-min meditation", "duration": 5, "intensity": "calm"},
        {"name": "Cook something healthy", "duration": 20, "intensity": "accomplishment"},
        {"name": "Listen to podcast episode", "duration": 15, "intensity": "learning"},
        {"name": "Do a quick workout", "duration": 10, "intensity": "energy"},
        {"name": "Write in journal (3 things)", "duration": 5, "intensity": "reflection"},
        {"name": "Take a shower/bath", "duration": 15, "intensity": "reset"},
        {"name": "Organize one drawer/space", "duration": 10, "intensity": "accomplishment"},
    ],
    
    # Deep Satisfaction (20+ min)
    DopamineCategory.DEEP_SATISFACTION: [
        {"name": "Exercise session", "duration": 30, "intensity": "energy"},
        {"name": "Deep clean one room", "duration": 45, "intensity": "accomplishment"},
        {"name": "Long nature hike", "duration": 60, "intensity": "renewal"},
        {"name": "Creative project time", "duration": 45, "intensity": "flow"},
        {"name": "Cook a full meal", "duration": 45, "intensity": "accomplishment"},
        {"name": "Video call with loved one", "duration": 30, "intensity": "connection"},
        {"name": "Volunteer/help someone", "duration": 60, "intensity": "purpose"},
        {"name": "Learn something new", "duration": 30, "intensity": "growth"},
        {"name": "Deep meditation session", "duration": 30, "intensity": "calm"},
        {"name": "Read for pleasure", "duration": 45, "intensity": "calm"},
    ],
}


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class DopamineActivity:
    """A single dopamine activity."""
    name: str
    duration_minutes: int
    intensity: str  # calm, boost, energy, accomplishment, connection, etc.
    category: DopamineCategory
    user_preferred: bool = False
    times_completed: int = 0


@dataclass
class CravingRecord:
    """Record of a craving episode."""
    timestamp: datetime
    trigger: str  # What triggered the craving
    intensity: int  # 1-10 scale
    activity_suggested: Optional[str] = None
    activity_completed: bool = False
    satisfaction_after: Optional[int] = None  # 1-10


@dataclass
class DopamineMenu:
    """User's personalized dopamine menu."""
    user_id: str
    activities: List[DopamineActivity] = field(default_factory=list)
    craving_history: List[CravingRecord] = field(default_factory=list)
    favorite_triggers: List[str] = field(default_factory=list)


# =============================================================================
# DOPAMINE MENU ENGINE
# =============================================================================

class DopamineMenuEngine:
    """
    Manages personalized dopamine menus.
    
    Features:
    - Pre-populated activity library
    - User preference tracking
    - Craving detection and response
    - Activity personalization
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.menus: Dict[str, DopamineMenu] = {}
    
    def get_or_create_menu(self, user_id: str) -> DopamineMenu:
        """Get or create a user's menu."""
        if user_id not in self.menus:
            menu = DopamineMenu(user_id=user_id)
            # Initialize with default activities
            self._populate_defaults(menu)
            self.menus[user_id] = menu
        return self.menus[user_id]
    
    def _populate_defaults(self, menu: DopamineMenu) -> None:
        """Populate menu with default activities."""
        for category, activities in DEFAULT_ACTIVITIES.items():
            for act in activities:
                activity = DopamineActivity(
                    name=act["name"],
                    duration_minutes=act["duration"],
                    intensity=act["intensity"],
                    category=category
                )
                menu.activities.append(activity)
    
    def get_activities_by_category(
        self, 
        user_id: str, 
        category: DopamineCategory
    ) -> List[DopamineActivity]:
        """Get activities filtered by category."""
        menu = self.get_or_create_menu(user_id)
        return [a for a in menu.activities if a.category == category]
    
    def get_activities_by_intensity(
        self, 
        user_id: str, 
        intensity: str
    ) -> List[DopamineActivity]:
        """Get activities filtered by intensity."""
        menu = self.get_or_create_menu(user_id)
        return [a for a in menu.activities if a.intensity == intensity]
    
    def record_craving(
        self, 
        user_id: str, 
        trigger: str, 
        intensity: int,
        activity_suggested: Optional[str] = None
    ) -> CravingRecord:
        """Record a craving episode."""
        menu = self.get_or_create_menu(user_id)
        
        craving = CravingRecord(
            timestamp=datetime.now(),
            trigger=trigger,
            intensity=intensity,
            activity_suggested=activity_suggested
        )
        
        menu.craving_history.append(craving)
        
        # Track trigger patterns
        if trigger not in menu.favorite_triggers:
            menu.favorite_triggers.append(trigger)
        
        return craving
    
    def complete_activity(
        self, 
        user_id: str, 
        activity_name: str, 
        satisfaction: int
    ) -> None:
        """Record activity completion."""
        menu = self.get_or_create_menu(user_id)
        
        # Find and update activity
        for activity in menu.activities:
            if activity.name == activity_name:
                activity.times_completed += 1
                activity.user_preferred = True
                break
        
        # Update most recent craving if exists
        if menu.craving_history:
            latest = menu.craving_history[-1]
            if latest.activity_suggested == activity_name:
                latest.activity_completed = True
                latest.satisfaction_after = satisfaction
    
    def suggest_activity(
        self, 
        user_id: str, 
        available_time: int,
        desired_intensity: str = "any"
    ) -> Optional[DopamineActivity]:
        """
        Suggest an activity based on available time and desired intensity.
        
        Args:
            user_id: User ID
            available_time: Minutes available
            desired_intensity: Preferred intensity (or "any")
            
        Returns:
            Recommended activity or None
        """
        menu = self.get_or_create_menu(user_id)
        
        # Filter by time
        available = [a for a in menu.activities if a.duration_minutes <= available_time]
        
        # Filter by intensity
        if desired_intensity != "any":
            available = [a for a in available if a.intensity == desired_intensity]
        
        # Sort by user preference (most completed first)
        available.sort(key=lambda x: (-x.times_completed, -x.user_preferred))
        
        return available[0] if available else None
    
    def get_menu_summary(self, user_id: str) -> Dict:
        """Get a summary of the user's dopamine menu."""
        menu = self.get_or_create_menu(user_id)
        
        return {
            "total_activities": len(menu.activities),
            "by_category": {
                c.value: len([a for a in menu.activities if a.category == c])
                for c in DopamineCategory
            },
            "preferred_count": len([a for a in menu.activities if a.user_preferred]),
            "total_cravings": len(menu.craving_history),
            "cravings_satisfied": len([c for c in menu.craving_history if c.activity_completed]),
        }


def create_engine() -> DopamineMenuEngine:
    """Factory function to create the engine."""
    return DopamineMenuEngine()
