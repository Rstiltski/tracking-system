"""
Variable Reward Scheduling Module

Implements B.F. Skinner's Variable Ratio reinforcement schedule for behavior change.
Based on the principle of Intermittent Reinforcement - providing rewards after an
unpredictable number of responses to maximize response rate and extinction resistance.

Key Concepts:
- Variable Ratio (VR): Reinforcement after unpredictable number of responses
- Dopamine Prediction Error: Unpredictability keeps dopamine response high
- Extinction Resistance: Behaviors persist longer when rewards cease
- Near-Miss Effect: "Almost won" triggers similar dopamine response

Reference:
- Skinner, B.F. (1953). "Science and Human Behavior"
- Eyal, N. (2014). "Hooked: How to Build Habit-Forming Products"

Effect: Highest response rate of any reinforcement schedule
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from enum import Enum
import random
import uuid
import math


class RewardType(Enum):
    """Types of variable rewards based on The Hook Model (Nir Eyal)."""
    TRIBE = "tribe"      # Social validation (likes, leaderboards, recognition)
    HUNT = "hunt"        # Material resources (badges, unlockables, points, XP)
    SELF = "self"        # Mastery & competence (leveling up, streak completion)


class Rarity(Enum):
    """Rarity levels for rewards with default weights."""
    COMMON = "common"           # 60% weight - High frequency
    UNCOMMON = "uncommon"       # 25% weight - Medium frequency
    RARE = "rare"               # 12% weight - Low frequency
    LEGENDARY = "legendary"     # 3% weight - Very rare
    
    @property
    def default_weight(self) -> float:
        """Get the default weight for this rarity."""
        weights = {
            Rarity.COMMON: 60.0,
            Rarity.UNCOMMON: 25.0,
            Rarity.RARE: 12.0,
            Rarity.LEGENDARY: 3.0
        }
        return weights[self]


@dataclass
class Reward:
    """
    A single reward that can be awarded to a user.
    
    Rewards are categorized by type (Tribe/Hunt/Self) and rarity,
    with weighted probability for selection.
    
    Example:
        Reward(
            name="Golden Badge",
            reward_type=RewardType.HUNT,
            rarity=Rarity.RARE,
            value=100,
            icon="🏆",
            description="A rare golden badge for dedication"
        )
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    reward_type: RewardType = RewardType.HUNT
    rarity: Rarity = Rarity.COMMON
    weight: float = 1.0  # Relative weight within rarity
    value: int = 0  # XP/points value
    icon: str = "🎁"
    description: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def effective_weight(self) -> float:
        """Calculate effective weight based on rarity and individual weight."""
        return self.rarity.default_weight * self.weight
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'reward_type': self.reward_type.value,
            'rarity': self.rarity.value,
            'weight': self.weight,
            'value': self.value,
            'icon': self.icon,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reward':
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', ''),
            reward_type=RewardType(data.get('reward_type', 'hunt')),
            rarity=Rarity(data.get('rarity', 'common')),
            weight=data.get('weight', 1.0),
            value=data.get('value', 0),
            icon=data.get('icon', '🎁'),
            description=data.get('description', ''),
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now()
        )


@dataclass
class RewardResult:
    """
    Result of a reward roll operation.
    
    Contains the reward (if any) and metadata about the roll.
    """
    reward: Optional[Reward]
    rolled: bool  # Whether the base chance succeeded
    near_miss: bool = False  # Whether this was a "near miss"
    context: Dict[str, Any] = field(default_factory=dict)
    rolled_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_rewarded(self) -> bool:
        """Check if a reward was actually given."""
        return self.reward is not None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'reward': self.reward.to_dict() if self.reward else None,
            'rolled': self.rolled,
            'near_miss': self.near_miss,
            'context': self.context,
            'rolled_at': self.rolled_at.isoformat()
        }


@dataclass
class RewardHistory:
    """
    Tracks reward history for a user to prevent satiation.
    
    Reward value decays with frequency: V ∝ 1/f
    """
    user_id: str
    rewards_received: List[Dict[str, Any]] = field(default_factory=list)
    total_rolls: int = 0
    total_rewards: int = 0
    
    def add_reward(self, reward: Reward) -> None:
        """Record a reward being given."""
        self.rewards_received.append({
            'reward_id': reward.id,
            'reward_name': reward.name,
            'rarity': reward.rarity.value,
            'received_at': datetime.now().isoformat()
        })
        self.total_rewards += 1
    
    def add_roll(self, rewarded: bool) -> None:
        """Record a roll attempt."""
        self.total_rolls += 1
    
    def get_recent_count(self, reward_id: str, days: int = 7) -> int:
        """Get count of a specific reward received recently."""
        cutoff = datetime.now() - timedelta(days=days)
        count = 0
        for record in self.rewards_received:
            if record['reward_id'] == reward_id:
                received_at = datetime.fromisoformat(record['received_at'])
                if received_at >= cutoff:
                    count += 1
        return count
    
    def get_rarity_count(self, rarity: Rarity, days: int = 7) -> int:
        """Get count of rewards of a specific rarity received recently."""
        cutoff = datetime.now() - timedelta(days=days)
        count = 0
        for record in self.rewards_received:
            if record['rarity'] == rarity.value:
                received_at = datetime.fromisoformat(record['received_at'])
                if received_at >= cutoff:
                    count += 1
        return count
    
    def calculate_satiation_factor(self, reward: Reward) -> float:
        """
        Calculate satiation factor for a reward.
        
        Returns a multiplier (0-1) that reduces probability of rewards
        that have been given frequently.
        """
        recent_count = self.get_recent_count(reward.id)
        # Satiation increases with frequency
        # Factor approaches 0 as count increases
        return 1.0 / (1.0 + recent_count * 0.2)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'rewards_received': self.rewards_received,
            'total_rolls': self.total_rolls,
            'total_rewards': self.total_rewards
        }


class RewardTable:
    """
    A collection of rewards with weighted probability selection.
    
    Implements the "Loot Table" pattern for variable rewards.
    Uses weighted random selection to choose rewards.
    
    Example:
        table = RewardTable(base_drop_chance=0.3)
        table.add_reward(Reward(name="XP Boost", rarity=Rarity.COMMON, value=10))
        table.add_reward(Reward(name="Golden Badge", rarity=Rarity.RARE, value=100))
        
        result = table.roll(user_context)
    """
    
    def __init__(self, base_drop_chance: float = 0.3):
        """
        Initialize the reward table.
        
        Args:
            base_drop_chance: Probability of getting ANY reward (0-1)
                             Default 0.3 = 30% chance
        """
        self.rewards: List[Reward] = []
        self.base_drop_chance = base_drop_chance
        self._near_miss_threshold = 0.05  # 5% below threshold = near miss
    
    def add_reward(self, reward: Reward) -> None:
        """Add a reward to the table."""
        self.rewards.append(reward)
    
    def remove_reward(self, reward_id: str) -> bool:
        """Remove a reward by ID."""
        original_count = len(self.rewards)
        self.rewards = [r for r in self.rewards if r.id != reward_id]
        return len(self.rewards) < original_count
    
    def get_active_rewards(self) -> List[Reward]:
        """Get all active rewards."""
        return [r for r in self.rewards if r.is_active]
    
    def get_rewards_by_type(self, reward_type: RewardType) -> List[Reward]:
        """Get rewards filtered by type."""
        return [r for r in self.rewards if r.reward_type == reward_type and r.is_active]
    
    def get_rewards_by_rarity(self, rarity: Rarity) -> List[Reward]:
        """Get rewards filtered by rarity."""
        return [r for r in self.rewards if r.rarity == rarity and r.is_active]
    
    def _select_weighted_reward(
        self, 
        rewards: List[Reward],
        satiation_factors: Optional[Dict[str, float]] = None
    ) -> Optional[Reward]:
        """
        Select a reward using weighted random selection.
        
        Args:
            rewards: List of rewards to choose from
            satiation_factors: Optional dict of reward_id -> factor (0-1)
        
        Returns:
            Selected reward or None if no rewards available
        """
        if not rewards:
            return None
        
        # Calculate effective weights
        weights = []
        for reward in rewards:
            weight = reward.effective_weight
            if satiation_factors and reward.id in satiation_factors:
                weight *= satiation_factors[reward.id]
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight <= 0:
            return None
        
        # Weighted random selection
        selected = random.choices(rewards, weights=weights, k=1)[0]
        return selected
    
    def roll(
        self, 
        context: Optional[Dict[str, Any]] = None,
        history: Optional[RewardHistory] = None
    ) -> RewardResult:
        """
        Roll for a reward.
        
        This is the core "slot machine" mechanic:
        1. Roll base chance (e.g., 30%)
        2. If success, select specific reward using weighted random
        3. Apply satiation factors if history provided
        
        Args:
            context: Optional context (user action, streak, etc.)
            history: Optional reward history for satiation calculation
            
        Returns:
            RewardResult with reward (or None) and metadata
        """
        context = context or {}
        active_rewards = self.get_active_rewards()
        
        if not active_rewards:
            return RewardResult(
                reward=None,
                rolled=False,
                context=context
            )
        
        # Roll base chance
        roll_value = random.random()
        rolled = roll_value < self.base_drop_chance
        
        # Check for near miss (close to winning but didn't)
        near_miss = not rolled and roll_value >= self.base_drop_chance - self._near_miss_threshold
        
        if not rolled:
            return RewardResult(
                reward=None,
                rolled=False,
                near_miss=near_miss,
                context=context
            )
        
        # Calculate satiation factors
        satiation_factors = {}
        if history:
            for reward in active_rewards:
                satiation_factors[reward.id] = history.calculate_satiation_factor(reward)
        
        # Select reward using weighted random
        selected_reward = self._select_weighted_reward(active_rewards, satiation_factors)
        
        return RewardResult(
            reward=selected_reward,
            rolled=True,
            near_miss=False,
            context=context
        )


class RewardEngine:
    """
    Main engine for managing variable rewards.
    
    Coordinates the reward system:
    - Manages reward tables
    - Tracks user history
    - Calculates satiation
    - Provides analytics
    
    Example:
        engine = RewardEngine()
        
        # Add rewards
        engine.add_reward(Reward(name="XP Boost", value=10, rarity=Rarity.COMMON))
        engine.add_reward(Reward(name="Golden Badge", value=100, rarity=Rarity.RARE))
        
        # Roll for a reward
        result = engine.roll_for_user("user-123")
        if result.is_rewarded:
            print(f"You got: {result.reward.name}!")
    """
    
    def __init__(self, base_drop_chance: float = 0.3):
        """
        Initialize the reward engine.
        
        Args:
            base_drop_chance: Base probability of getting a reward (0-1)
        """
        self.table = RewardTable(base_drop_chance=base_drop_chance)
        self.histories: Dict[str, RewardHistory] = {}
        self.reward_callbacks: Dict[str, Callable] = {}
    
    def add_reward(self, reward: Reward) -> None:
        """Add a reward to the table."""
        self.table.add_reward(reward)
    
    def remove_reward(self, reward_id: str) -> bool:
        """Remove a reward by ID."""
        return self.table.remove_reward(reward_id)
    
    def get_reward(self, reward_id: str) -> Optional[Reward]:
        """Get a reward by ID."""
        for reward in self.table.rewards:
            if reward.id == reward_id:
                return reward
        return None
    
    def get_all_rewards(self) -> List[Reward]:
        """Get all rewards."""
        return self.table.rewards
    
    def register_reward_callback(self, reward_id: str, callback: callable) -> None:
        """
        Register a callback to be called when a specific reward is given.
        
        Args:
            reward_id: ID of the reward
            callback: Function to call with (user_id, reward, context)
        """
        self.reward_callbacks[reward_id] = callback
    
    def get_user_history(self, user_id: str) -> RewardHistory:
        """Get or create reward history for a user."""
        if user_id not in self.histories:
            self.histories[user_id] = RewardHistory(user_id=user_id)
        return self.histories[user_id]
    
    def roll_for_user(
        self, 
        user_id: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> RewardResult:
        """
        Roll for a reward for a specific user.
        
        Args:
            user_id: User to roll for
            context: Optional context (action type, streak, etc.)
            
        Returns:
            RewardResult with reward and metadata
        """
        history = self.get_user_history(user_id)
        result = self.table.roll(context=context, history=history)
        
        # Record the roll
        history.add_roll(result.is_rewarded)
        
        # If rewarded, record and trigger callback
        if result.is_rewarded and result.reward:
            history.add_reward(result.reward)
            
            # Trigger callback if registered
            callback = self.reward_callbacks.get(result.reward.id)
            if callback:
                try:
                    callback(user_id, result.reward, context)
                except Exception:
                    pass  # Don't fail on callback errors
        
        return result
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get reward statistics for a user."""
        history = self.get_user_history(user_id)
        
        if history.total_rolls == 0:
            return {
                'user_id': user_id,
                'total_rolls': 0,
                'total_rewards': 0,
                'reward_rate': 0.0
            }
        
        return {
            'user_id': user_id,
            'total_rolls': history.total_rolls,
            'total_rewards': history.total_rewards,
            'reward_rate': history.total_rewards / history.total_rolls,
            'rewards_by_rarity': {
                rarity.value: history.get_rarity_count(rarity)
                for rarity in Rarity
            }
        }
    
    def get_reward_stats(self) -> Dict[str, Any]:
        """Get statistics about rewards."""
        rewards = self.get_all_rewards()
        
        return {
            'total_rewards': len(rewards),
            'by_type': {
                rt.value: len([r for r in rewards if r.reward_type == rt])
                for rt in RewardType
            },
            'by_rarity': {
                r.value: len([r for r in rewards if r.rarity == r])
                for r in Rarity
            }
        }


# Default reward presets
DEFAULT_REWARDS = [
    # Common rewards (Tribe)
    Reward(
        name="Community Recognition",
        reward_type=RewardType.TRIBE,
        rarity=Rarity.COMMON,
        value=5,
        icon="👋",
        description="Your progress is noticed by the community"
    ),
    # Common rewards (Hunt)
    Reward(
        name="Small XP Boost",
        reward_type=RewardType.HUNT,
        rarity=Rarity.COMMON,
        value=10,
        icon="⭐",
        description="A small boost of experience points"
    ),
    # Common rewards (Self)
    Reward(
        name="Progress Milestone",
        reward_type=RewardType.SELF,
        rarity=Rarity.COMMON,
        value=5,
        icon="📈",
        description="You're making great progress!"
    ),
    # Uncommon rewards (Hunt)
    Reward(
        name="Bonus Points",
        reward_type=RewardType.HUNT,
        rarity=Rarity.UNCOMMON,
        value=25,
        icon="💎",
        description="Bonus points for your dedication"
    ),
    # Uncommon rewards (Self)
    Reward(
        name="Streak Shield",
        reward_type=RewardType.SELF,
        rarity=Rarity.UNCOMMON,
        value=50,
        icon="🛡️",
        description="Protect your streak for one day"
    ),
    # Rare rewards (Hunt)
    Reward(
        name="Golden Badge",
        reward_type=RewardType.HUNT,
        rarity=Rarity.RARE,
        value=100,
        icon="🏆",
        description="A rare golden badge of achievement"
    ),
    # Rare rewards (Tribe)
    Reward(
        name="Leaderboard Feature",
        reward_type=RewardType.TRIBE,
        rarity=Rarity.RARE,
        value=75,
        icon="🏅",
        description="Featured on the leaderboard"
    ),
    # Legendary rewards (Hunt)
    Reward(
        name="Legendary Status",
        reward_type=RewardType.HUNT,
        rarity=Rarity.LEGENDARY,
        value=500,
        icon="👑",
        description="Legendary status achieved!"
    ),
    # Legendary rewards (Self)
    Reward(
        name="Streak Master",
        reward_type=RewardType.SELF,
        rarity=Rarity.LEGENDARY,
        value=300,
        icon="🔥",
        description="Permanent streak multiplier bonus"
    ),
]


def create_default_engine() -> RewardEngine:
    """Create a reward engine with default rewards."""
    engine = RewardEngine(base_drop_chance=0.3)
    for reward in DEFAULT_REWARDS:
        engine.add_reward(reward)
    return engine