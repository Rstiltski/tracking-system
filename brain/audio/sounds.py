"""
Sound Effect Definitions

Phase 7.3: Defines all sound effects for the tracking system.
Uses Web Audio API for browser-based sound generation.

Sound Categories:
- Habit sounds: Completion, streak, missed
- Achievement sounds: Unlock, level up
- Task sounds: Complete, overdue
- System sounds: Notification, error, success
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class SoundEffect(Enum):
    """All available sound effects."""
    
    # Habit sounds
    HABIT_COMPLETE = "habit_complete"
    HABIT_MISSED = "habit_missed"
    STREAK_CONTINUE = "streak_continue"
    STREAK_BREAK = "streak_break"
    
    # Achievement sounds
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    LEVEL_UP = "level_up"
    MILESTONE_REACHED = "milestone_reached"
    
    # Task sounds
    TASK_COMPLETE = "task_complete"
    TASK_OVERDUE = "task_overdue"
    
    # System sounds
    NOTIFICATION = "notification"
    SUCCESS = "success"
    ERROR = "error"
    CLICK = "click"
    POP = "pop"


@dataclass
class SoundDefinition:
    """
    Definition of a sound effect.
    
    For Web Audio API, we define the sound as a combination of:
    - Frequency (or frequencies for chords)
    - Waveform type (sine, square, triangle, sawtooth)
    - Duration
    - Envelope (attack, decay, sustain, release)
    """
    id: str
    name: str
    category: str
    description: str
    
    # Web Audio API parameters
    frequencies: list  # List of frequencies in Hz
    waveform: str = "sine"  # sine, square, triangle, sawtooth
    duration: float = 0.2  # Duration in seconds
    
    # Envelope (ADSR)
    attack: float = 0.01  # Attack time
    decay: float = 0.1  # Decay time
    sustain: float = 0.5  # Sustain level (0-1)
    release: float = 0.1  # Release time
    
    # Volume adjustment
    volume: float = 1.0  # Volume multiplier (0-1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "frequencies": self.frequencies,
            "waveform": self.waveform,
            "duration": self.duration,
            "attack": self.attack,
            "decay": self.decay,
            "sustain": self.sustain,
            "release": self.release,
            "volume": self.volume,
        }


class SoundLibrary:
    """
    Library of all sound effect definitions.
    
    Provides pre-defined sounds using Web Audio API synthesis.
    No external audio files required.
    """
    
    # Sound definitions using synthesized audio parameters
    SOUNDS: Dict[SoundEffect, SoundDefinition] = {
        # Habit completion - pleasant "ding"
        SoundEffect.HABIT_COMPLETE: SoundDefinition(
            id="habit_complete",
            name="Habit Complete",
            category="habits",
            description="Satisfying ding for habit completion",
            frequencies=[523.25, 659.25, 783.99],  # C5, E5, G5 chord
            waveform="sine",
            duration=0.3,
            attack=0.01,
            decay=0.1,
            sustain=0.3,
            release=0.15,
            volume=0.6,
        ),
        
        # Habit missed - soft descending tone
        SoundEffect.HABIT_MISSED: SoundDefinition(
            id="habit_missed",
            name="Habit Missed",
            category="habits",
            description="Soft descending tone for missed habit",
            frequencies=[392.00, 349.23],  # G4 to F4
            waveform="triangle",
            duration=0.4,
            attack=0.05,
            decay=0.15,
            sustain=0.2,
            release=0.2,
            volume=0.4,
        ),
        
        # Streak continue - ascending arpeggio
        SoundEffect.STREAK_CONTINUE: SoundDefinition(
            id="streak_continue",
            name="Streak Continue",
            category="habits",
            description="Ascending arpeggio for streak continuation",
            frequencies=[261.63, 329.63, 392.00, 523.25],  # C4, E4, G4, C5
            waveform="sine",
            duration=0.5,
            attack=0.01,
            decay=0.1,
            sustain=0.4,
            release=0.2,
            volume=0.5,
        ),
        
        # Streak break - warning sound
        SoundEffect.STREAK_BREAK: SoundDefinition(
            id="streak_break",
            name="Streak Break",
            category="habits",
            description="Warning sound for broken streak",
            frequencies=[220.00, 196.00, 174.61],  # A3, G3, F3 descending
            waveform="sawtooth",
            duration=0.5,
            attack=0.05,
            decay=0.1,
            sustain=0.3,
            release=0.3,
            volume=0.4,
        ),
        
        # Achievement unlock - triumphant fanfare
        SoundEffect.ACHIEVEMENT_UNLOCK: SoundDefinition(
            id="achievement_unlock",
            name="Achievement Unlock",
            category="achievements",
            description="Triumphant fanfare for achievement unlock",
            frequencies=[392.00, 493.88, 587.33, 783.99],  # G4, B4, D5, G5
            waveform="sine",
            duration=0.8,
            attack=0.02,
            decay=0.15,
            sustain=0.5,
            release=0.3,
            volume=0.7,
        ),
        
        # Level up - celebratory sound
        SoundEffect.LEVEL_UP: SoundDefinition(
            id="level_up",
            name="Level Up",
            category="achievements",
            description="Celebratory sound for level up",
            frequencies=[523.25, 659.25, 783.99, 1046.50],  # C5, E5, G5, C6
            waveform="sine",
            duration=1.0,
            attack=0.01,
            decay=0.1,
            sustain=0.6,
            release=0.4,
            volume=0.8,
        ),
        
        # Milestone reached - grand fanfare
        SoundEffect.MILESTONE_REACHED: SoundDefinition(
            id="milestone_reached",
            name="Milestone Reached",
            category="achievements",
            description="Grand fanfare for milestone achievements",
            frequencies=[261.63, 329.63, 392.00, 523.25, 659.25, 783.99],
            waveform="sine",
            duration=1.2,
            attack=0.02,
            decay=0.15,
            sustain=0.6,
            release=0.5,
            volume=0.8,
        ),
        
        # Task complete - quick click
        SoundEffect.TASK_COMPLETE: SoundDefinition(
            id="task_complete",
            name="Task Complete",
            category="tasks",
            description="Quick click for task completion",
            frequencies=[880.00],  # A5
            waveform="sine",
            duration=0.1,
            attack=0.005,
            decay=0.05,
            sustain=0.3,
            release=0.05,
            volume=0.4,
        ),
        
        # Task overdue - warning beep
        SoundEffect.TASK_OVERDUE: SoundDefinition(
            id="task_overdue",
            name="Task Overdue",
            category="tasks",
            description="Warning beep for overdue task",
            frequencies=[440.00, 440.00],  # Double beep
            waveform="square",
            duration=0.3,
            attack=0.01,
            decay=0.05,
            sustain=0.5,
            release=0.1,
            volume=0.3,
        ),
        
        # Notification - gentle ping
        SoundEffect.NOTIFICATION: SoundDefinition(
            id="notification",
            name="Notification",
            category="system",
            description="Gentle ping for notifications",
            frequencies=[587.33, 880.00],  # D5, A5
            waveform="sine",
            duration=0.25,
            attack=0.01,
            decay=0.1,
            sustain=0.4,
            release=0.1,
            volume=0.5,
        ),
        
        # Success - confirmation sound
        SoundEffect.SUCCESS: SoundDefinition(
            id="success",
            name="Success",
            category="system",
            description="Confirmation sound for successful action",
            frequencies=[523.25, 659.25],  # C5, E5
            waveform="sine",
            duration=0.2,
            attack=0.01,
            decay=0.08,
            sustain=0.5,
            release=0.1,
            volume=0.5,
        ),
        
        # Error - error sound
        SoundEffect.ERROR: SoundDefinition(
            id="error",
            name="Error",
            category="system",
            description="Error sound for failed action",
            frequencies=[196.00, 185.00],  # Dissonant
            waveform="sawtooth",
            duration=0.3,
            attack=0.02,
            decay=0.1,
            sustain=0.3,
            release=0.15,
            volume=0.4,
        ),
        
        # Click - UI click
        SoundEffect.CLICK: SoundDefinition(
            id="click",
            name="Click",
            category="system",
            description="UI click sound",
            frequencies=[1000.00],
            waveform="sine",
            duration=0.05,
            attack=0.001,
            decay=0.02,
            sustain=0.2,
            release=0.03,
            volume=0.3,
        ),
        
        # Pop - UI pop
        SoundEffect.POP: SoundDefinition(
            id="pop",
            name="Pop",
            category="system",
            description="UI pop sound",
            frequencies=[600.00, 800.00],
            waveform="sine",
            duration=0.08,
            attack=0.005,
            decay=0.03,
            sustain=0.3,
            release=0.05,
            volume=0.35,
        ),
    }
    
    @classmethod
    def get(cls, effect: SoundEffect) -> Optional[SoundDefinition]:
        """Get a sound definition by effect type."""
        return cls.SOUNDS.get(effect)
    
    @classmethod
    def get_by_category(cls, category: str) -> list:
        """Get all sounds in a category."""
        return [s for s in cls.SOUNDS.values() if s.category == category]
    
    @classmethod
    def list_all(cls) -> list:
        """List all available sounds."""
        return list(cls.SOUNDS.values())


# Default sound assignments for common actions
DEFAULT_SOUND_MAP = {
    "habit_complete": SoundEffect.HABIT_COMPLETE,
    "achievement_unlock": SoundEffect.ACHIEVEMENT_UNLOCK,
    "level_up": SoundEffect.LEVEL_UP,
    "task_complete": SoundEffect.TASK_COMPLETE,
    "streak_milestone": SoundEffect.STREAK_CONTINUE,
    "error": SoundEffect.ERROR,
    "success": SoundEffect.SUCCESS,
    "notification": SoundEffect.NOTIFICATION,
}


__all__ = [
    "SoundEffect",
    "SoundDefinition",
    "SoundLibrary",
    "DEFAULT_SOUND_MAP",
]