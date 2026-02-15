"""
Brain - Main entry point for command execution
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import time
import traceback
import sqlite3
import logging
import db
import json
logger = logging.getLogger(__name__)
from brain.core.command_event import CommandEvent
from brain.core.result import BrainResult
from brain.core.router import Router
from brain.policies.engine import PolicyEngine
from brain.tools.registry import ToolRegistry
from brain.state.machine import TransitionResult
from brain.fork.confirmation import ConfirmationManager
from brain.core.guardrails import get_safety_middleware
from brain.nervous_system import NervousSystem
from brain.fork.engine import DryRunResult

# Feature flags: detect optional integrations at import-time to avoid NameError
try:
    # Local-first integration may not be available in tests
    from local_first_integration import get_local_first_manager  # type: ignore
    HAS_LOCAL_FIRST = True
except ImportError:
    HAS_LOCAL_FIRST = False
    get_local_first_manager = None

try:
    import crypto_engine
    HAS_CRYPTO_ENGINE = True
except ImportError:
    HAS_CRYPTO_ENGINE = False
    crypto_engine = None

try:
    # Neural link may be unavailable in minimal test environments
    from brain.security.neural_link import NeuralCommandLink  # type: ignore
    HAS_NEURAL_LINK = True
except ImportError:
    HAS_NEURAL_LINK = False
    NeuralCommandLink = None

try:
    from services import debug_console  # type: ignore
    HAS_DEBUG_CONSOLE = True
except ImportError:
    HAS_DEBUG_CONSOLE = False
    debug_console = None

try:
    from cache_manager import clear_customer_caches, clear_job_caches, clear_profitability_caches
    HAS_CACHE_MANAGER = True
except ImportError:
    HAS_CACHE_MANAGER = False
    clear_customer_caches = None
    clear_job_caches = None
    clear_profitability_caches = None


def get_feature_availability() -> dict:
    """
    Get the availability status of optional features.

    This function provides graceful degradation information about which
    optional features are available in the current environment. Useful for
    UI components to show appropriate messaging when features are missing.

    Returns:
        Dict with feature names as keys and availability info as values.
    """
    return {
        'local_first': {
            'available': HAS_LOCAL_FIRST,
            'description': 'Offline-capable local-first architecture',
            'fallback': 'Data requires network connection'
        },
        'crypto_engine': {
            'available': HAS_CRYPTO_ENGINE,
            'description': 'End-to-end encryption for sensitive data',
            'fallback': 'Sensitive data stored without encryption'
        },
        'neural_link': {
            'available': HAS_NEURAL_LINK,
            'description': 'Secure encrypted command channel',
            'fallback': 'Commands sent via standard channel'
        },
        'debug_console': {
            'available': HAS_DEBUG_CONSOLE,
            'description': 'Advanced debugging and diagnostics',
            'fallback': 'Standard logging only'
        },
        'cache_manager': {
            'available': HAS_CACHE_MANAGER,
            'description': 'Intelligent cache invalidation',
            'fallback': 'Manual cache refresh may be needed'
        }
    }


def get_missing_features_warning() -> str:
    """
    Get a user-friendly warning message about missing optional features.

    Returns:
        Warning message string, or empty string if all features available.
    """
    features = get_feature_availability()
    missing = [name for name, info in features.items() if not info['available']]

    if not missing:
        return ""

    warnings = []
    for name in missing:
        info = features[name]
        warnings.append(f"- {info['description']}: {info['fallback']}")

    return "Some optional features are not available:\n" + "\n".join(warnings)


class Brain:
    """
    The Brain is the central nervous system of the system.

    Every command flows through the Brain:
    1. Router validates and routes
    2. Policies check preconditions
    3. State machines validate transitions (Phase 2)
    4. Planner generates execution plan
    5. Risk checker determines if confirmation needed
    6. Tools execute (or dry-run if high-risk)
    7. Audit log records everything

    Usage:
        brain = Brain()
        result = brain.run(command_event)
    """
    COMMAND_STATE_MAPPING = {'JobCreate': {'entity': 'job', 'state': 'DRAFT'}, 'JobQuote': {'entity': 'job', 'state': 'QUOTED'}, 'JobBook': {'entity': 'job', 'state': 'BOOKED'}, 'JobSchedule': {'entity': 'job', 'state': 'SCHEDULED'}, 'JobStart': {'entity': 'job', 'state': 'IN_PROGRESS'}, 'JobPause': {'entity': 'job', 'state': 'PAUSED'}, 'JobResume': {'entity': 'job', 'state': 'IN_PROGRESS'}, 'JobComplete': {'entity': 'job', 'state': 'AWAITING_SIGNOFF'}, 'JobAddSignOff': {'entity': 'job', 'state': 'COMPLETED'}, 'JobCancel': {'entity': 'job', 'state': 'CANCELLED'}, 'InvoiceCreate': {'entity': 'invoice', 'state': 'DRAFT'}, 'InvoiceSend': {'entity': 'invoice', 'state': 'SENT'}, 'InvoiceView': {'entity': 'invoice', 'state': 'VIEWED'}, 'InvoiceVoid': {'entity': 'invoice', 'state': 'VOID'}, 'QuoteCreate': {'entity': 'quote', 'state': 'DRAFT'}, 'QuoteSend': {'entity': 'quote', 'state': 'SENT'}, 'QuoteAccept': {'entity': 'quote', 'state': 'ACCEPTED'}, 'QuoteDecline': {'entity': 'quote', 'state': 'DECLINED'}, 'PaymentRecord': {'entity': 'payment', 'state': 'PENDING'}, 'PaymentConfirm': {'entity': 'payment', 'state': 'CLEARED'}, 'PaymentFail': {'entity': 'payment', 'state': 'FAILED'}, 'PaymentRefund': {'entity': 'payment', 'state': 'REFUNDED'}}

    def __init__(self, db_connection: sqlite3.Connection=None):
        try:
            from config import get_config
            config = get_config()
            lazy_loading = config.BRAIN_LAZY_TOOL_LOADING
        except Exception:
            lazy_loading = False
        try:
            from config import get_config
            config = get_config()
            auto_discover = getattr(config, 'AUTO_DISCOVER_TOOLS', False)
        except Exception:
            auto_discover = False
        self.router = Router()
        self.policy_engine = PolicyEngine()
        self.tool_registry = ToolRegistry(lazy_loading=lazy_loading, auto_discover=auto_discover)
        # Import here to avoid circular import
        from brain.audit.logger import AuditLogger
        self.audit_logger = AuditLogger()
        # Import here to avoid circular import
        from brain.state.manager import StateMachineManager
        self.state_machine_manager = StateMachineManager()
        if db_connection is None:
            self.db_connection = db.get_sqlite_conn()
        else:
            self.db_connection = db_connection
        # Import here to avoid circular import
        from brain.fork.engine import ForkEngine
        self.fork_engine = ForkEngine(self.db_connection) if db_connection else None
        self.confirmation_manager = ConfirmationManager(self.db_connection)
        # Import here to avoid circular import
        from brain.core.learning_mode_middleware import get_learning_mode_middleware
        self.learning_mode_middleware = get_learning_mode_middleware(self.db_connection)
        self.safety_middleware = get_safety_middleware()
        self.nervous_system = NervousSystem()
        # Import here to avoid circular import
        from brain.core.cerebellum import Cerebellum
        self.cerebellum = Cerebellum(db_connection=self.db_connection, nervous_system=self.nervous_system)
        # Import here to avoid circular import
        from brain.brains.ops_brain import OpsBrain
        self.ops_brain = OpsBrain(self.cerebellum, self.nervous_system, self.db_connection)
        # Import here to avoid circular import
        from brain.brains.finance_brain import FinanceBrain
        self.finance_brain = FinanceBrain(self.cerebellum, self.nervous_system, self.db_connection)
        # Import here to avoid circular import
        from brain.brains.relation_brain import RelationBrain
        self.relation_brain = RelationBrain(self.cerebellum, self.nervous_system, self.db_connection)
        self.local_first_manager = None
        self.entitlement_checking_enabled = False
        if HAS_LOCAL_FIRST:
            try:
                from config import get_config
                config = get_config()
                if config.LOCAL_FIRST_ENABLED:
                    self.local_first_manager = get_local_first_manager()
                    self.entitlement_checking_enabled = True
            except (ImportError, AttributeError) as e:
                logger.debug(f'Local-first mode not available: {e}')
        self.neural_link = None
        if HAS_NEURAL_LINK:
            try:
                from config import get_config
                if getattr(get_config(), 'NEURAL_LINK_ENABLED', False):
                    self.neural_link = NeuralCommandLink()
                    self.neural_link.initialize_system()
            except Exception as e:
                logger.error(f'Failed to initialize Neural Link: {e}')
        self._register_tools()

    def _register_tools(self):
        """
        Register all tools with lazy loading support.
        
        If auto_discover is enabled, tools are automatically discovered.
        Otherwise, tools are manually registered here for backward compatibility.
        """
        if self.tool_registry.auto_discover:
            logger.info(f'Auto-discovery enabled: {len(self.tool_registry)} tools registered')
        self.tool_registry.register_lazy('CreateJob', 'brain.tools.job_tools', 'CreateJobTool')
        self.tool_registry.register_lazy('UpdateJob', 'brain.tools.job_tools', 'UpdateJobTool')
        self.tool_registry.register_lazy('GetJob', 'brain.tools.job_tools', 'GetJobTool')
        self.tool_registry.register_lazy('CalculateJobActuals', 'brain.tools.job_actuals_tools', 'CalculateJobActualsTool')
        self.tool_registry.register_lazy('CreateCustomer', 'brain.tools.customer_tools', 'CreateCustomerTool')
        self.tool_registry.register_lazy('GetCustomer', 'brain.tools.customer_tools', 'GetCustomerTool')
        self.tool_registry.register_lazy('CreateInvoice', 'brain.tools.financial_tools', 'CreateInvoiceTool')
        self.tool_registry.register_lazy('SendInvoice', 'brain.tools.financial_tools', 'SendInvoiceTool')
        self.tool_registry.register_lazy('GetInvoice', 'brain.tools.financial_tools', 'GetInvoiceTool')
        self.tool_registry.register_lazy('RecordPayment', 'brain.tools.financial_tools', 'RecordPaymentTool')
        self.tool_registry.register_lazy('GetPayment', 'brain.tools.financial_tools', 'GetPaymentTool')
        self.tool_registry.register_lazy('ReconcileInvariants', 'brain.tools.reconciliation_tools', 'ReconcileInvariantsTool')
        self.tool_registry.register_lazy('GetReconciliationHistory', 'brain.tools.reconciliation_tools', 'GetReconciliationHistoryTool')
        self.tool_registry.register_lazy('CreateQuote', 'brain.tools.quote_tools', 'CreateQuoteTool')
        self.tool_registry.register_lazy('AddQuoteLineItem', 'brain.tools.quote_tools', 'AddQuoteLineItemTool')
        self.tool_registry.register_lazy('SendQuote', 'brain.tools.quote_tools', 'SendQuoteTool')
        self.tool_registry.register_lazy('AcceptQuote', 'brain.tools.quote_tools', 'AcceptQuoteTool')
        self.tool_registry.register_lazy('DeclineQuote', 'brain.tools.quote_tools', 'DeclineQuoteTool')
        self.tool_registry.register_lazy('GetQuote', 'brain.tools.quote_tools', 'GetQuoteTool')
        self.tool_registry.register_lazy('ConvertQuoteToJob', 'brain.tools.quote_tools', 'ConvertQuoteToJobTool')
        self.tool_registry.register_lazy('AddQuoteItem', 'brain.tools.quote_tools', 'AddQuoteItemTool')
        self.tool_registry.register_lazy('ClockIn', 'brain.tools.time_tracking_tools', 'ClockInTool')
        self.tool_registry.register_lazy('ClockOut', 'brain.tools.time_tracking_tools', 'ClockOutTool')
        self.tool_registry.register_lazy('AddWorkLog', 'brain.tools.time_tracking_tools', 'AddWorkLogTool')
        self.tool_registry.register_lazy('UpdateWorkLog', 'brain.tools.time_tracking_tools', 'UpdateWorkLogTool')
        self.tool_registry.register_lazy('ApproveTimesheet', 'brain.tools.time_tracking_tools', 'ApproveTimesheetTool')
        self.tool_registry.register_lazy('RejectTimesheet', 'brain.tools.time_tracking_tools', 'RejectTimesheetTool')
        self.tool_registry.register_lazy('AssignCrew', 'brain.tools.crew_management_tools', 'AssignCrewTool')
        self.tool_registry.register_lazy('UnassignCrew', 'brain.tools.crew_management_tools', 'UnassignCrewTool')
        self.tool_registry.register_lazy('CreateUser', 'brain.tools.crew_management_tools', 'CreateUserTool')
        self.tool_registry.register_lazy('UpdateUser', 'brain.tools.crew_management_tools', 'UpdateUserTool')
        self.tool_registry.register_lazy('DeleteUser', 'brain.tools.crew_management_tools', 'DeleteUserTool')
        self.tool_registry.register_lazy('ActivateUser', 'brain.tools.crew_management_tools', 'ActivateUserTool')
        self.tool_registry.register_lazy('DeactivateUser', 'brain.tools.crew_management_tools', 'DeactivateUserTool')
        self.tool_registry.register_lazy('SetUserRole', 'brain.tools.crew_management_tools', 'SetUserRoleTool')
        self.tool_registry.register_lazy('UpdateJobStatus', 'brain.tools.job_customer_tools', 'UpdateJobStatusTool')
        self.tool_registry.register_lazy('AddJobNote', 'brain.tools.job_customer_tools', 'AddJobNoteTool')
        self.tool_registry.register_lazy('DeleteJob', 'brain.tools.job_customer_tools', 'DeleteJobTool')
        self.tool_registry.register_lazy('UpdateCustomer', 'brain.tools.job_customer_tools', 'UpdateCustomerTool')
        self.tool_registry.register_lazy('AddCustomerNote', 'brain.tools.job_customer_tools', 'AddCustomerNoteTool')
        self.tool_registry.register_lazy('DeleteCustomer', 'brain.tools.job_customer_tools', 'DeleteCustomerTool')
        self.tool_registry.register_lazy('ViewAuditLog', 'brain.tools.audit_tools', 'ViewAuditLogTool')
        self.tool_registry.register_lazy('SendMessage', 'brain.tools.communication_tools', 'SendMessageTool')
        self.tool_registry.register_lazy('SendBulkMessage', 'brain.tools.communication_tools', 'SendBulkMessageTool')
        self.tool_registry.register_lazy('ScheduleMessage', 'brain.tools.communication_tools', 'ScheduleMessageTool')
        self.tool_registry.register_lazy('CancelMessage', 'brain.tools.communication_tools', 'CancelMessageTool')
        self.tool_registry.register_lazy('SendInvoiceEmail', 'brain.tools.communication_tools', 'SendInvoiceEmailTool')
        self.tool_registry.register_lazy('SendQuoteEmail', 'brain.tools.communication_tools', 'SendQuoteEmailTool')
        self.tool_registry.register_lazy('SendJobConfirmation', 'brain.tools.communication_tools', 'SendJobConfirmationTool')
        self.tool_registry.register_lazy('SendJobReminder', 'brain.tools.communication_tools', 'SendJobReminderTool')
        self.tool_registry.register_lazy('CreateMaterial', 'brain.tools.materials_tools', 'CreateMaterialTool')
        self.tool_registry.register_lazy('UpdateMaterial', 'brain.tools.materials_tools', 'UpdateMaterialTool')
        self.tool_registry.register_lazy('DeleteMaterial', 'brain.tools.materials_tools', 'DeleteMaterialTool')
        self.tool_registry.register_lazy('AdjustInventory', 'brain.tools.materials_tools', 'AdjustInventoryTool')
        self.tool_registry.register_lazy('RecordUsage', 'brain.tools.materials_tools', 'RecordUsageTool')
        self.tool_registry.register_lazy('ReorderMaterial', 'brain.tools.materials_tools', 'ReorderMaterialTool')
        self.tool_registry.register_lazy('ScheduleJob', 'brain.tools.scheduling_tools', 'ScheduleJobTool')
        self.tool_registry.register_lazy('RescheduleJob', 'brain.tools.scheduling_tools', 'RescheduleJobTool')
        self.tool_registry.register_lazy('CheckAvailability', 'brain.tools.scheduling_tools', 'CheckAvailabilityTool')
        self.tool_registry.register_lazy('BookResource', 'brain.tools.scheduling_tools', 'BookResourceTool')
        self.tool_registry.register_lazy('ReleaseResource', 'brain.tools.scheduling_tools', 'ReleaseResourceTool')
        self.tool_registry.register_lazy('CreateRecurringJob', 'brain.tools.scheduling_tools', 'CreateRecurringJobTool')
        self.tool_registry.register_lazy('RecordExpense', 'brain.tools.expense_credit_tools', 'RecordExpenseTool')
        self.tool_registry.register_lazy('UpdateExpense', 'brain.tools.expense_credit_tools', 'UpdateExpenseTool')
        self.tool_registry.register_lazy('DeleteExpense', 'brain.tools.expense_credit_tools', 'DeleteExpenseTool')
        self.tool_registry.register_lazy('LinkExpenseToJob', 'brain.tools.expense_credit_tools', 'LinkExpenseToJobTool')
        self.tool_registry.register_lazy('CreateCreditNote', 'brain.tools.expense_credit_tools', 'CreateCreditNoteTool')
        self.tool_registry.register_lazy('IssueCreditNote', 'brain.tools.expense_credit_tools', 'IssueCreditNoteTool')
        self.tool_registry.register_lazy('ApplyCreditNote', 'brain.tools.expense_credit_tools', 'ApplyCreditNoteTool')
        self.tool_registry.register_lazy('VoidCreditNote', 'brain.tools.expense_credit_tools', 'VoidCreditNoteTool')
        self.tool_registry.register_lazy('GeneratePortalToken', 'brain.tools.portal_tools', 'GeneratePortalTokenTool')
        self.tool_registry.register_lazy('RevokePortalToken', 'brain.tools.portal_tools', 'RevokePortalTokenTool')
        self.tool_registry.register_lazy('DeleteTemplate', 'brain.tools.delete_tools', 'DeleteTemplateTool')
        self.tool_registry.register_lazy('DeleteSupplier', 'brain.tools.delete_tools', 'DeleteSupplierTool')
        self.tool_registry.register_lazy('DeleteRole', 'brain.tools.delete_tools', 'DeleteRoleTool')
        self.tool_registry.register_lazy('DeleteTeam', 'brain.tools.delete_tools', 'DeleteTeamTool')
        self.tool_registry.register_lazy('RemoveTeamMember', 'brain.tools.delete_tools', 'RemoveTeamMemberTool')
        self.tool_registry.register_lazy('DeleteRecurringJob', 'brain.tools.delete_tools', 'DeleteRecurringJobTool')
        self.tool_registry.register_lazy('DeleteJobMaterial', 'brain.tools.delete_tools', 'DeleteJobMaterialTool')
        self.tool_registry.register_lazy('DeleteQuoteItem', 'brain.tools.delete_tools', 'DeleteQuoteItemTool')
        self.tool_registry.register_lazy('BulkJobStatusUpdate', 'brain.tools.bulk_operations', 'BulkJobStatusUpdateTool')
        self.tool_registry.register_lazy('BulkDeleteExpenses', 'brain.tools.bulk_operations', 'BulkDeleteExpensesTool')
        self.tool_registry.register_lazy('BulkJobAssignment', 'brain.tools.bulk_operations', 'BulkJobAssignmentTool')
        self.tool_registry.register_lazy('AddJobPhoto', 'brain.tools.admin_tools', 'AddJobPhotoTool')
        self.tool_registry.register_lazy('AddEquipmentBooking', 'brain.tools.admin_tools', 'AddEquipmentBookingTool')
        self.tool_registry.register_lazy('CompleteChecklistItem', 'brain.tools.admin_tools', 'CompleteChecklistItemTool')
        self.tool_registry.register_lazy('AddEquipmentLog', 'brain.tools.admin_tools', 'AddEquipmentLogTool')
        self.tool_registry.register_lazy('AddSupplier', 'brain.tools.admin_tools', 'AddSupplierTool')
        self.tool_registry.register_lazy('AddRole', 'brain.tools.admin_tools', 'AddRoleTool')
        self.tool_registry.register_lazy('SetRolePermissions', 'brain.tools.admin_tools', 'SetRolePermissionsTool')
        self.tool_registry.register_lazy('CreateTeam', 'brain.tools.admin_tools', 'CreateTeamTool')
        self.tool_registry.register_lazy('AddTeamMember', 'brain.tools.admin_tools', 'AddTeamMemberTool')
        self.tool_registry.register_lazy('SetPayRule', 'brain.tools.admin_tools', 'SetPayRuleTool')
        self.tool_registry.register_lazy('AddBonus', 'brain.tools.admin_tools', 'AddBonusTool')
        self.tool_registry.register_lazy('CreateInventoryItem', 'brain.tools.admin_tools', 'CreateInventoryItemTool')
        self.tool_registry.register_lazy('CreateCompany', 'brain.tools.admin_tools', 'CreateCompanyTool')
        self.tool_registry.register_lazy('UpdateCompany', 'brain.tools.admin_tools', 'UpdateCompanyTool')
        self.tool_registry.register_lazy('AddJobSignOff', 'brain.tools.job_extensions', 'AddJobSignOffTool')
        self.tool_registry.register_lazy('AddJobVariation', 'brain.tools.job_extensions', 'AddJobVariationTool')
        self.tool_registry.register_lazy('AddJobMeasurement', 'brain.tools.job_extensions', 'AddJobMeasurementTool')
        self.tool_registry.register_lazy('AddJobStatusUpdate', 'brain.tools.job_extensions', 'AddJobStatusUpdateTool')
        self.tool_registry.register_lazy('AddJobMaterial', 'brain.tools.job_extensions', 'AddJobMaterialTool')
        self.tool_registry.register_lazy('AddRecurring', 'brain.tools.recurring_job_tools', 'AddRecurringTool')
        self.tool_registry.register_lazy('UpdateRecurringJob', 'brain.tools.recurring_job_tools', 'UpdateRecurringJobTool')
        self.tool_registry.register_lazy('AddRecurringSkipDate', 'brain.tools.recurring_job_tools', 'AddRecurringSkipDateTool')
        self.tool_registry.register_lazy('DeleteRecurringSkipDate', 'brain.tools.recurring_job_tools', 'DeleteRecurringSkipDateTool')
        self.tool_registry.register_lazy('AddPhotoApproval', 'brain.tools.misc_tools', 'AddPhotoApprovalTool')
        self.tool_registry.register_lazy('UpdatePhotoApprovalStatus', 'brain.tools.misc_tools', 'UpdatePhotoApprovalStatusTool')
        self.tool_registry.register_lazy('AddVehicle', 'brain.tools.misc_tools', 'AddVehicleTool')
        self.tool_registry.register_lazy('UpdateVehicle', 'brain.tools.misc_tools', 'UpdateVehicleTool')
        self.tool_registry.register_lazy('AddTool', 'brain.tools.misc_tools', 'AddToolTool')
        self.tool_registry.register_lazy('AddTemplateMaterial', 'brain.tools.misc_tools', 'AddTemplateMaterialTool')
        self.tool_registry.register_lazy('AddTemplateTool', 'brain.tools.misc_tools', 'AddTemplateToolTool')
        self.tool_registry.register_lazy('AddComplianceDocument', 'brain.tools.misc_tools', 'AddComplianceDocumentTool')
        self.tool_registry.register_lazy('AddRequestAttachment', 'brain.tools.misc_tools', 'AddRequestAttachmentTool')
        self.tool_registry.register_lazy('AddRequestComment', 'brain.tools.misc_tools', 'AddRequestCommentTool')
        self.tool_registry.register_lazy('UpdateChangeRequestStatus', 'brain.tools.misc_tools', 'UpdateChangeRequestStatusTool')
        self.tool_registry.register_lazy('AddDeduction', 'brain.tools.misc_tools', 'AddDeductionTool')
        self.tool_registry.register_lazy('AddEntitlement', 'brain.tools.misc_tools', 'AddEntitlementTool')
        self.tool_registry.register_lazy('UpdateMessageTemplate', 'brain.tools.misc_tools', 'UpdateMessageTemplateTool')
        self.tool_registry.register_lazy('AddExpenseCategory', 'brain.tools.misc_tools', 'AddExpenseCategoryTool')
        self.tool_registry.register_lazy('AddAuditLog', 'brain.tools.misc_tools', 'AddAuditLogTool')

    def run(self, event: CommandEvent) -> BrainResult:
        """
        Execute a command.

        This is the main entry point for all command execution.
        """
        start_time = time.time()
        import os
        is_dev = os.getenv('ENVIRONMENT') == 'development'
        try:
            import os
            is_dev = os.getenv('ENVIRONMENT') == 'development'

            # Normalize params: some callers may pass JSON strings or bytes
            try:
                if not isinstance(event.params, dict):
                    if isinstance(event.params, (str, bytes)):
                        try:
                            event.params = json.loads(event.params)
                        except Exception:
                            event.params = {'_raw': event.params}
                    elif event.params is None:
                        event.params = {}
                    else:
                        # Attempt to coerce mapping-like objects to dict
                        try:
                            event.params = dict(event.params)
                        except Exception:
                            event.params = {}
            except Exception:
                event.params = {}

            # 1. Bypass Sanity/Loop Check
            if not is_dev:
                if not self.safety_middleware.check_sanity(user_id=event.user_id, command_type=event.command_type, params=event.params):
                    return BrainResult.fail(error_message='System Loop Detected: Command blocked for safety.', error_code='BRAIN_LOOP_DETECTED')

            # 2. Force Max Confidence for Dev
            confidence_score = 1.0 if is_dev else event.params.get('ai_confidence_score', 1.0)
            if HAS_CRYPTO_ENGINE and isinstance(event.params, (str, bytes)):
                try:
                    decrypted_params = crypto_engine.decrypt_data(event.params)
                    event.params = decrypted_params
                    logger.debug(f'Decrypted command params for {event.command_type}')
                except ValueError as e:
                    logger.warning(f'Decryption failed for {event.command_type}: {e} (assuming unencrypted)')
                except Exception as e:
                    logger.error(f'Unexpected decryption error for {event.command_type}: {e}', exc_info=True)
            risk_tier = self.router.get_risk_tier(event.command_type)
            self.audit_logger.log_command_received(event, risk_tier)
            policy_result = self.policy_engine.check(event)
            if policy_result.is_denied:
                result = BrainResult(success=False, status='DENIED', error_code=policy_result.error_code, error_message=policy_result.message, command_id=event.command_id, command_type=event.command_type)
                duration_ms = int((time.time() - start_time) * 1000)
                self.audit_logger.log_command_completed(event.command_id, result, duration_ms)
                return result
            if policy_result.is_duplicate:
                result = BrainResult(success=True, status='DUPLICATE', data=policy_result.cached_result, command_id=event.command_id, command_type=event.command_type)
                duration_ms = int((time.time() - start_time) * 1000)
                self.audit_logger.log_command_completed(event.command_id, result, duration_ms)
                return result
            if self.entitlement_checking_enabled and self.local_first_manager and event.company_id:
                try:
                    allowed, error_msg, upgrade_info = self.local_first_manager.check_command_entitlement(event.command_type, event.company_id)
                    if not allowed:
                        result = BrainResult(success=False, status='ENTITLEMENT_REQUIRED', error_code='BRAIN_ENTITLEMENT_REQUIRED', error_message=error_msg, command_id=event.command_id, command_type=event.command_type, data=upgrade_info if upgrade_info else {'upgrade_required': True})
                        duration_ms = int((time.time() - start_time) * 1000)
                        self.audit_logger.log_command_completed(event.command_id, result, duration_ms)
                        return result
                except Exception as e:
                    logger.warning(f'Entitlement check failed for {event.command_type}: {e}')
            state_info = self.COMMAND_STATE_MAPPING.get(event.command_type)
            state_before = None
            state_after = None
            entity_type = None
            entity_id = None
            if state_info:
                entity_type = state_info.get('entity', 0)
                target_state = state_info.get('state', 0)
                if event.command_type not in ['JobCreate', 'InvoiceCreate']:
                    entity_id = event.params.get(f'{entity_type}_id') or event.params.get('id')
                    if entity_id:
                        transition_attempt = self.state_machine_manager.validate_transition(entity_type=entity_type, entity_id=entity_id, command=event.command_type, new_state=target_state, context=event.params)
                        if not transition_attempt.success:
                            result = BrainResult(success=False, status='INVALID_TRANSITION', error_code='BRAIN_INVALID_STATE_TRANSITION', error_message=transition_attempt.error_message or 'Invalid state transition', command_id=event.command_id, command_type=event.command_type, entity_type=entity_type, entity_id=entity_id, state_before=transition_attempt.from_state, state_after=target_state)
                            self.audit_logger.log_state_transition(command_id=event.command_id, entity_type=entity_type, entity_id=entity_id, state_before=transition_attempt.from_state, state_after=target_state, transition_valid=False, preconditions_met=transition_attempt.result != TransitionResult.PRECONDITION_FAILED)
                            duration_ms = int((time.time() - start_time) * 1000)
                            self.audit_logger.log_command_completed(event.command_id, result, duration_ms)
                            return result
                        state_before = transition_attempt.from_state
                        state_after = target_state
            confidence_decision = self.learning_mode_middleware.check_execution_gate(user_id=event.user_id, command_type=event.command_type, risk_tier=risk_tier, confidence_score=confidence_score)
            self.learning_mode_middleware.log_confidence_decision(user_id=event.user_id, command_type=event.command_type, decision=confidence_decision, user_response=None)
            if not confidence_decision.should_execute:
                if confidence_decision.requires_nuclear_codes:
                    if self.fork_engine:
                        dry_run_result = self._execute_dry_run(event)
                        result = BrainResult(success=False, status='NUCLEAR_CODES_REQUIRED', requires_confirmation=True, requires_nuclear_codes=True, command_id=event.command_id, command_type=event.command_type, dry_run_preview=dry_run_result.to_dict() if dry_run_result.success else None, confirmation_phrase=self._get_confirmation_phrase(event.command_type), error_message=confidence_decision.reason)
                    else:
                        result = BrainResult(success=False, status='NUCLEAR_CODES_REQUIRED', requires_confirmation=True, requires_nuclear_codes=True, command_id=event.command_id, command_type=event.command_type, confirmation_phrase=self._get_confirmation_phrase(event.command_type), error_message=confidence_decision.reason)
                    duration_ms = int((time.time() - start_time) * 1000)
                    self.audit_logger.log_command_completed(event.command_id, result, duration_ms)
                    return result
                elif confidence_decision.requires_socratic:
                    result = BrainResult(success=False, status='SOCRATIC_CONFIRMATION_REQUIRED', requires_confirmation=True, requires_socratic=True, command_id=event.command_id, command_type=event.command_type, confidence_score=confidence_decision.confidence_score, learning_mode=confidence_decision.learning_mode, error_message=confidence_decision.reason)
                    duration_ms = int((time.time() - start_time) * 1000)
                    self.audit_logger.log_command_completed(event.command_id, result, duration_ms)
                    return result
            # 3. Bypass Router Confirmation in Dev
            requires_confirmation = self.router.requires_confirmation(event.command_type) and not is_dev
            if requires_confirmation and (not event.confirmation_token):
                if self.fork_engine:
                    dry_run_result = self._execute_dry_run(event)
                    if dry_run_result.success:
                        token = self.confirmation_manager.generate_token(command_type=event.command_type, params=event.params, user_id=event.user_id, company_id=event.company_id, dry_run_result=dry_run_result.to_dict())
                        result = BrainResult(success=False, status='CONFIRMATION_REQUIRED', requires_confirmation=True, command_id=event.command_id, command_type=event.command_type, confirmation_token=token.token, confirmation_expires_at=token.expires_at, dry_run_preview=dry_run_result.to_dict(), error_message='This command requires confirmation')
                    else:
                        result = BrainResult(success=False, status='DRY_RUN_FAILED', command_id=event.command_id, command_type=event.command_type, error_code='BRAIN_DRY_RUN_FAILED', error_message=dry_run_result.error)
                else:
                    result = BrainResult(success=False, status='CONFIRMATION_REQUIRED', requires_confirmation=True, command_id=event.command_id, command_type=event.command_type, error_message='This command requires confirmation')
                duration_ms = int((time.time() - start_time) * 1000)
                self.audit_logger.log_command_completed(event.command_id, result, duration_ms)
                return result
            if event.confirmation_token:
                is_valid, error_msg = self.confirmation_manager.validate_token(token=event.confirmation_token, command_type=event.command_type, user_id=event.user_id, company_id=event.company_id)
                if not is_valid:
                    result = BrainResult(success=False, status='INVALID_CONFIRMATION', command_id=event.command_id, command_type=event.command_type, error_code='BRAIN_INVALID_CONFIRMATION_TOKEN', error_message=error_msg)
                    duration_ms = int((time.time() - start_time) * 1000)
                    self.audit_logger.log_command_completed(event.command_id, result, duration_ms)
                    return result
            self.audit_logger.log_command_started(event.command_id)
            plan = self.router.route(event)
            tool_results = []
            for tool_call in plan:
                tool_name = tool_call.get('tool', 0)
                tool_params = tool_call.get('params', 0)
                if 'user_id' not in tool_params:
                    tool_params = {**tool_params, 'user_id': event.user_id}
                if 'company_id' not in tool_params:
                    tool_params = {**tool_params, 'company_id': event.company_id}
                self._current_tool_executing = tool_name
                tool_output = self.tool_registry.execute(tool_name, tool_params)
                self._current_tool_executing = None
                tool_results.append({'tool': tool_name, 'success': tool_output.success, 'data': tool_output.data, 'error': tool_output.error_message})
                self.audit_logger.log_tool_call(event.command_id, tool_name, tool_params, tool_output.data, tool_output.success, tool_output.error_code, tool_output.error_message)
                if not tool_output.success:
                    result = BrainResult(success=False, status='FAILED', error_code=tool_output.error_code, error_message=tool_output.error_message, command_id=event.command_id, command_type=event.command_type, plan=plan, tool_results=tool_results)
                    duration_ms = int((time.time() - start_time) * 1000)
                    self.audit_logger.log_command_completed(event.command_id, result, duration_ms, plan, tool_results)
                    return result
            last_tool_data = tool_results[-1].get('data', 0) if tool_results else None
            if entity_type and entity_id is None and last_tool_data:
                entity_id = last_tool_data.get(f'{entity_type}_id')
                if entity_id and state_info:
                    state_after = state_info.get('state', 0)
            result = BrainResult(success=True, status='SUCCESS', data=last_tool_data, command_id=event.command_id, command_type=event.command_type, plan=plan, tool_results=tool_results, entity_type=entity_type, entity_id=entity_id, state_before=state_before, state_after=state_after)
            if entity_type and entity_id and state_after:
                self.audit_logger.log_state_transition(command_id=event.command_id, entity_type=entity_type, entity_id=entity_id, state_before=state_before or 'NEW', state_after=state_after, transition_valid=True, preconditions_met=True)
            duration_ms = int((time.time() - start_time) * 1000)
            self.audit_logger.log_command_completed(event.command_id, result, duration_ms, plan, tool_results)
            self._invalidate_caches_for_command(event.command_type, entity_type)
            if event.confirmation_token:
                self.confirmation_manager.consume_token(event.confirmation_token)
            return result
        except Exception as e:
            stack_trace = traceback.format_exc()
            if HAS_DEBUG_CONSOLE:
                try:
                    debug_console.log_error(e, context=f'Command {event.command_type}')
                except Exception:
                    pass
            import sys
            print(f'[BRAIN ERROR] Command {event.command_id}: {str(e)}', file=sys.stderr)
            print(stack_trace, file=sys.stderr)
            try:
                from services.mechanic import CrashReport, save_crash_report
                import uuid
                from services.flight_recorder import FlightRecorder
                flight_recorder = FlightRecorder()
                flight_history = flight_recorder.capture_snapshot(event.user_id, event_count=50)
                crashed_tool = None
                if hasattr(self, '_current_tool_executing'):
                    crashed_tool = self._current_tool_executing
                crash_report = CrashReport(crash_id=str(uuid.uuid4()), command_event=event, error=e, stack_trace=stack_trace, tool_name=crashed_tool, flight_recorder_data=flight_history)
                save_crash_report(crash_report)
                logger.info(f'Crash report saved: {crash_report.crash_id}')
            except Exception as mechanic_error:
                logger.error(f'Failed to save crash report: {mechanic_error}')
            import os
            env = os.getenv('ENVIRONMENT', 'production').lower()
            include_stack_trace = env in ['development', 'dev', 'test']
            result = BrainResult(success=False, status='FAILED', error_code='BRAIN_UNEXPECTED_ERROR', error_message='An unexpected error occurred. Please contact support.' if not include_stack_trace else str(e), stack_trace=stack_trace if include_stack_trace else None, command_id=event.command_id, command_type=event.command_type)
            duration_ms = int((time.time() - start_time) * 1000)
            self.audit_logger.log_command_completed(event.command_id, result, duration_ms)
            return result

    def run_encrypted(self, encrypted_packet: bytes) -> BrainResult:
        """
        Secure Entry Point: Decrypts a neural packet and executes the command.
        
        This method provides an encrypted command channel using the Neural Command Link.
        Commands are encrypted with daily rotating keys for enhanced security.
        
        Args:
            encrypted_packet: Encrypted command packet bytes
            
        Returns:
            BrainResult with execution outcome
        """
        if not self.neural_link:
            return BrainResult(success=False, status='ERROR', error_message='Neural Command Link is disabled or not initialized.')
        try:
            command_data = self.neural_link.decrypt_packet(encrypted_packet)
            event = CommandEvent.from_dict(command_data)
            logger.info(f'SECURE CHANNEL: Received {event.command_type} (ID: {event.command_id})')
            return self.run(event)
        except Exception as e:
            logger.error(f'Neural Decryption Failed: {e}')
            return BrainResult(success=False, status='SECURITY_FAILURE', error_code='NEURAL_DECRYPTION_FAILED', error_message=f'Decryption failed. Check Daily Key rotation. ({str(e)})')

    def _execute_dry_run(self, event: CommandEvent) -> DryRunResult:
        """
        Execute command in dry-run mode using fork engine.
        
        Args:
            event: Command event to execute
            
        Returns:
            DryRunResult with preview of changes
        """
        # Import here to avoid circular import
        from brain.fork.engine import DryRunResult
        
        import db
        try:
            with self.fork_engine.fork() as fork_context:
                with db.override_connection(self.fork_engine.db_connection):
                    plan = self.router.route(event)
                    state_info = self.COMMAND_STATE_MAPPING.get(event.command_type)
                    if state_info:
                        entity_type = state_info.get('entity', 0)
                        entity_id = event.params.get(f'{entity_type}_id') or event.params.get('id')
                        if entity_id:
                            fork_context.track_entity(entity_type, entity_id)
                    new_entity_id = None
                    for tool_call in plan:
                        tool_name = tool_call.get('tool', 0)
                        tool_params = tool_call.get('params', 0)
                        if 'company_id' not in tool_params:
                            tool_params = {**tool_params, 'company_id': event.company_id}
                        tool_output = self.tool_registry.execute(tool_name, tool_params)
                        if not tool_output.success:
                            return DryRunResult(success=False, affected_entities=[], diffs=[], new_entities=[], error=tool_output.error_message)
                        if tool_output.data and state_info:
                            new_entity_id = tool_output.data.get(f"{state_info.get('entity', 0)}_id")
                            if new_entity_id and event.command_type in ['JobCreate', 'InvoiceCreate']:
                                fork_context.track_new_entity(state_info.get('entity', 0), new_entity_id)
                    diffs = fork_context.get_diffs()
                    new_entities = fork_context.get_new_entities()
                    affected = fork_context.get_affected_entities()
                    return DryRunResult(success=True, affected_entities=affected, diffs=diffs, new_entities=new_entities)
        except Exception as e:
            return DryRunResult(success=False, affected_entities=[], diffs=[], new_entities=[], error=f'Dry-run execution failed: {str(e)}')

    def _invalidate_caches_for_command(self, command_type: str, entity_type: str=None):
        """
        Invalidate relevant caches after successful command execution.
        
        This ensures cached data remains consistent with database updates.
        Called automatically after successful write operations.
        
        Note: Currently clears ALL Streamlit caches due to framework limitations.
        For production deployments with many concurrent users, consider Redis
        with key-pattern-based invalidation for more granular control.
        
        Args:
            command_type: The command that was executed (e.g., "CustomerCreate")
            entity_type: The entity type affected (e.g., "customer", "job")
        """
        if not HAS_CACHE_MANAGER:
            return
        try:
            if command_type in ['CustomerCreate', 'CustomerUpdate', 'CustomerDelete'] or entity_type == 'customer':
                clear_customer_caches()
            if command_type.startswith('Job') or entity_type == 'job':
                clear_job_caches()
            if command_type in ['InvoiceCreate', 'InvoiceSend', 'InvoiceVoid', 'PaymentRecord', 'PaymentRefund', 'ExpenseCreate', 'ExpenseUpdate', 'ExpenseDelete', 'CreditNoteCreate']:
                clear_profitability_caches()
            if command_type in ['JobComplete', 'JobAddSignOff']:
                clear_profitability_caches()
        except Exception as e:
            import sys
            print(f'Warning: Failed to invalidate caches for {command_type}: {e}', file=sys.stderr)

    def _get_confirmation_phrase(self, command_type: str) -> str:
        """
        Get the required confirmation phrase for Nuclear Codes Modal.
        
        Sentient System Phase 2: Maps command types to their confirmation phrases.
        This integrates with components_nuclear_modal.py.
        
        Args:
            command_type: The command type (e.g., "CustomerDelete")
            
        Returns:
            The confirmation phrase required for this command
        """
        from components_nuclear_modal import get_confirmation_phrase_for_command
        return get_confirmation_phrase_for_command(command_type)
