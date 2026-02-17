"""
Implementation Intentions Module

Implements Peter Gollwitzer's If-Then planning methodology for behavior change.
Based on the structure: "If situation X is encountered, then I will perform response Y"

Key Concepts:
- Implementation Intention: A self-regulatory strategy that delegates behavior
  control to environmental cues, bypassing willpower
- Strategic Automaticity: Creates automatic behavior triggers from chosen cues
- Intention-Behavior Gap: The gap this module helps close

Reference:
- Gollwitzer, P. M. (1999). "Implementation intentions: Strong effects of simple plans"
- American Psychologist, 54(7), 493-503

Effect Size: d = 0.6-0.8 on goal attainment (medium-to-large)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable, Union
from datetime import datetime, date, time
from enum import Enum
import uuid
import re
import json


class TriggerType(Enum):
    """Types of triggers for implementation intentions."""
    TIME = "time"              # Clock-based: "When it's 08:00"
    EVENT = "event"            # Event-based: "After I complete habit X"
    LOCATION = "location"      # Location-based: "When I arrive at gym"
    APP_STATE = "app_state"    # App-based: "When VS Code opens"
    CALENDAR = "calendar"      # Calendar-based: "Before meeting starts"
    CUSTOM = "custom"          # Custom predicate


class ActionType(Enum):
    """Types of actions for implementation intentions."""
    NOTIFICATION = "notification"  # Send a notification
    UI_CHANGE = "ui_change"        # Change UI state
    SCRIPT = "script"              # Execute a script
    HABIT_PROMPT = "habit_prompt"  # Prompt to complete a habit
    REMINDER = "reminder"          # Set a reminder


@dataclass
class IfCondition:
    """
    The "If" part of an implementation intention.
    
    Defines the trigger condition that will initiate the behavior.
    Must be specific and concrete for effectiveness.
    
    Example:
        IfCondition(
            trigger_type=TriggerType.TIME,
            source="clock",
            predicate="time == '08:00'"
        )
    """
    trigger_type: TriggerType
    source: str  # 'clock', 'calendar', 'habit_completion', 'location', etc.
    predicate: str  # The condition to evaluate
    description: str = ""  # Human-readable description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trigger_type': self.trigger_type.value,
            'source': self.source,
            'predicate': self.predicate,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IfCondition':
        return cls(
            trigger_type=TriggerType(data['trigger_type']),
            source=data['source'],
            predicate=data['predicate'],
            description=data.get('description', '')
        )
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate if the condition is met given the current context.
        
        Args:
            context: Dictionary containing current state (time, location, events, etc.)
            
        Returns:
            True if condition is met, False otherwise
        """
        if self.trigger_type == TriggerType.TIME:
            return self._evaluate_time(context)
        elif self.trigger_type == TriggerType.EVENT:
            return self._evaluate_event(context)
        elif self.trigger_type == TriggerType.LOCATION:
            return self._evaluate_location(context)
        elif self.trigger_type == TriggerType.APP_STATE:
            return self._evaluate_app_state(context)
        elif self.trigger_type == TriggerType.CALENDAR:
            return self._evaluate_calendar(context)
        else:
            return self._evaluate_custom(context)
    
    def _evaluate_time(self, context: Dict[str, Any]) -> bool:
        """Evaluate time-based conditions."""
        current_time = context.get('current_time')
        if not current_time:
            return False
        
        # Parse predicate like "time == '08:00'" or "time >= '09:00'"
        match = re.match(r"time\s*(==|>=|<=|>|<)\s*['\"]?(\d{1,2}:\d{2})['\"]?", self.predicate)
        if not match:
            return False
        
        operator, target_time_str = match.groups()
        target_time = datetime.strptime(target_time_str, "%H:%M").time()
        
        if isinstance(current_time, datetime):
            current_time = current_time.time()
        
        if operator == '==':
            return current_time.hour == target_time.hour and current_time.minute == target_time.minute
        elif operator == '>=':
            return current_time >= target_time
        elif operator == '<=':
            return current_time <= target_time
        elif operator == '>':
            return current_time > target_time
        elif operator == '<':
            return current_time < target_time
        
        return False
    
    def _evaluate_event(self, context: Dict[str, Any]) -> bool:
        """Evaluate event-based conditions."""
        recent_events = context.get('recent_events', [])
        event_type = context.get('event_type')
        
        # Parse predicate like "event_type == 'habit_completed'"
        match = re.match(r"event_type\s*==\s*['\"]?(\w+)['\"]?", self.predicate)
        if match:
            target_event = match.group(1)
            return event_type == target_event or any(e.get('type') == target_event for e in recent_events)
        
        # Parse predicate like "habit_id == 'habit_123'"
        match = re.match(r"habit_id\s*==\s*['\"]?([\w-]+)['\"]?", self.predicate)
        if match:
            target_habit = match.group(1)
            return any(e.get('habit_id') == target_habit for e in recent_events)
        
        return False
    
    def _evaluate_location(self, context: Dict[str, Any]) -> bool:
        """Evaluate location-based conditions."""
        current_location = context.get('current_location', '')
        
        # Parse predicate like "location == 'gym'"
        match = re.match(r"location\s*==\s*['\"]?(\w+)['\"]?", self.predicate)
        if match:
            target_location = match.group(1)
            return current_location.lower() == target_location.lower()
        
        return False
    
    def _evaluate_app_state(self, context: Dict[str, Any]) -> bool:
        """Evaluate app state conditions."""
        active_app = context.get('active_app', '')
        
        # Parse predicate like "app == 'VS Code'"
        match = re.match(r"app\s*==\s*['\"]?([\w\s]+)['\"]?", self.predicate)
        if match:
            target_app = match.group(1)
            return target_app.lower() in active_app.lower()
        
        return False
    
    def _evaluate_calendar(self, context: Dict[str, Any]) -> bool:
        """Evaluate calendar-based conditions."""
        upcoming_events = context.get('upcoming_events', [])
        
        # Parse predicate like "before_event == 'meeting'"
        match = re.match(r"before_event\s*==\s*['\"]?([\w\s]+)['\"]?", self.predicate)
        if match:
            target_event = match.group(1)
            return any(target_event.lower() in e.get('title', '').lower() for e in upcoming_events)
        
        return False
    
    def _evaluate_custom(self, context: Dict[str, Any]) -> bool:
        """Evaluate custom conditions using context."""
        # For custom predicates, evaluate against context
        try:
            # Simple evaluation - can be extended for complex predicates
            return context.get(self.predicate, False)
        except Exception:
            return False


@dataclass
class ThenAction:
    """
    The "Then" part of an implementation intention.
    
    Defines the action to take when the condition is met.
    Should be immediate and specific.
    
    Example:
        ThenAction(
            action_type=ActionType.NOTIFICATION,
            payload="Drink water now!"
        )
    """
    action_type: ActionType
    payload: str  # Action details (message, script, etc.)
    priority: int = 0  # Higher priority = more important
    delay_seconds: int = 0  # Delay before executing
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_type': self.action_type.value,
            'payload': self.payload,
            'priority': self.priority,
            'delay_seconds': self.delay_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThenAction':
        return cls(
            action_type=ActionType(data['action_type']),
            payload=data['payload'],
            priority=data.get('priority', 0),
            delay_seconds=data.get('delay_seconds', 0)
        )


@dataclass
class ImplementationIntention:
    """
    A complete implementation intention: If X, then Y.
    
    Combines a trigger condition with an action to create
    an automatic behavior pattern.
    
    Example:
        ImplementationIntention(
            goal_id="goal_health",
            if_condition=IfCondition(...),
            then_action=ThenAction(...),
            name="Morning water reminder"
        )
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal_id: str = ""
    user_id: str = ""
    name: str = ""
    if_condition: Optional[IfCondition] = None
    then_action: Optional[ThenAction] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    trigger_count: int = 0
    success_count: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate of this intention."""
        if self.trigger_count == 0:
            return 0.0
        return self.success_count / self.trigger_count
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'goal_id': self.goal_id,
            'user_id': self.user_id,
            'name': self.name,
            'if_condition': self.if_condition.to_dict() if self.if_condition else None,
            'then_action': self.then_action.to_dict() if self.then_action else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'trigger_count': self.trigger_count,
            'success_count': self.success_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImplementationIntention':
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            goal_id=data.get('goal_id', ''),
            user_id=data.get('user_id', ''),
            name=data.get('name', ''),
            if_condition=IfCondition.from_dict(data['if_condition']) if data.get('if_condition') else None,
            then_action=ThenAction.from_dict(data['then_action']) if data.get('then_action') else None,
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            trigger_count=data.get('trigger_count', 0),
            success_count=data.get('success_count', 0)
        )


class RuleMatcher:
    """
    Forward-chaining rule matcher for implementation intentions.
    
    Evaluates conditions against current context to find matching intentions.
    Implements the "If" part of the If-Then logic.
    """
    
    def __init__(self):
        self.intentions: List[ImplementationIntention] = []
    
    def add_intention(self, intention: ImplementationIntention) -> None:
        """Add an intention to the matcher."""
        self.intentions.append(intention)
    
    def remove_intention(self, intention_id: str) -> bool:
        """Remove an intention by ID."""
        original_count = len(self.intentions)
        self.intentions = [i for i in self.intentions if i.id != intention_id]
        return len(self.intentions) < original_count
    
    def find_matches(self, context: Dict[str, Any]) -> List[ImplementationIntention]:
        """
        Find all intentions whose conditions match the current context.
        
        Args:
            context: Current state (time, location, events, etc.)
            
        Returns:
            List of matching intentions
        """
        matches = []
        for intention in self.intentions:
            if intention.is_active and intention.if_condition:
                if intention.if_condition.evaluate(context):
                    matches.append(intention)
        return matches
    
    def find_best_match(self, context: Dict[str, Any]) -> Optional[ImplementationIntention]:
        """Find the highest priority matching intention."""
        matches = self.find_matches(context)
        if not matches:
            return None
        
        # Sort by action priority (higher = better)
        return max(matches, key=lambda i: i.then_action.priority if i.then_action else 0)


class IntentionEngine:
    """
    Main engine for managing implementation intentions.
    
    Coordinates the If-Then planning system:
    - Creates and stores intentions
    - Evaluates conditions against context
    - Dispatches actions when conditions are met
    
    Example:
        engine = IntentionEngine()
        
        # Create an intention
        intention = engine.create_intention(
            user_id="user-123",
            name="Morning water",
            if_condition=IfCondition(
                trigger_type=TriggerType.TIME,
                source="clock",
                predicate="time == '08:00'"
            ),
            then_action=ThenAction(
                action_type=ActionType.NOTIFICATION,
                payload="Drink a glass of water!"
            )
        )
        
        # Evaluate against current context
        matches = engine.evaluate({'current_time': datetime.now()})
    """
    
    def __init__(self):
        self.intentions: Dict[str, ImplementationIntention] = {}
        self.matcher = RuleMatcher()
        self.action_handlers: Dict[ActionType, Callable] = {}
    
    def register_action_handler(
        self, 
        action_type: ActionType, 
        handler: Callable[[ThenAction], None]
    ) -> None:
        """
        Register a handler for an action type.
        
        Args:
            action_type: Type of action to handle
            handler: Function to call when action is triggered
        """
        self.action_handlers[action_type] = handler
    
    def create_intention(
        self,
        user_id: str,
        name: str,
        if_condition: IfCondition,
        then_action: ThenAction,
        goal_id: str = ""
    ) -> ImplementationIntention:
        """
        Create a new implementation intention.
        
        Args:
            user_id: User creating the intention
            name: Human-readable name
            if_condition: The trigger condition
            then_action: The action to take
            goal_id: Optional associated goal
            
        Returns:
            The created ImplementationIntention
        """
        intention = ImplementationIntention(
            user_id=user_id,
            name=name,
            if_condition=if_condition,
            then_action=then_action,
            goal_id=goal_id
        )
        
        self.intentions[intention.id] = intention
        self.matcher.add_intention(intention)
        
        return intention
    
    def get_intention(self, intention_id: str) -> Optional[ImplementationIntention]:
        """Get an intention by ID."""
        return self.intentions.get(intention_id)
    
    def get_user_intentions(self, user_id: str) -> List[ImplementationIntention]:
        """Get all intentions for a user."""
        return [i for i in self.intentions.values() if i.user_id == user_id]
    
    def update_intention(
        self, 
        intention_id: str, 
        **updates
    ) -> Optional[ImplementationIntention]:
        """Update an intention's properties."""
        intention = self.intentions.get(intention_id)
        if not intention:
            return None
        
        for key, value in updates.items():
            if hasattr(intention, key):
                setattr(intention, key, value)
        
        return intention
    
    def delete_intention(self, intention_id: str) -> bool:
        """Delete an intention."""
        if intention_id in self.intentions:
            del self.intentions[intention_id]
            self.matcher.remove_intention(intention_id)
            return True
        return False
    
    def evaluate(self, context: Dict[str, Any]) -> List[ImplementationIntention]:
        """
        Evaluate all intentions against the current context.
        
        Args:
            context: Current state (time, location, events, etc.)
            
        Returns:
            List of intentions whose conditions matched
        """
        return self.matcher.find_matches(context)
    
    def dispatch(self, intention: ImplementationIntention) -> bool:
        """
        Dispatch the action for a matched intention.
        
        Args:
            intention: The intention to dispatch
            
        Returns:
            True if action was dispatched successfully
        """
        if not intention.then_action:
            return False
        
        action = intention.then_action
        handler = self.action_handlers.get(action.action_type)
        
        if handler:
            try:
                handler(action)
                intention.trigger_count += 1
                return True
            except Exception:
                return False
        
        return False
    
    def evaluate_and_dispatch(
        self, 
        context: Dict[str, Any]
    ) -> List[ImplementationIntention]:
        """
        Evaluate context and dispatch all matching intentions.
        
        Args:
            context: Current state
            
        Returns:
            List of dispatched intentions
        """
        matches = self.evaluate(context)
        dispatched = []
        
        for intention in matches:
            if self.dispatch(intention):
                dispatched.append(intention)
        
        return dispatched
    
    def mark_success(self, intention_id: str) -> None:
        """Mark an intention as successfully completed."""
        intention = self.intentions.get(intention_id)
        if intention:
            intention.success_count += 1
    
    def get_intention_analytics(self, intention_id: str) -> Dict[str, Any]:
        """Get analytics for a specific intention."""
        intention = self.intentions.get(intention_id)
        if not intention:
            return {'error': 'Intention not found'}
        
        return {
            'id': intention.id,
            'name': intention.name,
            'trigger_count': intention.trigger_count,
            'success_count': intention.success_count,
            'success_rate': intention.success_rate,
            'is_active': intention.is_active
        }
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for all of a user's intentions."""
        user_intentions = self.get_user_intentions(user_id)
        
        if not user_intentions:
            return {'total_intentions': 0}
        
        total_triggers = sum(i.trigger_count for i in user_intentions)
        total_successes = sum(i.success_count for i in user_intentions)
        
        return {
            'total_intentions': len(user_intentions),
            'active_intentions': sum(1 for i in user_intentions if i.is_active),
            'total_triggers': total_triggers,
            'total_successes': total_successes,
            'overall_success_rate': total_successes / total_triggers if total_triggers > 0 else 0.0,
            'intentions': [self.get_intention_analytics(i.id) for i in user_intentions]
        }


# Preset templates for common implementation intentions
INTENTION_PRESETS = [
    {
        'name': 'Morning Hydration',
        'description': 'Drink water first thing in the morning',
        'if_condition': IfCondition(
            trigger_type=TriggerType.TIME,
            source='clock',
            predicate="time == '07:00'",
            description='When it is 7:00 AM'
        ),
        'then_action': ThenAction(
            action_type=ActionType.NOTIFICATION,
            payload='Time to drink a glass of water! 💧',
            priority=5
        )
    },
    {
        'name': 'Post-Lunch Walk',
        'description': 'Take a short walk after lunch',
        'if_condition': IfCondition(
            trigger_type=TriggerType.TIME,
            source='clock',
            predicate="time == '13:00'",
            description='When it is 1:00 PM'
        ),
        'then_action': ThenAction(
            action_type=ActionType.NOTIFICATION,
            payload='Time for a short walk! 🚶',
            priority=3
        )
    },
    {
        'name': 'Evening Reflection',
        'description': 'Review your day before bed',
        'if_condition': IfCondition(
            trigger_type=TriggerType.TIME,
            source='clock',
            predicate="time == '21:00'",
            description='When it is 9:00 PM'
        ),
        'then_action': ThenAction(
            action_type=ActionType.NOTIFICATION,
            payload='Time for daily reflection! 📝',
            priority=4
        )
    },
    {
        'name': 'Habit Chain Trigger',
        'description': 'Trigger next habit after completing one',
        'if_condition': IfCondition(
            trigger_type=TriggerType.EVENT,
            source='habit_completion',
            predicate="event_type == 'habit_completed'",
            description='After completing a habit'
        ),
        'then_action': ThenAction(
            action_type=ActionType.HABIT_PROMPT,
            payload='Ready for the next habit in your stack?',
            priority=5
        )
    }
]


def get_preset_intentions() -> List[Dict[str, Any]]:
    """Get all preset intention templates."""
    return INTENTION_PRESETS
    
