# 🔧 Brain Tools - Operation Layer

**100+ tools for every operation in the system.**

---

## Overview

The `brain/tools/` directory contains all the tools that execute actual operations. Each tool wraps database calls and provides a consistent interface for the Brain.

---

## Tool Files

| File | Domain | Tools |
|------|--------|-------|
| `job_tools.py` | Jobs | CreateJob, UpdateJob, GetJob |
| `job_customer_tools.py` | Job/Customer | UpdateJobStatus, AddJobNote, DeleteJob |
| `job_extensions.py` | Job Extensions | AddJobSignOff, AddJobVariation, AddJobMaterial |
| `job_actuals_tools.py` | Job Costs | CalculateJobActuals |
| `customer_tools.py` | Customers | CreateCustomer, GetCustomer |
| `financial_tools.py` | Finance | CreateInvoice, SendInvoice, GetInvoice |
| `quote_tools.py` | Quotes | CreateQuote, SendQuote, AcceptQuote |
| `scheduling_tools.py` | Scheduling | ScheduleJob, RescheduleJob, CheckAvailability |
| `communication_tools.py` | Messaging | SendMessage, SendBulkMessage, ScheduleMessage |
| `materials_tools.py` | Inventory | CreateMaterial, UpdateMaterial, AdjustInventory |
| `time_tracking_tools.py` | Time | ClockIn, ClockOut, AddWorkLog |
| `crew_management_tools.py` | Crew | AssignCrew, CreateUser, SetUserRole |
| `expense_credit_tools.py` | Expenses | RecordExpense, CreateCreditNote |
| `portal_tools.py` | Portal | GeneratePortalToken, RevokePortalToken |
| `audit_tools.py` | Audit | ViewAuditLog |
| `admin_tools.py` | Admin | AddJobPhoto, CreateTeam, AddSupplier |
| `delete_tools.py` | Deletion | DeleteTemplate, DeleteSupplier, DeleteTeam |
| `bulk_operations.py` | Bulk | BulkJobStatusUpdate, BulkDeleteExpenses |
| `reconciliation_tools.py` | Integrity | ReconcileInvariants |
| `recurring_job_tools.py` | Recurring | AddRecurring, UpdateRecurringJob |
| `misc_tools.py` | Misc | AddVehicle, AddTool, AddDeduction |
| `registry.py` | Registry | ToolRegistry class |
| `decorators.py` | Decorators | @register_tool decorator |

---

## Tool Categories

### Job Management
```
CreateJob      - Create a new job
UpdateJob      - Update job details
GetJob         - Retrieve job information
DeleteJob      - Delete a job (CRITICAL)
ScheduleJob    - Schedule a job
RescheduleJob  - Reschedule a job
```

### Customer Management
```
CreateCustomer   - Create a new customer
GetCustomer      - Retrieve customer info
UpdateCustomer   - Update customer details
DeleteCustomer   - Delete a customer (CRITICAL)
AddCustomerNote  - Add a note to customer
```

### Financial Operations
```
CreateInvoice    - Create an invoice
SendInvoice      - Send invoice to customer
GetInvoice       - Retrieve invoice
RecordPayment    - Record a payment (HIGH)
```

### Quote Operations
```
CreateQuote        - Create a quote
SendQuote          - Send quote to customer
AcceptQuote        - Accept a quote
DeclineQuote       - Decline a quote
ConvertQuoteToJob  - Convert accepted quote to job
```

### Communication
```
SendMessage        - Send a single message
SendBulkMessage    - Send bulk messages (HIGH)
ScheduleMessage    - Schedule a message
SendInvoiceEmail   - Send invoice via email
```

### Time Tracking
```
ClockIn           - Clock in for work
ClockOut          - Clock out from work
AddWorkLog        - Add a work log entry
ApproveTimesheet  - Approve a timesheet
```

---

## Creating a New Tool

### Step 1: Create the Tool Class

```python
# brain/tools/my_tools.py
from brain.core.tool import Tool
from brain.core.result import ToolOutput
from brain.tools.decorators import register_tool

@register_tool
class MyNewTool(Tool):
    """Tool description for documentation."""
    
    @property
    def name(self) -> str:
        return "MyNewTool"
    
    @property
    def description(self) -> str:
        return "Detailed description of what this tool does"
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter 1 description"
                },
                "param2": {
                    "type": "integer",
                    "description": "Parameter 2 description",
                    "default": 0
                }
            },
            "required": ["param1"]
        }
    
    @property
    def output_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "result": {"type": "string"},
                "id": {"type": "string"}
            }
        }
    
    @property
    def risk_tier(self) -> str:
        return "LOW"  # TRIVIAL, LOW, MEDIUM, HIGH, CRITICAL
    
    def execute(self, params: dict) -> ToolOutput:
        # Validate inputs
        param1 = params.get("param1")
        if not param1:
            return ToolOutput(
                success=False,
                error_code="MISSING_PARAM",
                error_message="param1 is required"
            )
        
        # Execute operation
        try:
            # ... actual implementation ...
            result = do_something(param1)
            
            return ToolOutput(
                success=True,
                data={"result": result, "id": "123"}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="EXECUTION_ERROR",
                error_message=str(e)
            )
```

### Step 2: Register the Tool

```python
# In brain/core/brain.py _register_tools()
self.tool_registry.register_lazy(
    "MyNewTool",
    "brain.tools.my_tools",
    "MyNewTool"
)
```

### Step 3: Add Router Mapping

```python
# In brain/core/router.py route()
if command_type == "MyNewCommand":
    return [{"tool": "MyNewTool", "params": event.params}]
```

---

## Tool Registry

The `ToolRegistry` class manages all tools:

```python
from brain.tools.registry import ToolRegistry

# Create registry
registry = ToolRegistry(lazy_loading=True, auto_discover=True)

# Register tools
registry.register(MyTool())  # Eager
registry.register_lazy("MyTool", "brain.tools.my_tools", "MyTool")  # Lazy

# Execute tools
output = registry.execute("MyTool", {"param": "value"})

# List tools
tools = registry.list_tools()

# Check if tool exists
if "MyTool" in registry:
    print("Tool registered")
```

---

## Tool Decorators

Use decorators for automatic registration:

```python
from brain.tools.decorators import register_tool

@register_tool
class AutoRegisteredTool(Tool):
    # Tool will be auto-discovered and registered
    pass
```

---

## Error Handling

Tools should always return `ToolOutput`:

```python
# Success
return ToolOutput(
    success=True,
    data={"id": "123", "name": "Result"}
)

# Failure
return ToolOutput(
    success=False,
    error_code="VALIDATION_ERROR",
    error_message="Invalid input parameter"
)

# With warnings
return ToolOutput(
    success=True,
    data={...},
    warnings=["Deprecated field used"]
)
```

---

## Risk Tier Guidelines

| Tier | When to Use |
|------|-------------|
| TRIVIAL | Read operations, adding notes/photos |
| LOW | Standard CRUD operations |
| MEDIUM | Customer-facing changes, scheduling |
| HIGH | Financial operations, bulk actions |
| CRITICAL | Irreversible deletions, voids |

---

## Cross-References

| Topic | File |
|-------|------|
| Tool contracts | `brain/design/04_tool_contracts.md` |
| Risk tiers | `brain/design/05_risk_tiers.md` |
| Core brain | `brain/core/README.md` |
| Router | `brain/core/router.py` |

---

**Last Updated:** February 2026