"""
Commitment Contracts Model

Binding commitments with stakes/rewards to increase follow-through.

Based on Task 11.2.3 from PHASE_11_INTEGRATION_ROADMAP.md
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# CONTRACT TYPES
# =============================================================================

class ContractStatus(Enum):
    """Status of a commitment contract."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StakeType(Enum):
    """Type of stake for commitment."""
    SOCIAL = "social"           # Accountability partner
    FINANCIAL = "financial"     # Money
    IDENTITY = "identity"     # Self-image
    PRIVILEGE = "privilege"    # Giving up something


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class CommitmentContract:
    """A commitment contract."""
    id: str
    user_id: str
    title: str
    description: str
    target_date: datetime
    created_at: datetime
    status: ContractStatus
    
    # Stakes
    stake_type: StakeType
    stake_description: str
    stake_amount: Optional[float] = None  # For financial stakes
    
    # Accountability
    accountability_partner: Optional[str] = None
    check_in_frequency_days: int = 1
    
    # Progress
    completed_check_ins: int = 0
    total_check_ins: int = 0
    last_check_in: Optional[datetime] = None


@dataclass
class CheckIn:
    """A check-in for a commitment."""
    id: str
    contract_id: str
    timestamp: datetime
    progress_note: str
    on_track: bool
    mood: int  # 1-10


# =============================================================================
# COMMITMENT ENGINE
# =============================================================================

class CommitmentEngine:
    """
    Manages commitment contracts.
    
    Features:
    - Contract creation with stakes
    - Check-in tracking
    - Success/failure detection
    - Accountability partner integration
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.contracts: Dict[str, CommitmentContract] = {}
        self.check_ins: Dict[str, List[CheckIn]] = {}
    
    def create_contract(
        self,
        user_id: str,
        title: str,
        description: str,
        target_date: datetime,
        stake_type: StakeType,
        stake_description: str,
        accountability_partner: Optional[str] = None,
        stake_amount: Optional[float] = None
    ) -> CommitmentContract:
        """Create a new commitment contract."""
        import uuid
        
        contract = CommitmentContract(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            description=description,
            target_date=target_date,
            created_at=datetime.now(),
            status=ContractStatus.ACTIVE,
            stake_type=stake_type,
            stake_description=stake_description,
            stake_amount=stake_amount,
            accountability_partner=accountability_partner
        )
        
        self.contracts[contract.id] = contract
        self.check_ins[contract.id] = []
        
        return contract
    
    def check_in(
        self,
        contract_id: str,
        progress_note: str,
        on_track: bool,
        mood: int
    ) -> CheckIn:
        """Record a check-in."""
        import uuid
        
        if contract_id not in self.contracts:
            raise ValueError("Contract not found")
        
        check_in = CheckIn(
            id=str(uuid.uuid4()),
            contract_id=contract_id,
            timestamp=datetime.now(),
            progress_note=progress_note,
            on_track=on_track,
            mood=mood
        )
        
        self.check_ins[contract_id].append(check_in)
        
        # Update contract
        contract = self.contracts[contract_id]
        contract.completed_check_ins += 1
        contract.last_check_in = datetime.now()
        
        return check_in
    
    def get_contract(self, contract_id: str) -> Optional[CommitmentContract]:
        """Get a contract by ID."""
        return self.contracts.get(contract_id)
    
    def get_user_contracts(
        self, 
        user_id: str, 
        status: Optional[ContractStatus] = None
    ) -> List[CommitmentContract]:
        """Get all contracts for a user."""
        contracts = [
            c for c in self.contracts.values()
            if c.user_id == user_id
        ]
        
        if status:
            contracts = [c for c in contracts if c.status == status]
        
        return contracts
    
    def evaluate_contract(self, contract_id: str) -> ContractStatus:
        """
        Evaluate if a contract succeeded or failed.
        
        Returns:
            Updated contract status
        """
        contract = self.contracts.get(contract_id)
        if not contract:
            return ContractStatus.DRAFT
        
        # Check if past target date
        if datetime.now() > contract.target_date:
            check_ins = self.check_ins.get(contract_id, [])
            
            # Count on-track check-ins
            on_track_count = sum(1 for c in check_ins if c.on_track)
            
            if len(check_ins) > 0:
                success_rate = on_track_count / len(check_ins)
                
                if success_rate >= 0.7:
                    contract.status = ContractStatus.COMPLETED
                else:
                    contract.status = ContractStatus.FAILED
            else:
                contract.status = ContractStatus.FAILED
        
        return contract.status
    
    def cancel_contract(self, contract_id: str) -> None:
        """Cancel a contract."""
        contract = self.contracts.get(contract_id)
        if contract:
            contract.status = ContractStatus.CANCELLED
    
    def get_contract_summary(self, user_id: str) -> Dict:
        """Get summary of user's contracts."""
        contracts = self.get_user_contracts(user_id)
        
        active = [c for c in contracts if c.status == ContractStatus.ACTIVE]
        completed = [c for c in contracts if c.status == ContractStatus.COMPLETED]
        failed = [c for c in contracts if c.status == ContractStatus.FAILED]
        
        return {
            "total": len(contracts),
            "active": len(active),
            "completed": len(completed),
            "failed": len(failed),
            "success_rate": len(completed) / (len(completed) + len(failed)) if (len(completed) + len(failed)) > 0 else 0
        }


def create_engine() -> CommitmentEngine:
    """Factory function to create engine."""
    return CommitmentEngine()
