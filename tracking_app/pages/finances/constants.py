"""
Constants for the Finances page.

Contains categories, options, and configuration values.
"""

# Transaction categories
EXPENSE_CATEGORIES = [
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

INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Investment",
    "Gift",
    "Bonus",
    "Rental",
    "Business",
    "Other",
]

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