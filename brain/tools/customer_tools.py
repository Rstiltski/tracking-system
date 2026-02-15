"""
Customer-related tools
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

from dataclasses import dataclass
from typing import Optional
from brain.core.tool import Tool, ToolInput
from brain.core.result import ToolOutput
from brain.tools.decorators import register_tool
import db


# ===== CREATE CUSTOMER =====

@dataclass
class CreateCustomerInput(ToolInput):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    user_id: Optional[int] = None  # Added to fix the "Invalid Input" warning


@register_tool(name="CreateCustomer", risk="Low", category="customer")
class CreateCustomerTool(Tool):
    """Create new customer record"""

    @property
    def input_schema(self):
        return CreateCustomerInput

    def execute(self, input_data: CreateCustomerInput) -> ToolOutput:
        try:
            customer_id = db.brain_create_customer(
                name=input_data.name,
                phone=input_data.phone,
                email=input_data.email or "",
                address=input_data.address or "",
                postcode=input_data.postcode or "",
                company_id=input_data.company_id
            )

            return ToolOutput(
                success=True,
                data={"customer_id": customer_id}
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_CUSTOMER_CREATE_FAILED",
                error_message=str(e)
            )


# ===== GET CUSTOMER =====

@dataclass
class GetCustomerInput(ToolInput):
    customer_id: int


@register_tool(name="GetCustomer", risk="Low", category="customer")
class GetCustomerTool(Tool):
    """Retrieve customer details"""

    @property
    def input_schema(self):
        return GetCustomerInput

    def execute(self, input_data: GetCustomerInput) -> ToolOutput:
        try:
            customer = db.get_customer(input_data.customer_id, company_id=input_data.company_id)

            if not customer:
                return ToolOutput(
                    success=False,
                    error_code="TOOL_CUSTOMER_GET_NOT_FOUND",
                    error_message=f"Customer {input_data.customer_id} not found"
                )

            return ToolOutput(
                success=True,
                data=dict(customer)
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                error_code="TOOL_CUSTOMER_GET_FAILED",
                error_message=str(e)
            )
