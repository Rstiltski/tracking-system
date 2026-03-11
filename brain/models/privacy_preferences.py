"""
Privacy Preferences Model - Consent Management

Implements granular consent management for data privacy compliance:
- Data category definitions (required vs optional)
- Consent tracking (opt-in per category)
- Consent history (when granted/withdrawn)
- Data retention policies

Based on Task 11.1.2 from PHASE_11_INTEGRATION_ROADMAP.md

Legal Requirements:
- 2025 state privacy law compliance
- Data minimization by default
- No dark patterns
- Transparent consent management
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import json


# =============================================================================
# DATA CATEGORY DEFINITIONS
# =============================================================================

class DataCategory(str, Enum):
    """Categories of data collected by the system."""
    HABITS = "habits"
    TASKS = "tasks"
    FINANCES = "finances"
    HEALTH = "health"
    EMOTIONAL = "emotional"
    TIME = "time"
    GOALS = "goals"
    ACHIEVEMENTS = "achievements"
    ANALYTICS = "analytics"  # Usage analytics
    IMPROVEMENT = "improvement"  # AI-generated suggestions


class DataSensitivity(str, Enum):
    """Sensitivity level of data categories."""
    REQUIRED = "required"    # Data required for core functionality
    OPTIONAL = "optional"   # Data user can opt out of
    SENSITIVE = "sensitive" # Highly sensitive (health, emotional, finances)


# Define data categories with their properties
DATA_CATEGORIES: Dict[DataCategory, Dict] = {
    DataCategory.HABITS: {
        "name": "Habit Tracking",
        "description": "Your daily habit completions and streaks",
        "sensitivity": DataSensitivity.REQUIRED,
        "required_for": "Core tracking functionality",
    },
    DataCategory.TASKS: {
        "name": "Task Management",
        "description": "Your todo lists and task completions",
        "sensitivity": DataSensitivity.REQUIRED,
        "required_for": "Task management functionality",
    },
    DataCategory.FINANCES: {
        "name": "Financial Data",
        "description": "Income, expenses, and budget information",
        "sensitivity": DataSensitivity.SENSITIVE,
        "required_for": "Financial tracking features",
    },
    DataCategory.HEALTH: {
        "name": "Health Metrics",
        "description": "Health measurements and metrics",
        "sensitivity": DataSensitivity.SENSITIVE,
        "required_for": "Health tracking features",
    },
    DataCategory.EMOTIONAL: {
        "name": "Emotional State",
        "description": "Mood tracking and emotional assessments",
        "sensitivity": DataSensitivity.SENSITIVE,
        "required_for": "Emotional health features",
    },
    DataCategory.TIME: {
        "name": "Time Tracking",
        "description": "Time logs and productivity data",
        "sensitivity": DataSensitivity.OPTIONAL,
        "required_for": "Time tracking features",
    },
    DataCategory.GOALS: {
        "name": "Goals",
        "description": "Your goals and progress",
        "sensitivity": DataSensitivity.REQUIRED,
        "required_for": "Goal tracking features",
    },
    DataCategory.ACHIEVEMENTS: {
        "name": "Achievements",
        "description": "XP, levels, badges, and gamification data",
        "sensitivity": DataSensitivity.OPTIONAL,
        "required_for": "Gamification features",
    },
    DataCategory.ANALYTICS: {
        "name": "Usage Analytics",
        "description": "Anonymous usage patterns to improve the app",
        "sensitivity": DataSensitivity.OPTIONAL,
        "required_for": "App improvement (anonymous)",
    },
    DataCategory.IMPROVEMENT: {
        "name": "AI Suggestions",
        "description": "AI-generated habit suggestions and insights",
        "sensitivity": DataSensitivity.OPTIONAL,
        "required_for": "Personalized recommendations",
    },
}


# =============================================================================
# CONSENT STATUS
# =============================================================================

class ConsentStatus(str, Enum):
    """Status of consent for a data category."""
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"  # Awaiting user decision


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ConsentRecord:
    """
    Record of consent for a specific data category.
    
    Attributes:
        category: The data category
        status: Current consent status
        granted_at: When consent was granted
        withdrawn_at: When consent was withdrawn (if applicable)
        reason: Optional reason for withdrawal
    """
    category: DataCategory
    status: ConsentStatus
    granted_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    reason: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "category": self.category.value,
            "status": self.status.value,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "withdrawn_at": self.withdrawn_at.isoformat() if self.withdrawn_at else None,
            "reason": self.reason,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ConsentRecord":
        """Create instance from dictionary."""
        return cls(
            category=DataCategory(data["category"]),
            status=ConsentStatus(data["status"]),
            granted_at=datetime.fromisoformat(data["granted_at"]) if data.get("granted_at") else None,
            withdrawn_at=datetime.fromisoformat(data["withdrawn_at"]) if data.get("withdrawn_at") else None,
            reason=data.get("reason", ""),
        )


@dataclass
class PrivacyPreferences:
    """
    User's privacy preferences and consent management.
    
    Attributes:
        user_id: The user this belongs to
        consents: Map of category to consent record
        last_review: Last time privacy settings were reviewed
        data_retention_days: How long to keep data (0 = forever)
    """
    user_id: str = ""
    consents: Dict[DataCategory, ConsentRecord] = field(default_factory=dict)
    last_review: Optional[date] = None
    data_retention_days: int = 0  # 0 = keep forever
    
    def __post_init__(self):
        """Initialize default consents."""
        if not self.consents:
            # Default: required categories granted, optional pending
            for category, info in DATA_CATEGORIES.items():
                if info["sensitivity"] == DataSensitivity.REQUIRED:
                    self.consents[category] = ConsentRecord(
                        category=category,
                        status=ConsentStatus.GRANTED,
                        granted_at=datetime.now()
                    )
                else:
                    self.consents[category] = ConsentRecord(
                        category=category,
                        status=ConsentStatus.PENDING
                    )
    
    def grant_consent(self, category: DataCategory, reason: str = "") -> bool:
        """
        Grant consent for a data category.
        
        Args:
            category: The category to grant consent for
            reason: Optional reason/notes
            
        Returns:
            True if consent was granted successfully
        """
        if category not in self.consents:
            self.consents[category] = ConsentRecord(
                category=category,
                status=ConsentStatus.PENDING
            )
        
        record = self.consents[category]
        record.status = ConsentStatus.GRANTED
        record.granted_at = datetime.now()
        record.withdrawn_at = None
        record.reason = reason
        
        return True
    
    def withdraw_consent(self, category: DataCategory, reason: str = "") -> bool:
        """
        Withdraw consent for a data category.
        
        Args:
            category: The category to withdraw consent from
            reason: Optional reason for withdrawal
            
        Returns:
            True if consent was withdrawn successfully
        """
        if category not in self.consents:
            return False
        
        # Check if this is a required category
        if DATA_CATEGORIES[category]["sensitivity"] == DataSensitivity.REQUIRED:
            return False  # Cannot withdraw consent for required data
        
        record = self.consents[category]
        record.status = ConsentStatus.WITHDRAWN
        record.withdrawn_at = datetime.now()
        record.reason = reason
        
        return True
    
    def is_consent_granted(self, category: DataCategory) -> bool:
        """Check if consent is granted for a category."""
        if category not in self.consents:
            return DATA_CATEGORIES[category]["sensitivity"] == DataSensitivity.REQUIRED
        return self.consents[category].status == ConsentStatus.GRANTED
    
    def get_consent_record(self, category: DataCategory) -> ConsentRecord:
        """Get consent record for a category."""
        if category not in self.consents:
            self.consents[category] = ConsentRecord(
                category=category,
                status=ConsentStatus.PENDING
            )
        return self.consents[category]
    
    def get_categories_by_status(self, status: ConsentStatus) -> List[DataCategory]:
        """Get all categories with a specific consent status."""
        return [
            cat for cat, record in self.consents.items()
            if record.status == status
        ]
    
    def get_required_categories(self) -> List[DataCategory]:
        """Get all required data categories."""
        return [
            cat for cat, info in DATA_CATEGORIES.items()
            if info["sensitivity"] == DataSensitivity.REQUIRED
        ]
    
    def get_optional_categories(self) -> List[DataCategory]:
        """Get all optional data categories."""
        return [
            cat for cat, info in DATA_CATEGORIES.items()
            if info["sensitivity"] in [DataSensitivity.OPTIONAL, DataSensitivity.SENSITIVE]
        ]
    
    def get_pending_categories(self) -> List[DataCategory]:
        """Get all categories awaiting consent decision."""
        return self.get_categories_by_status(ConsentStatus.PENDING)
    
    def mark_reviewed(self) -> None:
        """Mark that user has reviewed privacy settings."""
        self.last_review = date.today()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "user_id": self.user_id,
            "consents": {
                cat.value: record.to_dict()
                for cat, record in self.consents.items()
            },
            "last_review": self.last_review.isoformat() if self.last_review else None,
            "data_retention_days": self.data_retention_days,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "PrivacyPreferences":
        """Create instance from dictionary."""
        prefs = cls(
            user_id=data.get("user_id", ""),
            last_review=date.fromisoformat(data["last_review"]) if data.get("last_review") else None,
            data_retention_days=data.get("data_retention_days", 0),
        )
        prefs.consents = {
            DataCategory(cat): ConsentRecord.from_dict(record)
            for cat, record in data.get("consents", {}).items()
        }
        return prefs


# =============================================================================
# PRIVACY DASHBOARD HELPERS
# =============================================================================

def get_category_info(category: DataCategory) -> Dict:
    """Get full info for a data category."""
    base_info = DATA_CATEGORIES.get(category, {})
    return {
        **base_info,
        "category": category,
    }


def calculate_privacy_score(prefs: PrivacyPreferences) -> float:
    """
    Calculate a privacy score based on user settings.
    
    Returns:
        Score from 0.0 to 1.0 (1.0 = most private)
    """
    if not prefs.consents:
        return 0.5
    
    total = len(DATA_CATEGORIES)
    granted = sum(1 for cat in prefs.consents if prefs.is_consent_granted(cat))
    
    return 1.0 - (granted / total)


def should_show_quarterly_review(prefs: PrivacyPreferences) -> bool:
    """
    Check if it's time for a quarterly privacy review.
    
    Returns:
        True if review is due (90+ days since last review)
    """
    if prefs.last_review is None:
        return True
    
    days_since_review = (date.today() - prefs.last_review).days
    return days_since_review >= 90


# =============================================================================
# FACTORY
# =============================================================================

def create_privacy_preferences(user_id: str) -> PrivacyPreferences:
    """Factory function to create new privacy preferences."""
    return PrivacyPreferences(user_id=user_id)
