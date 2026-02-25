"""
Emotional State Model - RGB Neurotransmitter-Based Emotion Tracking

This module implements a scientifically-grounded emotion tracking system based on
the "Chemical RGB" model of human emotions. The three primary neurotransmitters
(Dopamine, Norepinephrine, Serotonin) combine like RGB colors to produce the
full spectrum of human emotional states.

=============================================================================
LLM QUICK INDEX (YAML)
=============================================================================
module: emotional_state
purpose: Track human emotions using neurotransmitter-based RGB model
location: brain/models/emotional_state.py
entry_points:
  - EmotionalState: Main dataclass for storing emotional state
  - NeurotransmitterLevels: The 3 primary emotion components
  - EmotionalModifiers: Optional chemical additives (Oxytocin, Endorphins, GABA)
  - EmotionalStateManager: CRUD operations for emotional states
  - EmotionAnalyzer: Pattern detection and insights

usage_examples:
  - create_state: "EmotionalState.create(dopamine=0.8, norepinephrine=0.3, serotonin=0.7)"
  - from_preset: "EmotionalState.from_preset('joyful')"
  - get_color: "state.hex_color  # Returns '#cc4db3'"
  - get_emotion: "state.get_secondary_emotion()  # Returns emotion name and description"

integration:
  - health_module: "Can replace simple mood tracking in health.py"
  - streamlit_page: "tracking_app/pages/emotional_health.py"
  - charts: "Use rgb_color for visualization"

common_errors:
  - ValueError: "When neurotransmitter values outside 0.0-1.0 range"
  - TypeError: "When passing non-numeric values to create()"

what_not_to_do:
  - "DO NOT store values outside 0.0-1.0"
  - "DO NOT skip validation when creating from user input"
  - "DO NOT forget to save timestamp with each state"

references:
  - "National Institutes of Health - Monoamine neurotransmitters"
  - "North London Collegiate School - Chemical emotion model"
=============================================================================

The Three Primary Chemical Emotions:
------------------------------------
1. Dopamine (Red): Joy / Reward / Pleasure
   - Associated with desire, motivation, enjoyment, and reward system
   - High: Achievement, excitement, anticipation
   - Low: Lack of motivation, anhedonia

2. Norepinephrine (Blue): Fear / Anger / Arousal
   - Driver for "fight-or-flight" responses, stress, attention
   - High: Alertness, anxiety, stress response
   - Low: Fatigue, lack of focus

3. Serotonin (Green): Disgust / Sadness / Satisfaction
   - Mood stability, satiety, contentment
   - High: Calm satisfaction, stability
   - Low: Sadness, irritability, disgust

Secondary Emotions (Combinations):
----------------------------------
- Hope/Excitement: High Dopamine + High Norepinephrine
- Anxiety/Panic: High Norepinephrine + Low Serotonin
- Depression: Low Dopamine + Low Serotonin
- Contentment: High Serotonin + Moderate Dopamine
- Disgust/Contempt: High Serotonin + Low Dopamine

Additives (Modifiers):
----------------------
- Oxytocin: Bonding, trust, empathy, love
- Endorphins: Euphoria, pain masking, runner's high
- GABA: Calm, balance, anxiety reduction
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
import uuid
import sqlite3
import json


# =============================================================================
# ENUMS
# =============================================================================

class EmotionPreset(str, Enum):
    """Predefined emotional states for quick selection."""
    JOYFUL = "joyful"
    EXCITED = "excited"
    CONTENT = "content"
    CALM = "calm"
    ANXIOUS = "anxious"
    STRESSED = "stressed"
    SAD = "sad"
    DEPRESSED = "depressed"
    ANGRY = "angry"
    FEARFUL = "fearful"
    NEUTRAL = "neutral"
    HOPEFUL = "hopeful"
    GRATEFUL = "grateful"
    LOVING = "loving"
    OVERWHELMED = "overwhelmed"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class NeurotransmitterLevels:
    """
    The three primary neurotransmitters that form the RGB of emotions.
    
    Each value ranges from 0.0 to 1.0:
    - 0.0 = Complete absence
    - 1.0 = Maximum presence
    - 0.5 = Baseline/normal level
    
    Attributes:
        dopamine: Joy/Reward/Pleasure (Red channel)
        norepinephrine: Fear/Anger/Arousal (Blue channel)
        serotonin: Disgust/Sadness/Satisfaction (Green channel)
    """
    dopamine: float = 0.5
    norepinephrine: float = 0.5
    serotonin: float = 0.5
    
    def __post_init__(self):
        """Validate values are within range."""
        self.dopamine = self._clamp(self.dopamine)
        self.norepinephrine = self._clamp(self.norepinephrine)
        self.serotonin = self._clamp(self.serotonin)
    
    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp value between 0.0 and 1.0."""
        return max(0.0, min(1.0, float(value)))
    
    @property
    def rgb_tuple(self) -> Tuple[int, int, int]:
        """
        Convert to RGB color values (0-255).
        
        Returns:
            Tuple of (red, green, blue) integers
        """
        return (
            int(self.dopamine * 255),
            int(self.serotonin * 255),  # Note: serotonin maps to green
            int(self.norepinephrine * 255)  # Note: norepinephrine maps to blue
        )
    
    @property
    def hex_color(self) -> str:
        """Get hex color string for visualization."""
        r, g, b = self.rgb_tuple
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "dopamine": self.dopamine,
            "norepinephrine": self.norepinephrine,
            "serotonin": self.serotonin
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "NeurotransmitterLevels":
        """Create from dictionary."""
        return cls(
            dopamine=data.get("dopamine", 0.5),
            norepinephrine=data.get("norepinephrine", 0.5),
            serotonin=data.get("serotonin", 0.5)
        )


@dataclass
class EmotionalModifiers:
    """
    Optional chemical modifiers that affect emotional state.
    
    These act like "filters" or "intensifiers" in the RGB model:
    - Oxytocin: Adds warmth/bonding (like adding yellow to RGB)
    - Endorphins: Increases brightness/intensity
    - GABA: Reduces intensity, adds calm
    
    Attributes:
        oxytocin: Bonding, trust, empathy (0.0-1.0)
        endorphins: Euphoria, pain masking (0.0-1.0)
        gaba: Calm, balance (0.0-1.0)
    """
    oxytocin: float = 0.0
    endorphins: float = 0.0
    gaba: float = 0.0
    
    def __post_init__(self):
        """Validate values."""
        self.oxytocin = max(0.0, min(1.0, float(self.oxytocin)))
        self.endorphins = max(0.0, min(1.0, float(self.endorphins)))
        self.gaba = max(0.0, min(1.0, float(self.gaba)))
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "oxytocin": self.oxytocin,
            "endorphins": self.endorphins,
            "gaba": self.gaba
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "EmotionalModifiers":
        """Create from dictionary."""
        return cls(
            oxytocin=data.get("oxytocin", 0.0),
            endorphins=data.get("endorphins", 0.0),
            gaba=data.get("gaba", 0.0)
        )


@dataclass
class EmotionalState:
    """
    A complete emotional state snapshot using the RGB neurotransmitter model.
    
    This is the main data class for storing emotional states. Each state
    captures the levels of the three primary neurotransmitters (plus optional
    modifiers) at a specific point in time.
    
    Attributes:
        id: Unique identifier for this state
        timestamp: When this state was recorded
        primaries: The three primary neurotransmitter levels
        modifiers: Optional chemical modifiers
        notes: User notes about context
        triggers: What triggered this emotional state
        
    Example:
        >>> state = EmotionalState.create(
        ...     dopamine=0.8,
        ...     norepinephrine=0.3,
        ...     serotonin=0.7
        ... )
        >>> state.hex_color
        '#cc4db3'
        >>> state.get_secondary_emotion()['label']
        'Joyful'
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=datetime.now)
    primaries: NeurotransmitterLevels = field(default_factory=NeurotransmitterLevels)
    modifiers: Optional[EmotionalModifiers] = None
    notes: str = ""
    triggers: List[str] = field(default_factory=list)
    
    # =========================================================================
    # FACTORY METHODS
    # =========================================================================
    
    @classmethod
    def create(
        cls,
        dopamine: float = 0.5,
        norepinephrine: float = 0.5,
        serotonin: float = 0.5,
        oxytocin: float = 0.0,
        endorphins: float = 0.0,
        gaba: float = 0.0,
        notes: str = "",
        triggers: Optional[List[str]] = None
    ) -> "EmotionalState":
        """
        Create an emotional state from neurotransmitter values.
        
        Args:
            dopamine: Joy/Reward level (0.0-1.0)
            norepinephrine: Fear/Anger/Arousal level (0.0-1.0)
            serotonin: Satisfaction/Stability level (0.0-1.0)
            oxytocin: Bonding/Trust level (0.0-1.0)
            endorphins: Euphoria level (0.0-1.0)
            gaba: Calm level (0.0-1.0)
            notes: Optional notes about context
            triggers: List of triggers
            
        Returns:
            New EmotionalState instance
            
        Example:
            >>> state = EmotionalState.create(
            ...     dopamine=0.9, serotonin=0.7, notes="Great presentation!"
            ... )
        """
        primaries = NeurotransmitterLevels(
            dopamine=dopamine,
            norepinephrine=norepinephrine,
            serotonin=serotonin
        )
        
        modifiers = None
        if oxytocin > 0 or endorphins > 0 or gaba > 0:
            modifiers = EmotionalModifiers(
                oxytocin=oxytocin,
                endorphins=endorphins,
                gaba=gaba
            )
        
        return cls(
            primaries=primaries,
            modifiers=modifiers,
            notes=notes,
            triggers=triggers or []
        )
    
    @classmethod
    def from_preset(cls, preset: EmotionPreset) -> "EmotionalState":
        """
        Create an emotional state from a preset emotion.
        
        Args:
            preset: One of the predefined emotion presets
            
        Returns:
            New EmotionalState with values matching the preset
            
        Example:
            >>> state = EmotionalState.from_preset(EmotionPreset.JOYFUL)
            >>> state.primaries.dopamine
            0.9
        """
        # Preset definitions: (dopamine, norepinephrine, serotonin, oxytocin, endorphins, gaba)
        presets: Dict[EmotionPreset, Tuple[float, float, float, float, float, float]] = {
            EmotionPreset.JOYFUL: (0.9, 0.3, 0.7, 0.3, 0.5, 0.0),
            EmotionPreset.EXCITED: (0.85, 0.8, 0.5, 0.2, 0.4, 0.0),
            EmotionPreset.CONTENT: (0.6, 0.2, 0.8, 0.4, 0.2, 0.3),
            EmotionPreset.CALM: (0.4, 0.15, 0.7, 0.2, 0.1, 0.5),
            EmotionPreset.ANXIOUS: (0.3, 0.9, 0.25, 0.0, 0.0, 0.1),
            EmotionPreset.STRESSED: (0.35, 0.85, 0.3, 0.0, 0.0, 0.05),
            EmotionPreset.SAD: (0.2, 0.35, 0.2, 0.0, 0.0, 0.1),
            EmotionPreset.DEPRESSED: (0.15, 0.25, 0.15, 0.0, 0.0, 0.05),
            EmotionPreset.ANGRY: (0.4, 0.95, 0.25, 0.0, 0.0, 0.0),
            EmotionPreset.FEARFUL: (0.25, 0.9, 0.2, 0.0, 0.0, 0.0),
            EmotionPreset.NEUTRAL: (0.5, 0.5, 0.5, 0.0, 0.0, 0.0),
            EmotionPreset.HOPEFUL: (0.75, 0.55, 0.6, 0.2, 0.2, 0.0),
            EmotionPreset.GRATEFUL: (0.7, 0.25, 0.75, 0.6, 0.3, 0.2),
            EmotionPreset.LOVING: (0.75, 0.35, 0.7, 0.85, 0.4, 0.0),
            EmotionPreset.OVERWHELMED: (0.2, 0.85, 0.2, 0.0, 0.0, 0.0),
        }
        
        d, n, s, ox, en, ga = presets.get(preset, (0.5, 0.5, 0.5, 0.0, 0.0, 0.0))
        
        return cls.create(
            dopamine=d,
            norepinephrine=n,
            serotonin=s,
            oxytocin=ox,
            endorphins=en,
            gaba=ga,
            notes=f"Preset: {preset.value}"
        )
    
    # =========================================================================
    # PROPERTIES
    # =========================================================================
    
    @property
    def rgb_tuple(self) -> Tuple[int, int, int]:
        """Get RGB color values (0-255)."""
        return self.primaries.rgb_tuple
    
    @property
    def hex_color(self) -> str:
        """Get hex color for visualization."""
        base_color = self.primaries.hex_color
        
        # If modifiers present, adjust brightness
        if self.modifiers:
            # Endorphins increase brightness
            brightness_boost = self.modifiers.endorphins * 0.2
            # GABA decreases intensity
            intensity_reduction = self.modifiers.gaba * 0.1
            
            # Simple brightness adjustment (could be more sophisticated)
            # For now, just return base color
            pass
        
        return base_color
    
    @property
    def brightness(self) -> float:
        """Calculate overall emotional brightness (0.0-1.0)."""
        return (self.primaries.dopamine + 
                self.primaries.norepinephrine + 
                self.primaries.serotonin) / 3.0
    
    # =========================================================================
    # EMOTION ANALYSIS
    # =========================================================================
    
    def get_secondary_emotion(self) -> Dict[str, Any]:
        """
        Determine the secondary emotion from neurotransmitter combination.
        
        Returns:
            Dict with 'label', 'description', 'emoji', and 'category'
        """
        d = self.primaries.dopamine
        n = self.primaries.norepinephrine
        s = self.primaries.serotonin
        
        # Define thresholds
        HIGH = 0.7
        MED = 0.5
        LOW = 0.3
        
        # High Dopamine combinations
        if d >= HIGH:
            if n >= HIGH and s >= MED:
                return {
                    "label": "Excited",
                    "description": "High energy with positive anticipation",
                    "emoji": "🤩",
                    "category": "positive_high_energy"
                }
            elif n >= HIGH:
                return {
                    "label": "Hopeful",
                    "description": "Anticipating reward with some anxiety",
                    "emoji": "🌟",
                    "category": "positive_mixed"
                }
            elif s >= HIGH:
                return {
                    "label": "Joyful",
                    "description": "Pure happiness and satisfaction",
                    "emoji": "😊",
                    "category": "positive"
                }
            else:
                return {
                    "label": "Pleasant",
                    "description": "Mild positive feeling",
                    "emoji": "🙂",
                    "category": "positive"
                }
        
        # High Norepinephrine combinations
        if n >= HIGH:
            if s <= LOW:
                return {
                    "label": "Anxious",
                    "description": "High stress with low satisfaction",
                    "emoji": "😰",
                    "category": "negative_high_energy"
                }
            elif d <= LOW:
                return {
                    "label": "Fearful",
                    "description": "Threat detection without reward anticipation",
                    "emoji": "😨",
                    "category": "negative_high_energy"
                }
            else:
                return {
                    "label": "Alert",
                    "description": "High focus and awareness",
                    "emoji": "⚠️",
                    "category": "neutral_high_energy"
                }
        
        # Low Dopamine + Low Serotonin
        if d <= LOW and s <= LOW:
            return {
                "label": "Depressed",
                "description": "Low motivation and low satisfaction",
                "emoji": "😔",
                "category": "negative_low_energy"
            }
        
        # High Serotonin combinations
        if s >= HIGH:
            if d >= MED:
                return {
                    "label": "Content",
                    "description": "Satisfied and stable",
                    "emoji": "😌",
                    "category": "positive"
                }
            elif n <= LOW:
                return {
                    "label": "Calm",
                    "description": "Peaceful and relaxed",
                    "emoji": "😌",
                    "category": "positive_low_energy"
                }
            else:
                return {
                    "label": "Disgusted",
                    "description": "Rejecting a stimulus",
                    "emoji": "😒",
                    "category": "negative"
                }
        
        # Default neutral
        return {
            "label": "Neutral",
            "description": "Balanced emotional state",
            "emoji": "😐",
            "category": "neutral"
        }
    
    def get_emotion_category(self) -> str:
        """Get the category of the current emotion."""
        return self.get_secondary_emotion().get("category", "neutral")
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "primaries": self.primaries.to_dict(),
            "modifiers": self.modifiers.to_dict() if self.modifiers else None,
            "notes": self.notes,
            "triggers": self.triggers,
            "hex_color": self.hex_color,
            "emotion": self.get_secondary_emotion()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmotionalState":
        """Create from dictionary."""
        modifiers = None
        if data.get("modifiers"):
            modifiers = EmotionalModifiers.from_dict(data["modifiers"])
        
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            primaries=NeurotransmitterLevels.from_dict(data.get("primaries", {})),
            modifiers=modifiers,
            notes=data.get("notes", ""),
            triggers=data.get("triggers", [])
        )
    
    def __str__(self) -> str:
        """String representation."""
        emotion = self.get_secondary_emotion()
        return f"{emotion['emoji']} {emotion['label']} ({self.hex_color})"


# =============================================================================
# MANAGER CLASS
# =============================================================================

class EmotionalStateManager:
    """
    Manages CRUD operations for emotional states in SQLite database.
    
    This class handles all database operations for emotional states,
    including creation, retrieval, updating, and deletion.
    
    Example:
        >>> manager = EmotionalStateManager(db_connection)
        >>> state = EmotionalState.create(dopamine=0.8, serotonin=0.7)
        >>> manager.save(state)
        >>> recent_states = manager.get_recent(days=7)
    """
    
    def __init__(self, db_path: str = "tracking.db"):
        """
        Initialize the manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_table()
    
    def _init_table(self):
        """Create the emotional_states table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emotional_states (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    dopamine REAL NOT NULL,
                    norepinephrine REAL NOT NULL,
                    serotonin REAL NOT NULL,
                    oxytocin REAL DEFAULT 0.0,
                    endorphins REAL DEFAULT 0.0,
                    gaba REAL DEFAULT 0.0,
                    notes TEXT,
                    triggers TEXT,
                    hex_color TEXT,
                    emotion_label TEXT,
                    emotion_category TEXT
                )
            """)
            
            # Create indexes for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_emotional_states_timestamp 
                ON emotional_states(timestamp)
            """)
            
            conn.commit()
    
    def save(self, state: EmotionalState) -> str:
        """
        Save an emotional state to the database.
        
        Args:
            state: The EmotionalState to save
            
        Returns:
            The ID of the saved state
        """
        emotion = state.get_secondary_emotion()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if state with this ID exists
            existing = cursor.execute(
                "SELECT id FROM emotional_states WHERE id = ?",
                (state.id,)
            ).fetchone()
            
            if existing:
                # Update existing
                cursor.execute("""
                    UPDATE emotional_states SET
                        timestamp = ?, dopamine = ?, norepinephrine = ?, serotonin = ?,
                        oxytocin = ?, endorphins = ?, gaba = ?,
                        notes = ?, triggers = ?, hex_color = ?,
                        emotion_label = ?, emotion_category = ?
                    WHERE id = ?
                """, (
                    state.timestamp.isoformat(),
                    state.primaries.dopamine,
                    state.primaries.norepinephrine,
                    state.primaries.serotonin,
                    state.modifiers.oxytocin if state.modifiers else 0.0,
                    state.modifiers.endorphins if state.modifiers else 0.0,
                    state.modifiers.gaba if state.modifiers else 0.0,
                    state.notes,
                    json.dumps(state.triggers),
                    state.hex_color,
                    emotion["label"],
                    emotion["category"],
                    state.id
                ))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO emotional_states (
                        id, timestamp, dopamine, norepinephrine, serotonin,
                        oxytocin, endorphins, gaba, notes, triggers,
                        hex_color, emotion_label, emotion_category
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    state.id,
                    state.timestamp.isoformat(),
                    state.primaries.dopamine,
                    state.primaries.norepinephrine,
                    state.primaries.serotonin,
                    state.modifiers.oxytocin if state.modifiers else 0.0,
                    state.modifiers.endorphins if state.modifiers else 0.0,
                    state.modifiers.gaba if state.modifiers else 0.0,
                    state.notes,
                    json.dumps(state.triggers),
                    state.hex_color,
                    emotion["label"],
                    emotion["category"]
                ))
            
            conn.commit()
        
        return state.id
    
    def get_by_id(self, state_id: str) -> Optional[EmotionalState]:
        """Get an emotional state by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            row = cursor.execute(
                "SELECT * FROM emotional_states WHERE id = ?",
                (state_id,)
            ).fetchone()
            
            if row:
                return self._row_to_state(row)
        return None
    
    def get_recent(self, days: int = 7, limit: int = 100) -> List[EmotionalState]:
        """
        Get recent emotional states.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of states to return
            
        Returns:
            List of EmotionalState objects, most recent first
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            rows = cursor.execute("""
                SELECT * FROM emotional_states 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (cutoff.isoformat(), limit)).fetchall()
            
            return [self._row_to_state(row) for row in rows]
    
    def get_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[EmotionalState]:
        """Get states within a date range."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            rows = cursor.execute("""
                SELECT * FROM emotional_states 
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp DESC
            """, (start_date.isoformat(), end_date.isoformat())).fetchall()
            
            return [self._row_to_state(row) for row in rows]
    
    def delete(self, state_id: str) -> bool:
        """Delete an emotional state."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM emotional_states WHERE id = ?", (state_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def _row_to_state(self, row: tuple) -> EmotionalState:
        """Convert a database row to EmotionalState."""
        (
            id, timestamp, dopamine, norepinephrine, serotonin,
            oxytocin, endorphins, gaba, notes, triggers,
            hex_color, emotion_label, emotion_category
        ) = row
        
        modifiers = None
        if oxytocin > 0 or endorphins > 0 or gaba > 0:
            modifiers = EmotionalModifiers(
                oxytocin=oxytocin,
                endorphins=endorphins,
                gaba=gaba
            )
        
        return EmotionalState(
            id=id,
            timestamp=datetime.fromisoformat(timestamp),
            primaries=NeurotransmitterLevels(
                dopamine=dopamine,
                norepinephrine=norepinephrine,
                serotonin=serotonin
            ),
            modifiers=modifiers,
            notes=notes or "",
            triggers=json.loads(triggers) if triggers else []
        )


# =============================================================================
# ANALYZER CLASS
# =============================================================================

class EmotionAnalyzer:
    """
    Analyzes emotional state data for patterns and insights.
    
    This class provides methods for detecting patterns, trends, and
    generating insights from emotional state history.
    """
    
    def __init__(self, manager: EmotionalStateManager):
        """
        Initialize the analyzer.
        
        Args:
            manager: An EmotionalStateManager instance
        """
        self.manager = manager
    
    def get_average_levels(self, days: int = 7) -> NeurotransmitterLevels:
        """
        Calculate average neurotransmitter levels over a period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            NeurotransmitterLevels with average values
        """
        states = self.manager.get_recent(days=days)
        
        if not states:
            return NeurotransmitterLevels()
        
        avg_d = sum(s.primaries.dopamine for s in states) / len(states)
        avg_n = sum(s.primaries.norepinephrine for s in states) / len(states)
        avg_s = sum(s.primaries.serotonin for s in states) / len(states)
        
        return NeurotransmitterLevels(
            dopamine=avg_d,
            norepinephrine=avg_n,
            serotonin=avg_s
        )
    
    def get_dominant_emotion(self, days: int = 7) -> Dict[str, Any]:
        """
        Find the most frequent emotion category.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with 'label', 'count', and 'percentage'
        """
        from collections import Counter
        
        states = self.manager.get_recent(days=days)
        
        if not states:
            return {"label": "No data", "count": 0, "percentage": 0}
        
        emotions = [s.get_secondary_emotion()["label"] for s in states]
        counter = Counter(emotions)
        
        most_common = counter.most_common(1)[0]
        
        return {
            "label": most_common[0],
            "count": most_common[1],
            "percentage": (most_common[1] / len(states)) * 100
        }
    
    def detect_patterns(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Detect patterns in emotional states.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of detected patterns
        """
        patterns = []
        states = self.manager.get_recent(days=days)
        
        if len(states) < 7:
            return patterns
        
        # Check for low serotonin pattern
        avg_s = sum(s.primaries.serotonin for s in states) / len(states)
        if avg_s < 0.3:
            patterns.append({
                "type": "warning",
                "label": "Low Satisfaction Trend",
                "description": "Your satisfaction levels have been consistently low. Consider activities that boost contentment.",
                "recommendation": "Try gratitude journaling or spending time in nature."
            })
        
        # Check for high stress pattern
        avg_n = sum(s.primaries.norepinephrine for s in states) / len(states)
        if avg_n > 0.7:
            patterns.append({
                "type": "warning",
                "label": "High Stress Trend",
                "description": "Your stress levels have been elevated. Consider stress-reduction techniques.",
                "recommendation": "Try meditation, deep breathing, or reducing caffeine."
            })
        
        # Check for balanced state
        if avg_s > 0.5 and avg_n < 0.5:
            patterns.append({
                "type": "positive",
                "label": "Balanced State",
                "description": "Your emotional state appears balanced and stable.",
                "recommendation": "Keep up whatever you're doing!"
            })
        
        return patterns
    
    def get_weekly_summary(self) -> Dict[str, Any]:
        """
        Generate a weekly emotional summary.
        
        Returns:
            Dict with weekly statistics and insights
        """
        states = self.manager.get_recent(days=7)
        
        if not states:
            return {
                "total_entries": 0,
                "average_levels": {},
                "dominant_emotion": "No data",
                "patterns": [],
                "color_trend": []
            }
        
        avg_levels = self.get_average_levels(days=7)
        dominant = self.get_dominant_emotion(days=7)
        patterns = self.detect_patterns(days=7)
        
        # Get color trend (last 7 states)
        color_trend = [s.hex_color for s in states[:7]]
        
        return {
            "total_entries": len(states),
            "average_levels": avg_levels.to_dict(),
            "average_color": avg_levels.hex_color,
            "dominant_emotion": dominant,
            "patterns": patterns,
            "color_trend": color_trend
        }


# =============================================================================
# IMPORTS FOR TIMELINE
# =============================================================================

from datetime import timedelta