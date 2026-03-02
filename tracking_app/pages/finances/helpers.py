"""
Helper functions for the Finances page.

Contains utility functions for date handling, calculations, and formatting.
"""

from datetime import date, timedelta
from typing import List

from tracking_app.models import Transaction, TransactionType

from .constants import DEFAULT_CURRENCY


def get_date_range(period: str) -> tuple:
    """
    Get start and end dates for a period.
    
    Args:
        period: Period identifier (this_week, this_month, etc.)
        
    Returns:
        Tuple of (start_date, end_date)
    """
    today = date.today()
    
    if period == "this_week":
        start = today - timedelta(days=today.weekday())
        end = today
    elif period == "this_month":
        start = today.replace(day=1)
        end = today
    elif period == "last_month":
        first_of_this_month = today.replace(day=1)
        end = first_of_this_month - timedelta(days=1)
        start = end.replace(day=1)
    elif period == "this_year":
        start = today.replace(month=1, day=1)
        end = today
    elif period == "all_time":
        start = date(2000, 1, 1)
        end = today
    else:
        start = today
        end = today
    
    return start, end


def calculate_totals(transactions: List[Transaction]) -> dict:
    """
    Calculate income, expenses, and balance from transactions.
    
    Args:
        transactions: List of Transaction objects
        
    Returns:
        Dict with income, expenses, and balance
    """
    income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME.value)
    expenses = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE.value)
    balance = income - expenses
    
    return {
        "income": income,
        "expenses": expenses,
        "balance": balance
    }


def get_category_totals(transactions: List[Transaction], trans_type: str) -> dict:
    """
    Get totals by category for a transaction type.
    
    Args:
        transactions: List of Transaction objects
        trans_type: Transaction type to filter by
        
    Returns:
        Dict mapping category to total amount
    """
    filtered = [t for t in transactions if t.type == trans_type]
    
    categories = {}
    for t in filtered:
        if t.category not in categories:
            categories[t.category] = 0
        categories[t.category] += t.amount
    
    return categories


def format_currency(amount: float, currency: str = DEFAULT_CURRENCY) -> str:
    """
    Format an amount as currency.
    
    Args:
        amount: The amount to format
        currency: Currency symbol to use
        
    Returns:
        Formatted currency string
    """
    return f"{currency}{amount:,.2f}"


def get_transactions_for_period(storage, period: str, trans_type: str = None) -> List[Transaction]:
    """
    Get transactions for a specific period and optionally filter by type.
    
    Args:
        storage: Storage instance
        period: Period identifier
        trans_type: Optional transaction type filter
        
    Returns:
        List of filtered transactions
    """
    start_date, end_date = get_date_range(period)
    transactions = storage.get_transactions(start_date=start_date, end_date=end_date)
    
    if trans_type and trans_type != "all":
        transactions = [t for t in transactions if t.type == trans_type]
    
    return transactions