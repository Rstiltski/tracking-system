"""
Phase 3b: The Digital Amygdala - Chroma-Density Engine

Visualizes binary system health as emotional color.
Input: Binary Events (1/0)
Output: Emotional State + Color Codes

Usage:
    engine = ChromaEmotionEngine(nervous_system)
    state = engine.get_current_state()
    print(state.get_console_display())
"""

from dataclasses import dataclass, field
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

# Configuration
MEMORY_SIZE_BITS = 64


class EmotionState(str, Enum):
    """Emotional states based on signal density"""
    EUPHORIC = "EUPHORIC"
    OPTIMISTIC = "OPTIMISTIC"
    STABLE = "STABLE"
    STRESSED = "STRESSED"
    ANXIOUS = "ANXIOUS"
    DESPAIR = "DESPAIR"


# Maps System Events to Binary Signals
# 1 = Dopamine (Success), 0 = Cortisol (Stress)
BINARY_MAP = {
    # Good (1) - Dopamine events
    "JOB_COMPLETED": 1,
    "JOB_CREATED": 1,
    "INVOICE_PAID": 1,
    "INVOICE_SENT": 1,
    "PAYMENT_RECORDED": 1,
    "PAYMENT_CLEARED": 1,
    "CUSTOMER_CREATED": 1,
    "QUOTE_ACCEPTED": 1,
    "HABIT_COMPLETED": 1,
    "STREAK_MAINTAINED": 1,
    "GOAL_ACHIEVED": 1,
    "TASK_COMPLETED": 1,
    "SYSTEM_GREEN": 1,
    "ACHIEVEMENT_UNLOCKED": 1,
    "LEVEL_UP": 1,
    
    # Bad (0) - Cortisol events
    "JOB_CANCELLED": 0,
    "JOB_DELAYED": 0,
    "SYSTEM_ERROR": 0,
    "STREAK_BROKEN": 0,
    "PAYMENT_FAILED": 0,
    "PAYMENT_REFUNDED": 0,
    "INVOICE_VOIDED": 0,
    "QUOTE_DECLINED": 0,
    "BURNOUT_RISK_HIGH": 0,
    "SECURITY_ALERT": 0,
    "INVARIANT_VIOLATED": 0,
    "TASK_OVERDUE": 0,
    "GOAL_MISSED": 0,
}


@dataclass
class EmotionalState:
    """Represents the current emotional state of the system"""
    name: str              # e.g., "EUPHORIC"
    density: float         # 0.0 to 1.0
    hex_color: str         # Web format: "#39FF14"
    ansi_color: str        # Terminal format: "\033[92m"
    bitstream: str         # Visual representation of bits
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_console_display(self) -> str:
        """Returns a colored ASCII bar for the terminal."""
        bar_len = 20
        fill = int(self.density * bar_len)
        bar = "█" * fill + "░" * (bar_len - fill)
        reset = "\033[0m"
        return f"{self.ansi_color}[{self.name:<10}] {bar} {int(self.density*100)}%{reset}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "name": self.name,
            "density": round(self.density, 4),
            "hex_color": self.hex_color,
            "ansi_color": self.ansi_color,
            "bitstream": self.bitstream,
            "timestamp": self.timestamp.isoformat(),
            "percentage": int(self.density * 100)
        }


class ChromaEmotionEngine:
    """
    The Digital Amygdala - Tracks system health as emotional color.
    
    This engine maintains a rolling window of binary signals (1s and 0s)
    representing success/failure events. The density of 1s determines
    the system's emotional state, which is mapped to a color.
    
    Features:
    - Rolling bitstream window (default 64 events)
    - Automatic event subscription via NervousSystem
    - Color mapping for both UI (hex) and CLI (ANSI)
    - Visual bitstream representation
    """
    
    def __init__(self, nervous_system=None):
        """
        Initialize the Chroma Emotion Engine.
        
        Args:
            nervous_system: Optional NervousSystem instance for event subscription
        """
        self.ns = nervous_system
        # Start "Stable" (50/50 mix)
        self._bitstream = deque(
            [1, 0] * (MEMORY_SIZE_BITS // 2), 
            maxlen=MEMORY_SIZE_BITS
        )
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 100
        
        if self.ns:
            self._register_listeners()
    
    def _register_listeners(self):
        """Register event listeners with the NervousSystem"""
        for event_name in BINARY_MAP.keys():
            try:
                # Try to subscribe via NervousSystem
                self.ns.subscribe(
                    event_name, 
                    self._process_event, 
                    brain_name="EmotionEngine"
                )
            except Exception:
                pass  # Event might not exist in enum yet
    
    def _process_event(self, event):
        """
        Process an incoming event and update the bitstream.
        
        Args:
            event: The event to process (IEvent or Event type)
        """
        # Extract event type string
        if hasattr(event, 'event_type'):
            if isinstance(event.event_type, str):
                event_type = event.event_type
            else:
                event_type = event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)
        else:
            event_type = str(event)
        
        # Get binary signal
        signal = BINARY_MAP.get(event_type)
        if signal is not None:
            self._bitstream.append(signal)
            
            # Record in history
            self._event_history.append({
                "event_type": event_type,
                "signal": signal,
                "timestamp": datetime.now().isoformat()
            })
            
            # Trim history
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]
    
    def process_event_type(self, event_type: str) -> Optional[int]:
        """
        Process an event type string directly.
        
        Args:
            event_type: The event type string (e.g., "JOB_COMPLETED")
            
        Returns:
            The binary signal (1 or 0) or None if not mapped
        """
        signal = BINARY_MAP.get(event_type)
        if signal is not None:
            self._bitstream.append(signal)
        return signal
    
    def get_current_state(self) -> EmotionalState:
        """
        Calculate and return the current emotional state.
        
        Returns:
            EmotionalState with name, density, colors, and bitstream
        """
        density = sum(self._bitstream) / len(self._bitstream) if self._bitstream else 0.5
        
        # Color Logic based on density thresholds
        if density >= 0.90:
            name, hex_c, ansi = "EUPHORIC", "#39FF14", "\033[92m"  # Bright Green
        elif density >= 0.75:
            name, hex_c, ansi = "OPTIMISTIC", "#00FFFF", "\033[96m"  # Cyan
        elif density >= 0.50:
            name, hex_c, ansi = "STABLE", "#4D4DFF", "\033[94m"  # Blue
        elif density >= 0.30:
            name, hex_c, ansi = "STRESSED", "#FFFF00", "\033[93m"  # Yellow
        elif density >= 0.15:
            name, hex_c, ansi = "ANXIOUS", "#FF9900", "\033[31m"  # Red (Standard)
        else:
            name, hex_c, ansi = "DESPAIR", "#FF0000", "\033[41;97m"  # Red Background

        # Visualize bits: Green 1s, Red 0s
        visual_bits = ""
        for b in list(self._bitstream)[-16:]:  # Show last 16
            color = "\033[92m" if b == 1 else "\033[91m"
            visual_bits += f"{color}{b}\033[0m"

        return EmotionalState(
            name=name,
            density=density,
            hex_color=hex_c,
            ansi_color=ansi,
            bitstream=visual_bits
        )
    
    def get_density(self) -> float:
        """Get the current signal density (0.0 to 1.0)"""
        if not self._bitstream:
            return 0.5
        return sum(self._bitstream) / len(self._bitstream)
    
    def get_bitstream_list(self) -> List[int]:
        """Get the bitstream as a list of integers"""
        return list(self._bitstream)
    
    def force_state(self, num_ones: int, num_zeros: int):
        """
        Force a specific state by setting the bitstream directly.
        Useful for testing or manual overrides.
        
        Args:
            num_ones: Number of 1s (success signals)
            num_zeros: Number of 0s (failure signals)
        """
        total = num_ones + num_zeros
        if total > MEMORY_SIZE_BITS:
            # Scale down proportionally
            scale = MEMORY_SIZE_BITS / total
            num_ones = int(num_ones * scale)
            num_zeros = MEMORY_SIZE_BITS - num_ones
        
        self._bitstream = deque(
            [1] * num_ones + [0] * num_zeros,
            maxlen=MEMORY_SIZE_BITS
        )
    
    def add_success(self, count: int = 1):
        """Add success signals (1s) to the bitstream"""
        for _ in range(count):
            self._bitstream.append(1)
    
    def add_failure(self, count: int = 1):
        """Add failure signals (0s) to the bitstream"""
        for _ in range(count):
            self._bitstream.append(0)
    
    def get_event_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent event history"""
        return self._event_history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        state = self.get_current_state()
        bitstream = list(self._bitstream)
        
        return {
            "state": state.to_dict(),
            "total_events": len(self._event_history),
            "bitstream_length": len(bitstream),
            "ones_count": sum(bitstream),
            "zeros_count": len(bitstream) - sum(bitstream),
            "recent_events": self.get_event_history(10)
        }


# Singleton instance for global access
_emotion_engine: Optional[ChromaEmotionEngine] = None


def get_emotion_engine(nervous_system=None) -> ChromaEmotionEngine:
    """
    Get the global ChromaEmotionEngine instance.
    
    Args:
        nervous_system: Optional NervousSystem for first initialization
        
    Returns:
        ChromaEmotionEngine singleton instance
    """
    global _emotion_engine
    if _emotion_engine is None:
        _emotion_engine = ChromaEmotionEngine(nervous_system)
    return _emotion_engine


def reset_emotion_engine():
    """Reset the global emotion engine (for testing)"""
    global _emotion_engine
    _emotion_engine = None


# --- Test ---
if __name__ == "__main__":
    # Simulate usage
    class MockNS:
        def subscribe(self, *a, **k):
            pass
    
    eng = ChromaEmotionEngine(MockNS())
    
    # Force Mood Swings
    print("\n--- EMOTION TEST ---")
    
    eng._bitstream = deque([1]*60 + [0]*4, maxlen=64)  # Mostly 1s
    print(eng.get_current_state().get_console_display())
    
    eng._bitstream = deque([1]*32 + [0]*32, maxlen=64)  # 50/50
    print(eng.get_current_state().get_console_display())
    
    eng._bitstream = deque([0]*60 + [1]*4, maxlen=64)  # Mostly 0s
    print(eng.get_current_state().get_console_display())
    
    # Test all states
    print("\n--- ALL STATES ---")
    for density, label in [(0.95, "EUPHORIC"), (0.80, "OPTIMISTIC"), (0.60, "STABLE"), 
                           (0.40, "STRESSED"), (0.20, "ANXIOUS"), (0.05, "DESPAIR")]:
        ones = int(density * 64)
        zeros = 64 - ones
        eng._bitstream = deque([1]*ones + [0]*zeros, maxlen=64)
        state = eng.get_current_state()
        print(f"{label}: {state.get_console_display()}")