"""
Basic Admin Tools for Brain System

Contains administrative tools for managing the brain system and performing
administrative operations in the landscaping management system.
"""
from __future__ import annotations
import logging
from typing import Dict, Any
from pydantic import BaseModel, Field

from brain.core.tool import Tool, ToolOutput
from brain.core.enums import RiskTier
from database.queries.misc import get_system_stats, get_setting, update_setting

# Initialize logger
logger = logging.getLogger(__name__)

class SystemStatsInput(BaseModel):
    """Input schema for getting system statistics."""
    include_sensitive: bool = Field(default=False, description="Include sensitive stats")


class SystemStatsTool(Tool):
    """Tool for retrieving system statistics."""
    
    def __init__(self):
        super().__init__(
            name="get_system_stats",
            description="Retrieve system statistics and health information",
            risk_tier=RiskTier.LOW
        )
    
    @property
    def input_schema(self) -> type[BaseModel]:
        return SystemStatsInput
    
    def execute(self, input_data: SystemStatsInput) -> ToolOutput:
        """Execute the system stats retrieval."""
        try:
            stats = get_system_stats(include_sensitive=input_data.include_sensitive)
            return ToolOutput.success(
                data=stats,
                metadata={"operation": "get_system_stats"}
            )
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return ToolOutput.failure(
                error_code="SYSTEM_STATS_ERROR",
                error_message=f"Failed to retrieve system stats: {str(e)}"
            )


class GetSettingInput(BaseModel):
    """Input schema for getting a system setting."""
    key: str = Field(..., description="The setting key to retrieve")


class GetSettingTool(Tool):
    """Tool for retrieving a system setting."""
    
    def __init__(self):
        super().__init__(
            name="get_setting",
            description="Retrieve a system setting by key",
            risk_tier=RiskTier.LOW
        )
    
    @property
    def input_schema(self) -> type[BaseModel]:
        return GetSettingInput
    
    def execute(self, input_data: GetSettingInput) -> ToolOutput:
        """Execute the get setting operation."""
        try:
            value = get_setting(input_data.key)
            return ToolOutput.success(
                data={"key": input_data.key, "value": value},
                metadata={"operation": "get_setting", "setting_key": input_data.key}
            )
        except Exception as e:
            logger.error(f"Error getting setting {input_data.key}: {e}")
            return ToolOutput.failure(
                error_code="GET_SETTING_ERROR",
                error_message=f"Failed to retrieve setting '{input_data.key}': {str(e)}"
            )


class UpdateSettingInput(BaseModel):
    """Input schema for updating a system setting."""
    key: str = Field(..., description="The setting key to update")
    value: str = Field(..., description="The new value for the setting")


class UpdateSettingTool(Tool):
    """Tool for updating a system setting."""
    
    def __init__(self):
        super().__init__(
            name="update_setting",
            description="Update a system setting",
            risk_tier=RiskTier.MEDIUM  # Medium risk as it modifies system configuration
        )
    
    @property
    def input_schema(self) -> type[BaseModel]:
        return UpdateSettingInput
    
    def execute(self, input_data: UpdateSettingInput) -> ToolOutput:
        """Execute the update setting operation."""
        try:
            # Validate the setting key to prevent unauthorized changes
            allowed_keys = [
                'company_name', 'company_address', 'default_hourly_rate', 
                'tax_rate', 'payment_terms', 'email_signature'
            ]
            
            if input_data.key not in allowed_keys:
                return ToolOutput.failure(
                    error_code="INVALID_SETTING_KEY",
                    error_message=f"Setting key '{input_data.key}' is not allowed. Allowed keys: {allowed_keys}"
                )
            
            update_setting(input_data.key, input_data.value)
            return ToolOutput.success(
                data={"key": input_data.key, "value": input_data.value},
                metadata={"operation": "update_setting", "setting_key": input_data.key}
            )
        except Exception as e:
            logger.error(f"Error updating setting {input_data.key}: {e}")
            return ToolOutput.failure(
                error_code="UPDATE_SETTING_ERROR",
                error_message=f"Failed to update setting '{input_data.key}': {str(e)}"
            )


class CreateUserInput(BaseModel):
    """Input schema for creating a user."""
    username: str = Field(..., description="Username for the new user")
    email: str = Field(..., description="Email address for the new user")
    role: str = Field(..., description="Role for the new user (admin, manager, staff, customer)")
    password: str = Field(..., description="Password for the new user")


class CreateUserTool(Tool):
    """Tool for creating a new user account."""
    
    def __init__(self):
        super().__init__(
            name="create_user",
            description="Create a new user account",
            risk_tier=RiskTier.MEDIUM  # Creating users is medium risk
        )
    
    @property
    def input_schema(self) -> type[BaseModel]:
        return CreateUserInput
    
    def execute(self, input_data: CreateUserInput) -> ToolOutput:
        """Execute the create user operation."""
        try:
            from database.queries.users import create_user
            
            # Validate role
            valid_roles = ['admin', 'manager', 'staff', 'customer']
            if input_data.role not in valid_roles:
                return ToolOutput.failure(
                    error_code="INVALID_ROLE",
                    error_message=f"Invalid role '{input_data.role}'. Valid roles: {valid_roles}"
                )
            
            # Create the user
            user = create_user(
                username=input_data.username,
                email=input_data.email,
                role=input_data.role,
                password=input_data.password
            )
            
            if user:
                return ToolOutput.success(
                    data={"user_id": user['id'], "username": user['username']},
                    metadata={"operation": "create_user", "user_id": user['id']}
                )
            else:
                return ToolOutput.failure(
                    error_code="USER_CREATION_FAILED",
                    error_message="Failed to create user"
                )
        except Exception as e:
            logger.error(f"Error creating user {input_data.username}: {e}")
            return ToolOutput.failure(
                error_code="CREATE_USER_ERROR",
                error_message=f"Failed to create user '{input_data.username}': {str(e)}"
            )


# List of all tools in this module
TOOLS = [
    SystemStatsTool(),
    GetSettingTool(),
    UpdateSettingTool(),
    CreateUserTool()
]