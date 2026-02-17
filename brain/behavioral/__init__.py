"""
Brain Behavioral Module

This module provides behavioral science implementations for habit formation:
- Habit Stacking (BJ Fogg's Tiny Habits methodology)
- Implementation Intentions (If-Then planning)
- Variable Reward Scheduling (Skinner's Operant Conditioning)
- Social Accountability (Zajonc's Social Facilitation)

Key Components:
- HabitStackingEngine: Create and manage habit stacks
- StackConversionTracker: Track stack effectiveness
- SRBAISurvey: Measure habit automaticity
- IntentionEngine: Manage If-Then planning
- RuleMatcher: Evaluate conditions against context
- RewardEngine: Variable reward scheduling
- AccountabilityEngine: Manage commitment contracts and social broadcasting

Usage:
    from brain.behavioral import HabitStackingEngine, HabitStack
    from brain.behavioral import IntentionEngine, ImplementationIntention
    from brain.behavioral import RewardEngine, Reward
    from brain.behavioral import AccountabilityEngine, AccountabilityPact
    
    # Create a habit stack
    stack_engine = HabitStackingEngine()
    stack = stack_engine.create_stack(
        name="Morning Routine",
        trigger="After I pour my coffee"
    )
    stack_engine.add_habit_to_stack(stack.id, habit_id, position=0)
    
    # Create an implementation intention
    intention_engine = IntentionEngine()
    intention = intention_engine.create_intention(
        user_id="user-123",
        name="Morning water",
        if_condition=IfCondition(...),
        then_action=ThenAction(...)
    )
    
    # Roll for a variable reward
    reward_engine = RewardEngine()
    result = reward_engine.roll_for_user("user-123")
    if result.is_rewarded:
        print(f"You got: {result.reward.name}!")
    
    # Create an accountability pact
    accountability_engine = AccountabilityEngine()
    pact = accountability_engine.create_pact(
        user_id="user-123",
        title="Morning Workout",
        description="30 min workout every morning",
        stakes_type=StakeType.ANTI_CHARITY,
        stakes_amount=50.0
    )
"""

from brain.behavioral.habit_stacking import (
    HabitStack,
    StackItem,
    HabitStackingEngine,
    StackConversionTracker,
    SRBAISurvey,
    AnchorCategory,
    AnchorPreset
)

from brain.behavioral.implementation_intentions import (
    TriggerType,
    ActionType,
    IfCondition,
    ThenAction,
    ImplementationIntention,
    RuleMatcher,
    IntentionEngine,
    get_preset_intentions
)

from brain.behavioral.rewards import (
    RewardType,
    Rarity,
    Reward,
    RewardResult,
    RewardHistory,
    RewardTable,
    RewardEngine,
    DEFAULT_REWARDS,
    create_default_engine
)

from brain.behavioral.accountability import (
    StakeType,
    VisibilityLevel,
    PactStatus,
    BroadcastChannel,
    AccountabilityPartner,
    AccountabilityPact,
    PactVerification,
    BroadcastMessage,
    WebhookBroadcaster,
    AccountabilityEngine,
    accountability_engine,
    create_pact,
    get_pact,
    start_engine,
    stop_engine
)

__all__ = [
    # Habit Stacking
    'HabitStack',
    'StackItem',
    'HabitStackingEngine',
    'StackConversionTracker',
    'SRBAISurvey',
    'AnchorCategory',
    'AnchorPreset',
    
    # Implementation Intentions
    'TriggerType',
    'ActionType',
    'IfCondition',
    'ThenAction',
    'ImplementationIntention',
    'RuleMatcher',
    'IntentionEngine',
    'get_preset_intentions',
    
    # Variable Rewards
    'RewardType',
    'Rarity',
    'Reward',
    'RewardResult',
    'RewardHistory',
    'RewardTable',
    'RewardEngine',
    'DEFAULT_REWARDS',
    'create_default_engine',
    
    # Social Accountability
    'StakeType',
    'VisibilityLevel',
    'PactStatus',
    'BroadcastChannel',
    'AccountabilityPartner',
    'AccountabilityPact',
    'PactVerification',
    'BroadcastMessage',
    'WebhookBroadcaster',
    'AccountabilityEngine',
    'accountability_engine',
    'create_pact',
    'get_pact',
    'start_engine',
    'stop_engine',
]

__version__ = '1.0.0'
