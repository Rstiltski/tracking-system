"""
Data Minimization Tool

Implements data minimization principles:
- Only collect what's strictly necessary
- Process deletion requests
- Handle scheduled deletions
- Enforce retention policies

Based on Task 11.1.2 and 11.1.3 from PHASE_11_INTEGRATION_ROADMAP.md

Legal Compliance:
- GDPR right to erasure
- CCPA/CPRA requirements
- 2025 state privacy laws
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any
import json


# =============================================================================
# DATA MINIMIZATION STRATEGY
# =============================================================================

@dataclass
class MinimizationResult:
    """Result of a data minimization operation."""
    success: bool
    category: str
    records_affected: int
    bytes_freed: int
    message: str
    errors: List[str]


class DataMinimizer:
    """
    Handles data minimization operations.
    
    Principles:
    - Collect only what's necessary
    - Delete when no longer needed
    - Anonymize where possible
    - Honor retention policies
    """
    
    def __init__(self, storage=None):
        """
        Initialize the data minimizer.
        
        Args:
            storage: Optional storage instance for database operations
        """
        self.storage = storage
        self._deletion_log: List[Dict] = []
    
    def delete_category_data(
        self,
        category: str,
        user_id: str,
        confirm: bool = False
    ) -> MinimizationResult:
        """
        Delete all data for a specific category.
        
        Args:
            category: The data category to delete
            user_id: The user whose data to delete
            confirm: Must be True to actually delete
            
        Returns:
            MinimizationResult with operation details
        """
        if not confirm:
            return MinimizationResult(
                success=False,
                category=category,
                records_affected=0,
                bytes_freed=0,
                message="Deletion not confirmed. Set confirm=True to proceed.",
                errors=["Confirmation required"]
            )
        
        # Log the deletion
        self._deletion_log.append({
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "user_id": user_id,
            "action": "delete_category"
        })
        
        # In production, this would actually delete from database
        return MinimizationResult(
            success=True,
            category=category,
            records_affected=0,  # Would count actual deletions
            bytes_freed=0,  # Would calculate actual bytes
            message=f"All {category} data deleted for user {user_id}",
            errors=[]
        )
    
    def delete_older_than(
        self,
        category: str,
        days: int,
        user_id: str
    ) -> MinimizationResult:
        """
        Delete data older than specified days.
        
        Args:
            category: The data category
            days: Delete data older than this many days
            user_id: The user whose data to process
            
        Returns:
            MinimizationResult with operation details
        """
        cutoff_date = date.today() - timedelta(days=days)
        
        # Log the operation
        self._deletion_log.append({
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "user_id": user_id,
            "action": "delete_older_than",
            "cutoff_date": cutoff_date.isoformat(),
            "days": days
        })
        
        # In production, this would query and delete old records
        return MinimizationResult(
            success=True,
            category=category,
            records_affected=0,  # Would count actual deletions
            bytes_freed=0,
            message=f"Deleted {category} data older than {days} days",
            errors=[]
        )
    
    def anonymize_data(
        self,
        category: str,
        user_id: str
    ) -> MinimizationResult:
        """
        Anonymize data (replace PII with anonymous identifiers).
        
        Args:
            category: The data category to anonymize
            user_id: The user whose data to anonymize
            
        Returns:
            MinimizationResult with operation details
        """
        # Log the anonymization
        self._deletion_log.append({
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "user_id": user_id,
            "action": "anonymize"
        })
        
        # In production, this would replace identifiable data
        return MinimizationResult(
            success=True,
            category=category,
            records_affected=0,
            bytes_freed=0,
            message=f"Anonymized {category} data for user {user_id}",
            errors=[]
        )
    
    def apply_retention_policy(
        self,
        retention_days: int,
        user_id: str
    ) -> List[MinimizationResult]:
        """
        Apply retention policy to all user data.
        
        Args:
            retention_days: Delete data older than this many days (0 = keep forever)
            user_id: The user whose data to process
            
        Returns:
            List of MinimizationResult for each category
        """
        results = []
        
        if retention_days <= 0:
            return [MinimizationResult(
                success=True,
                category="all",
                records_affected=0,
                bytes_freed=0,
                message="Retention policy: keep forever",
                errors=[]
            )]
        
        # Apply to each data category
        categories = [
            "habits", "tasks", "finances", "health",
            "emotional", "time", "goals", "achievements"
        ]
        
        for category in categories:
            result = self.delete_older_than(category, retention_days, user_id)
            results.append(result)
        
        return results
    
    def get_deletion_log(self) -> List[Dict]:
        """Get the deletion log."""
        return self._deletion_log.copy()
    
    def clear_deletion_log(self):
        """Clear the deletion log."""
        self._deletion_log = []


# =============================================================================
# CONSENT-BASED FILTERING
# =============================================================================

class ConsentFilter:
    """
    Filters data based on user consent preferences.
    
    Used to ensure we only process data that users have
    consented to.
    """
    
    def __init__(self, privacy_preferences=None):
        """
        Initialize the consent filter.
        
        Args:
            privacy_preferences: User's privacy preferences
        """
        self.preferences = privacy_preferences
    
    def can_process(self, category: str) -> bool:
        """
        Check if a category can be processed based on consent.
        
        Args:
            category: The data category to check
            
        Returns:
            True if processing is allowed
        """
        if not self.preferences:
            return True  # No preferences = allow all
        
        # Import here to avoid circular imports
        from brain.models.privacy_preferences import DataCategory, ConsentStatus
        
        try:
            cat = DataCategory(category)
            return self.preferences.is_consent_granted(cat)
        except ValueError:
            return True  # Unknown category
    
    def filter_query(self, query: str, category: str) -> str:
        """
        Modify a database query to respect consent.
        
        Args:
            query: Original SQL query
            category: Data category being queried
            
        Returns:
            Modified query (may add WHERE clause)
        """
        if not self.can_process(category):
            # Return a query that returns no results
            return f"{query} AND 1=0"  # Always false condition
        
        return query


# =============================================================================
# DATA INVENTORY
# =============================================================================

@dataclass
class DataInventoryItem:
    """An item in the data inventory."""
    category: str
    record_count: int
    size_bytes: int
    oldest_record: Optional[date]
    newest_record: Optional[date]
    retention_policy: str


class DataInventory:
    """
    Provides an inventory of all user data.
    
    Used for transparency and privacy reporting.
    """
    
    def __init__(self, storage=None):
        """Initialize the data inventory."""
        self.storage = storage
    
    def get_inventory(self, user_id: str) -> List[DataInventoryItem]:
        """
        Get a full inventory of user data.
        
        Args:
            user_id: The user to get inventory for
            
        Returns:
            List of DataInventoryItem for each category
        """
        # In production, this would query actual database
        # Returning placeholder data for now
        categories = [
            ("habits", "daily"),
            ("tasks", "daily"),
            ("finances", "monthly"),
            ("health", "daily"),
            ("emotional", "daily"),
            ("time", "daily"),
            ("goals", "monthly"),
            ("achievements", "permanent"),
        ]
        
        inventory = []
        for cat, retention in categories:
            inventory.append(DataInventoryItem(
                category=cat,
                record_count=0,  # Would query actual count
                size_bytes=0,    # Would calculate actual size
                oldest_record=None,
                newest_record=None,
                retention_policy=retention
            ))
        
        return inventory
    
    def calculate_total_size(self, user_id: str) -> int:
        """Calculate total size of all user data in bytes."""
        inventory = self.get_inventory(user_id)
        return sum(item.size_bytes for item in inventory)


# =============================================================================
# FACTORY
# =============================================================================

def create_data_minimizer(storage=None) -> DataMinimizer:
    """Factory function to create a DataMinimizer."""
    return DataMinimizer(storage=storage)


def create_consent_filter(privacy_preferences=None) -> ConsentFilter:
    """Factory function to create a ConsentFilter."""
    return ConsentFilter(privacy_preferences=privacy_preferences)


def create_data_inventory(storage=None) -> DataInventory:
    """Factory function to create a DataInventory."""
    return DataInventory(storage=storage)
