# 💰 Finances Module

Financial tracking and budgeting for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Categories, icons, options |
| [`helpers.py`](helpers.py) | Currency formatting, calculations |
| [`session_state.py`](session_state.py) | Filter state management |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Transaction Tracking**: Record income and expenses
- **Category Management**: Organize by custom categories
- **Financial Summary**: View income, expenses, balance
- **Filtering**: Filter by period and transaction type
- **Category Breakdown**: Visual breakdown of spending

---

## Public API

### Constants

```python
from tracking_app.pages.finances import (
    EXPENSE_CATEGORIES,  # List of expense categories
    INCOME_CATEGORIES,   # List of income categories
    PERIOD_OPTIONS,      # Time period filter options
    TYPE_OPTIONS,        # Transaction type filter options
)
```

### Helper Functions

```python
from tracking_app.pages.finances import (
    format_currency,     # Format number as currency
    calculate_totals,    # Calculate income/expenses/balance
    get_category_totals, # Get totals by category
    get_date_range,      # Get start/end dates for period
)
```

### Components

```python
from tracking_app.pages.finances import (
    render_header,              # Page header
    render_summary,             # Financial summary metrics
    render_add_transaction_form,# Add transaction form
    render_filters,             # Filter controls
    render_transactions_list,   # Transaction list
    render_category_breakdown,  # Category chart
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.finances import (
    init_session_state,
    render_header,
    render_summary,
    render_add_transaction_form,
)

# Initialize state
init_session_state()

# Render components
render_header()
render_summary()
render_add_transaction_form()
```

---

## Dependencies

- `streamlit` - UI framework
- `datetime` - Date handling
- `tracking_app.models` - Transaction model

---

## Related Pages

- **Goals**: Set financial goals
- **Insights**: Financial analytics
- **Data Export**: Export financial data

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Finance implementation | `../tracking_app/pages/finances.py` |
| Finance models | `../brain/models/` |
| Data export | `../tracking_app/pages/data_export/` |

---

**Last Updated:** March 2026
