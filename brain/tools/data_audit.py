"""
Data Audit Tool - Data Collection Auditing

Audits what data is collected and ensures minimization compliance.

Based on Task 11.1.3 from PHASE_11_INTEGRATION_ROADMAP.md
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional


# =============================================================================
# DATA COLLECTION AUDIT
# =============================================================================

@dataclass
class DataCollectionRecord:
    """Record of data collected."""
    category: str
    field: str
    collected: bool
    necessity_score: float  # 0.0 to 1.0
    justification: str
    last_collected: Optional[datetime]


class DataAudit:
    """
    Audit data collection for compliance.
    
    Ensures:
    - All data has documented necessity
    - Minimization principles followed
    - Retention policies enforced
    """
    
    # Default retention periods (days)
    RETENTION_POLICIES = {
        "raw_data": 90,      # Raw tracking data
        "aggregated": 730,   # Aggregated analytics (2 years)
        "logs": 30,          # System logs
        "sessions": 30,       # Session data
    }
    
    def __init__(self):
        """Initialize the data audit."""
        self._collection_records: List[DataCollectionRecord] = []
    
    def audit_collection(self, category: str) -> Dict:
        """
        Audit data collection for a category.
        
        Returns:
            Audit results
        """
        records = [r for r in self._collection_records if r.category == category]
        
        if not records:
            return {"status": "no_records", "compliant": True}
        
        # Check necessity scores
        low_necessity = [r for r in records if r.necessity_score < 0.5]
        
        return {
            "status": "audited",
            "total_fields": len(records),
            "low_necessity_count": len(low_necessity),
            "compliant": len(low_necessity) == 0,
            "average_necessity": sum(r.necessity_score for r in records) / len(records)
        }
    
    def check_retention_compliance(self, data_date: date, category: str) -> bool:
        """Check if data is within retention period."""
        days_old = (date.today() - data_date).days
        policy = self.RETENTION_POLICITIES.get(category, 90)
        return days_old <= policy


def create_data_audit() -> DataAudit:
    """Factory function to create a data audit."""
    return DataAudit()
