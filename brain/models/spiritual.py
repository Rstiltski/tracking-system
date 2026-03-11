"""
Spiritual/Voice Journaling Model

AI-guided spiritual pattern recognition for voice journals.

Based on Task 11.2.7 from PHASE_11_INTEGRATION_ROADMAP.md

Untapped market - voice journaling removes friction!
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class JournalType(Enum):
    """Types of spiritual journals."""
    VOICE = "voice"           # Voice recording
    TEXT = "text"            # Written journal
    REFLECTION = "reflection"  # Guided reflection
    PRAYER = "prayer"        # Prayer/intention
    MEDITATION = "meditation"  # Meditation log


class SpiritualTheme(Enum):
    """Spiritual themes."""
    PURPOSE = "purpose"       # Life purpose
    MEANING = "meaning"       # Meaning in life
    CONNECTION = "connection"  # Connection to something greater
    COMPASSION = "compassion"  # Love and compassion
    STILLNESS = "stillness"   # Inner peace
    GROWTH = "growth"        # Spiritual growth
    GRATITUDE = "gratitude"  # Thankfulness
    FORGIVENESS = "forgiveness"  # Letting go


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class JournalEntry:
    """A spiritual journal entry."""
    id: str
    user_id: str
    date: date
    timestamp: datetime
    journal_type: JournalType
    theme: Optional[SpiritualTheme]
    transcript: str  # Text from voice or manual entry
    audio_path: Optional[str] = None
    duration_seconds: Optional[int] = None
    # AI analysis
    mood_score: Optional[int] = None  # 1-10
    sentiment: Optional[str] = None
    themes_detected: List[str] = field(default_factory=list)
    ai_insights: Optional[str] = None


@dataclass
class SpiritualPattern:
    """Detected spiritual pattern."""
    id: str
    theme: SpiritualTheme
    frequency: int
    trend: str  # increasing, decreasing, stable
    last_detected: date
    description: str


# =============================================================================
# SPIRITUAL JOURNALING ENGINE
# =============================================================================

class SpiritualEngine:
    """
    Manages spiritual journaling.
    
    Features:
    - Voice journal support (placeholder for transcription)
    - Theme detection
    - Pattern recognition
    - AI-guided reflections
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.entries: List[JournalEntry] = []
        self.patterns: Dict[str, List[SpiritualPattern]] = {}
    
    def add_entry(
        self,
        user_id: str,
        journal_type: JournalType,
        transcript: str,
        theme: Optional[SpiritualTheme] = None,
        audio_path: Optional[str] = None,
        duration_seconds: Optional[int] = None
    ) -> JournalEntry:
        """Add a journal entry."""
        import uuid
        
        entry = JournalEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            date=date.today(),
            timestamp=datetime.now(),
            journal_type=journal_type,
            theme=theme,
            transcript=transcript,
            audio_path=audio_path,
            duration_seconds=duration_seconds
        )
        
        # Analyze entry
        self._analyze_entry(entry)
        
        self.entries.append(entry)
        return entry
    
    def _analyze_entry(self, entry: JournalEntry) -> None:
        """Analyze journal entry for themes and sentiment."""
        text = entry.transcript.lower()
        
        # Simple theme detection
        theme_keywords = {
            "purpose": ["purpose", "meaning", "calling", "why", "reason"],
            "meaning": ["meaning", "meaningful", "significant", "important"],
            "connection": ["connected", "one", "whole", "universe", "god", "divine"],
            "compassion": ["love", "kind", "forgive", "care", "heart"],
            "stillness": ["peace", "calm", "quiet", "still", "rest"],
            "growth": ["grow", "change", "learn", "improve", "become"],
            "gratitude": ["thankful", "grateful", "appreciate", "blessed"],
            "forgiveness": ["forgive", "release", "let go", "accept"],
        }
        
        detected = []
        for theme, keywords in theme_keywords.items():
            if any(kw in text for kw in keywords):
                detected.append(theme)
        
        entry.themes_detected = detected
        
        # Simple sentiment (positive/negative words)
        positive = ["good", "great", "love", "happy", "peaceful", "grateful", "blessed"]
        negative = ["bad", "sad", "angry", "hurt", "pain", "struggle"]
        
        pos_count = sum(1 for w in positive if w in text)
        neg_count = sum(1 for w in negative if w in text)
        
        if pos_count > neg_count:
            entry.sentiment = "positive"
        elif neg_count > pos_count:
            entry.sentiment = "challenging"
        else:
            entry.sentiment = "neutral"
        
        # Mood score (simple heuristic)
        if entry.sentiment == "positive":
            entry.mood_score = 7
        elif entry.sentiment == "challenging":
            entry.mood_score = 5
        else:
            entry.mood_score = 6
    
    def get_entries(
        self, 
        user_id: str, 
        days: int = 30
    ) -> List[JournalEntry]:
        """Get recent entries."""
        from datetime import timedelta
        
        cutoff = date.today() - timedelta(days=days)
        
        return [
            e for e in self.entries
            if e.user_id == user_id and e.date >= cutoff
        ]
    
    def detect_patterns(self, user_id: str) -> List[SpiritualPattern]:
        """Detect spiritual patterns."""
        entries = self.get_entries(user_id, days=30)
        
        if len(entries) < 3:
            return []
        
        # Count theme frequency
        theme_counts = {}
        for entry in entries:
            if entry.themes_detected:
                for theme in entry.themes_detected:
                    theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        patterns = []
        for theme, count in theme_counts.items():
            if count >= 2:
                pattern = SpiritualPattern(
                    id=f"pattern_{theme}",
                    theme=SpiritualTheme(theme),
                    frequency=count,
                    trend="stable" if count >= 3 else "emerging",
                    last_detected=max(e.date for e in entries),
                    description=f"Detected {count} times in last 30 days"
                )
                patterns.append(pattern)
        
        return patterns
    
    def get_insights(self, user_id: str) -> Dict:
        """Get spiritual insights."""
        entries = self.get_entries(user_id, days=30)
        patterns = self.detect_patterns(user_id)
        
        return {
            "total_entries": len(entries),
            "voice_entries": len([e for e in entries if e.journal_type == JournalType.VOICE]),
            "patterns_detected": len(patterns),
            "dominant_theme": patterns[0].theme.value if patterns else None,
            "avg_mood": sum(e.mood_score for e in entries if e.mood_score) / len(entries) if entries else 0,
            "recent_themes": list(set(t for e in entries for t in e.themes_detected))[:5]
        }


def create_engine() -> SpiritualEngine:
    """Factory function."""
    return SpiritualEngine()
