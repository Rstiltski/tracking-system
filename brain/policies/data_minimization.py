"""
Data Minimization Policy - Enforces Data Minimization

Policy module for enforcing data minimization principles.

Based on Task 11.1.3 from PHASE_11_INTEGRATION_ROADMAP.md

Legal: GDPR, CCPA, 2025 state privacy laws
"""

from datetime import date, timedelta
from typing import Dict, List, Optional


# =============================================================================
# RETENTION POLICIES
# =============================================================================

# Default retention periods (in days)
RETENTION_POLICIES = {
    # Raw tracking data
    "habit_entries": 90,
    "task_entries": 90,
    "health_metrics": 180,
    "financial_data": 365 * 3,  # 3 years for tax purposes
    "emotional_logs": 90,
    "time_logs": 90,
    
    # Aggregated data (longer retention)
    "aggregated_stats": 730,  # 2 years
    "streak_history": 730,
    "achievement_history": 730,
    
    # Short-term data
    "session_data": 30,
    "audit_logs": 90,
    "temp_cache": 7,
}


# =============================================================================
# MINIMIZATION RULES
# =============================================================================

MINIMIZATION_RULES = {
    "collect_only_necessary": True,
    "auto_delete_raw_after_retention": True,
    "aggregate_before_delete": True,
    "anonymize_analytics": True,
    "no_unnecessary_pii": True,
}


# =============================================================================
# POLICY ENFORCEMENT
# =============================================================================

class DataMinimizationPolicy:
    """
    Enforces data minimization policies.
    """
    
    def __init__(self):
        """Initialize the policy enforcer."""
        self.policies = RETENTION_POLICIES
        self.rules = MINIMIZATION_RULES
    
    def should_delete(self, data_category: str, data_date: date) -> bool:
        """Check if data should be deleted based on retention policy."""
        if data_category not in self.policies:
            return False
        
        retention_days = self.policies[data_category]
        age = (date.today() - data_date).days
        
        return age > retention_days
    
    def get_retention_days(self, data_category: str) -> int:
        """Get retention days for a category."""
        return self.policies.get(data_category, 90)
    
    def can_collect(self, field: str, purpose: str) -> bool:
        """Check if field can be collected based on necessity."""
        # Core necessary fields
        necessary_fields = {
            "habits": ["name", "frequency", "completed"],
            "tasks": ["title", "status", "due_date"],
            "health": ["metric_type", "value", "date"],
        }
        
        # Check if field is in necessary list
        for category, fields in necessary_fields.items():
            if field in fields:
                return True
        
        # Default to False - require justification
        return False


def create_policy() -> DataMinimizationPolicy:
    """Factory function to create policy enforcer."""
    return DataMinimizationPolicy()
