"""
Finances API - FastAPI routes for transactions.

This API wraps the existing tracking_app.storage methods:
- get_transactions
- create_transaction
- delete_transaction
"""

import sys
import os
from datetime import date
from typing import Optional, List

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException

from backend.schemas.finances import (
    Transaction,
    TransactionCreate,
    TransactionUpdate,
    FinanceSummary,
    TransactionTypeEnum,
)

# Import storage from tracking_app
from tracking_app.storage import get_storage


router = APIRouter(prefix="/api/finances", tags=["finances"])


def get_storage_instance():
    """Get storage instance."""
    return get_storage()


@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
):
    """
    Get transactions with optional filtering.
    
    - **start_date**: Filter transactions from this date
    - **end_date**: Filter transactions until this date
    - **limit**: Maximum number of transactions to return
    """
    storage = get_storage_instance()
    
    try:
        transactions = storage.get_transactions(start_date, end_date)
        
        # Convert to API response format
        return [
            Transaction(
                id=t.id,
                description=t.description,
                amount=t.amount,
                type=TransactionTypeEnum(t.type),
                category=t.category,
                trans_date=t.trans_date,
                created_at=t.created_at,
            )
            for t in transactions[:limit]
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transactions: {str(e)}")


@router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    """
    Create a new transaction.
    
    - **description**: Transaction description
    - **amount**: Transaction amount
    - **type**: Transaction type (income/expense)
    - **category**: Transaction category
    - **trans_date**: Transaction date
    """
    storage = get_storage_instance()
    
    try:
        # Convert to storage format
        trans_type = transaction.type.value if isinstance(transaction.type, TransactionTypeEnum) else transaction.type
        
        new_transaction = storage.create_transaction(
            description=transaction.description,
            amount=transaction.amount,
            trans_type=trans_type,
            category=transaction.category,
            trans_date=transaction.trans_date,
        )
        
        # Convert to API response format
        return Transaction(
            id=new_transaction.id,
            description=new_transaction.description,
            amount=new_transaction.amount,
            type=TransactionTypeEnum(new_transaction.type),
            category=new_transaction.category,
            trans_date=new_transaction.trans_date,
            created_at=new_transaction.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating transaction: {str(e)}")


@router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str):
    """Get a specific transaction by ID."""
    storage = get_storage_instance()
    
    try:
        transactions = storage.get_transactions()
        
        for t in transactions:
            if t.id == transaction_id:
                return Transaction(
                    id=t.id,
                    description=t.description,
                    amount=t.amount,
                    type=TransactionTypeEnum(t.type),
                    category=t.category,
                    trans_date=t.trans_date,
                    created_at=t.created_at,
                )
        
        raise HTTPException(status_code=404, detail="Transaction not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transaction: {str(e)}")


@router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(
    transaction_id: str,
    transaction: TransactionUpdate,
):
    """Update a transaction."""
    storage = get_storage_instance()
    
    try:
        # Build update kwargs
        update_kwargs = {}
        if transaction.description is not None:
            update_kwargs["description"] = transaction.description
        if transaction.amount is not None:
            update_kwargs["amount"] = transaction.amount
        if transaction.type is not None:
            update_kwargs["trans_type"] = transaction.type.value
        if transaction.category is not None:
            update_kwargs["category"] = transaction.category
        if transaction.trans_date is not None:
            update_kwargs["trans_date"] = transaction.trans_date
        
        if not update_kwargs:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updated = storage.update_transaction(transaction_id, **update_kwargs)
        
        if not updated:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return Transaction(
            id=updated.id,
            description=updated.description,
            amount=updated.amount,
            type=TransactionTypeEnum(updated.type),
            category=updated.category,
            trans_date=updated.trans_date,
            created_at=updated.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating transaction: {str(e)}")


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    """Delete a transaction."""
    storage = get_storage_instance()
    
    try:
        success = storage.delete_transaction(transaction_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return {"message": "Transaction deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting transaction: {str(e)}")


@router.get("/summary", response_model=FinanceSummary)
async def get_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """
    Get finance summary for a period.
    
    - **start_date**: Start of period
    - **end_date**: End of period
    """
    storage = get_storage_instance()
    
    try:
        transactions = storage.get_transactions(start_date, end_date)
        
        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.type == "income")
        total_expenses = sum(t.amount for t in transactions if t.type == "expense")
        
        # Group by category
        by_category = {}
        for t in transactions:
            cat = t.category or "Uncategorized"
            if cat not in by_category:
                by_category[cat] = 0
            by_category[cat] += t.amount
        
        return FinanceSummary(
            total_income=total_income,
            total_expenses=total_expenses,
            net=total_income - total_expenses,
            by_category=by_category,
            transaction_count=len(transactions),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary: {str(e)}")
