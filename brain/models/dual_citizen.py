"""
Dual Citizen Co-Creation

Co-tracking with partners, accountability buddies, or teams.

Based on Task 11.3.5 from PHASE_11_INTEGRATION_ROADMAP.md

Co-tracking with partners, accountability, teams.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class CitizenType(Enum):
    """Types of co-trackers."""
    PARTNER = "partner"
    ACCOUNTABILITY_BUDDY = "accountability_buddy"
    COUPLE = "couple"
    TEAM = "team"
    MENTOR = "mentor"
    COACH = "coach"


class RelationshipStatus(Enum):
    """Status of the co-tracking relationship."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


class Permission(Enum):
    """Permissions in co-tracking."""
    VIEW_ONLY = "view_only"
    SUGGEST = "suggest"
    COLLABORATE = "collaborate"
    FULL_CONTROL = "full_control"


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class CoTrackerProfile:
    """Profile for co-tracking relationship."""
    id: str
    user_id: str
    partner_id: str
    
    # Relationship
    citizen_type: CitizenType
    relationship_status: RelationshipStatus
    
    # Permissions
    my_permissions: Permission
    partner_permissions: Permission
    
    # Ground rules
    communication_preference: str  # daily_check-in, weekly_review
    conflict_resolution: str
    goals_alignment: str
    
    # Tracking
    created_at: datetime
    last_interaction: Optional[datetime] = None


@dataclass
class SharedGoal:
    """A goal shared between co-trackers."""
    id: str
    owner_id: str
    partner_id: str
    
    # Goal
    name: str
    description: str
    
    # Ownership
    owner: str  # who created it
    co_owner: str  # who co-created
    
    # Progress
    progress: float  # 0-100
    last_update: datetime
    
    # Check-ins
    check_ins: List[Dict] = field(default_factory=list)


@dataclass
class CheckIn:
    """A co-tracker check-in."""
    id: str
    goal_id: str
    user_id: str
    timestamp: datetime
    
    # Content
    status: str  # on_track, struggling, completed
    note: str
    request_support: bool = False
    
    # Partner response
    partner_response: Optional[str] = None
    partner_response_time: Optional[datetime] = None


# =============================================================================
# DUAL CITIZEN ENGINE
# =============================================================================

class DualCitizenEngine:
    """
    Co-tracking with partners.
    
    Features:
    - Partner profiles
    - Shared goals
    - Check-ins
    - Permission management
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.profiles: Dict[str, CoTrackerProfile] = {}
        self.shared_goals: Dict[str, SharedGoal] = {}
        self.check_ins: Dict[str, List[CheckIn]] = {}
    
    def create_partnership(
        self,
        user_id: str,
        partner_id: str,
        citizen_type: CitizenType,
        communication_preference: str,
        conflict_resolution: str,
        goals_alignment: str
    ) -> CoTrackerProfile:
        """Create a co-tracking partnership."""
        import uuid
        
        profile = CoTrackerProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            partner_id=partner_id,
            citizen_type=citizen_type,
            relationship_status=RelationshipStatus.PENDING,
            my_permissions=Permission.COLLABORATE,
            partner_permissions=Permission.COLLABORATE,
            communication_preference=communication_preference,
            conflict_resolution=conflict_resolution,
            goals_alignment=goals_alignment,
            created_at=datetime.now()
        )
        
        self.profiles[profile.id] = profile
        return profile
    
    def activate_partnership(self, profile_id: str) -> None:
        """Activate a partnership."""
        profile = self.profiles.get(profile_id)
        if profile:
            profile.relationship_status = RelationshipStatus.ACTIVE
            profile.last_interaction = datetime.now()
    
    def create_shared_goal(
        self,
        owner_id: str,
        partner_id: str,
        name: str,
        description: str
    ) -> SharedGoal:
        """Create a shared goal."""
        import uuid
        
        goal = SharedGoal(
            id=str(uuid.uuid4()),
            owner_id=owner_id,
            partner_id=partner_id,
            name=name,
            description=description,
            owner=owner_id,
            co_owner=partner_id,
            progress=0.0,
            last_update=datetime.now()
        )
        
        self.shared_goals[goal.id] = goal
        self.check_ins[goal.id] = []
        return goal
    
    def update_progress(
        self,
        goal_id: str,
        progress: float,
        user_id: str
    ) -> None:
        """Update goal progress."""
        goal = self.shared_goals.get(goal_id)
        if goal:
            goal.progress = max(0, min(100, progress))
            goal.last_update = datetime.now()
    
    def add_check_in(
        self,
        goal_id: str,
        user_id: str,
        status: str,
        note: str,
        request_support: bool = False
    ) -> CheckIn:
        """Add a check-in."""
        import uuid
        
        check_in = CheckIn(
            id=str(uuid.uuid4()),
            goal_id=goal_id,
            user_id=user_id,
            timestamp=datetime.now(),
            status=status,
            note=note,
            request_support=request_support
        )
        
        self.check_ins[goal_id].append(check_in)
        return check_in
    
    def respond_to_check_in(
        self,
        goal_id: str,
        check_in_id: str,
        responder_id: str,
        response: str
    ) -> None:
        """Respond to a check-in."""
        check_ins = self.check_ins.get(goal_id, [])
        for check_in in check_ins:
            if check_in.id == check_in_id:
                check_in.partner_response = response
                check_in.partner_response_time = datetime.now()
                # Update profile last interaction
                for profile in self.profiles.values():
                    if profile.partner_id == responder_id:
                        profile.last_interaction = datetime.now()
                return
    
    def get_partnership_summary(self, profile_id: str) -> Dict:
        """Get a summary of a partnership."""
        profile = self.profiles.get(profile_id)
        if not profile:
            return {}
        
        # Find shared goals
        shared = [
            g for g in self.shared_goals.values()
            if g.partner_id == profile.partner_id
        ]
        
        # Calculate stats
        active_goals = [g for g in shared if g.progress < 100]
        completed = [g for g in shared if g.progress >= 100]
        
        avg_progress = sum(g.progress for g in shared) / len(shared) if shared else 0
        
        # Check recent check-ins
        recent_check_ins = 0
        week_ago = datetime.now() - timedelta(days=7)
        for goal in shared:
            for ci in self.check_ins.get(goal.id, []):
                if ci.timestamp > week_ago:
                    recent_check_ins += 1
        
        return {
            "partner_id": profile.partner_id,
            "citizen_type": profile.citizen_type.value,
            "status": profile.relationship_status.value,
            "total_shared_goals": len(shared),
            "active_goals": len(active_goals),
            "completed_goals": len(completed),
            "avg_progress": avg_progress,
            "check_ins_this_week": recent_check_ins,
            "last_interaction": profile.last_interaction
        }
    
    def get_user_partnerships(self, user_id: str) -> List[CoTrackerProfile]:
        """Get all partnerships for a user."""
        return [
            p for p in self.profiles.values()
            if p.user_id == user_id or p.partner_id == user_id
        ]


def create_engine() -> DualCitizenEngine:
    """Factory function."""
    return DualCitizenEngine()
