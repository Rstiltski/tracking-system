"""
Energy Management System

Track energy, not just time. Schedule tasks to circadian peaks.

Based on Task 11.2.2 from PHASE_11_INTEGRATION_ROADMAP.md

PARADIGM SHIFT feature!
"""

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# ENERGY STATES
# =============================================================================

class EnergyLevel(Enum):
    """Energy levels throughout the day."""
    VERY_LOW = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    PEAK = 5


class EnergyType(Enum):
    """Types of energy."""
    PHYSICAL = "physical"      # Body energy
    MENTAL = "mental"          # Cognitive energy  
    EMOTIONAL = "emotional"    # Emotional state
    SPIRITUAL = "spiritual"    # Purpose/meaning


# Default circadian schedule (can be customized)
DEFAULT_CIRCADIAN_PATTERN = {
    # Hour -> Energy level
    5: EnergyLevel.LOW,
    6: EnergyLevel.LOW,
    7: EnergyLevel.MODERATE,
    8: EnergyLevel.HIGH,
    9: EnergyLevel.PEAK,
    10: EnergyLevel.PEAK,
    11: EnergyLevel.HIGH,
    12: EnergyLevel.MODERATE,
    13: EnergyLevel.LOW,
    14: EnergyLevel.MODERATE,
    15: EnergyLevel.HIGH,
    16: EnergyLevel.HIGH,
    17: EnergyLevel.MODERATE,
    18: EnergyLevel.LOW,
    19: EnergyLevel.LOW,
    20: EnergyLevel.MODERATE,
    21: EnergyLevel.LOW,
    22: EnergyLevel.VERY_LOW,
}


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class EnergyReading:
    """A single energy reading."""
    id: str
    timestamp: datetime
    energy_type: EnergyType
    level: EnergyLevel
    note: Optional[str] = None


@dataclass
class TaskEnergyMatch:
    """Match between task difficulty and energy level."""
    task_name: str
    required_energy: EnergyLevel
    recommended_time: Optional[time]
    reason: str


@dataclass
class CircadianProfile:
    """User's personalized circadian rhythm."""
    user_id: str
    wake_time: time = time(7, 0)
    peak_morning_start: time = time(9, 0)
    peak_morning_end: time = time(11, 0)
    afternoon_peak_start: time = time(14, 0)
    afternoon_peak_end: time = time(16, 0)
    wind_down_start: time = time(21, 0)
    sleep_time: time = time(22, 0)
    
    # Custom energy overrides
    custom_pattern: Dict[int, EnergyLevel] = field(default_factory=dict)
    
    def get_energy_at(self, hour: int) -> EnergyLevel:
        """Get energy level at specific hour."""
        # Check custom first
        if hour in self.custom_pattern:
            return self.custom_pattern[hour]
        
        # Fall back to default
        return DEFAULT_CIRCADIAN_PATTERN.get(hour, EnergyLevel.MODERATE)
    
    def get_peak_hours(self) -> List[int]:
        """Get list of peak energy hours."""
        hours = []
        for h in range(24):
            level = self.get_energy_at(h)
            if level in [EnergyLevel.PEAK, EnergyLevel.HIGH]:
                hours.append(h)
        return hours


# =============================================================================
# ENERGY TRACKING ENGINE
# =============================================================================

class EnergyManager:
    """
    Manages energy tracking and task scheduling.
    
    Features:
    - Energy level logging
    - Circadian profile management
    - Task-energy matching
    - Optimal scheduling suggestions
    """
    
    def __init__(self):
        """Initialize the manager."""
        self.readings: List[EnergyReading] = []
        self.profiles: Dict[str, CircadianProfile] = {}
    
    def get_or_create_profile(self, user_id: str) -> CircadianProfile:
        """Get or create circadian profile."""
        if user_id not in self.profiles:
            self.profiles[user_id] = CircadianProfile(user_id=user_id)
        return self.profiles[user_id]
    
    def log_energy(
        self,
        user_id: str,
        energy_type: EnergyType,
        level: EnergyLevel,
        note: Optional[str] = None
    ) -> EnergyReading:
        """Log an energy reading."""
        import uuid
        
        reading = EnergyReading(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            energy_type=energy_type,
            level=level,
            note=note
        )
        
        self.readings.append(reading)
        return reading
    
    def get_current_energy(self, user_id: str, energy_type: EnergyType) -> EnergyLevel:
        """Get estimated current energy based on circadian profile."""
        profile = self.get_or_create_profile(user_id)
        current_hour = datetime.now().hour
        return profile.get_energy_at(current_hour)
    
    def suggest_task_timing(
        self,
        task_name: str,
        required_energy: EnergyLevel,
        user_id: str
    ) -> TaskEnergyMatch:
        """Suggest optimal timing for a task."""
        profile = self.get_or_create_profile(user_id)
        
        # Find best hours for this energy level
        best_hours = []
        
        for h in range(24):
            level = profile.get_energy_at(h)
            if required_energy == EnergyLevel.VERY_LOW:
                if level in [EnergyLevel.VERY_LOW, EnergyLevel.LOW]:
                    best_hours.append(h)
            elif required_energy == EnergyLevel.LOW:
                if level in [EnergyLevel.LOW, EnergyLevel.MODERATE]:
                    best_hours.append(h)
            elif required_energy == EnergyLevel.MODERATE:
                if level in [EnergyLevel.MODERATE]:
                    best_hours.append(h)
            elif required_energy == EnergyLevel.HIGH:
                if level in [EnergyLevel.HIGH, EnergyLevel.PEAK]:
                    best_hours.append(h)
            elif required_energy == EnergyLevel.PEAK:
                if level == EnergyLevel.PEAK:
                    best_hours.append(h)
        
        if best_hours:
            suggested_time = time(best_hours[0], 0)
            reason = f"Energy peaks at {best_hours[0]}:00, matching {required_energy.name} requirement"
        else:
            suggested_time = None
            reason = "No optimal time found - try adjusting task difficulty"
        
        return TaskEnergyMatch(
            task_name=task_name,
            required_energy=required_energy,
            recommended_time=suggested_time,
            reason=reason
        )
    
    def get_energy_summary(self, user_id: str) -> Dict:
        """Get energy summary for the day."""
        profile = self.get_or_create_profile(user_id)
        
        # Get today's readings
        today_readings = [
            r for r in self.readings
            if r.timestamp.date() == datetime.now().date()
        ]
        
        # Current energy
        current = self.get_current_energy(user_id, EnergyType.PHYSICAL)
        
        # Peak hours
        peak_hours = profile.get_peak_hours()
        
        return {
            "current_energy": current.name,
            "readings_today": len(today_readings),
            "peak_hours": peak_hours,
            "next_peak": peak_hours[0] if peak_hours and peak_hours[0] > datetime.now().hour else (peak_hours[1] if len(peak_hours) > 1 else None),
            "profile": {
                "wake": profile.wake_time.strftime("%H:%M"),
                "sleep": profile.sleep_time.strftime("%H:%M"),
            }
        }
    
    def update_profile(
        self,
        user_id: str,
        wake_time: Optional[time] = None,
        sleep_time: Optional[time] = None,
        peak_morning_start: Optional[time] = None,
        peak_morning_end: Optional[time] = None
    ) -> CircadianProfile:
        """Update circadian profile."""
        profile = self.get_or_create_profile(user_id)
        
        if wake_time:
            profile.wake_time = wake_time
        if sleep_time:
            profile.sleep_time = sleep_time
        if peak_morning_start:
            profile.peak_morning_start = peak_morning_start
        if peak_morning_end:
            profile.peak_morning_end = peak_morning_end
        
        return profile


def create_manager() -> EnergyManager:
    """Factory function to create manager."""
    return EnergyManager()
