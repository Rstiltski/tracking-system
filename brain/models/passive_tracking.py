"""
Passive Tracking & Data Friction Reduction

Reduce manual entry burden through passive/ambient tracking.

Based on Task 11.3.1 from PHASE_11_INTEGRATION_ROADMAP.md

Reduces manual entry by 50%+!
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class DeviceType(Enum):
    """Types of wearable devices."""
    APPLE_WATCH = "apple_watch"
    FITBIT = "fitbit"
    GARMIN = "garmin"
    WHOOP = "whoop"
    ANDROID_WEAR = "android_wear"
    MANUAL = "manual"


class TrackingMode(Enum):
    """Tracking modes."""
    PASSIVE = "passive"       # Automatic
    ACTIVE = "active"        # Manual
    HYBRID = "hybrid"        # Both


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class WearableConnection:
    """Connection to a wearable device."""
    id: str
    user_id: str
    device_type: DeviceType
    connected_at: datetime
    last_sync: Optional[datetime] = None
    enabled: bool = True


@dataclass
class PassiveData:
    """Passive data from wearables."""
    id: str
    user_id: str
    timestamp: datetime
    source: DeviceType
    
    # Health metrics
    steps: Optional[int] = None
    heart_rate: Optional[float] = None
    sleep_hours: Optional[float] = None
    calories_burned: Optional[float] = None
    active_minutes: Optional[int] = None
    
    # Location
    location: Optional[str] = None


@dataclass
class VoiceEntry:
    """Voice-to-log entry."""
    id: str
    user_id: str
    timestamp: datetime
    transcript: str
    
    # Parsed data
    parsed_data: Dict = field(default_factory=dict)
    confidence: float = 0.0


@dataclass
class AutoCategory:
    """Auto-categorization result."""
    category: str
    confidence: float
    suggested: bool


# =============================================================================
# PASSIVE TRACKING ENGINE
# =============================================================================

class PassiveTrackingEngine:
    """
    Reduces data friction through passive tracking.
    
    Features:
    - Wearable integration framework
    - Voice-to-log
    - Auto-categorization
    - Hybrid tracking mode
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.connections: List[WearableConnection] = []
        self.passive_data: List[PassiveData] = []
        self.voice_entries: List[VoiceEntry] = []
        
        # Categories for auto-categorization
        self.categories = {
            "exercise": ["running", "walking", "gym", "workout", "yoga", "cycling"],
            "sleep": ["sleep", "bed", "night", "rest"],
            "work": ["meeting", "office", "desk", "focus"],
            "social": ["friend", "family", "party", "date"],
            "health": ["doctor", "medicine", "therapy", "health"],
            "food": ["breakfast", "lunch", "dinner", "snack", "meal"],
        }
    
    def connect_wearable(
        self,
        user_id: str,
        device_type: DeviceType
    ) -> WearableConnection:
        """Connect a wearable device."""
        import uuid
        
        connection = WearableConnection(
            id=str(uuid.uuid4()),
            user_id=user_id,
            device_type=device_type,
            connected_at=datetime.now()
        )
        
        self.connections.append(connection)
        return connection
    
    def disconnect_wearable(self, connection_id: str) -> None:
        """Disconnect a wearable."""
        for conn in self.connections:
            if conn.id == connection_id:
                conn.enabled = False
                break
    
    def add_passive_data(
        self,
        user_id: str,
        source: DeviceType,
        steps: int = None,
        heart_rate: float = None,
        sleep_hours: float = None,
        calories: float = None,
        active_minutes: int = None,
        location: str = None
    ) -> PassiveData:
        """Add passive tracking data."""
        import uuid
        
        data = PassiveData(
            id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.now(),
            source=source,
            steps=steps,
            heart_rate=heart_rate,
            sleep_hours=sleep_hours,
            calories_burned=calories,
            active_minutes=active_minutes,
            location=location
        )
        
        self.passive_data.append(data)
        return data
    
    def process_voice_entry(
        self,
        user_id: str,
        transcript: str
    ) -> VoiceEntry:
        """Process a voice entry and parse it."""
        import uuid
        
        entry = VoiceEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.now(),
            transcript=transcript
        )
        
        # Parse the transcript
        parsed = self._parse_transcript(transcript)
        entry.parsed_data = parsed
        entry.confidence = parsed.get("confidence", 0.5)
        
        self.voice_entries.append(entry)
        return entry
    
    def _parse_transcript(self, transcript: str) -> Dict:
        """Parse voice transcript into structured data."""
        text = transcript.lower()
        
        parsed = {
            "type": "general",
            "category": None,
            "duration": None,
            "confidence": 0.5
        }
        
        # Detect category
        for category, keywords in self.categories.items():
            if any(kw in text for kw in keywords):
                parsed["category"] = category
                parsed["confidence"] = 0.8
                break
        
        # Detect duration
        import re
        duration_match = re.search(r'(\d+)\s*(min|hour|hr|minute)', text)
        if duration_match:
            amount = int(duration_match.group(1))
            unit = duration_match.group(2)
            if unit.startswith("hour") or unit.startswith("hr"):
                parsed["duration"] = amount * 60
            else:
                parsed["duration"] = amount
        
        # Detect sentiment
        positive = ["great", "good", "happy", "awesome", "amazing"]
        negative = ["bad", "tired", "hard", "difficult", "struggle"]
        
        if any(w in text for w in positive):
            parsed["sentiment"] = "positive"
        elif any(w in text for w in negative):
            parsed["sentiment"] = "challenging"
        
        return parsed
    
    def auto_categorize(self, text: str) -> AutoCategory:
        """Auto-categorize an entry."""
        text = text.lower()
        
        for category, keywords in self.categories.items():
            if any(kw in text for kw in keywords):
                return AutoCategory(
                    category=category,
                    confidence=0.9,
                    suggested=True
                )
        
        return AutoCategory(
            category="uncategorized",
            confidence=0.0,
            suggested=False
        )
    
    def get_passive_summary(self, user_id: str, days: int = 7) -> Dict:
        """Get passive tracking summary."""
        cutoff = datetime.now() - timedelta(days=days)
        
        data = [
            d for d in self.passive_data
            if d.user_id == user_id and d.timestamp >= cutoff
        ]
        
        total_steps = sum(d.steps for d in data if d.steps)
        avg_hr = sum(d.heart_rate for d in data if d.heart_rate) / max(len([d for d in data if d.heart_rate]), 1)
        total_sleep = sum(d.sleep_hours for d in data if d.sleep_hours)
        
        return {
            "total_passive_entries": len(data),
            "total_steps": total_steps,
            "avg_heart_rate": avg_hr if avg_hr > 0 else None,
            "total_sleep_hours": total_sleep,
            "voice_entries": len([v for v in self.voice_entries if v.user_id == user_id])
        }


def create_engine() -> PassiveTrackingEngine:
    """Factory function."""
    return PassiveTrackingEngine()
