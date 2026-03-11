"""
Identity-Based Tracking Model

Track "who am I becoming?" not just "what did I do?"

Based on Task 11.2.1 from PHASE_11_INTEGRATION_ROADMAP.md

Highest differentiation feature!
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# IDENTITY TYPES
# =============================================================================

class IdentityType(Enum):
    """Types of possible selves."""
    CURRENT = "current"        # Who I am now
    IDEAL = "ideal"           # Who I want to become
    FEARED = "feared"         # Who I fear becoming


# Predefined identity dimensions
IDENTITY_DIMENSIONS = [
    "Health & Fitness",
    "Career & Work",
    "Relationships",
    "Creativity",
    "Spirituality",
    "Finances",
    "Personal Growth",
    "Community",
    "Fun & Adventure",
    "Physical Environment",
]


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class IdentityStatement:
    """An identity statement like 'I am a runner' or 'I am someone who meditates'."""
    id: str
    dimension: str
    statement: str
    identity_type: IdentityType
    created_at: datetime
    evidence_count: int = 0
    last_strengthened: Optional[datetime] = None


@dataclass
class IdentityEvidence:
    """Evidence of identity-consistent behavior."""
    id: str
    identity_statement_id: str
    description: str
    date: datetime
    impact_score: float = 1.0  # How much this strengthens identity


@dataclass
class IdentityConflict:
    """Conflict between identity and behavior."""
    id: str
    dimension: str
    identity_statement: str
    conflicting_behavior: str
    detected_at: datetime
    severity: int  # 1-5


@dataclass
class IdentityScore:
    """Overall identity alignment score."""
    dimension: str
    current_score: float  # 0-100
    ideal_score: float    # 0-100
    alignment: float       # 0-100
    evidence_count: int


# =============================================================================
# IDENTITY TRACKING ENGINE
# =============================================================================

class IdentityTracker:
    """
    Tracks identity development and alignment.
    
    Features:
    - Identity statement creation (current/ideal/feared)
    - Evidence tracking
    - Conflict detection
    - Alignment scoring
    """
    
    def __init__(self):
        """Initialize the tracker."""
        self.identity_statements: Dict[str, IdentityStatement] = {}
        self.evidence: Dict[str, List[IdentityEvidence]] = {}
        self.conflicts: List[IdentityConflict] = []
    
    def create_identity_statement(
        self,
        dimension: str,
        statement: str,
        identity_type: IdentityType
    ) -> IdentityStatement:
        """Create a new identity statement."""
        import uuid
        
        stmt = IdentityStatement(
            id=str(uuid.uuid4()),
            dimension=dimension,
            statement=statement,
            identity_type=identity_type,
            created_at=datetime.now()
        )
        
        self.identity_statements[stmt.id] = stmt
        self.evidence[stmt.id] = []
        
        return stmt
    
    def add_evidence(
        self,
        identity_statement_id: str,
        description: str,
        impact_score: float = 1.0
    ) -> IdentityEvidence:
        """Add evidence supporting an identity."""
        import uuid
        
        if identity_statement_id not in self.identity_statements:
            raise ValueError("Identity statement not found")
        
        evidence = IdentityEvidence(
            id=str(uuid.uuid4()),
            identity_statement_id=identity_statement_id,
            description=description,
            date=datetime.now(),
            impact_score=impact_score
        )
        
        self.evidence[identity_statement_id].append(evidence)
        
        # Update statement
        stmt = self.identity_statements[identity_statement_id]
        stmt.evidence_count += 1
        stmt.last_strengthened = datetime.now()
        
        return evidence
    
    def detect_conflicts(
        self,
        dimension: str,
        conflicting_behavior: str
    ) -> Optional[IdentityConflict]:
        """Detect conflict between identity and behavior."""
        import uuid
        
        # Find identity statements in this dimension
        dimension_statements = [
            s for s in self.identity_statements.values()
            if s.dimension == dimension and s.identity_type == IdentityType.IDEAL
        ]
        
        if not dimension_statements:
            return None
        
        conflict = IdentityConflict(
            id=str(uuid.uuid4()),
            dimension=dimension,
            identity_statement=dimension_statements[0].statement,
            conflicting_behavior=conflicting_behavior,
            detected_at=datetime.now(),
            severity=3  # Default moderate
        )
        
        self.conflicts.append(conflict)
        return conflict
    
    def calculate_alignment(self, dimension: str) -> IdentityScore:
        """Calculate identity alignment for a dimension."""
        dimension_statements = [
            s for s in self.identity_statements.values()
            if s.dimension == dimension
        ]
        
        if not dimension_statements:
            return IdentityScore(
                dimension=dimension,
                current_score=0.0,
                ideal_score=0.0,
                alignment=0.0,
                evidence_count=0
            )
        
        # Calculate current (average evidence count)
        current = sum(s.evidence_count for s in dimension_statements if s.identity_type == IdentityType.CURRENT)
        ideal = sum(s.evidence_count for s in dimension_statements if s.identity_type == IdentityType.IDEAL)
        
        # Convert to 0-100 scale (rough heuristic)
        current_score = min(100.0, current * 10)  # 10 pieces of evidence = 100
        ideal_score = min(100.0, ideal * 10)
        
        # Alignment = how close current is to ideal
        if ideal_score > 0:
            alignment = (current_score / ideal_score) * 100
        else:
            alignment = 100.0
        
        # Evidence count
        evidence_count = sum(
            len(self.evidence.get(s.id, [])) 
            for s in dimension_statements
        )
        
        return IdentityScore(
            dimension=dimension,
            current_score=current_score,
            ideal_score=ideal_score,
            alignment=alignment,
            evidence_count=evidence_count
        )
    
    def get_dashboard_summary(self) -> Dict:
        """Get overall identity dashboard summary."""
        scores = [self.calculate_alignment(d) for d in IDENTITY_DIMENSIONS]
        
        return {
            "total_identities": len(self.identity_statements),
            "total_evidence": sum(len(e) for e in self.evidence.values()),
            "conflicts_detected": len(self.conflicts),
            "dimensions": [
                {
                    "name": s.dimension,
                    "alignment": s.alignment,
                    "current": s.current_score,
                    "ideal": s.ideal_score
                }
                for s in scores
            ],
            "avg_alignment": sum(s.alignment for s in scores) / len(scores) if scores else 0
        }


def create_tracker() -> IdentityTracker:
    """Factory function to create tracker."""
    return IdentityTracker()
