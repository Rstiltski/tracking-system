"""
Brain AI Coach - Intervention Engine

Core engine that combines assessment, rules, and suggestions to generate
coaching interventions.

Usage:
    from brain.ai.coach.intervention_engine import InterventionEngine
    
    engine = InterventionEngine()
    interventions = engine.check_and_intervene(user_data)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

from brain.ai.coach.personality import PersonalityConfig, get_default_config
from brain.ai.coach.user_assessment import UserAssessment, UserState
from brain.ai.coach.rules import RuleEngine, TriggeredRule, InterventionType
from brain.ai.coach.suggestion_engine import SuggestionEngine, Suggestion


@dataclass
class Intervention:
    """
    A complete coaching intervention.
    
    Attributes:
        id: Unique intervention identifier
        triggered_rule: The rule that triggered this intervention
        user_state: User state at time of intervention
        suggestion: The suggestion to present
        created_at: When intervention was created
        delivered: Whether intervention was delivered to user
        dismissed: Whether user dismissed the intervention
        action_taken: Whether user took the suggested action
    """
    id: str
    triggered_rule: TriggeredRule
    user_state: UserState
    suggestion: Suggestion
    created_at: datetime = field(default_factory=datetime.now)
    delivered: bool = False
    dismissed: bool = False
    action_taken: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "rule_name": self.triggered_rule.rule.name,
            "intervention_type": self.triggered_rule.rule.intervention_type.value,
            "priority": self.triggered_rule.rule.priority.value,
            "suggestion": self.suggestion.to_dict(),
            "created_at": self.created_at.isoformat(),
            "delivered": self.delivered,
            "dismissed": self.dismissed,
            "action_taken": self.action_taken
        }


class InterventionEngine:
    """
    Core engine for generating coaching interventions.
    
    Combines:
    - User assessment (state evaluation)
    - Rule engine (condition checking)
    - Suggestion engine (recommendation generation)
    
    Usage:
        engine = InterventionEngine()
        interventions = engine.check_and_intervene(user_data)
        for intervention in interventions:
            print(f"{intervention.suggestion.title}: {intervention.suggestion.message}")
    """
    
    def __init__(
        self,
        personality: Optional[PersonalityConfig] = None,
        user_assessment: Optional[UserAssessment] = None,
        rule_engine: Optional[RuleEngine] = None,
        suggestion_engine: Optional[SuggestionEngine] = None
    ):
        """
        Initialize the intervention engine.
        
        Args:
            personality: Coach personality configuration
            user_assessment: Assessment engine instance
            rule_engine: Rule engine instance
            suggestion_engine: Suggestion engine instance
        """
        self.personality = personality or get_default_config()
        self.assessor = user_assessment or UserAssessment()
        self.rules = rule_engine or RuleEngine()
        self.suggestions = suggestion_engine or SuggestionEngine(self.personality)
        
        self._intervention_history: List[Intervention] = []
    
    def check_and_intervene(
        self, 
        user_data: Dict[str, Any],
        max_interventions: Optional[int] = None
    ) -> List[Intervention]:
        """
        Assess user state and generate interventions.
        
        Args:
            user_data: User tracking data dictionary
            max_interventions: Maximum interventions to return (from personality if None)
            
        Returns:
            List of Intervention objects
        """
        # Get max from personality if not specified
        if max_interventions is None:
            max_interventions = self.personality.get_max_interventions_per_day()
        
        # 1. Assess user state
        user_state = self.assessor.assess(user_data)
        
        # 2. Check rules against state
        state_dict = user_state.to_dict()
        triggered_rules = self.rules.check(state_dict)
        
        # 3. Filter by enabled intervention types
        enabled_types = self.personality.enabled_intervention_types
        filtered_rules = [
            tr for tr in triggered_rules
            if tr.rule.intervention_type.value in enabled_types
        ]
        
        # 4. Generate interventions
        interventions = []
        for triggered in filtered_rules[:max_interventions]:
            suggestion = self.suggestions.generate(
                triggered.rule.intervention_type,
                state_dict
            )
            
            intervention = Intervention(
                id=self._generate_id(triggered),
                triggered_rule=triggered,
                user_state=user_state,
                suggestion=suggestion
            )
            interventions.append(intervention)
        
        # 5. Store in history
        self._intervention_history.extend(interventions)
        
        return interventions
    
    def assess_only(self, user_data: Dict[str, Any]) -> UserState:
        """
        Perform assessment without generating interventions.
        
        Args:
            user_data: User tracking data
            
        Returns:
            UserState without interventions
        """
        return self.assessor.assess(user_data)
    
    def get_intervention_history(
        self,
        limit: int = 50,
        include_dismissed: bool = True
    ) -> List[Intervention]:
        """
        Get intervention history.
        
        Args:
            limit: Maximum interventions to return
            include_dismissed: Include dismissed interventions
            
        Returns:
            List of past interventions
        """
        history = self._intervention_history
        
        if not include_dismissed:
            history = [i for i in history if not i.dismissed]
        
        return history[-limit:]
    
    def mark_delivered(self, intervention_id: str) -> bool:
        """Mark an intervention as delivered."""
        for intervention in self._intervention_history:
            if intervention.id == intervention_id:
                intervention.delivered = True
                return True
        return False
    
    def mark_dismissed(self, intervention_id: str) -> bool:
        """Mark an intervention as dismissed by user."""
        for intervention in self._intervention_history:
            if intervention.id == intervention_id:
                intervention.dismissed = True
                return True
        return False
    
    def mark_action_taken(self, intervention_id: str) -> bool:
        """Mark that user took the suggested action."""
        for intervention in self._intervention_history:
            if intervention.id == intervention_id:
                intervention.action_taken = True
                return True
        return False
    
    def _generate_id(self, triggered: TriggeredRule) -> str:
        """Generate a unique intervention ID."""
        import uuid
        return f"{triggered.rule.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    def update_personality(self, personality: PersonalityConfig) -> None:
        """Update coach personality configuration."""
        self.personality = personality
        self.suggestions.personality = personality


class DigitalCoach:
    """
    High-level Digital Coach interface.
    
    Provides a simple interface for the coaching system:
    - Automatic intervention checking
    - State assessment
    - History tracking
    
    Usage:
        coach = DigitalCoach()
        
        # Check for interventions
        interventions = coach.check(user_data)
        
        # Get current user state
        state = coach.get_state(user_data)
        
        # Mark intervention as handled
        coach.acknowledge(intervention_id)
    """
    
    def __init__(self, personality: Optional[PersonalityConfig] = None):
        """
        Initialize the Digital Coach.
        
        Args:
            personality: Coach personality configuration
        """
        self.personality = personality or get_default_config()
        self.engine = InterventionEngine(self.personality)
        self._last_check: Optional[datetime] = None
        self._current_state: Optional[UserState] = None
        self._active_interventions: List[Intervention] = []
    
    def check(
        self, 
        user_data: Dict[str, Any],
        force: bool = False
    ) -> List[Intervention]:
        """
        Check for interventions.
        
        Args:
            user_data: User tracking data
            force: Force check even if recently checked
            
        Returns:
            List of new interventions
        """
        # Update state
        self._current_state = self.engine.assess_only(user_data)
        
        # Get interventions
        interventions = self.engine.check_and_intervene(user_data)
        self._active_interventions = interventions
        self._last_check = datetime.now()
        
        return interventions
    
    def get_state(self, user_data: Dict[str, Any]) -> UserState:
        """
        Get current user state assessment.
        
        Args:
            user_data: User tracking data
            
        Returns:
            UserState object
        """
        if self._current_state is None:
            self._current_state = self.engine.assess_only(user_data)
        return self._current_state
    
    def acknowledge(self, intervention_id: str, action_taken: bool = False) -> bool:
        """
        Acknowledge an intervention.
        
        Args:
            intervention_id: Intervention to acknowledge
            action_taken: Whether user took the suggested action
            
        Returns:
            True if intervention was found
        """
        if action_taken:
            return self.engine.mark_action_taken(intervention_id)
        return self.engine.mark_delivered(intervention_id)
    
    def dismiss(self, intervention_id: str) -> bool:
        """Dismiss an intervention."""
        return self.engine.mark_dismissed(intervention_id)
    
    def get_active_interventions(self) -> List[Intervention]:
        """Get currently active (non-dismissed) interventions."""
        return [i for i in self._active_interventions if not i.dismissed]
    
    def get_history(self, limit: int = 50) -> List[Intervention]:
        """Get intervention history."""
        return self.engine.get_intervention_history(limit)
    
    def set_personality(self, personality: PersonalityConfig) -> None:
        """Update coach personality."""
        self.personality = personality
        self.engine.update_personality(personality)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get coach status summary."""
        return {
            "personality": self.personality.personality.value,
            "tone": self.personality.tone.value,
            "intervention_frequency": self.personality.intervention_frequency.value,
            "last_check": self._last_check.isoformat() if self._last_check else None,
            "active_interventions": len(self.get_active_interventions()),
            "current_burnout_risk": self._current_state.burnout_risk if self._current_state else None,
            "current_streak_health": self._current_state.streak_health if self._current_state else None
        }