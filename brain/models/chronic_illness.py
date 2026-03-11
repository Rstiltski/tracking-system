"""
Chronic Illness Self-Advocacy Model

Support for chronic illness self-management and healthcare advocacy.

Based on Task 11.2.8 from PHASE_11_INTEGRATION_ROADMAP.md

Life-changing for chronic illness community!
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class SymptomCategory(Enum):
    """Categories of symptoms."""
    PAIN = "pain"
    FATIGUE = "fatigue"
    MOBILITY = "mobility"
    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"
    GASTROINTESTINAL = "gastrointestinal"
    SLEEP = "sleep"
    OTHER = "other"


class ProviderType(Enum):
    """Types of healthcare providers."""
    PRIMARY = "primary_care"
    SPECIALIST = "specialist"
    THERAPIST = "therapist"
    NATUROPATH = "naturopath"
    CHIROPRACTOR = "chiropractor"
    OTHER = "other"


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class SymptomEntry:
    """A symptom entry."""
    id: str
    user_id: str
    date: date
    category: SymptomCategory
    severity: int  # 1-10
    description: str
    triggers: List[str] = field(default_factory=list)
    relief: List[str] = field(default_factory=list)


@dataclass
class Provider:
    """A healthcare provider."""
    id: str
    name: str
    provider_type: ProviderType
    specialty: str
    phone: Optional[str] = None
    notes: str = ""


@dataclass
class Appointment:
    """A healthcare appointment."""
    id: str
    provider_id: str
    date: datetime
    reason: str
    notes: str = ""
    action_items: List[str] = field(default_factory=list)


@dataclass
class Question:
    """A question for healthcare provider."""
    id: str
    user_id: str
    question: str
    provider_id: Optional[str] = None
    answered: bool = False
    answer: Optional[str] = None


# =============================================================================
# CHRONIC ILLNESS ENGINE
# =============================================================================

class ChronicIllnessEngine:
    """
    Supports chronic illness self-management.
    
    Features:
    - Symptom tracking
    - Provider management
    - Appointment scheduling
    - Question tracking for providers
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.symptoms: List[SymptomEntry] = []
        self.providers: Dict[str, Provider] = {}
        self.appointments: List[Appointment] = []
        self.questions: List[Question] = []
    
    def log_symptom(
        self,
        user_id: str,
        category: SymptomCategory,
        severity: int,
        description: str,
        triggers: List[str] = None,
        relief: List[str] = None
    ) -> SymptomEntry:
        """Log a symptom entry."""
        import uuid
        
        entry = SymptomEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            date=date.today(),
            category=category,
            severity=severity,
            description=description,
            triggers=triggers or [],
            relief=relief or []
        )
        
        self.symptoms.append(entry)
        return entry
    
    def add_provider(
        self,
        name: str,
        provider_type: ProviderType,
        specialty: str,
        phone: Optional[str] = None,
        notes: str = ""
    ) -> Provider:
        """Add a healthcare provider."""
        import uuid
        
        provider = Provider(
            id=str(uuid.uuid4()),
            name=name,
            provider_type=provider_type,
            specialty=specialty,
            phone=phone,
            notes=notes
        )
        
        self.providers[provider.id] = provider
        return provider
    
    def add_appointment(
        self,
        provider_id: str,
        date: datetime,
        reason: str,
        notes: str = ""
    ) -> Appointment:
        """Add an appointment."""
        import uuid
        
        appointment = Appointment(
            id=str(uuid.uuid4()),
            provider_id=provider_id,
            date=date,
            reason=reason,
            notes=notes
        )
        
        self.appointments.append(appointment)
        return appointment
    
    def add_question(
        self,
        user_id: str,
        question: str,
        provider_id: Optional[str] = None
    ) -> Question:
        """Add a question for provider."""
        import uuid
        
        q = Question(
            id=str(uuid.uuid4()),
            user_id=user_id,
            question=question,
            provider_id=provider_id
        )
        
        self.questions.append(q)
        return q
    
    def answer_question(self, question_id: str, answer: str) -> None:
        """Answer a question."""
        for q in self.questions:
            if q.id == question_id:
                q.answered = True
                q.answer = answer
                break
    
    def get_symptom_summary(self, user_id: str, days: int = 30) -> Dict:
        """Get symptom summary."""
        from datetime import timedelta
        
        cutoff = date.today() - timedelta(days=days)
        
        entries = [
            e for e in self.symptoms
            if e.user_id == user_id and e.date >= cutoff
        ]
        
        # Category breakdown
        categories = {}
        for e in entries:
            cat = e.category.value
            categories[cat] = categories.get(cat, 0) + 1
        
        avg_severity = sum(e.severity for e in entries) / len(entries) if entries else 0
        
        return {
            "total_entries": len(entries),
            "categories": categories,
            "avg_severity": avg_severity,
            "severe_days": sum(1 for e in entries if e.severity >= 7)
        }
    
    def get_upcoming_appointments(self) -> List[Appointment]:
        """Get upcoming appointments."""
        now = datetime.now()
        return [
            a for a in self.appointments
            if a.date >= now
        ]


def create_engine() -> ChronicIllnessEngine:
    """Factory function."""
    return ChronicIllnessEngine()
