"""
Brain AI Coach - Recovery Mode

Adaptive coaching mode that adjusts intervention intensity based on user state.
Switches between push mode (growth) and recovery mode (rest).

Usage:
    from brain.ai.coach.recovery_mode import RecoveryModeManager
    
    manager = RecoveryModeManager()
    mode = manager.determine_mode(user_state)
    print(mode)  # "push", "recovery", or "crisis"
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

from brain.ai.coach.user_assessment import UserState, RiskLevel


class RecoveryMode(Enum):
    """Coaching mode based on user state."""
    PUSH = "push"              # Normal coaching, encourages growth
    MAINTENANCE = "maintenance" # Reduced expectations, focus on consistency
    RECOVERY = "recovery"       # Gentle coaching, prioritize rest
    CRISIS = "crisis"           # Minimal interventions, crisis support


@dataclass
class ModeConfig:
    """
    Configuration for a coaching mode.
    
    Attributes:
        mode: The coaching mode
        habit_target_multiplier: Multiplier for daily habit targets
        show_celebrations: Whether to show celebration interventions
        allow_new_habits: Whether to allow adding new habits
        max_daily_interventions: Maximum interventions per day
        message_tone: Tone for messages in this mode
        focus_areas: Priority focus areas
    """
    mode: RecoveryMode
    habit_target_multiplier: float = 1.0
    show_celebrations: bool = True
    allow_new_habits: bool = True
    max_daily_interventions: int = 4
    message_tone: str = "encouraging"
    focus_areas: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mode": self.mode.value,
            "habit_target_multiplier": self.habit_target_multiplier,
            "show_celebrations": self.show_celebrations,
            "allow_new_habits": self.allow_new_habits,
            "max_daily_interventions": self.max_daily_interventions,
            "message_tone": self.message_tone,
            "focus_areas": self.focus_areas
        }


# Default configurations for each mode
MODE_CONFIGS = {
    RecoveryMode.PUSH: ModeConfig(
        mode=RecoveryMode.PUSH,
        habit_target_multiplier=1.0,
        show_celebrations=True,
        allow_new_habits=True,
        max_daily_interventions=6,
        message_tone="motivational",
        focus_areas=["growth", "achievement", "consistency"]
    ),
    
    RecoveryMode.MAINTENANCE: ModeConfig(
        mode=RecoveryMode.MAINTENANCE,
        habit_target_multiplier=0.75,
        show_celebrations=True,
        allow_new_habits=False,
        max_daily_interventions=4,
        message_tone="supportive",
        focus_areas=["consistency", "health"]
    ),
    
    RecoveryMode.RECOVERY: ModeConfig(
        mode=RecoveryMode.RECOVERY,
        habit_target_multiplier=0.5,
        show_celebrations=False,
        allow_new_habits=False,
        max_daily_interventions=2,
        message_tone="gentle",
        focus_areas=["rest", "self_care", "health"]
    ),
    
    RecoveryMode.CRISIS: ModeConfig(
        mode=RecoveryMode.CRISIS,
        habit_target_multiplier=0.0,
        show_celebrations=False,
        allow_new_habits=False,
        max_daily_interventions=1,
        message_tone="caring",
        focus_areas=["rest", "support"]
    )
}


class RecoveryModeManager:
    """
    Manages coaching mode transitions based on user state.
    
    The manager determines the appropriate coaching mode based on:
    - Burnout risk level
    - Streak health
    - Recent performance trends
    - Time since last mode change
    
    Usage:
        manager = RecoveryModeManager()
        
        # Determine current mode
        mode = manager.determine_mode(user_state)
        
        # Get mode configuration
        config = manager.get_mode_config(mode)
        
        # Check if mode transition is needed
        if manager.should_transition(user_state):
            new_mode = manager.transition(user_state)
    """
    
    # Thresholds for mode determination
    BURNOUT_PUSH_THRESHOLD = 30
    BURNOUT_MAINTENANCE_THRESHOLD = 50
    BURNOUT_RECOVERY_THRESHOLD = 70
    
    STREAK_HEALTH_WARNING = 50
    STREAK_HEALTH_CRITICAL = 30
    
    # Minimum time between mode transitions
    MIN_TRANSITION_INTERVAL = timedelta(hours=12)
    
    def __init__(self):
        """Initialize the recovery mode manager."""
        self._current_mode: RecoveryMode = RecoveryMode.PUSH
        self._last_transition: Optional[datetime] = None
        self._mode_history: List[Dict[str, Any]] = []
    
    @property
    def current_mode(self) -> RecoveryMode:
        """Get current coaching mode."""
        return self._current_mode
    
    def determine_mode(self, user_state: UserState) -> RecoveryMode:
        """
        Determine the appropriate coaching mode.
        
        Args:
            user_state: Current user state assessment
            
        Returns:
            Appropriate RecoveryMode
        """
        burnout_risk = user_state.burnout_risk
        streak_health = user_state.streak_health
        
        # Crisis mode: Critical burnout risk
        if burnout_risk >= self.BURNOUT_RECOVERY_THRESHOLD + 10:
            return RecoveryMode.CRISIS
        
        # Recovery mode: High burnout risk
        if burnout_risk >= self.BURNOUT_RECOVERY_THRESHOLD:
            return RecoveryMode.RECOVERY
        
        # Recovery mode: Critical streak health
        if streak_health < self.STREAK_HEALTH_CRITICAL:
            return RecoveryMode.RECOVERY
        
        # Maintenance mode: Moderate burnout risk
        if burnout_risk >= self.BURNOUT_MAINTENANCE_THRESHOLD:
            return RecoveryMode.MAINTENANCE
        
        # Maintenance mode: Warning streak health
        if streak_health < self.STREAK_HEALTH_WARNING:
            return RecoveryMode.MAINTENANCE
        
        # Push mode: Low burnout risk, healthy streaks
        return RecoveryMode.PUSH
    
    def should_transition(self, user_state: UserState) -> bool:
        """
        Check if mode transition is needed.
        
        Args:
            user_state: Current user state
            
        Returns:
            True if transition is recommended
        """
        # Check minimum interval
        if self._last_transition:
            if datetime.now() - self._last_transition < self.MIN_TRANSITION_INTERVAL:
                return False
        
        # Check if mode would change
        recommended = self.determine_mode(user_state)
        return recommended != self._current_mode
    
    def transition(self, user_state: UserState) -> RecoveryMode:
        """
        Transition to the appropriate mode.
        
        Args:
            user_state: Current user state
            
        Returns:
            New RecoveryMode
        """
        new_mode = self.determine_mode(user_state)
        
        if new_mode != self._current_mode:
            # Record transition
            self._mode_history.append({
                "from_mode": self._current_mode.value,
                "to_mode": new_mode.value,
                "timestamp": datetime.now().isoformat(),
                "burnout_risk": user_state.burnout_risk,
                "streak_health": user_state.streak_health
            })
            
            self._current_mode = new_mode
            self._last_transition = datetime.now()
        
        return self._current_mode
    
    def get_mode_config(self, mode: Optional[RecoveryMode] = None) -> ModeConfig:
        """
        Get configuration for a coaching mode.
        
        Args:
            mode: Mode to get config for (defaults to current)
            
        Returns:
            ModeConfig instance
        """
        mode = mode or self._current_mode
        return MODE_CONFIGS.get(mode, MODE_CONFIGS[RecoveryMode.PUSH])
    
    def get_adjusted_targets(
        self,
        habits: List[Dict[str, Any]],
        mode: Optional[RecoveryMode] = None
    ) -> List[Dict[str, Any]]:
        """
        Adjust habit targets based on coaching mode.
        
        Args:
            habits: List of habit data
            mode: Coaching mode (defaults to current)
            
        Returns:
            List of habits with adjusted targets
        """
        config = self.get_mode_config(mode)
        multiplier = config.habit_target_multiplier
        
        adjusted = []
        for habit in habits:
            adjusted_habit = habit.copy()
            
            # Adjust target if applicable
            if "daily_target" in habit:
                adjusted_habit["adjusted_target"] = habit["daily_target"] * multiplier
            
            # Add mode-specific flags
            adjusted_habit["in_recovery_mode"] = multiplier < 1.0
            adjusted_habit["priority"] = "essential" if multiplier < 0.5 else "normal"
            
            adjusted.append(adjusted_habit)
        
        return adjusted
    
    def get_filtered_interventions(
        self,
        intervention_types: List[str],
        mode: Optional[RecoveryMode] = None
    ) -> List[str]:
        """
        Filter intervention types based on coaching mode.
        
        Args:
            intervention_types: List of intervention type strings
            mode: Coaching mode (defaults to current)
            
        Returns:
            Filtered list of allowed intervention types
        """
        config = self.get_mode_config(mode)
        
        # In crisis mode, only allow critical interventions
        if config.mode == RecoveryMode.CRISIS:
            return ["burnout_warning", "recovery_suggestion"]
        
        # In recovery mode, filter out celebrations and growth-focused
        if config.mode == RecoveryMode.RECOVERY:
            excluded = ["streak_celebration", "milestone_celebration", "milestone_approach"]
            return [t for t in intervention_types if t not in excluded]
        
        # In maintenance mode, allow most but limit
        if config.mode == RecoveryMode.MAINTENANCE:
            return intervention_types
        
        # In push mode, allow all
        return intervention_types
    
    def get_mode_message(self, mode: Optional[RecoveryMode] = None) -> str:
        """
        Get a message explaining the current coaching mode.
        
        Args:
            mode: Coaching mode (defaults to current)
            
        Returns:
            Human-readable mode message
        """
        mode = mode or self._current_mode
        
        messages = {
            RecoveryMode.PUSH: (
                "You're in growth mode! Keep pushing your limits. "
                "I'll provide full coaching support to help you achieve your goals."
            ),
            RecoveryMode.MAINTENANCE: (
                "You're in maintenance mode. Let's focus on consistency rather than growth. "
                "I've slightly reduced your targets to help you maintain momentum."
            ),
            RecoveryMode.RECOVERY: (
                "You're in recovery mode. Your well-being is the priority right now. "
                "I've reduced your targets significantly. Focus on self-care and rest."
            ),
            RecoveryMode.CRISIS: (
                "You're in crisis mode. Please prioritize your health above all else. "
                "Consider taking a complete break. Your habits will be here when you're ready."
            )
        }
        
        return messages.get(mode, messages[RecoveryMode.PUSH])
    
    def get_transition_message(self, from_mode: RecoveryMode, to_mode: RecoveryMode) -> str:
        """
        Get a message for mode transition.
        
        Args:
            from_mode: Previous mode
            to_mode: New mode
            
        Returns:
            Transition message
        """
        # Transition to easier mode (concern)
        if to_mode.value > from_mode.value:
            if to_mode == RecoveryMode.RECOVERY:
                return (
                    "Based on your recent metrics, I'm switching to recovery mode. "
                    "Your burnout risk has increased. Let's focus on rest and recovery."
                )
            elif to_mode == RecoveryMode.CRISIS:
                return (
                    "I'm very concerned about your current state. "
                    "Please prioritize your health and take time to recover."
                )
            else:
                return (
                    "I'm adjusting your coaching mode to help you maintain balance. "
                    "Let's focus on consistency rather than growth for now."
                )
        
        # Transition to harder mode (celebration)
        else:
            if to_mode == RecoveryMode.PUSH:
                return (
                    "Great news! Your metrics have improved and you're ready for growth mode. "
                    "Let's get back to pushing toward your goals!"
                )
            else:
                return (
                    "You're showing improvement! I'm adjusting your coaching mode. "
                    "Keep up the good work!"
                )
    
    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get mode transition history.
        
        Args:
            limit: Maximum entries to return
            
        Returns:
            List of transition records
        """
        return self._mode_history[-limit:]
    
    def force_mode(self, mode: RecoveryMode, reason: str = "user_request") -> None:
        """
        Force a specific coaching mode.
        
        Args:
            mode: Mode to force
            reason: Reason for forcing
        """
        old_mode = self._current_mode
        self._current_mode = mode
        self._last_transition = datetime.now()
        
        self._mode_history.append({
            "from_mode": old_mode.value,
            "to_mode": mode.value,
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "forced": True
        })