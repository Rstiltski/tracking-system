"""
Mindset Model - Growth Mindset Assessment & Interventions

Implements growth mindset framing to prevent abandonment after setbacks.

Features:
- Mindset type detection (fixed vs growth)
- Language pattern analysis
- Reframing interventions
- Self-compassion prompts
- Post-setback protocols

Based on Task 11.1.4 from PHASE_11_INTEGRATION_ROADMAP.md

Ethical Principles:
- NEVER shame for fixed mindset language
- ALWAYS offer reframing as invitation
- Validate difficulty before problem-solving
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class MindsetType(str, Enum):
    """Types of mindset."""
    FIXED = "fixed"       # Beliefs abilities are static
    GROWTH = "growth"     # Beliefs abilities can develop
    MIXED = "mixed"       # Shows traits of both


class InterventionType(str, Enum):
    """Types of mindset interventions."""
    REFRAME = "reframe"           # Reframe negative self-talk
    SELF_COMPASSION = "compassion"  # Self-compassion prompt
    PROCESS_PRAISE = "process"     # Praise the process, not outcome
    YET_PROMPT = "yet"            # "I can't do this... yet"
    SETBACK_PROTOCOL = "setback"  # Post-setback recovery
    VALIDATION = "validation"      # Validate feelings first


# =============================================================================
# LANGUAGE PATTERNS
# =============================================================================

# Fixed mindset language patterns
FIXED_MINDSET_PATTERNS = [
    "i can't",
    "i'm not good at",
    "i'm bad at",
    "i'm not smart",
    "i'm not talented",
    "i'll never",
    "i always",
    "i never",
    "i'm a failure",
    "i'm worthless",
    "i'm useless",
    "i give up",
    "it's impossible",
    "i don't have the talent",
    "i don't have the ability",
    "i was born this way",
    "i'm just not a",
    "i'm naturally bad at",
    "there's no point",
    "what's the point",
    "i'll never be able to",
    "i'm not disciplined enough",
    "i don't have willpower",
]

# Growth mindset language patterns
GROWTH_MINDSET_PATTERNS = [
    "i'm working on",
    "i'm improving",
    "i'm learning",
    "i can grow",
    "i can develop",
    "i'm getting better",
    "i'm practicing",
    "i haven't figured out yet",
    "i'm exploring",
    "i'm experimenting",
    "i'm trying",
    "i'm building",
    "i'm developing",
    "i'm progressing",
    "i'm working towards",
    "i can improve",
    "i'm becoming",
    "i'm focusing on the process",
    "effort is how i",
    "mistakes help me",
    "challenges are opportunities",
]


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class MindsetSignal:
    """A signal indicating mindset type from language."""
    pattern: str
    is_fixed: bool
    confidence: float
    context: str = ""


@dataclass
class Intervention:
    """A mindset intervention to present to the user."""
    intervention_type: InterventionType
    message: str
    is_invitation: bool = True  # Always offer as invitation, not command
    follow_up: Optional[str] = None


@dataclass
class MindsetAssessment:
    """
    Complete mindset assessment for a user.
    
    Attributes:
        overall_type: Fixed, Growth, or Mixed
        signals: Detected mindset signals
        recommended_interventions: Interventions to offer
        last_assessment: When assessment was done
    """
    overall_type: MindsetType = MindsetType.MIXED
    signals: List[MindsetSignal] = field(default_factory=list)
    recommended_interventions: List[Intervention] = field(default_factory=list)
    last_assessment: datetime = field(default_factory=datetime.now)
    assessment_source: str = ""  # e.g., "onboarding", "periodic", "real-time"


# =============================================================================
# REFRAMING MESSAGES
# =============================================================================

REFRAME_MESSAGES = {
    "i can't": [
        "You can't do it *yet* - that's different from not being able to!",
        "Right now you can't, but with practice you can develop this skill.",
        "Instead of 'I can't', try 'I'm learning to...'",
    ],
    "i'm not good at": [
        "You're not good at it *yet* - but you weren't good at many things before you practiced!",
        "Not being good at something is the first step to getting good at it.",
    ],
    "i'm bad at": [
        "You're not bad at it - you're just early in your learning journey!",
        "What feels like 'bad' is often just 'new'.",
    ],
    "i give up": [
        "Taking a break is different from giving up. Rest can help you come back stronger!",
        "Instead of giving up, what about trying a different approach?",
    ],
    "i'm a failure": [
        "One setback doesn't define you. Failures are just data points in learning!",
        "You're not a failure - you're in progress!",
    ],
    "i'll never": [
        "Never is a very long time. What can you do *today* instead?",
        "Instead of 'I'll never', try 'I haven't yet, and I'm working on it.'",
    ],
    "i always": [
        "Saying 'always' or 'never' is often a sign we're being hard on ourselves. Is it really *always*?",
        "Let's look for evidence to the contrary - there might be exceptions!",
    ],
    "i never": [
        "Saying 'always' or 'never' is often a sign we're being hard on ourselves.",
        "What about that one time it did work? Let's celebrate that!",
    ],
}

SELF_COMPASSION_PROMPTS = [
    "🌸 This is a hard moment. Can you acknowledge that to yourself?",
    "💚 Suffering is part of life - can you be kind to yourself right now?",
    "🫂 Would you talk to a friend the way you're talking to yourself?",
    "🌿 You're doing your best. That's enough.",
    "🍃 Mistakes don't define your worth. You are more than your habits.",
    "🌻 What would you tell a friend who was going through this?",
]

PROCESS_PRAISE_EXAMPLES = [
    "🌟 I notice you showed up today - that's the real win!",
    "💪 The fact that you're trying matters more than the result!",
    "🏆 You're building discipline - that's more valuable than perfection!",
    "🎯 Every effort builds the skill, regardless of the outcome.",
    "📈 The process is where the growth happens!",
]

YET_PROMPTS = [
    "You haven't figured it out *yet* - that's exciting!",
    "Not knowing how to do something yet is the first step to learning.",
    "Your future self who can do this is being built right now!",
]


# =============================================================================
# MINDSET DETECTOR
# =============================================================================

class MindsetDetector:
    """
    Detects mindset type from user language and behavior.
    
    Uses pattern matching to identify fixed vs growth mindset language.
    """
    
    def __init__(self):
        """Initialize the mindset detector."""
        self._signal_history: List[MindsetSignal] = []
    
    def detect_from_text(self, text: str) -> List[MindsetSignal]:
        """
        Detect mindset signals from text.
        
        Args:
            text: User's text input
            
        Returns:
            List of detected signals
        """
        text_lower = text.lower()
        signals = []
        
        # Check for fixed mindset patterns
        for pattern in FIXED_MINDSET_PATTERNS:
            if pattern in text_lower:
                signals.append(MindsetSignal(
                    pattern=pattern,
                    is_fixed=True,
                    confidence=0.8,
                    context=self._extract_context(text_lower, pattern)
                ))
        
        # Check for growth mindset patterns
        for pattern in GROWTH_MINDSET_PATTERNS:
            if pattern in text_lower:
                signals.append(MindsetSignal(
                    pattern=pattern,
                    is_fixed=False,
                    confidence=0.8,
                    context=self._extract_context(text_lower, pattern)
                ))
        
        # Store in history
        self._signal_history.extend(signals)
        
        return signals
    
    def _extract_context(self, text: str, pattern: str) -> str:
        """Extract context around a pattern."""
        idx = text.find(pattern)
        if idx == -1:
            return ""
        
        start = max(0, idx - 20)
        end = min(len(text), idx + len(pattern) + 20)
        
        return text[start:end]
    
    def assess_mindset(self, signals: List[MindsetSignal] = None) -> MindsetAssessment:
        """
        Assess overall mindset from signals.
        
        Args:
            signals: List of signals (uses history if not provided)
            
        Returns:
            Complete mindset assessment
        """
        if signals is None:
            signals = self._signal_history
        
        if not signals:
            return MindsetAssessment(
                overall_type=MindsetType.MIXED,
                assessment_source="insufficient_data"
            )
        
        # Count fixed vs growth signals
        fixed_count = sum(1 for s in signals if s.is_fixed)
        growth_count = sum(1 for s in signals if not s.is_fixed)
        
        # Determine overall type
        if fixed_count == 0:
            overall = MindsetType.GROWTH
        elif growth_count == 0:
            overall = MindsetType.FIXED
        else:
            overall = MindsetType.MIXED
        
        assessment = MindsetAssessment(
            overall_type=overall,
            signals=signals[-10:],  # Last 10 signals
            assessment_source="language_analysis"
        )
        
        # Generate interventions
        assessment.recommended_interventions = self._generate_interventions(signals)
        
        return assessment
    
    def _generate_interventions(self, signals: List[MindsetSignal]) -> List[Intervention]:
        """Generate appropriate interventions based on signals."""
        interventions = []
        
        # Get most recent fixed mindset signal
        recent_fixed = None
        for signal in reversed(signals):
            if signal.is_fixed:
                recent_fixed = signal
                break
        
        if recent_fixed:
            # Generate reframe intervention
            message = self._get_reframe_message(recent_fixed.pattern)
            if message:
                interventions.append(Intervention(
                    intervention_type=InterventionType.REFRAME,
                    message=message
                ))
        
        # Add self-compassion prompt
        interventions.append(Intervention(
            intervention_type=InterventionType.SELF_COMPASSION,
            message=",".join(SELF_COMPASSION_PROMPTS[:2])
        ))
        
        # Add process praise
        interventions.append(Intervention(
            intervention_type=InterventionType.PROCESS_PRAISE,
            message=PROCESS_PRAISE_EXAMPLES[0]
        ))
        
        return interventions
    
    def _get_reframe_message(self, pattern: str) -> Optional[str]:
        """Get a reframe message for a fixed mindset pattern."""
        # Find the closest matching pattern
        for key in REFRAME_MESSAGES:
            if key in pattern:
                import random
                return random.choice(REFRAME_MESSAGES[key])
        
        return None


# =============================================================================
# POST-SETBACK PROTOCOL
# =============================================================================

class SetbackProtocol:
    """
    Protocol for helping users recover from setbacks.
    
    Based on research on growth mindset and self-compassion.
    """
    
    @staticmethod
    def get_post_setback_message(days_missed: int) -> str:
        """
        Get appropriate message based on how long user has been away.
        
        Args:
            days_missed: Number of days since last completion
            
        Returns:
            Encouraging message
        """
        if days_missed == 1:
            return "Welcome back! One day off doesn't change anything. Let's get started!"
        
        elif days_missed <= 3:
            return """
            ### 🌟 Welcome Back!
            
            You took a short break - that's completely normal! 
            
            **Remember:**
            - Your streak isn't as important as your consistency
            - Every day is a new start
            - The fact that you're here matters!
            
            Ready to continue your journey?
            """
        
        elif days_missed <= 7:
            return """
            ### 💪 Welcome Back!
            
            It's been a little while, but that's okay! Habits can be rebuilt.
            
            **Consider starting fresh:**
            - Pick 1-2 habits to rebuild first
            - Don't try to do everything at once
            - Celebrate small wins
            
            **Growth mindset reminder:**
            - Missing days doesn't mean you're a failure
            - It just means you're human!
            - Your next choice is what matters
            """
        
        else:
            return """
            ### 🌱 New Beginning
            
            It's great to see you again! Starting over is always an option.
            
            **Let's make this time different:**
            - Be realistic about what you can maintain
            - Focus on building one habit at a time
            - Celebrate showing up, not perfection
            
            **Remember:**
            - You're not starting from zero - you have experience!
            - Every expert was once a beginner
            - The best time to start was yesterday. The next best time is today!
            """
    
    @staticmethod
    def get_compassion_reminder() -> str:
        """Get a self-compassion reminder."""
        import random
        return random.choice(SELF_COMPASSION_PROMPTS)


# =============================================================================
# FACTORY
# =============================================================================

def create_mindset_detector() -> MindsetDetector:
    """Factory function to create a mindset detector."""
    return MindsetDetector()
