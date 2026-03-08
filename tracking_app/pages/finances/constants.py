"""
Constants for the Finances page.

Contains categories, options, and configuration values.
"""

import streamlit as st
from typing import Dict, List

# Transaction categories
EXPENSE_CATEGORIES: List[str] = [
    "Food",
    "Transport",
    "Entertainment",
    "Shopping",
    "Bills",
    "Healthcare",
    "Education",
    "Rent",
    "Utilities",
    "Insurance",
    "Savings",
    "Other",
]

INCOME_CATEGORIES: List[str] = [
    "Salary",
    "Freelance",
    "Investment",
    "Gift",
    "Bonus",
    "Rental",
    "Business",
    "Other",
]

# Cached category lookup for O(1) access
@st.cache_data(ttl=3600)
def get_expense_category_index_map() -> Dict[str, int]:
    """Create a mapping of expense category to index for O(1) lookup."""
    return {cat: idx for idx, cat in enumerate(EXPENSE_CATEGORIES)}


@st.cache_data(ttl=3600)
def get_income_category_index_map() -> Dict[str, int]:
    """Create a mapping of income category to index for O(1) lookup."""
    return {cat: idx for idx, cat in enumerate(INCOME_CATEGORIES)}

# Filter period options
PERIOD_OPTIONS = {
    "this_week": "This Week",
    "this_month": "This Month",
    "last_month": "Last Month",
    "this_year": "This Year",
    "all_time": "All Time",
}

# Transaction type options
TYPE_OPTIONS = {
    "all": "All Types",
    "income": "💵 Income",
    "expense": "💸 Expense",
}

# Default currency
DEFAULT_CURRENCY = "$"

# Icons
INCOME_ICON = "💵"
EXPENSE_ICON = "💸"
BALANCE_ICON = "📊"