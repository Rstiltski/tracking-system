# Command Namespace

**Rule:** Do not use scripts to edit code.

**Version:** 1.0
**Status:** Draft
**Last Updated:** 2026-01-01

## Overview

This document defines the **complete namespace of commands** that the Brain can execute. Every user action, scheduled task, or system operation must map to one of these commands.

## Command Naming Convention

```
<Domain><Entity><Action>
```

**Examples:**
- `JobCreate` - Create a new job
- `InvoiceSend` - Send an invoice to a customer
- `PaymentRecord` - Record a payment received
- `MessageSendSMS` - Send an SMS message

## Command Categories

Commands are organized into **10 domains**:

1. [Job Management](#1-job-management) (24 commands)
2. [Customer Management](#2-customer-management) (12 commands)
3. [Financial Operations](#3-financial-operations) (28 commands)
4. [Materials & Inventory](#4-materials--inventory) (10 commands)
5. [Crew & Time Tracking](#5-crew--time-tracking) (14 commands)
6. [Communication](#6-communication) (10 commands)
7. [Scheduling & Calendar](#7-scheduling--calendar) (8 commands)
8. [Action Queue](#8-action-queue) (6 commands)
9. [System & Admin](#9-system--admin) (12 commands)
10. [Portal & Customer Access](#10-portal--customer-access) (6 commands)

**Total Commands:** 130

---

## 1. Job Management

### Job Lifecycle

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `JobCreate` | Create a new job | 1 | ✅ Yes |
| `JobUpdate` | Update job details | 2 | ✅ Yes |
| `JobDelete` | Delete a job (soft delete) | 4 | ⚠️ No |
| `JobQuote` | Generate quote for a job | 2 | ✅ Yes |
| `JobBook` | Convert quote to booked appointment | 3 | ✅ Yes |
| `JobSchedule` | Assign date/time/crew to job | 2 | ✅ Yes |
| `JobReschedule` | Change job date/time | 3 | ✅ Yes |
| `JobStart` | Clock in crew, start job | 2 | ⚠️ No |
| `JobPause` | Pause ongoing job | 2 | ✅ Yes |
| `JobResume` | Resume paused job | 2 | ✅ Yes |
| `JobComplete` | Mark job as completed | 3 | ✅ Yes |
| `JobCancel` | Cancel a job | 4 | ✅ Yes |
| `JobReopen` | Reopen a completed/cancelled job | 3 | ✅ Yes |

### Job Details & Documentation

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `JobAddPhoto` | Upload photo to job | 1 | ✅ Yes |
| `JobDeletePhoto` | Remove photo from job | 2 | ⚠️ No |
| `JobAddNote` | Add internal note to job | 1 | ✅ Yes |
| `JobAddSignOff` | Record customer sign-off | 2 | ✅ Yes |
| `JobSetPriority` | Update job priority (Low/Med/High) | 1 | ✅ Yes |
| `JobSetNextAction` | Update next action status | 1 | ✅ Yes |

### Job Assignments & Resources

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `JobAssignCrew` | Assign crew member(s) to job | 2 | ✅ Yes |
| `JobUnassignCrew` | Remove crew assignment | 2 | ✅ Yes |
| `JobAssignVehicle` | Assign vehicle to job | 2 | ✅ Yes |
| `JobAddMaterial` | Add material requirement to job | 1 | ✅ Yes |
| `JobUpdateMeasurements` | Update property measurements | 2 | ✅ Yes |

---

## 2. Customer Management

### Customer CRUD

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `CustomerCreate` | Create new customer record | 1 | ✅ Yes |
| `CustomerUpdate` | Update customer details | 2 | ✅ Yes |
| `CustomerDelete` | Delete customer (soft delete) | 4 | ⚠️ No |
| `CustomerMerge` | Merge duplicate customers | 4 | ⚠️ No |

### Customer Relationship

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `CustomerAddNote` | Add note to customer record | 1 | ✅ Yes |
| `CustomerSetVIP` | Mark customer as VIP | 2 | ✅ Yes |
| `CustomerSetPaymentRisk` | Update payment risk status | 2 | ✅ Yes |
| `CustomerCalculateHealthScore` | Recalculate health score | 1 | ✅ Yes |
| `CustomerAddPhoto` | Add property photo | 1 | ✅ Yes |
| `CustomerSetPreferences` | Update customer preferences | 1 | ✅ Yes |
| `CustomerSetContactPreferences` | Update contact preferences (SMS/Email) | 1 | ✅ Yes |
| `CustomerRecordFeedback` | Record customer feedback | 1 | ✅ Yes |

---

## 3. Financial Operations

### Invoicing

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `InvoiceCreate` | Create invoice from job | 3 | ✅ Yes |
| `InvoiceUpdate` | Update invoice details | 3 | ✅ Yes |
| `InvoiceDelete` | Delete invoice (soft delete) | 5 | ⚠️ No |
| `InvoiceSend` | Send invoice to customer | 4 | ✅ Yes* |
| `InvoiceAddLineItem` | Add line item to invoice | 2 | ✅ Yes |
| `InvoiceRemoveLineItem` | Remove line item | 2 | ⚠️ No |
| `InvoiceMarkPaid` | Mark invoice as fully paid | 4 | ✅ Yes |
| `InvoiceMarkOverdue` | Flag invoice as overdue | 2 | ✅ Yes |
| `InvoiceVoid` | Void an invoice | 5 | ⚠️ No |

*Idempotent with deduplication check

### Payments

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `PaymentRecord` | Record payment received | 4 | ✅ Yes* |
| `PaymentRecordDeposit` | Record deposit payment | 4 | ✅ Yes* |
| `PaymentRecordBalance` | Record balance payment | 4 | ✅ Yes* |
| `PaymentRefund` | Process refund | 5 | ⚠️ No |
| `PaymentDelete` | Delete payment record | 5 | ⚠️ No |
| `PaymentGenerateReceipt` | Generate payment receipt | 2 | ✅ Yes |
| `PaymentSendReceipt` | Send receipt to customer | 3 | ✅ Yes* |

*Idempotent with deduplication check

### Quotes

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `QuoteCreate` | Create new quote | 2 | ✅ Yes |
| `QuoteUpdate` | Update quote details | 2 | ✅ Yes |
| `QuoteDelete` | Delete quote | 3 | ⚠️ No |
| `QuoteSend` | Send quote to customer | 3 | ✅ Yes* |
| `QuoteAccept` | Mark quote as accepted | 3 | ✅ Yes |
| `QuoteReject` | Mark quote as rejected | 2 | ✅ Yes |
| `QuoteExpire` | Mark quote as expired | 2 | ✅ Yes |

*Idempotent with deduplication check

### Expenses

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `ExpenseCreate` | Record new expense | 2 | ✅ Yes |
| `ExpenseUpdate` | Update expense details | 2 | ✅ Yes |
| `ExpenseDelete` | Delete expense | 3 | ⚠️ No |
| `ExpenseAddReceipt` | Attach receipt to expense | 1 | ✅ Yes |
| `ExpenseSetCategory` | Update expense category | 1 | ✅ Yes |

### Credit Notes

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `CreditNoteCreate` | Create credit note | 4 | ✅ Yes |
| `CreditNoteApply` | Apply credit to invoice | 4 | ⚠️ No |
| `CreditNoteVoid` | Void credit note | 5 | ⚠️ No |

---

## 4. Materials & Inventory

### Materials Management

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `MaterialCreate` | Add material to catalog | 1 | ✅ Yes |
| `MaterialUpdate` | Update material details/price | 2 | ✅ Yes |
| `MaterialDelete` | Remove material from catalog | 3 | ⚠️ No |
| `MaterialAdjustStock` | Adjust quantity on hand | 2 | ⚠️ No |
| `MaterialSetReorderPoint` | Update reorder threshold | 1 | ✅ Yes |
| `MaterialGeneratePurchaseOrder` | Generate PO for reorder | 2 | ✅ Yes |

### Suppliers

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `SupplierCreate` | Add supplier record | 1 | ✅ Yes |
| `SupplierUpdate` | Update supplier details | 1 | ✅ Yes |
| `SupplierDelete` | Remove supplier | 2 | ⚠️ No |
| `SupplierAddContact` | Add supplier contact info | 1 | ✅ Yes |

---

## 5. Crew & Time Tracking

### Time Entries

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `TimeClockIn` | Clock in for shift | 2 | ⚠️ No |
| `TimeClockOut` | Clock out from shift | 2 | ⚠️ No |
| `TimeStartBreak` | Start break | 1 | ⚠️ No |
| `TimeEndBreak` | End break | 1 | ⚠️ No |
| `TimeEntryCreate` | Manually create time entry | 2 | ✅ Yes |
| `TimeEntryUpdate` | Update time entry | 2 | ✅ Yes |
| `TimeEntryDelete` | Delete time entry | 3 | ⚠️ No |

### Timesheets & Approval

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `TimesheetSubmit` | Submit timesheet for approval | 2 | ✅ Yes |
| `TimesheetApprove` | Approve timesheet | 3 | ✅ Yes |
| `TimesheetReject` | Reject timesheet | 3 | ✅ Yes |
| `TimesheetCalculate` | Calculate weekly hours/cost | 1 | ✅ Yes |

### Crew Management

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `CrewSetAvailable` | Mark crew as available | 1 | ✅ Yes |
| `CrewSetUnavailable` | Mark crew as unavailable | 1 | ✅ Yes |
| `CrewAddToTeam` | Add crew member to team | 1 | ✅ Yes |

---

## 6. Communication

### Messaging

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `MessageSendSMS` | Send SMS to customer | 3 | ✅ Yes* |
| `MessageSendEmail` | Send email to customer | 3 | ✅ Yes* |
| `MessageSendBulkSMS` | Send bulk SMS | 5 | ✅ Yes* |
| `MessageSendBulkEmail` | Send bulk email | 5 | ✅ Yes* |
| `MessageLogCall` | Log phone call | 1 | ✅ Yes |
| `MessageSchedule` | Schedule message for later | 2 | ✅ Yes |
| `MessageCancel` | Cancel scheduled message | 2 | ⚠️ No |

*Idempotent with deduplication check

### Templates

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `MessageTemplateCreate` | Create message template | 1 | ✅ Yes |
| `MessageTemplateUpdate` | Update template | 1 | ✅ Yes |
| `MessageTemplateDelete` | Delete template | 2 | ⚠️ No |

---

## 7. Scheduling & Calendar

### Calendar Operations

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `CalendarAddEvent` | Add event to calendar | 1 | ✅ Yes |
| `CalendarUpdateEvent` | Update calendar event | 2 | ✅ Yes |
| `CalendarDeleteEvent` | Delete calendar event | 2 | ⚠️ No |
| `CalendarCheckConflicts` | Check for scheduling conflicts | 1 | ✅ Yes |

### Recurring Jobs

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `RecurringJobCreate` | Create recurring job template | 2 | ✅ Yes |
| `RecurringJobUpdate` | Update recurring job | 2 | ✅ Yes |
| `RecurringJobPause` | Pause recurring job | 2 | ✅ Yes |
| `RecurringJobAddSkipDate` | Skip specific occurrence | 1 | ✅ Yes |

---

## 8. Action Queue

### Action Management

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `ActionCreate` | Create action item | 1 | ✅ Yes |
| `ActionUpdate` | Update action details | 1 | ✅ Yes |
| `ActionComplete` | Mark action as complete | 1 | ✅ Yes |
| `ActionDismiss` | Dismiss action | 1 | ✅ Yes |
| `ActionAssign` | Assign action to user | 1 | ✅ Yes |
| `ActionSetPriority` | Update action priority | 1 | ✅ Yes |

---

## 9. System & Admin

### User Management

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `UserCreate` | Create new user account | 3 | ✅ Yes |
| `UserUpdate` | Update user details | 2 | ✅ Yes |
| `UserDelete` | Delete user account | 5 | ⚠️ No |
| `UserSetRole` | Update user role | 4 | ✅ Yes |
| `UserResetPassword` | Reset user password | 3 | ⚠️ No |
| `UserDisable` | Disable user account | 4 | ✅ Yes |

### System Configuration

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `SettingsUpdate` | Update system settings | 4 | ✅ Yes |
| `CompanyUpdate` | Update company details | 3 | ✅ Yes |
| `AuditLogQuery` | Query audit log | 1 | ✅ Yes |
| `AuditLogReplay` | Replay command from log | 5 | ⚠️ No |
| `SystemBackup` | Trigger database backup | 2 | ✅ Yes |
| `SystemRestore` | Restore from backup | 5 | ⚠️ No |

---

## 10. Portal & Customer Access

### Portal Management

| Command | Description | Risk Tier | Idempotent |
|---------|-------------|-----------|------------|
| `PortalGenerateMagicLink` | Generate customer portal link | 2 | ✅ Yes |
| `PortalSendMagicLink` | Send magic link to customer | 3 | ✅ Yes* |
| `PortalSetPIN` | Set customer portal PIN | 2 | ✅ Yes |
| `PortalRevokeAccess` | Revoke portal access | 3 | ✅ Yes |
| `PortalGenerateJobToken` | Generate job-specific token | 2 | ✅ Yes |
| `PortalLogActivity` | Log customer portal activity | 1 | ✅ Yes |

*Idempotent with deduplication check

---

## Command Properties

### Risk Tiers (1-5)

| Tier | Description | Examples | Confirmation Required |
|------|-------------|----------|----------------------|
| 1 | **Low Risk** - Read-only or trivial updates | Notes, photos, priorities | ❌ No |
| 2 | **Medium Risk** - Standard operations | Job updates, scheduling | ❌ No |
| 3 | **High Risk** - Financial or customer-facing | Send quote, book job | ⚠️ Conditional |
| 4 | **Very High Risk** - Money or bulk comms | Record payment, send invoice | ✅ Yes |
| 5 | **Critical Risk** - Irreversible or destructive | Delete, refund, void | ✅ Yes + Reason |

### Idempotency

Commands marked as **Idempotent** can be safely retried:
- Same input → same result
- No duplicate side effects (e.g., duplicate invoices, double payments)

Implementation strategies:
- **Deduplication tokens** - For messages, invoice sends
- **State checks** - For payments (check if already recorded)
- **Timestamps** - For clock-in/clock-out (detect duplicates within window)

---

## Reserved Commands (Future)

These commands are reserved for future phases:

| Command | Description | Phase |
|---------|-------------|-------|
| `AICommandParse` | Parse natural language to CommandEvent | Phase 7 |
| `AIReceiptExtract` | Extract data from receipt photo | Phase 7 |
| `AIMessageDraft` | Draft message using AI | Phase 7 |
| `AIActionRecommend` | Generate recommended actions | Phase 7 |
| `AutopilotRunDaily` | Execute daily autopilot tasks | Phase 8 |
| `AutopilotSendReminders` | Send automated reminders | Phase 8 |
| `OptimiserUpdateHeuristics` | Update pricing/duration heuristics | Phase 9 |
| `OptimiserCompressSnapshots` | Build customer/job snapshots | Phase 9 |

---

## Command Event Structure

Every command follows this structure:

```python
@dataclass
class CommandEvent:
    """Base class for all commands"""
    command_id: str           # UUID for this command execution
    command_type: str         # e.g., "JobCreate", "InvoiceSend"
    timestamp: datetime       # When command was issued
    user_id: int              # Who issued the command
    company_id: int           # Which company (multi-tenant)
    params: dict              # Command-specific parameters
    idempotency_key: Optional[str] = None  # For deduplication
    confirmation_token: Optional[str] = None  # For high-risk commands
    metadata: dict = field(default_factory=dict)  # Extra context
```

---

## Next Steps

1. ✅ Define all commands
2. ⏳ Map commands to state machines (Phase 01)
3. ⏳ Assign risk tiers to each command (Phase 05)
4. ⏳ Define tool contracts for each command (Phase 04)
5. ⏳ Implement router and command registry (Phase 1 implementation)

---

**Status:** Approved - Commands implemented
**Reviewer:** Development Team
