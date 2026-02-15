"""
Router - Routes commands to execution plans

FUTURE ENHANCEMENT OPPORTUNITY - SEMANTIC ROUTING:
Currently uses string matching and regex to route commands to tools.
For improved AI capabilities, consider implementing Semantic Router:

1. Semantic Understanding:
   - Embed user requests into vectors (using OpenAI/Anthropic embeddings)
   - Compare request vectors against tool description vectors
   - Match by semantic similarity rather than keyword matching
   
2. Benefits:
   - "Bill John" → CreateInvoice (no hardcoded string match needed)
   - "Send invoice to John" → CreateInvoice + InvoiceSend
   - "Charge John" → CreateInvoice
   - All understood as the same intent without hundreds of if/else rules
   
3. Implementation:
   - Use langchain SemanticRouter or implement with embeddings
   - Store tool embeddings in registry at startup
   - At runtime: embed(user_query) → find_nearest(tool_embeddings)
   - Threshold for confidence (e.g., similarity > 0.85)
   
4. Example code:
   from langchain.embeddings import OpenAIEmbeddings
   from sklearn.metrics.pairwise import cosine_similarity
   
   embeddings = OpenAIEmbeddings()
   query_vec = embeddings.embed_query("bill john for lawn service")
   tool_vecs = [embeddings.embed_query(tool.description) for tool in tools]
   similarities = cosine_similarity([query_vec], tool_vecs)
   best_match = tools[similarities.argmax()]

This would make the Brain truly intelligent rather than pattern-matching.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from brain.core.command_event import CommandEvent
from brain.core.enums import RiskTier


class Router:
    """
    Routes commands to execution plans.

    The router determines:
    - Which tools to call for a command
    - In what order to call them
    - Risk tier of the command
    """

    # Risk tier assignments
    RISK_TIERS = {
        # Tier 1: Trivial (read-only, safe updates)
        "JobAddNote": RiskTier.TRIVIAL,
        "JobAddPhoto": RiskTier.TRIVIAL,
        "CustomerAddNote": RiskTier.TRIVIAL,
        "GetJob": RiskTier.TRIVIAL,
        "GetCustomer": RiskTier.TRIVIAL,
        "GetInvoice": RiskTier.TRIVIAL,
        "GetPayment": RiskTier.TRIVIAL,
        "GetReconciliationHistory": RiskTier.TRIVIAL,

        # Tier 2: Low (standard operations)
        "JobCreate": RiskTier.LOW,
        "JobUpdate": RiskTier.LOW,
        "JobSchedule": RiskTier.LOW,
        "CalculateJobActuals": RiskTier.LOW,  # Calculate actual costs from time entries
        "CustomerCreate": RiskTier.LOW,
        "CustomerUpdate": RiskTier.LOW,
        "TimeClockIn": RiskTier.LOW,
        "TimeClockOut": RiskTier.LOW,
        "WorkLogAdd": RiskTier.LOW,
        "WorkLogUpdate": RiskTier.LOW,
        "TimesheetApprove": RiskTier.MEDIUM,  # Manager approval
        "TimesheetReject": RiskTier.MEDIUM,    # Manager action

        # Tier 3: Medium (customer-facing)
        "JobQuote": RiskTier.MEDIUM,
        "JobBook": RiskTier.MEDIUM,
        "JobComplete": RiskTier.MEDIUM,
        "QuoteCreate": RiskTier.MEDIUM,
        "AddQuoteLineItem": RiskTier.MEDIUM,
        "AddQuoteItem": RiskTier.MEDIUM,  # Legacy quote_items table
        "QuoteSend": RiskTier.MEDIUM,
        "QuoteAccept": RiskTier.MEDIUM,
        "QuoteDecline": RiskTier.MEDIUM,
        "QuoteConvertToJob": RiskTier.MEDIUM,
        "GetQuote": RiskTier.TRIVIAL,
        "ReconcileInvariants": RiskTier.MEDIUM,  # Check data integrity

        # Tier 4: High (money, bulk comms, role changes)
        "InvoiceCreate": RiskTier.HIGH,
        "InvoiceSend": RiskTier.HIGH,
        "PaymentRecord": RiskTier.HIGH,
        "PaymentRecordDeposit": RiskTier.HIGH,
        "PaymentRecordBalance": RiskTier.HIGH,
        "MessageSendBulkSMS": RiskTier.HIGH,
        "MessageSendBulkEmail": RiskTier.HIGH,
        "SetUserRole": RiskTier.HIGH,  # Role changes are high risk

        # Tier 3: Medium (crew management)
        "AssignCrew": RiskTier.MEDIUM,
        "UnassignCrew": RiskTier.MEDIUM,
        "CreateUser": RiskTier.MEDIUM,
        "UpdateUser": RiskTier.LOW,
        "UpdateCompany": RiskTier.LOW,
        "ActivateUser": RiskTier.MEDIUM,
        "DeactivateUser": RiskTier.MEDIUM,

        # Tier 2-3: Job & Customer Management (Phase 4B)
        "UpdateJobStatus": RiskTier.LOW,
        "AddJobNote": RiskTier.TRIVIAL,
        "UpdateCustomer": RiskTier.LOW,
        "AddCustomerNote": RiskTier.TRIVIAL,

        # Tier 1: Audit & History (Phase 4C)
        "ViewAuditLog": RiskTier.TRIVIAL,

        # Tier 3-4: Communication Tools (Phase 4B)
        "SendMessage": RiskTier.MEDIUM,
        "SendBulkMessage": RiskTier.HIGH,  # Bulk requires confirmation
        "ScheduleMessage": RiskTier.MEDIUM,
        "CancelMessage": RiskTier.LOW,
        "SendInvoiceEmail": RiskTier.MEDIUM,
        "SendQuoteEmail": RiskTier.MEDIUM,
        "SendJobConfirmation": RiskTier.MEDIUM,
        "SendJobReminder": RiskTier.MEDIUM,

        # Tier 2-4: Materials & Inventory Tools (Phase 4C)
        "MaterialCreate": RiskTier.MEDIUM,
        "MaterialUpdate": RiskTier.LOW,
        "MaterialDelete": RiskTier.HIGH,  # Requires confirmation
        "InventoryAdjust": RiskTier.MEDIUM,
        "MaterialRecordUsage": RiskTier.MEDIUM,
        "MaterialReorder": RiskTier.LOW,

        # Tier 2-3: Scheduling Tools (Phase 4D)
        "ScheduleJob": RiskTier.MEDIUM,
        "RescheduleJob": RiskTier.MEDIUM,
        "CheckAvailability": RiskTier.LOW,
        "BookResource": RiskTier.MEDIUM,
        "ReleaseResource": RiskTier.LOW,
        "CreateRecurringJob": RiskTier.MEDIUM,

        # Tier 2-4: Expense Tools (Phase 4E)
        "RecordExpense": RiskTier.MEDIUM,
        "UpdateExpense": RiskTier.LOW,
        "DeleteExpense": RiskTier.HIGH,  # Requires confirmation
        "LinkExpenseToJob": RiskTier.LOW,

        # Tier 3-5: Credit Note Tools (Phase 4E)
        "CreateCreditNote": RiskTier.MEDIUM,
        "IssueCreditNote": RiskTier.HIGH,  # Requires confirmation
        "ApplyCreditNote": RiskTier.MEDIUM,
        "VoidCreditNote": RiskTier.HIGH,  # Requires confirmation

        # Tier 2-3: Portal Tools (Phase 5)
        "GeneratePortalToken": RiskTier.MEDIUM,  # Creates public access
        "RevokePortalToken": RiskTier.MEDIUM,  # Removes access

        # Bulk Operations (Phase 3 - Advanced Features)
        "BulkJobStatusUpdate": RiskTier.HIGH,  # Requires confirmation - affects multiple jobs
        "BulkDeleteExpenses": RiskTier.CRITICAL,  # Requires confirmation - destructive bulk operation
        "BulkJobAssignment": RiskTier.MEDIUM,  # Affects multiple jobs but reversible

        # Tier 5: Critical (irreversible, destructive)
        "JobDelete": RiskTier.CRITICAL,
        "CustomerDelete": RiskTier.CRITICAL,
        "InvoiceVoid": RiskTier.CRITICAL,
        "InvoiceDelete": RiskTier.CRITICAL,
        "PaymentRefund": RiskTier.CRITICAL,
        "PaymentDelete": RiskTier.CRITICAL,
        "UserDelete": RiskTier.CRITICAL,
        "TemplateDelete": RiskTier.CRITICAL,
        "RoleDelete": RiskTier.CRITICAL,
        
        # Tier 4: High (delete operations requiring confirmation)
        "SupplierDelete": RiskTier.HIGH,
        "TeamDelete": RiskTier.HIGH,
        "RecurringJobDelete": RiskTier.HIGH,
        
        # Tier 3: Medium (removal operations)
        "TeamMemberRemove": RiskTier.MEDIUM,
        "JobMaterialDelete": RiskTier.MEDIUM,
        
        # Tier 2: Low (soft deletes or temporary items)
        "QuoteItemDelete": RiskTier.LOW,
    }

    def get_risk_tier(self, command_type: str) -> RiskTier:
        """Get risk tier for command"""
        return self.RISK_TIERS.get(command_type, RiskTier.LOW)

    def requires_confirmation(self, command_type: str) -> bool:
        """Check if command requires confirmation"""
        risk_tier = self.get_risk_tier(command_type)
        return risk_tier >= RiskTier.HIGH

    def route(self, event: CommandEvent) -> list[dict]:
        """
        Route command to execution plan.

        Returns list of tool calls to execute.
        """
        command_type = event.command_type

        # Map command to tool calls
        # For now, simple 1:1 mapping of command to tool
        # Later, this will be more sophisticated

        if command_type == "JobCreate":
            return [{"tool": "CreateJob", "params": event.params}]

        if command_type == "JobUpdate":
            return [{"tool": "UpdateJob", "params": event.params}]

        if command_type == "CustomerCreate":
            return [{"tool": "CreateCustomer", "params": event.params}]

        if command_type == "InvoiceCreate":
            return [{"tool": "CreateInvoice", "params": event.params}]

        if command_type == "PaymentRecord":
            return [{"tool": "RecordPayment", "params": event.params}]

        if command_type == "InvoiceSend":
            return [{"tool": "SendInvoice", "params": event.params}]

        if command_type == "GetInvoice":
            return [{"tool": "GetInvoice", "params": event.params}]

        if command_type == "GetPayment":
            return [{"tool": "GetPayment", "params": event.params}]
        
        if command_type == "ReconcileInvariants":
            return [{"tool": "ReconcileInvariants", "params": event.params}]
        
        if command_type == "GetReconciliationHistory":
            return [{"tool": "GetReconciliationHistory", "params": event.params}]
        
        # Quote commands
        if command_type == "QuoteCreate":
            return [{"tool": "CreateQuote", "params": event.params}]
        
        if command_type == "AddQuoteLineItem":
            return [{"tool": "AddQuoteLineItem", "params": event.params}]
        
        if command_type == "AddQuoteItem":
            return [{"tool": "AddQuoteItem", "params": event.params}]
        
        if command_type == "QuoteSend":
            return [{"tool": "SendQuote", "params": event.params}]
        
        if command_type == "QuoteAccept":
            return [{"tool": "AcceptQuote", "params": event.params}]
        
        if command_type == "QuoteDecline":
            return [{"tool": "DeclineQuote", "params": event.params}]
        
        if command_type == "GetQuote":
            return [{"tool": "GetQuote", "params": event.params}]
        
        if command_type == "QuoteConvertToJob":
            return [{"tool": "ConvertQuoteToJob", "params": event.params}]
        
        # Time tracking commands
        if command_type == "TimeClockIn":
            return [{"tool": "ClockIn", "params": event.params}]
        
        if command_type == "TimeClockOut":
            return [{"tool": "ClockOut", "params": event.params}]
        
        if command_type == "WorkLogAdd":
            return [{"tool": "AddWorkLog", "params": event.params}]
        
        if command_type == "WorkLogUpdate":
            return [{"tool": "UpdateWorkLog", "params": event.params}]
        
        if command_type == "TimesheetApprove":
            return [{"tool": "ApproveTimesheet", "params": event.params}]
        
        if command_type == "TimesheetReject":
            return [{"tool": "RejectTimesheet", "params": event.params}]
        
        # Crew management commands
        if command_type == "AssignCrew":
            return [{"tool": "AssignCrew", "params": event.params}]
        
        if command_type == "UnassignCrew":
            return [{"tool": "UnassignCrew", "params": event.params}]
        
        if command_type == "CreateUser":
            return [{"tool": "CreateUser", "params": event.params}]
        
        if command_type == "UpdateUser":
            return [{"tool": "UpdateUser", "params": event.params}]
        
        if command_type == "UpdateCompany":
            return [{"tool": "UpdateCompany", "params": event.params}]
        
        if command_type == "DeleteUser":
            return [{"tool": "DeleteUser", "params": event.params}]
        
        if command_type == "ActivateUser":
            return [{"tool": "ActivateUser", "params": event.params}]
        
        if command_type == "DeactivateUser":
            return [{"tool": "DeactivateUser", "params": event.params}]
        
        if command_type == "SetUserRole":
            return [{"tool": "SetUserRole", "params": event.params}]

        # Job & Customer management commands (Phase 4B)
        if command_type == "UpdateJobStatus":
            return [{"tool": "UpdateJobStatus", "params": event.params}]

        if command_type == "AddJobNote":
            return [{"tool": "AddJobNote", "params": event.params}]

        if command_type == "JobDelete":
            return [{"tool": "DeleteJob", "params": event.params}]

        if command_type == "UpdateCustomer":
            return [{"tool": "UpdateCustomer", "params": event.params}]

        if command_type == "AddCustomerNote":
            return [{"tool": "AddCustomerNote", "params": event.params}]

        if command_type == "CustomerDelete":
            return [{"tool": "DeleteCustomer", "params": event.params}]

        # Audit & History commands (Phase 4C)
        if command_type == "ViewAuditLog":
            return [{"tool": "ViewAuditLog", "params": event.params}]

        # Communication commands (Phase 4B)
        if command_type == "SendMessage":
            return [{"tool": "SendMessage", "params": event.params}]

        if command_type == "SendBulkMessage":
            return [{"tool": "SendBulkMessage", "params": event.params}]

        if command_type == "ScheduleMessage":
            return [{"tool": "ScheduleMessage", "params": event.params}]

        if command_type == "CancelMessage":
            return [{"tool": "CancelMessage", "params": event.params}]

        if command_type == "SendInvoiceEmail":
            return [{"tool": "SendInvoiceEmail", "params": event.params}]

        if command_type == "SendQuoteEmail":
            return [{"tool": "SendQuoteEmail", "params": event.params}]

        if command_type == "SendJobConfirmation":
            return [{"tool": "SendJobConfirmation", "params": event.params}]

        if command_type == "SendJobReminder":
            return [{"tool": "SendJobReminder", "params": event.params}]

        # Materials & Inventory commands (Phase 4C)
        if command_type == "MaterialCreate":
            return [{"tool": "CreateMaterial", "params": event.params}]

        if command_type == "MaterialUpdate":
            return [{"tool": "UpdateMaterial", "params": event.params}]

        if command_type == "MaterialDelete":
            return [{"tool": "DeleteMaterial", "params": event.params}]

        if command_type == "InventoryAdjust":
            return [{"tool": "AdjustInventory", "params": event.params}]

        if command_type == "MaterialRecordUsage":
            return [{"tool": "RecordUsage", "params": event.params}]

        if command_type == "MaterialReorder":
            return [{"tool": "ReorderMaterial", "params": event.params}]

        # Scheduling commands (Phase 4D)
        if command_type == "ScheduleJob":
            return [{"tool": "ScheduleJob", "params": event.params}]

        if command_type == "RescheduleJob":
            return [{"tool": "RescheduleJob", "params": event.params}]

        if command_type == "CheckAvailability":
            return [{"tool": "CheckAvailability", "params": event.params}]

        if command_type == "BookResource":
            return [{"tool": "BookResource", "params": event.params}]

        if command_type == "ReleaseResource":
            return [{"tool": "ReleaseResource", "params": event.params}]

        if command_type == "CreateRecurringJob":
            return [{"tool": "CreateRecurringJob", "params": event.params}]

        # Expense commands (Phase 4E)
        if command_type == "RecordExpense":
            return [{"tool": "RecordExpense", "params": event.params}]

        if command_type == "UpdateExpense":
            return [{"tool": "UpdateExpense", "params": event.params}]

        if command_type == "DeleteExpense":
            return [{"tool": "DeleteExpense", "params": event.params}]

        if command_type == "LinkExpenseToJob":
            return [{"tool": "LinkExpenseToJob", "params": event.params}]

        # Credit Note commands (Phase 4E)
        if command_type == "CreateCreditNote":
            return [{"tool": "CreateCreditNote", "params": event.params}]

        if command_type == "IssueCreditNote":
            return [{"tool": "IssueCreditNote", "params": event.params}]

        if command_type == "ApplyCreditNote":
            return [{"tool": "ApplyCreditNote", "params": event.params}]

        if command_type == "VoidCreditNote":
            return [{"tool": "VoidCreditNote", "params": event.params}]

        # Portal commands (Phase 5)
        if command_type == "GeneratePortalToken":
            return [{"tool": "GeneratePortalToken", "params": event.params}]

        if command_type == "RevokePortalToken":
            return [{"tool": "RevokePortalToken", "params": event.params}]

        # Additional delete commands
        if command_type == "TemplateDelete":
            return [{"tool": "DeleteTemplate", "params": event.params}]

        if command_type == "SupplierDelete":
            return [{"tool": "DeleteSupplier", "params": event.params}]

        if command_type == "RoleDelete":
            return [{"tool": "DeleteRole", "params": event.params}]

        if command_type == "TeamDelete":
            return [{"tool": "DeleteTeam", "params": event.params}]

        if command_type == "TeamMemberRemove":
            return [{"tool": "RemoveTeamMember", "params": event.params}]

        if command_type == "RecurringJobDelete":
            return [{"tool": "DeleteRecurringJob", "params": event.params}]

        if command_type == "JobMaterialDelete":
            return [{"tool": "DeleteJobMaterial", "params": event.params}]

        if command_type == "QuoteItemDelete":
            return [{"tool": "DeleteQuoteItem", "params": event.params}]

        # Default: assume tool name matches command type
        return [{"tool": command_type, "params": event.params}]
