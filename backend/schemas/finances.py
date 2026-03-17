"""
Finances Schema - Pydantic models for transactions API.

This schema wraps the existing Transaction model from tracking_app.models.
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class TransactionTypeEnum(str, Enum):
    """Types of financial transactions."""
    INCOME = "income"
    EXPENSE = "expense"


class TransactionBase(BaseModel):
    """Base transaction model."""
    description: str = Field(min_length=1, description="Transaction description")
    amount: float = Field(gt=0, description="Transaction amount")
    type: TransactionTypeEnum = Field(description="Transaction type (income/expense)")
    category: str = Field(default="", description="Transaction category")
    trans_date: date = Field(default_factory=date.today, description="Transaction date")


class TransactionCreate(TransactionBase):
    """Model for creating a new transaction."""
    pass


class Transaction(TransactionBase):
    """Complete transaction model with ID and timestamps."""
    id: str = Field(description="Unique identifier")
    created_at: datetime = Field(description="Creation timestamp")
    
    class Config:
        from_attributes = True


class TransactionUpdate(BaseModel):
    """Model for updating a transaction."""
    description: Optional[str] = Field(None, description="Transaction description")
    amount: Optional[float] = Field(None, gt=0, description="Transaction amount")
    type: Optional[TransactionTypeEnum] = Field(None, description="Transaction type")
    category: Optional[str] = Field(None, description="Transaction category")
    trans_date: Optional[date] = Field(None, description="Transaction date")


class FinanceSummary(BaseModel):
    """Summary of finances for a period."""
    total_income: float = Field(description="Total income")
    total_expenses: float = Field(description="Total expenses")
    net: float = Field(description="Net (income - expenses)")
    by_category: dict = Field(description="Amounts by category")
    transaction_count: int = Field(description="Number of transactions")
