"""
Integration Layer - Connects Sentient Enterprise components with existing Brain

This module provides the integration between:
- Brainstem (security gateway) 
- Cerebellum (write coordinator)
- Tri-Brain architecture (OpsBrain, FinanceBrain, RelationBrain)
- Nervous System (event bus)
- Existing Brain command execution

Purpose: Allow gradual migration from monolithic Brain to distributed Sentient Enterprise
architecture while maintaining backward compatibility.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from typing import Optional, Dict, Any
import sqlite3

from brain.core.brain import Brain
from brain.core.command_event import CommandEvent
from brain.core.result import BrainResult
from brain.core.contracts import ICommand, create_command, EventType, create_event
from brain.core.stem import Brainstem
from brain.core.cerebellum import Cerebellum, WriteCommand, WriteOperation
from brain.brains.ops_brain import OpsBrain
from brain.brains.finance_brain import FinanceBrain
from brain.brains.relation_brain import RelationBrain
from brain.nervous_system import get_nervous_system
from brain import nervous_system
from brain.core import result


class IntegratedBrain:
    """
    Integrated Brain that combines legacy Brain with Sentient Enterprise components.
    
    This provides a migration path:
    1. Start: Use existing Brain for all commands
    2. Gradual: Route specific commands through Sentient components
    3. Complete: Full Sentient Enterprise architecture
    
    Flow:
        UI/API → Brainstem (auth) → IntegratedBrain → Appropriate Brain → Cerebellum → DB
                                                    ↓
                                            Nervous System (events)
    """
    
    def __init__(
        self, 
        db_connection: Optional[sqlite3.Connection] = None,
        enable_sentient: bool = False
    ):
        """
        Initialize integrated brain.
        
        Args:
            db_connection: Database connection
            enable_sentient: If True, route commands through Sentient components
        """
        self.db_connection = db_connection
        self.enable_sentient = enable_sentient
        
        # Legacy Brain (existing system)
        self.legacy_brain = Brain(db_connection)
        
        # Sentient Enterprise components
        if enable_sentient:
            self.nervous_system = get_nervous_system(db_connection)
            self.brainstem = Brainstem()
            self.cerebellum = Cerebellum(db_connection=db_connection, nervous_system=self.nervous_system)
            
            # The 3 Brains
            self.ops_brain = OpsBrain(
                self.cerebellum, 
                self.nervous_system, 
                db_connection
            )
            self.finance_brain = FinanceBrain(
                self.cerebellum,
                self.nervous_system,
                db_connection
            )
            self.relation_brain = RelationBrain(
                self.cerebellum,
                self.nervous_system,
                db_connection
            )
        else:
            self.nervous_system = None
            self.brainstem = None
            self.cerebellum = None
            self.ops_brain = None
            self.finance_brain = None
            self.relation_brain = None
    
    def run(self, event: CommandEvent) -> BrainResult:
        """
        Execute a command through the appropriate path.
        
        Args:
            event: Command event to execute
            
        Returns:
            BrainResult with execution outcome
        """
        if not self.enable_sentient:
            # Legacy path: use existing Brain
            return self.legacy_brain.run(event)
        
        # Sentient path: route through Brainstem and appropriate Brain
        return self._run_sentient(event)
    
    def _run_sentient(self, event: CommandEvent) -> BrainResult:
        """
        Execute command through Sentient Enterprise architecture.
        
        Flow:
            1. Convert CommandEvent to ICommand
            2. Authenticate through Brainstem
            3. Route to appropriate Brain
            4. Execute via Cerebellum
            5. Emit events via Nervous System
        
        Args:
            event: Command event to execute
            
        Returns:
            BrainResult with execution outcome
        """
        # Step 1: Convert to ICommand (Phase 0 contract)
        try:
            command = self._convert_to_icommand(event)
        except Exception as e:
            return BrainResult(
                success=False,
                status="FAILED",
                error_message=f"Command validation failed: {str(e)}",
                error_code="INVALID_COMMAND"
            )
        
        # Step 2: Authenticate through Brainstem (Phase 1)
        auth_result = self.brainstem.process(command)
        if not auth_result.success:
            return BrainResult(
                success=False,
                status="DENIED",
                error_message=auth_result.error_message,
                error_code=auth_result.error_code
            )
        
        # Step 3: Route to appropriate Brain (Phase 5)
        try:
            brain_result = self._route_to_brain(command, event)
            return brain_result
        except Exception as e:
            return BrainResult(
                success=False,
                status="FAILED",
                error_message=f"Execution failed: {str(e)}",
                error_code="EXECUTION_ERROR"
            )
    
    def _convert_to_icommand(self, event: CommandEvent) -> ICommand:
        """
        Convert legacy CommandEvent to Phase 0 ICommand.
        
        Args:
            event: Legacy command event
            
        Returns:
            ICommand with proper contracts
        """
        return create_command(
            command_type=event.command_type,
            user_id=event.user_id,
            payload=event.params,
            company_id=event.company_id,
            idempotency_key=event.idempotency_key,
            confirmation_token=event.confirmation_token,
            dry_run=False  # Legacy CommandEvent doesn't have dry_run
        )
    
    def _route_to_brain(self, command: ICommand, event: CommandEvent) -> BrainResult:
        """
        Route command to the appropriate specialized brain.
        
        Command Routing:
        - Jobs, Crew, Scheduling → OpsBrain
        - Invoices, Payments, Quotes → FinanceBrain  
        - Customers, Messages, Portal → RelationBrain
        
        Args:
            command: Validated ICommand
            event: Original CommandEvent (for backward compatibility)
            
        Returns:
            BrainResult from the appropriate brain
        """
        command_type = command.command_type
        
        # Operations commands → OpsBrain
        ops_commands = [
            "JobCreate", "JobUpdate", "JobSchedule", "JobStart", "JobComplete",
            "JobCancel", "CrewAssign", "CrewUnassign", "ScheduleJob",
            "MaterialCreate", "MaterialUpdate", "TimeTrack"
        ]
        
        # Finance commands → FinanceBrain
        finance_commands = [
            "InvoiceCreate", "InvoiceSend", "InvoiceVoid",
            "PaymentRecord", "QuoteCreate", "QuoteAccept", "QuoteDecline"
        ]
        
        # Relations commands → RelationBrain
        relation_commands = [
            "CustomerCreate", "CustomerUpdate", "MessageSend",
            "PortalTokenGenerate", "PortalTokenRevoke"
        ]
        
        # Route to appropriate brain
        if command_type in ops_commands:
            # Route to OpsBrain
            return self.ops_brain.handle_command(command)
        
        elif command_type in finance_commands:
            # Route to FinanceBrain
            return self.finance_brain.handle_command(command)
        
        elif command_type in relation_commands:
            # Route to RelationBrain
            return self.relation_brain.handle_command(command)
        
        else:
            # Unknown command, use legacy path
            return self.legacy_brain.run(event)
    
    def get_nervous_system(self):
        """Get the Nervous System for event listening"""
        return self.nervous_system
    
    def get_cerebellum(self):
        """Get the Cerebellum for write operations"""
        return self.cerebellum


class IntegrationHelper:
    """
    Helper utilities for integration between legacy and Sentient systems.
    """
    
    @staticmethod
    def emit_legacy_event(
        nervous_system,
        event_type: str,
        command_id: str,
        user_id: int,
        payload: Dict[str, Any],
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None
    ):
        """
        Emit an event in the Nervous System using legacy event type strings.
        
        This bridges the gap between legacy string-based events and Phase 0 EventType enum.
        
        Args:
            nervous_system: NervousSystem instance
            event_type: Legacy event type string (e.g., "job_completed")
            command_id: ID of the command that caused this event
            user_id: User who triggered the event
            payload: Event payload data
            entity_type: Optional entity type
            entity_id: Optional entity ID
        """
        # Map legacy event types to Phase 0 EventType enum
        event_type_mapping = {
            "job_created": EventType.JOB_CREATED,
            "job_completed": EventType.JOB_COMPLETED,
            "job_cancelled": EventType.JOB_CANCELLED,
            "invoice_created": EventType.INVOICE_CREATED,
            "invoice_sent": EventType.INVOICE_SENT,
            "invoice_paid": EventType.INVOICE_PAID,
            "payment_recorded": EventType.PAYMENT_RECORDED,
            "customer_created": EventType.CUSTOMER_CREATED,
            "quote_created": EventType.QUOTE_CREATED,
            "quote_accepted": EventType.QUOTE_ACCEPTED,
        }
        
        # Get EventType enum value
        enum_event_type = event_type_mapping.get(
            event_type.lower(),
            EventType.SYSTEM_ERROR  # Default fallback
        )
        
        # Create Phase 0 compliant event
        event = create_event(
            event_type=enum_event_type,
            caused_by_command_id=command_id,
            caused_by_user_id=user_id,
            payload=payload,
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        # Emit to Nervous System
        nervous_system.emit(event)
    
    @staticmethod
    def convert_brain_result_to_legacy(result: BrainResult) -> Dict[str, Any]:
        """
        Convert BrainResult to legacy dictionary format.
        
        Used for backward compatibility with existing UI code.
        
        Args:
            result: BrainResult from execution
            
        Returns:
            Dictionary in legacy format
        """
        return {
            'success': result.success,
            'data': result.data,
            'error': result.error_message,
            'error_code': result.error_code,
            'requires_confirmation': result.requires_confirmation,
            'confirmation_token': result.confirmation_token,
            'dry_run_preview': result.dry_run_preview
        }


def create_integrated_brain(
    db_connection: Optional[sqlite3.Connection] = None,
    enable_sentient: bool = False
) -> IntegratedBrain:
    """
    Factory function to create an IntegratedBrain.
    
    Args:
        db_connection: Database connection
        enable_sentient: If True, enable Sentient Enterprise components
        
    Returns:
        IntegratedBrain instance
    """
    return IntegratedBrain(db_connection, enable_sentient)
