"""
Brain AI Coach - Personality Configuration

Defines coach personality traits and configuration for customizing
the coaching experience.

Usage:
    from brain.ai.coach.personality import CoachPersonality, PersonalityConfig
    
    config = PersonalityConfig(
        personality=CoachPersonality.ENCOURAGING,
        tone="gentle",
        intervention_frequency="daily"
    )
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


class CoachPersonality(Enum):
    """Available coach personality types."""
    ENCOURAGING = "encouraging"  # Supportive, positive reinforcement
    DIRECT = "direct"           # Straightforward, no-nonsense
    GENTLE = "gentle"           # Soft-spoken, empathetic
    PLAYFUL = "playful"         # Fun, gamification-focused
    ANALYTICAL = "analytical"   # Data-driven, logical
    STERN = "stern"             # Strict, accountability-focused


class InterventionFrequency(Enum):
    """How often the coach can intervene."""
    MINIMAL = "minimal"      # Only critical interventions
    LOW = "low"              # Important interventions only
    NORMAL = "normal"        # Standard intervention frequency
    HIGH = "high"            # Frequent check-ins
    INTENSIVE = "intensive"  # Maximum support mode


class ToneStyle(Enum):
    """Communication tone options."""
    CASUAL = "casual"        # Friendly, informal
    FORMAL = "formal"        # Professional
    WARM = "warm"           # Caring, nurturing
    NEUTRAL = "neutral"      # Matter-of-fact
    MOTIVATIONAL = "motivational"  # Energetic, inspiring


@dataclass
class PersonalityConfig:
    """
    Configuration for coach personality.
    
    Attributes:
        personality: Base personality type
        tone: Communication tone style
        intervention_frequency: How often to intervene
        use_emojis: Whether to include emojis in messages
        use_gamification: Whether to use gamified language
        custom_prompts: Custom prompt templates
        enabled_intervention_types: Which intervention types are enabled
    """
    personality: CoachPersonality = CoachPersonality.ENCOURAGING
    tone: ToneStyle = ToneStyle.WARM
    intervention_frequency: InterventionFrequency = InterventionFrequency.NORMAL
    use_emojis: bool = True
    use_gamification: bool = True
    custom_prompts: Dict[str, str] = field(default_factory=dict)
    enabled_intervention_types: list = field(default_factory=lambda: [
        "burnout_warning",
        "streak_break",
        "milestone_celebration",
        "improvement_encouragement",
        "low_engagement"
    ])
    
    def get_system_prompt_modifier(self) -> str:
        """
        Get a prompt modifier based on personality configuration.
        
        Returns:
            String to append to system prompts
        """
        modifiers = {
            CoachPersonality.ENCOURAGING: "Be supportive and positive. Celebrate small wins. Use encouraging language.",
            CoachPersonality.DIRECT: "Be straightforward and concise. Focus on actionable advice. Skip pleasantries.",
            CoachPersonality.GENTLE: "Be soft-spoken and empathetic. Acknowledge feelings. Avoid pressure.",
            CoachPersonality.PLAYFUL: "Be fun and engaging. Use humor where appropriate. Make it feel like a game.",
            CoachPersonality.ANALYTICAL: "Be data-driven and logical. Reference specific metrics. Use evidence-based suggestions.",
            CoachPersonality.STERN: "Be strict but fair. Hold the user accountable. No excuses."
        }
        
        tone_modifiers = {
            ToneStyle.CASUAL: "Use casual, friendly language. Contractions are fine.",
            ToneStyle.FORMAL: "Use professional language. Be respectful and polished.",
            ToneStyle.WARM: "Use caring, nurturing language. Show empathy.",
            ToneStyle.NEUTRAL: "Use neutral, matter-of-fact language.",
            ToneStyle.MOTIVATIONAL: "Use energetic, inspiring language. Pump them up!"
        }
        
        base = modifiers.get(self.personality, "")
        tone = tone_modifiers.get(self.tone, "")
        
        if self.use_emojis:
            emoji_instruction = "Use relevant emojis to enhance messages. "
        else:
            emoji_instruction = "Do not use emojis. "
        
        if self.use_gamification:
            gamification_instruction = "Use gamification language (XP, levels, achievements) when relevant."
        else:
            gamification_instruction = "Avoid gamification language."
        
        return f"{base} {tone} {emoji_instruction} {gamification_instruction}"
    
    def get_max_interventions_per_day(self) -> int:
        """Get maximum interventions per day based on frequency."""
        limits = {
            InterventionFrequency.MINIMAL: 1,
            InterventionFrequency.LOW: 2,
            InterventionFrequency.NORMAL: 4,
            InterventionFrequency.HIGH: 6,
            InterventionFrequency.INTENSIVE: 10
        }
        return limits.get(self.intervention_frequency, 4)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "personality": self.personality.value,
            "tone": self.tone.value,
            "intervention_frequency": self.intervention_frequency.value,
            "use_emojis": self.use_emojis,
            "use_gamification": self.use_gamification,
            "custom_prompts": self.custom_prompts,
            "enabled_intervention_types": self.enabled_intervention_types
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PersonalityConfig":
        """Create from dictionary."""
        return cls(
            personality=CoachPersonality(data.get("personality", "encouraging")),
            tone=ToneStyle(data.get("tone", "warm")),
            intervention_frequency=InterventionFrequency(data.get("intervention_frequency", "normal")),
            use_emojis=data.get("use_emojis", True),
            use_gamification=data.get("use_gamification", True),
            custom_prompts=data.get("custom_prompts", {}),
            enabled_intervention_types=data.get("enabled_intervention_types", [
                "burnout_warning", "streak_break", "milestone_celebration",
                "improvement_encouragement", "low_engagement"
            ])
        )


# Default configurations for quick setup
DEFAULT_CONFIGS = {
    "balanced": PersonalityConfig(
        personality=CoachPersonality.ENCOURAGING,
        tone=ToneStyle.WARM,
        intervention_frequency=InterventionFrequency.NORMAL
    ),
    "intensive": PersonalityConfig(
        personality=CoachPersonality.STERN,
        tone=ToneStyle.MOTIVATIONAL,
        intervention_frequency=InterventionFrequency.INTENSIVE
    ),
    "minimal": PersonalityConfig(
        personality=CoachPersonality.ANALYTICAL,
        tone=ToneStyle.NEUTRAL,
        intervention_frequency=InterventionFrequency.MINIMAL
    ),
    "gentle": PersonalityConfig(
        personality=CoachPersonality.GENTLE,
        tone=ToneStyle.WARM,
        intervention_frequency=InterventionFrequency.LOW
    ),
    "gamer": PersonalityConfig(
        personality=CoachPersonality.PLAYFUL,
        tone=ToneStyle.CASUAL,
        intervention_frequency=InterventionFrequency.HIGH,
        use_gamification=True
    )
}


def get_default_config(name: str = "balanced") -> PersonalityConfig:
    """
    Get a default personality configuration.
    
    Args:
        name: Configuration name (balanced, intensive, minimal, gentle, gamer)
        
    Returns:
        PersonalityConfig instance
    """
    return DEFAULT_CONFIGS.get(name, DEFAULT_CONFIGS["balanced"])