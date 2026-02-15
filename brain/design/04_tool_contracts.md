# Tool Contracts

**Rule:** Do not use scripts to edit code.

**Version:** 1.0
**Status:** Draft
**Last Updated:** 2026-01-01

## Overview

**Tools** are the atomic operations that the Brain executes. Each tool wraps one or more `db.py` functions and provides:

- ✅ **Typed inputs** - Clear parameter types and validation
- ✅ **Typed outputs** - Structured return values
- ✅ **Error handling** - Specific error codes for failures
- ✅ **Idempotency** - Safe retry behavior
- ✅ **Audit logging** - Automatic logging of all calls

## Tool Architecture

```
Command → Planner → Plan (list of ToolCalls)
                     ↓
              Tool Registry
                     ↓
              Tool Wrapper (validates, logs, executes)
                     ↓
              db.py function
                     ↓
              Database
```

## Tool Categories

1. [Job Tools](#1-job-tools) (15 tools)
2. [Customer Tools](#2-customer-tools) (8 tools)
3. [Financial Tools](#3-financial-tools) (18 tools)
4. [Material Tools](#4-material-tools) (6 tools)
5. [Crew Tools](#5-crew-tools) (8 tools)
6. [Communication Tools](#6-communication-tools) (6 tools)
7. [Scheduling Tools](#7-scheduling-tools) (5 tools)
8. [System Tools](#8-system-tools) (4 tools)

**Total Tools:** 70

---

## Tool Contract Structure

Every tool follows this contract:

```python
@dataclass
class ToolInput:
    """Base class for tool inputs"""
    pass

@dataclass
class ToolOutput:
    """Base class for tool outputs"""
    success: bool
    data: Any
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class Tool:
    """Base tool class"""

    name: str
    description: str
    input_schema: Type[ToolInput]
    output_schema: Type[ToolOutput]

    def validate_input(self, params: dict) -> ToolInput:
        """Validate and parse input parameters"""
        pass

    def execute(self, input: ToolInput) -> ToolOutput:
        """Execute the tool"""
        pass

    def handle_error(self, error: Exception) -> ToolOutput:
        """Convert exceptions to ToolOutput"""
        pass
```

---

## 1. Job Tools

### T-JOB-001: CreateJob

**Description:** Create a new job record

**Input:**
```python
@dataclass
class CreateJobInput(ToolInput):
    customer_id: int
    title: str
    description: Optional[str] = None
    job_type: str = "landscaping"  # mow, hedge, fencing, paving, design, landscaping
    job_date: Optional[date] = None
    priority: str = "Medium"  # Low, Medium, High
    estimated_hours: Optional[float] = None
```

**Output:**
```python
@dataclass
class CreateJobOutput(ToolOutput):
    job_id: int
    status: str  # "DRAFT"
```

**Errors:**
- `TOOL_JOB_CREATE_CUSTOMER_NOT_FOUND` - Customer doesn't exist
- `TOOL_JOB_CREATE_INVALID_TYPE` - Invalid job_type
- `TOOL_JOB_CREATE_DB_ERROR` - Database error

**DB Function:** `db.create_job(customer_id, title, description, job_date, job_type)`

---

### T-JOB-002: UpdateJob

**Description:** Update job details

**Input:**
```python
@dataclass
class UpdateJobInput(ToolInput):
    job_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    job_type: Optional[str] = None
    priority: Optional[str] = None
    estimated_hours: Optional[float] = None
    quoted_price: Optional[float] = None
    status: Optional[str] = None
```

**Output:**
```python
@dataclass
class UpdateJobOutput(ToolOutput):
    job_id: int
    updated_fields: list[str]
```

**Errors:**
- `TOOL_JOB_UPDATE_NOT_FOUND` - Job doesn't exist
- `TOOL_JOB_UPDATE_INVALID_STATUS` - Invalid status transition
- `TOOL_JOB_UPDATE_DB_ERROR` - Database error

**DB Function:** `db.update_job(job_id, **kwargs)`, `db.update_job_full(job_id, **kwargs)`

---

### T-JOB-003: GetJob

**Description:** Retrieve job details

**Input:**
```python
@dataclass
class GetJobInput(ToolInput):
    job_id: int
```

**Output:**
```python
@dataclass
class GetJobOutput(ToolOutput):
    job: dict  # Full job record with customer details
```

**Errors:**
- `TOOL_JOB_GET_NOT_FOUND` - Job doesn't exist

**DB Function:** `db.get_job(job_id)`

---

### T-JOB-004: DeleteJob

**Description:** Soft-delete a job

**Input:**
```python
@dataclass
class DeleteJobInput(ToolInput):
    job_id: int
    reason: str
```

**Output:**
```python
@dataclass
class DeleteJobOutput(ToolOutput):
    job_id: int
    deleted_at: datetime
```

**Errors:**
- `TOOL_JOB_DELETE_NOT_FOUND` - Job doesn't exist
- `TOOL_JOB_DELETE_HAS_INVOICE` - Cannot delete job with invoice
- `TOOL_JOB_DELETE_HAS_PAYMENTS` - Cannot delete job with payments

**DB Function:** `db.delete_job(job_id)` (to be created)

---

### T-JOB-005: QuoteJob

**Description:** Set quote price and mark as quoted

**Input:**
```python
@dataclass
class QuoteJobInput(ToolInput):
    job_id: int
    quoted_price: float
    materials_cost: Optional[float] = None
    labor_hours: Optional[float] = None
```

**Output:**
```python
@dataclass
class QuoteJobOutput(ToolOutput):
    job_id: int
    quoted_price: float
    quoted_at: datetime
```

**Errors:**
- `TOOL_JOB_QUOTE_NOT_FOUND` - Job doesn't exist
- `TOOL_JOB_QUOTE_INVALID_PRICE` - Price <= 0
- `TOOL_JOB_QUOTE_ALREADY_BOOKED` - Job already booked

**DB Function:** `db.update_job(job_id, quoted_price=..., status="QUOTED")`

---

### T-JOB-006: BookJob

**Description:** Accept quote and book job

**Input:**
```python
@dataclass
class BookJobInput(ToolInput):
    job_id: int
    job_date: Optional[date] = None
    deposit_percentage: Optional[float] = None  # e.g., 0.25 for 25%
```

**Output:**
```python
@dataclass
class BookJobOutput(ToolOutput):
    job_id: int
    booked_at: datetime
    deposit_amount: Optional[float]
```

**Errors:**
- `TOOL_JOB_BOOK_NOT_FOUND` - Job doesn't exist
- `TOOL_JOB_BOOK_NOT_QUOTED` - Job not in QUOTED state
- `TOOL_JOB_BOOK_INVALID_DEPOSIT` - Deposit percentage invalid

**DB Function:** `db.update_job(job_id, status="BOOKED", booked_at=...)`

---

### T-JOB-007: ScheduleJob

**Description:** Assign date, time, and crew to job

**Input:**
```python
@dataclass
class ScheduleJobInput(ToolInput):
    job_id: int
    job_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    crew_ids: list[int] = field(default_factory=list)
    vehicle_id: Optional[int] = None
```

**Output:**
```python
@dataclass
class ScheduleJobOutput(ToolOutput):
    job_id: int
    scheduled_at: datetime
    crew_count: int
```

**Errors:**
- `TOOL_JOB_SCHEDULE_NOT_FOUND` - Job doesn't exist
- `TOOL_JOB_SCHEDULE_CREW_CONFLICT` - Crew already assigned
- `TOOL_JOB_SCHEDULE_VEHICLE_CONFLICT` - Vehicle already assigned

**DB Function:** `db.update_job_datetime(job_id, job_date, start_time, end_time)`

---

### T-JOB-008: StartJob

**Description:** Start work on job (clock in crew)

**Input:**
```python
@dataclass
class StartJobInput(ToolInput):
    job_id: int
    crew_ids: list[int]
```

**Output:**
```python
@dataclass
class StartJobOutput(ToolOutput):
    job_id: int
    started_at: datetime
    time_entry_ids: list[int]
```

**Errors:**
- `TOOL_JOB_START_NOT_FOUND` - Job doesn't exist
- `TOOL_JOB_START_NOT_SCHEDULED` - Job not scheduled
- `TOOL_JOB_START_ALREADY_STARTED` - Job already in progress

**DB Function:** `db.update_job(job_id, status="IN_PROGRESS")`, `db.create_time_entry(...)`

---

### T-JOB-009: CompleteJob

**Description:** Mark job as completed

**Input:**
```python
@dataclass
class CompleteJobInput(ToolInput):
    job_id: int
    completion_notes: Optional[str] = None
    sign_off_photo_id: Optional[int] = None
```

**Output:**
```python
@dataclass
class CompleteJobOutput(ToolOutput):
    job_id: int
    completed_at: datetime
```

**Errors:**
- `TOOL_JOB_COMPLETE_NOT_FOUND` - Job doesn't exist
- `TOOL_JOB_COMPLETE_NOT_STARTED` - Job not started
- `TOOL_JOB_COMPLETE_MISSING_SIGNOFF` - Sign-off required

**DB Function:** `db.update_job(job_id, status="COMPLETED", completed_at=...)`

---

### T-JOB-010: CancelJob

**Description:** Cancel a job

**Input:**
```python
@dataclass
class CancelJobInput(ToolInput):
    job_id: int
    cancellation_reason: str
```

**Output:**
```python
@dataclass
class CancelJobOutput(ToolOutput):
    job_id: int
    cancelled_at: datetime
```

**Errors:**
- `TOOL_JOB_CANCEL_NOT_FOUND` - Job doesn't exist
- `TOOL_JOB_CANCEL_ALREADY_INVOICED` - Cannot cancel invoiced job

**DB Function:** `db.update_job(job_id, status="CANCELLED", cancellation_reason=...)`

---

### T-JOB-011: AddJobPhoto

**Description:** Upload photo to job

**Input:**
```python
@dataclass
class AddJobPhotoInput(ToolInput):
    job_id: int
    photo_data: bytes
    photo_type: str  # "before", "during", "after", "sign_off"
    caption: Optional[str] = None
```

**Output:**
```python
@dataclass
class AddJobPhotoOutput(ToolOutput):
    photo_id: int
    uploaded_at: datetime
```

**Errors:**
- `TOOL_JOB_PHOTO_ADD_NOT_FOUND` - Job doesn't exist
- `TOOL_JOB_PHOTO_INVALID_TYPE` - Invalid photo type
- `TOOL_JOB_PHOTO_UPLOAD_FAILED` - Upload failed

**DB Function:** `db.add_job_photo(job_id, photo_data, photo_type, caption)`

---

### T-JOB-012: AddJobNote

**Description:** Add internal note to job

**Input:**
```python
@dataclass
class AddJobNoteInput(ToolInput):
    job_id: int
    note: str
    user_id: int
```

**Output:**
```python
@dataclass
class AddJobNoteOutput(ToolOutput):
    note_id: int
    created_at: datetime
```

**Errors:**
- `TOOL_JOB_NOTE_ADD_NOT_FOUND` - Job doesn't exist

**DB Function:** `db.add_job_note(job_id, note, user_id)`

---

### T-JOB-013: AssignCrew

**Description:** Assign crew member(s) to job

**Input:**
```python
@dataclass
class AssignCrewInput(ToolInput):
    job_id: int
    crew_ids: list[int]
```

**Output:**
```python
@dataclass
class AssignCrewOutput(ToolOutput):
    assignment_ids: list[int]
```

**Errors:**
- `TOOL_JOB_ASSIGN_CREW_NOT_FOUND` - Job doesn't exist
- `TOOL_JOB_ASSIGN_CREW_USER_NOT_FOUND` - User doesn't exist
- `TOOL_JOB_ASSIGN_CREW_CONFLICT` - Crew already assigned

**DB Function:** `db.assign_crew_to_job(job_id, crew_ids)`

---

### T-JOB-014: AddJobMaterial

**Description:** Add material requirement to job

**Input:**
```python
@dataclass
class AddJobMaterialInput(ToolInput):
    job_id: int
    material_id: int
    quantity: float
```

**Output:**
```python
@dataclass
class AddJobMaterialOutput(ToolOutput):
    job_material_id: int
```

**Errors:**
- `TOOL_JOB_MATERIAL_JOB_NOT_FOUND` - Job doesn't exist
- `TOOL_JOB_MATERIAL_NOT_FOUND` - Material doesn't exist

**DB Function:** `db.add_job_material(job_id, material_id, quantity)`

---

### T-JOB-015: UpdateJobMeasurements

**Description:** Update property measurements for job

**Input:**
```python
@dataclass
class UpdateJobMeasurementsInput(ToolInput):
    job_id: int
    measurements: dict  # {length, width, depth, area, etc.}
```

**Output:**
```python
@dataclass
class UpdateJobMeasurementsOutput(ToolOutput):
    job_id: int
    updated_fields: list[str]
```

**Errors:**
- `TOOL_JOB_MEAS_NOT_FOUND` - Job doesn't exist

**DB Function:** `db.update_job_measurements(job_id, measurements)`

---

## 2. Customer Tools

### T-CUST-001: CreateCustomer

**Description:** Create new customer record

**Input:**
```python
@dataclass
class CreateCustomerInput(ToolInput):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
```

**Output:**
```python
@dataclass
class CreateCustomerOutput(ToolOutput):
    customer_id: int
```

**Errors:**
- `TOOL_CUST_CREATE_DUPLICATE_PHONE` - Phone already exists
- `TOOL_CUST_CREATE_INVALID_EMAIL` - Invalid email format

**DB Function:** `db.create_customer(name, phone, email, address, postcode)`

---

### T-CUST-002: UpdateCustomer

**Description:** Update customer details

**Input:**
```python
@dataclass
class UpdateCustomerInput(ToolInput):
    customer_id: int
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
```

**Output:**
```python
@dataclass
class UpdateCustomerOutput(ToolOutput):
    customer_id: int
    updated_fields: list[str]
```

**Errors:**
- `TOOL_CUST_UPDATE_NOT_FOUND` - Customer doesn't exist

**DB Function:** `db.update_customer(customer_id, **kwargs)`

---

### T-CUST-003: GetCustomer

**Description:** Retrieve customer details

**Input:**
```python
@dataclass
class GetCustomerInput(ToolInput):
    customer_id: int
```

**Output:**
```python
@dataclass
class GetCustomerOutput(ToolOutput):
    customer: dict
```

**Errors:**
- `TOOL_CUST_GET_NOT_FOUND` - Customer doesn't exist

**DB Function:** `db.get_customer(customer_id)`

---

### T-CUST-004: DeleteCustomer

**Description:** Soft-delete customer

**Input:**
```python
@dataclass
class DeleteCustomerInput(ToolInput):
    customer_id: int
    reason: str
```

**Output:**
```python
@dataclass
class DeleteCustomerOutput(ToolOutput):
    customer_id: int
    deleted_at: datetime
```

**Errors:**
- `TOOL_CUST_DELETE_NOT_FOUND` - Customer doesn't exist
- `TOOL_CUST_DELETE_HAS_JOBS` - Cannot delete customer with jobs

**DB Function:** `db.delete_customer(customer_id)` (to be created)

---

### T-CUST-005: AddCustomerNote

**Description:** Add note to customer record

**Input:**
```python
@dataclass
class AddCustomerNoteInput(ToolInput):
    customer_id: int
    note: str
    note_type: str = "general"  # general, complaint, praise, follow_up
```

**Output:**
```python
@dataclass
class AddCustomerNoteOutput(ToolOutput):
    note_id: int
```

**Errors:**
- `TOOL_CUST_NOTE_NOT_FOUND` - Customer doesn't exist

**DB Function:** `db.add_customer_note(customer_id, note, note_type)`

---

### T-CUST-006: SetCustomerVIP

**Description:** Mark customer as VIP

**Input:**
```python
@dataclass
class SetCustomerVIPInput(ToolInput):
    customer_id: int
    is_vip: bool
```

**Output:**
```python
@dataclass
class SetCustomerVIPOutput(ToolOutput):
    customer_id: int
    is_vip: bool
```

**Errors:**
- `TOOL_CUST_VIP_NOT_FOUND` - Customer doesn't exist

**DB Function:** `db.update_customer(customer_id, is_vip=is_vip)`

---

### T-CUST-007: CalculateHealthScore

**Description:** Recalculate customer health score

**Input:**
```python
@dataclass
class CalculateHealthScoreInput(ToolInput):
    customer_id: int
```

**Output:**
```python
@dataclass
class CalculateHealthScoreOutput(ToolOutput):
    customer_id: int
    health_score: int  # 0-100
```

**Errors:**
- `TOOL_CUST_HEALTH_NOT_FOUND` - Customer doesn't exist

**DB Function:** `db.calculate_customer_health_score(customer_id)`

---

### T-CUST-008: SetContactPreferences

**Description:** Update customer contact preferences

**Input:**
```python
@dataclass
class SetContactPreferencesInput(ToolInput):
    customer_id: int
    allow_sms: bool
    allow_email: bool
    allow_phone: bool
```

**Output:**
```python
@dataclass
class SetContactPreferencesOutput(ToolOutput):
    customer_id: int
```

**Errors:**
- `TOOL_CUST_PREF_NOT_FOUND` - Customer doesn't exist

**DB Function:** `db.update_customer(customer_id, allow_sms=..., allow_email=..., allow_phone=...)`

---

## 3. Financial Tools

### T-FIN-001: CreateInvoice

**Description:** Create invoice from job

**Input:**
```python
@dataclass
class CreateInvoiceInput(ToolInput):
    job_id: int
    invoice_no: str
    total: float
    line_items: list[dict]
    due_date: date
```

**Output:**
```python
@dataclass
class CreateInvoiceOutput(ToolOutput):
    invoice_id: int
    invoice_no: str
```

**Errors:**
- `TOOL_FIN_INV_CREATE_JOB_NOT_FOUND` - Job doesn't exist
- `TOOL_FIN_INV_CREATE_DUPLICATE_NO` - Invoice number exists
- `TOOL_FIN_INV_CREATE_JOB_HAS_INVOICE` - Job already invoiced

**DB Function:** `db.create_invoice_from_job(job_id, invoice_no, deposit_percentage)`

---

### T-FIN-002: SendInvoice

**Description:** Send invoice to customer

**Input:**
```python
@dataclass
class SendInvoiceInput(ToolInput):
    invoice_id: int
    channel: str  # "email", "sms", "both"
```

**Output:**
```python
@dataclass
class SendInvoiceOutput(ToolOutput):
    invoice_id: int
    sent_at: datetime
    message_ids: list[int]
```

**Errors:**
- `TOOL_FIN_INV_SEND_NOT_FOUND` - Invoice doesn't exist
- `TOOL_FIN_INV_SEND_NO_CONTACT` - Customer has no email/phone

**DB Function:** `db.send_invoice(invoice_id)` + `services.notifications.send_email/sms`

---

### T-FIN-003: RecordPayment

**Description:** Record payment received

**Input:**
```python
@dataclass
class RecordPaymentInput(ToolInput):
    invoice_id: int
    amount: float
    payment_method: str  # "cash", "card", "bank_transfer"
    payment_date: date
    reference: Optional[str] = None
```

**Output:**
```python
@dataclass
class RecordPaymentOutput(ToolOutput):
    payment_id: int
    invoice_balance: float
```

**Errors:**
- `TOOL_FIN_PAY_RECORD_INV_NOT_FOUND` - Invoice doesn't exist
- `TOOL_FIN_PAY_RECORD_EXCEEDS_BALANCE` - Payment exceeds balance
- `TOOL_FIN_PAY_RECORD_INVALID_AMOUNT` - Amount <= 0

**DB Function:** `db.record_payment(invoice_id, amount, payment_method, payment_date)`

---

### T-FIN-004: RefundPayment

**Description:** Process refund

**Input:**
```python
@dataclass
class RefundPaymentInput(ToolInput):
    payment_id: int
    refund_amount: float
    refund_reason: str
```

**Output:**
```python
@dataclass
class RefundPaymentOutput(ToolOutput):
    refund_id: int
    refund_date: datetime
```

**Errors:**
- `TOOL_FIN_PAY_REFUND_NOT_FOUND` - Payment doesn't exist
- `TOOL_FIN_PAY_REFUND_EXCEEDS_AMOUNT` - Refund exceeds payment
- `TOOL_FIN_PAY_REFUND_NO_REASON` - Reason required

**DB Function:** `db.refund_payment(payment_id, refund_amount, refund_reason)`

---

### T-FIN-005: VoidInvoice

**Description:** Void an invoice

**Input:**
```python
@dataclass
class VoidInvoiceInput(ToolInput):
    invoice_id: int
    void_reason: str
```

**Output:**
```python
@dataclass
class VoidInvoiceOutput(ToolOutput):
    invoice_id: int
    voided_at: datetime
```

**Errors:**
- `TOOL_FIN_INV_VOID_NOT_FOUND` - Invoice doesn't exist
- `TOOL_FIN_INV_VOID_HAS_PAYMENTS` - Cannot void paid invoice
- `TOOL_FIN_INV_VOID_NO_REASON` - Reason required

**DB Function:** `db.void_invoice(invoice_id, void_reason)`

---

### T-FIN-006: CreateQuote

**Description:** Create quote for job

**Input:**
```python
@dataclass
class CreateQuoteInput(ToolInput):
    job_id: int
    customer_id: int
    quoted_price: float
    line_items: list[dict]
    valid_until: date
```

**Output:**
```python
@dataclass
class CreateQuoteOutput(ToolOutput):
    quote_id: int
```

**Errors:**
- `TOOL_FIN_QUOTE_CREATE_JOB_NOT_FOUND` - Job doesn't exist
- `TOOL_FIN_QUOTE_CREATE_INVALID_PRICE` - Price <= 0

**DB Function:** `db.create_quote(job_id, customer_id, items, total_price)`

---

### T-FIN-007: SendQuote

**Description:** Send quote to customer

**Input:**
```python
@dataclass
class SendQuoteInput(ToolInput):
    quote_id: int
    channel: str  # "email", "sms", "both"
```

**Output:**
```python
@dataclass
class SendQuoteOutput(ToolOutput):
    quote_id: int
    sent_at: datetime
    message_ids: list[int]
```

**Errors:**
- `TOOL_FIN_QUOTE_SEND_NOT_FOUND` - Quote doesn't exist

**DB Function:** `db.send_quote(quote_id)` + notifications

---

### T-FIN-008: CreateExpense

**Description:** Record expense

**Input:**
```python
@dataclass
class CreateExpenseInput(ToolInput):
    job_id: Optional[int] = None
    category: str
    supplier: str
    amount: float
    expense_date: date
    description: Optional[str] = None
```

**Output:**
```python
@dataclass
class CreateExpenseOutput(ToolOutput):
    expense_id: int
```

**Errors:**
- `TOOL_FIN_EXP_CREATE_INVALID_AMOUNT` - Amount <= 0

**DB Function:** `db.create_expense(...)`

---

*(Continuing with remaining financial, material, crew, communication, scheduling, and system tools...)*

---

## Tool Registry

All tools are registered in a central registry:

```python
class ToolRegistry:
    """Central registry of all tools"""

    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a tool"""
        self.tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """Get tool by name"""
        return self.tools.get(name)

    def execute(self, name: str, params: dict) -> ToolOutput:
        """Execute tool by name"""
        tool = self.get(name)
        if not tool:
            return ToolOutput(
                success=False,
                data=None,
                error_code="TOOL_NOT_FOUND",
                error_message=f"Tool {name} not found"
            )

        try:
            input_obj = tool.validate_input(params)
            output = tool.execute(input_obj)
            return output
        except Exception as e:
            return tool.handle_error(e)
```

---

## Error Code Format

All tool error codes follow this format:

```
TOOL_<CATEGORY>_<OPERATION>_<ERROR_TYPE>
```

**Examples:**
- `TOOL_JOB_CREATE_CUSTOMER_NOT_FOUND`
- `TOOL_FIN_PAY_RECORD_EXCEEDS_BALANCE`
- `TOOL_COMM_MSG_SEND_RATE_LIMIT`

---

## Next Steps

1. ✅ Define tool contracts for key operations
2. ⏳ Implement remaining tool contracts (70 total)
3. ⏳ Create tool wrapper base class (Phase 1)
4. ⏳ Implement tool registry (Phase 1)
5. ⏳ Write tool tests (Phase 1)

---

**Status:** Approved - Tools implemented
**Reviewer:** Development Team

**Note:** This document defines tool contracts. See `/brain/tools/` for current implementation.
