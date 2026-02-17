"""
Habit Stacking Module

Implements BJ Fogg's Tiny Habits methodology for habit formation.
Based on the "Anchor" Protocol: "After I [Current Habit], I will [New Habit]"

Key Concepts:
- Anchor: An existing behavior that triggers a new habit
- Tiny Habit: A new behavior scaled down to < 30 seconds
- Stack: A chain of habits linked together

Reference:
- BJ Fogg, "Tiny Habits" (2019)
- Research on implementation intentions and habit stacking
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, date
from enum import Enum
import uuid


class AnchorCategory(Enum):
    """Categories for anchor habits."""
    MORNING = "morning"
    TRANSIT = "transit"
    EVENING = "evening"
    WORK = "work"
    MEAL = "meal"
    HYGIENE = "hygiene"
    EXERCISE = "exercise"
    CUSTOM = "custom"


@dataclass
class AnchorPreset:
    """
    Predefined anchor options for users.
    
    These are common behaviors that make reliable anchors
    because they are specific, observable, and occur regularly.
    """
    id: str
    name: str
    description: str
    category: AnchorCategory
    example_trigger: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'example_trigger': self.example_trigger
        }


# Default anchor presets based on BJ Fogg's research
DEFAULT_ANCHOR_PRESETS: List[AnchorPreset] = [
    # Morning anchors
    AnchorPreset(
        id="anchor_wake",
        name="Wake up",
        description="After I wake up",
        category=AnchorCategory.MORNING,
        example_trigger="After I wake up, I will..."
    ),
    AnchorPreset(
        id="anchor_alarm",
        name="Turn off alarm",
        description="After I turn off my alarm",
        category=AnchorCategory.MORNING,
        example_trigger="After I turn off my alarm, I will..."
    ),
    AnchorPreset(
        id="anchor_brush",
        name="Brush teeth",
        description="After I brush my teeth",
        category=AnchorCategory.HYGIENE,
        example_trigger="After I brush my teeth, I will..."
    ),
    AnchorPreset(
        id="anchor_coffee",
        name="Brew coffee",
        description="After I brew my coffee",
        category=AnchorCategory.MORNING,
        example_trigger="After I brew my coffee, I will..."
    ),
    AnchorPreset(
        id="anchor_coffee_drink",
        name="Drink coffee",
        description="After I take my first sip of coffee",
        category=AnchorCategory.MORNING,
        example_trigger="After I take my first sip of coffee, I will..."
    ),
    AnchorPreset(
        id="anchor_shower",
        name="Shower",
        description="After I finish my shower",
        category=AnchorCategory.HYGIENE,
        example_trigger="After I finish my shower, I will..."
    ),
    
    # Transit anchors
    AnchorPreset(
        id="anchor_car_start",
        name="Start car",
        description="After I start my car",
        category=AnchorCategory.TRANSIT,
        example_trigger="After I start my car, I will..."
    ),
    AnchorPreset(
        id="anchor_arrive_desk",
        name="Arrive at desk",
        description="After I sit down at my desk",
        category=AnchorCategory.WORK,
        example_trigger="After I sit down at my desk, I will..."
    ),
    AnchorPreset(
        id="anchor_front_door",
        name="Enter home",
        description="After I walk through my front door",
        category=AnchorCategory.TRANSIT,
        example_trigger="After I walk through my front door, I will..."
    ),
    
    # Meal anchors
    AnchorPreset(
        id="anchor_breakfast",
        name="Finish breakfast",
        description="After I finish eating breakfast",
        category=AnchorCategory.MEAL,
        example_trigger="After I finish eating breakfast, I will..."
    ),
    AnchorPreset(
        id="anchor_lunch",
        name="Finish lunch",
        description="After I finish eating lunch",
        category=AnchorCategory.MEAL,
        example_trigger="After I finish eating lunch, I will..."
    ),
    AnchorPreset(
        id="anchor_dinner",
        name="Finish dinner",
        description="After I finish eating dinner",
        category=AnchorCategory.MEAL,
        example_trigger="After I finish eating dinner, I will..."
    ),
    
    # Evening anchors
    AnchorPreset(
        id="anchor_dishes",
        name="Wash dishes",
        description="After I finish washing dishes",
        category=AnchorCategory.EVENING,
        example_trigger="After I finish washing dishes, I will..."
    ),
    AnchorPreset(
        id="anchor_pajamas",
        name="Put on pajamas",
        description="After I put on my pajamas",
        category=AnchorCategory.EVENING,
        example_trigger="After I put on my pajamas, I will..."
    ),
    AnchorPreset(
        id="anchor_lights",
        name="Turn off lights",
        description="After I turn off the lights",
        category=AnchorCategory.EVENING,
        example_trigger="After I turn off the lights, I will..."
    ),
    AnchorPreset(
        id="anchor_bed",
        name="Get into bed",
        description="After I get into bed",
        category=AnchorCategory.EVENING,
        example_trigger="After I get into bed, I will..."
    ),
    
    # Exercise anchors
    AnchorPreset(
        id="anchor_workout",
        name="Finish workout",
        description="After I finish my workout",
        category=AnchorCategory.EXERCISE,
        example_trigger="After I finish my workout, I will..."
    ),
    AnchorPreset(
        id="anchor_stretch",
        name="Finish stretching",
        description="After I finish stretching",
        category=AnchorCategory.EXERCISE,
        example_trigger="After I finish stretching, I will..."
    ),
]


@dataclass
class StackItem:
    """
    A habit within a stack.
    
    Represents a single link in the habit chain with its
    position and optional delay before the next habit.
    """
    habit_id: str
    position_index: int
    delay_seconds: int = 0  # Buffer time before this habit
    is_tiny: bool = True  # Whether this is a "tiny" version (< 30 sec)
    tiny_version_description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'habit_id': self.habit_id,
            'position_index': self.position_index,
            'delay_seconds': self.delay_seconds,
            'is_tiny': self.is_tiny,
            'tiny_version_description': self.tiny_version_description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StackItem':
        return cls(
            habit_id=data['habit_id'],
            position_index=data['position_index'],
            delay_seconds=data.get('delay_seconds', 0),
            is_tiny=data.get('is_tiny', True),
            tiny_version_description=data.get('tiny_version_description')
        )


@dataclass
class HabitStack:
    """
    A chain of habits linked together.
    
    The stack represents a sequence of behaviors where each
    habit triggers the next, starting from an anchor event.
    
    Example:
        "Morning Routine" Stack:
        1. After I brew coffee (anchor)
        2. → I will drink a glass of water
        3. → I will take my vitamins
        4. → I will do 2 pushups
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    name: str = ""  # e.g., "Morning Routine"
    trigger_description: str = ""  # e.g., "After I pour my coffee"
    anchor_category: AnchorCategory = AnchorCategory.CUSTOM
    items: List[StackItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    
    @property
    def stack_depth(self) -> int:
        """Number of habits in the stack."""
        return len(self.items)
    
    @property
    def is_valid(self) -> bool:
        """Check if stack follows Tiny Habits rules."""
        # Stack should have at least one item
        if not self.items:
            return False
        # Position indices should be sequential
        positions = [item.position_index for item in self.items]
        return positions == list(range(len(self.items)))
    
    def get_habit_at_position(self, position: int) -> Optional[StackItem]:
        """Get the habit at a specific position in the stack."""
        for item in self.items:
            if item.position_index == position:
                return item
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'trigger_description': self.trigger_description,
            'anchor_category': self.anchor_category.value,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HabitStack':
        items = [StackItem.from_dict(item) for item in data.get('items', [])]
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            name=data.get('name', ''),
            trigger_description=data.get('trigger_description', ''),
            anchor_category=AnchorCategory(data.get('anchor_category', 'custom')),
            items=items,
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            is_active=data.get('is_active', True)
        )


@dataclass
class StackCompletion:
    """Record of a stack completion attempt."""
    stack_id: str
    date: date
    completed_items: List[str]  # habit_ids that were completed
    completion_order: List[str]  # Order in which habits were completed
    stack_conversion_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'stack_id': self.stack_id,
            'date': self.date.isoformat(),
            'completed_items': self.completed_items,
            'completion_order': self.completion_order,
            'stack_conversion_rate': self.stack_conversion_rate
        }


@dataclass
class SRBAIResult:
    """
    Self-Report Behavioural Automaticity Index result.
    
    The SRBAI is a 4-item self-report measure of habit automaticity.
    Users rate each item on a 1-7 scale.
    
    Reference:
    Gardner, B., et al. (2012). "Towards a comprehensive test of 
    the habit-formation process in health behaviour."
    """
    habit_id: str
    user_id: str
    date: date
    # Four SRBAI questions (1-7 scale each)
    q1_automatic: int  # "I do this automatically"
    q2_without_thinking: int  # "I do this without thinking"
    q3_start_unintentionally: int  # "I start doing this without realizing"
    q4_difficult_not_to_do: int  # "It would be difficult not to do this"
    
    @property
    def automaticity_score(self) -> float:
        """Calculate average automaticity score (1-7 scale)."""
        return (self.q1_automatic + self.q2_without_thinking + 
                self.q3_start_unintentionally + self.q4_difficult_not_to_do) / 4
    
    @property
    def is_habit_formed(self) -> bool:
        """Determine if habit is considered formed (score >= 5.5)."""
        return self.automaticity_score >= 5.5
    
    @property
    def habit_strength(self) -> str:
        """Interpret automaticity score."""
        score = self.automaticity_score
        if score >= 6:
            return "Strong habit"
        elif score >= 5:
            return "Moderate habit"
        elif score >= 4:
            return "Developing"
        elif score >= 3:
            return "Weak"
        return "Not a habit"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'habit_id': self.habit_id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'q1_automatic': self.q1_automatic,
            'q2_without_thinking': self.q2_without_thinking,
            'q3_start_unintentionally': self.q3_start_unintentionally,
            'q4_difficult_not_to_do': self.q4_difficult_not_to_do,
            'automaticity_score': round(self.automaticity_score, 2),
            'is_habit_formed': self.is_habit_formed,
            'habit_strength': self.habit_strength
        }


class StackConversionTracker:
    """
    Tracks the effectiveness of habit stacks.
    
    Measures:
    - Stack Conversion Rate: % times Habit B completed given Habit A
    - Stack Decay: Where users drop off in a chain
    - Overall stack effectiveness
    """
    
    def __init__(self):
        self.completions: List[StackCompletion] = []
    
    def record_completion(
        self, 
        stack: HabitStack, 
        completed_habit_ids: List[str]
    ) -> StackCompletion:
        """
        Record a stack completion attempt.
        
        Args:
            stack: The habit stack being tracked
            completed_habit_ids: List of habit IDs that were completed
            
        Returns:
            StackCompletion with calculated metrics
        """
        completion = StackCompletion(
            stack_id=stack.id,
            date=date.today(),
            completed_items=completed_habit_ids,
            completion_order=completed_habit_ids.copy()
        )
        
        # Calculate stack conversion rate
        if stack.items:
            completion.stack_conversion_rate = len(completed_habit_ids) / len(stack.items)
        
        self.completions.append(completion)
        return completion
    
    def get_stack_conversion_rate(self, stack_id: str) -> float:
        """
        Calculate overall conversion rate for a stack.
        
        Returns the average % of habits completed when the stack is started.
        """
        stack_completions = [c for c in self.completions if c.stack_id == stack_id]
        if not stack_completions:
            return 0.0
        return sum(c.stack_conversion_rate for c in stack_completions) / len(stack_completions)
    
    def get_link_conversion_rate(
        self, 
        stack: HabitStack, 
        position_a: int, 
        position_b: int
    ) -> float:
        """
        Calculate conversion rate between two specific habits.
        
        What % of times was habit B completed given habit A was completed?
        """
        habit_a = stack.get_habit_at_position(position_a)
        habit_b = stack.get_habit_at_position(position_b)
        
        if not habit_a or not habit_b:
            return 0.0
        
        stack_completions = [c for c in self.completions if c.stack_id == stack.id]
        
        a_completed_count = 0
        both_completed_count = 0
        
        for completion in stack_completions:
            if habit_a.habit_id in completion.completed_items:
                a_completed_count += 1
                if habit_b.habit_id in completion.completed_items:
                    both_completed_count += 1
        
        if a_completed_count == 0:
            return 0.0
        
        return both_completed_count / a_completed_count
    
    def get_stack_decay(self, stack: HabitStack) -> Dict[int, float]:
        """
        Identify where users drop off in a chain.
        
        Returns a dict mapping position -> completion rate.
        Low rates indicate weak links in the chain.
        """
        decay = {}
        stack_completions = [c for c in self.completions if c.stack_id == stack.id]
        
        if not stack_completions:
            return {item.position_index: 0.0 for item in stack.items}
        
        for item in stack.items:
            completed_count = sum(
                1 for c in stack_completions 
                if item.habit_id in c.completed_items
            )
            decay[item.position_index] = completed_count / len(stack_completions)
        
        return decay
    
    def identify_weak_links(
        self, 
        stack: HabitStack, 
        threshold: float = 0.6
    ) -> List[int]:
        """
        Find positions where conversion rate drops below threshold.
        
        These are candidates for stack optimization:
        - Habit may be too difficult (not "tiny")
        - Delay may be too short
        - Habit may not fit the anchor
        """
        decay = self.get_stack_decay(stack)
        weak_links = []
        
        for position, rate in decay.items():
            if rate < threshold:
                weak_links.append(position)
        
        return weak_links


class SRBAISurvey:
    """
    Manages the Self-Report Behavioural Automaticity Index survey.
    
    The SRBAI should be administered after 14 days of consistent
    habit performance to measure automaticity.
    """
    
    QUESTIONS = [
        {
            'id': 'q1_automatic',
            'text': 'I do this automatically',
            'description': 'Behavior happens without conscious decision'
        },
        {
            'id': 'q2_without_thinking',
            'text': 'I do this without thinking',
            'description': 'Behavior requires minimal mental effort'
        },
        {
            'id': 'q3_start_unintentionally',
            'text': 'I start doing this without realizing',
            'description': 'Behavior initiation is unconscious'
        },
        {
            'id': 'q4_difficult_not_to_do',
            'text': 'It would be difficult not to do this',
            'description': 'Behavior has become necessary/expected'
        }
    ]
    
    SCALE_MIN = 1  # Strongly disagree
    SCALE_MAX = 7  # Strongly agree
    
    def __init__(self):
        self.results: List[SRBAIResult] = []
    
    def should_survey(self, habit_id: str, days_since_start: int) -> bool:
        """
        Determine if user should be surveyed for a habit.
        
        Survey is recommended after 14 days of streak.
        """
        return days_since_start >= 14
    
    def submit_survey(
        self,
        habit_id: str,
        user_id: str,
        q1: int,
        q2: int,
        q3: int,
        q4: int
    ) -> SRBAIResult:
        """
        Submit SRBAI survey responses.
        
        Args:
            habit_id: The habit being surveyed
            user_id: The user submitting
            q1-q4: Responses on 1-7 scale
            
        Returns:
            SRBAIResult with calculated automaticity score
        """
        # Validate responses
        for q_val in [q1, q2, q3, q4]:
            if not (self.SCALE_MIN <= q_val <= self.SCALE_MAX):
                raise ValueError(f"Response must be between {self.SCALE_MIN} and {self.SCALE_MAX}")
        
        result = SRBAIResult(
            habit_id=habit_id,
            user_id=user_id,
            date=date.today(),
            q1_automatic=q1,
            q2_without_thinking=q2,
            q3_start_unintentionally=q3,
            q4_difficult_not_to_do=q4
        )
        
        self.results.append(result)
        return result
    
    def get_latest_result(self, habit_id: str) -> Optional[SRBAIResult]:
        """Get the most recent SRBAI result for a habit."""
        habit_results = [r for r in self.results if r.habit_id == habit_id]
        if not habit_results:
            return None
        return max(habit_results, key=lambda r: r.date)


class HabitStackingEngine:
    """
    Main engine for creating and managing habit stacks.
    
    Implements BJ Fogg's Tiny Habits methodology:
    - Create stacks with specific anchors
    - Add habits in sequence (one at a time recommended)
    - Track effectiveness and automaticity
    
    Example:
        engine = HabitStackingEngine()
        
        # Create a morning stack
        stack = engine.create_stack(
            user_id="user-123",
            name="Morning Routine",
            trigger="After I brew my coffee",
            category=AnchorCategory.MORNING
        )
        
        # Add habits to the stack
        engine.add_habit_to_stack(stack.id, "habit-water", position=0)
        engine.add_habit_to_stack(stack.id, "habit-vitamins", position=1)
        
        # Track completion
        engine.record_completion(stack, ["habit-water", "habit-vitamins"])
    """
    
    def __init__(self):
        self.stacks: Dict[str, HabitStack] = {}
        self.tracker = StackConversionTracker()
        self.srbai = SRBAISurvey()
    
    def create_stack(
        self,
        user_id: str,
        name: str,
        trigger: str,
        category: AnchorCategory = AnchorCategory.CUSTOM
    ) -> HabitStack:
        """
        Create a new habit stack.
        
        Args:
            user_id: User creating the stack
            name: Name for the stack (e.g., "Morning Routine")
            trigger: The anchor description (e.g., "After I brew coffee")
            category: Category of the anchor
            
        Returns:
            The created HabitStack
        """
        stack = HabitStack(
            user_id=user_id,
            name=name,
            trigger_description=trigger,
            anchor_category=category
        )
        
        self.stacks[stack.id] = stack
        return stack
    
    def add_habit_to_stack(
        self,
        stack_id: str,
        habit_id: str,
        position: Optional[int] = None,
        delay_seconds: int = 0,
        is_tiny: bool = True,
        tiny_description: Optional[str] = None
    ) -> StackItem:
        """
        Add a habit to a stack.
        
        Args:
            stack_id: ID of the stack to add to
            habit_id: ID of the habit to add
            position: Position in the stack (default: end)
            delay_seconds: Buffer time before this habit
            is_tiny: Whether this is a "tiny" version (< 30 sec)
            tiny_description: Description of the tiny version
            
        Returns:
            The created StackItem
        """
        stack = self.stacks.get(stack_id)
        if not stack:
            raise ValueError(f"Stack {stack_id} not found")
        
        # Determine position
        if position is None:
            position = len(stack.items)
        
        # Validate position
        if position < 0 or position > len(stack.items):
            raise ValueError(f"Invalid position {position}")
        
        # Shift existing items if inserting
        for item in stack.items:
            if item.position_index >= position:
                item.position_index += 1
        
        # Create the stack item
        item = StackItem(
            habit_id=habit_id,
            position_index=position,
            delay_seconds=delay_seconds,
            is_tiny=is_tiny,
            tiny_version_description=tiny_description
        )
        
        stack.items.append(item)
        stack.items.sort(key=lambda x: x.position_index)
        
        return item
    
    def remove_habit_from_stack(self, stack_id: str, habit_id: str) -> bool:
        """Remove a habit from a stack."""
        stack = self.stacks.get(stack_id)
        if not stack:
            return False
        
        original_count = len(stack.items)
        stack.items = [item for item in stack.items if item.habit_id != habit_id]
        
        # Re-index positions
        for i, item in enumerate(stack.items):
            item.position_index = i
        
        return len(stack.items) < original_count
    
    def reorder_habit(self, stack_id: str, habit_id: str, new_position: int) -> bool:
        """Move a habit to a new position in the stack."""
        stack = self.stacks.get(stack_id)
        if not stack:
            return False
        
        # Find the item
        item = None
        for i in stack.items:
            if i.habit_id == habit_id:
                item = i
                break
        
        if not item:
            return False
        
        # Validate new position
        if new_position < 0 or new_position >= len(stack.items):
            return False
        
        # Reorder
        stack.items.remove(item)
        stack.items.insert(new_position, item)
        
        # Re-index
        for i, i_item in enumerate(stack.items):
            i_item.position_index = i
        
        return True
    
    def get_stack(self, stack_id: str) -> Optional[HabitStack]:
        """Get a stack by ID."""
        return self.stacks.get(stack_id)
    
    def get_user_stacks(self, user_id: str) -> List[HabitStack]:
        """Get all stacks for a user."""
        return [s for s in self.stacks.values() if s.user_id == user_id]
    
    def record_completion(
        self,
        stack: HabitStack,
        completed_habit_ids: List[str]
    ) -> StackCompletion:
        """Record a stack completion."""
        return self.tracker.record_completion(stack, completed_habit_ids)
    
    def get_stack_analytics(self, stack_id: str) -> Dict[str, Any]:
        """Get analytics for a stack."""
        stack = self.stacks.get(stack_id)
        if not stack:
            return {'error': 'Stack not found'}
        
        return {
            'stack_id': stack_id,
            'name': stack.name,
            'stack_depth': stack.stack_depth,
            'conversion_rate': self.tracker.get_stack_conversion_rate(stack_id),
            'decay': self.tracker.get_stack_decay(stack),
            'weak_links': self.tracker.identify_weak_links(stack),
            'link_conversion': {
                f"{i}->{i+1}": self.tracker.get_link_conversion_rate(stack, i, i+1)
                for i in range(len(stack.items) - 1)
            }
        }
    
    def get_anchor_presets(self, category: Optional[AnchorCategory] = None) -> List[AnchorPreset]:
        """Get anchor presets, optionally filtered by category."""
        if category:
            return [p for p in DEFAULT_ANCHOR_PRESETS if p.category == category]
        return DEFAULT_ANCHOR_PRESETS
    
    def suggest_tiny_version(self, habit_name: str) -> str:
        """
        Suggest a "tiny" version of a habit.
        
        Scale down the habit to take < 30 seconds.
        """
        # Common scaling patterns
        tiny_patterns = {
            'floss': 'floss one tooth',
            'exercise': 'do 2 pushups',
            'read': 'read one page',
            'meditate': 'take 3 deep breaths',
            'stretch': 'stretch for 10 seconds',
            'write': 'write one sentence',
            'drink water': 'take one sip of water',
            'walk': 'walk for 30 seconds',
        }
        
        habit_lower = habit_name.lower()
        for key, tiny in tiny_patterns.items():
            if key in habit_lower:
                return tiny
        
        # Default: add "tiny" prefix
        return f"tiny version of {habit_name}"