"""
Finances Page - Financial Tracking

Streamlit page for tracking income, expenses, and budget monitoring.

Usage:
    streamlit run tracking_app/pages/finances.py
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage
from tracking_app.models import Transaction, TransactionType
from tracking_app.components.sidebar import render_sidebar


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Finances - Veryfyn",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# SESSION STATE
# =============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    if 'filter_period' not in st.session_state:
        st.session_state.filter_period = "this_month"
    
    if 'filter_type' not in st.session_state:
        st.session_state.filter_type = "all"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_date_range(period: str) -> tuple:
    """Get start and end dates for a period."""
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
    """Calculate income, expenses, and balance."""
    income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME.value)
    expenses = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE.value)
    balance = income - expenses
    
    return {
        "income": income,
        "expenses": expenses,
        "balance": balance
    }


def get_category_totals(transactions: List[Transaction], trans_type: str) -> dict:
    """Get totals by category for a transaction type."""
    filtered = [t for t in transactions if t.type == trans_type]
    
    categories = {}
    for t in filtered:
        if t.category not in categories:
            categories[t.category] = 0
        categories[t.category] += t.amount
    
    return categories


# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

def render_header():
    """Render page header."""
    st.title("💰 Finances")
    st.markdown("Track your income, expenses, and monitor your budget.")


def render_summary():
    """Render financial summary."""
    storage = st.session_state.storage
    start_date, end_date = get_date_range(st.session_state.filter_period)
    
    transactions = storage.get_transactions(start_date=start_date, end_date=end_date)
    totals = calculate_totals(transactions)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💵 Income",
            f"${totals['income']:,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "💸 Expenses",
            f"${totals['expenses']:,.2f}",
            delta=None
        )
    
    with col3:
        delta = "positive" if totals['balance'] >= 0 else "negative"
        st.metric(
            "📊 Balance",
            f"${totals['balance']:,.2f}",
            delta=None
        )


def render_add_transaction_form():
    """Render form to add a new transaction."""
    st.subheader("➕ Add Transaction")
    
    with st.form("add_transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            description = st.text_input("Description", placeholder="e.g., Grocery shopping")
            amount = st.number_input("Amount", min_value=0.0, value=0.0, step=0.01)
            
            # Transaction type
            trans_type = st.radio(
                "Type",
                [TransactionType.EXPENSE.value, TransactionType.INCOME.value],
                format_func=lambda x: "💸 Expense" if x == "expense" else "💵 Income"
            )
        
        with col2:
            # Category
            if trans_type == "expense":
                categories = ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Healthcare", "Education", "Other"]
            else:
                categories = ["Salary", "Freelance", "Investment", "Gift", "Other"]
            
            category = st.selectbox("Category", categories)
            
            trans_date = st.date_input("Date", value=date.today())
            notes = st.text_input("Notes (optional)", placeholder="Additional details")
        
        submitted = st.form_submit_button("Add Transaction", use_container_width=True, type="primary")
        
        if submitted and description and amount > 0:
            storage = st.session_state.storage
            transaction = storage.create_transaction(
                description=description,
                amount=amount,
                trans_type=trans_type,
                category=category,
                trans_date=trans_date
            )
            st.success(f"✅ Added: {transaction.description} (${transaction.amount:,.2f})")
            st.rerun()


def render_filters():
    """Render filter controls."""
    col1, col2 = st.columns(2)
    
    with col1:
        period_options = {
            "this_week": "This Week",
            "this_month": "This Month",
            "last_month": "Last Month",
            "this_year": "This Year",
            "all_time": "All Time"
        }
        st.session_state.filter_period = st.selectbox(
            "Time Period",
            options=list(period_options.keys()),
            format_func=lambda x: period_options[x]
        )
    
    with col2:
        type_options = {"all": "All Types", "income": "💵 Income", "expense": "💸 Expense"}
        st.session_state.filter_type = st.selectbox(
            "Transaction Type",
            options=list(type_options.keys()),
            format_func=lambda x: type_options[x]
        )


def render_transactions_list():
    """Render the list of transactions."""
    st.subheader("📜 Transactions")
    
    storage = st.session_state.storage
    start_date, end_date = get_date_range(st.session_state.filter_period)
    
    transactions = storage.get_transactions(start_date=start_date, end_date=end_date)
    
    # Apply type filter
    if st.session_state.filter_type != "all":
        transactions = [t for t in transactions if t.type == st.session_state.filter_type]
    
    if not transactions:
        st.info("No transactions found for the selected period.")
        return
    
    # Sort by date (newest first)
    transactions.sort(key=lambda t: t.trans_date, reverse=True)
    
    # Display transactions
    for trans in transactions:
        render_transaction_card(trans)


def render_transaction_card(trans: Transaction):
    """Render a single transaction card."""
    storage = st.session_state.storage
    
    with st.container():
        col1, col2, col3, col4 = st.columns([1, 4, 2, 1])
        
        with col1:
            icon = "💵" if trans.type == TransactionType.INCOME.value else "💸"
            st.markdown(f"### {icon}")
        
        with col2:
            st.markdown(f"**{trans.description}**")
            st.caption(f"📁 {trans.category} • 📅 {trans.trans_date.strftime('%b %d, %Y')}")
        
        with col3:
            amount_color = "green" if trans.type == TransactionType.INCOME.value else "red"
            prefix = "+" if trans.type == TransactionType.INCOME.value else "-"
            st.markdown(f"**${prefix}{trans.amount:,.2f}**")
        
        with col4:
            if st.button("🗑️", key=f"delete_trans_{trans.id}", help="Delete transaction"):
                storage.delete_transaction(trans.id)
                st.rerun()
        
        st.divider()


def render_category_breakdown():
    """Render category breakdown charts."""
    st.subheader("📊 Category Breakdown")
    
    storage = st.session_state.storage
    start_date, end_date = get_date_range(st.session_state.filter_period)
    
    transactions = storage.get_transactions(start_date=start_date, end_date=end_date)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💸 Expenses by Category")
        expense_categories = get_category_totals(transactions, TransactionType.EXPENSE.value)
        
        if expense_categories:
            import pandas as pd
            
            df = pd.DataFrame(
                list(expense_categories.items()),
                columns=['Category', 'Amount']
            ).sort_values('Amount', ascending=False)
            
            st.bar_chart(df.set_index('Category'))
            
            # Show totals
            for cat, amount in sorted(expense_categories.items(), key=lambda x: x[1], reverse=True):
                st.caption(f"**{cat}**: ${amount:,.2f}")
        else:
            st.info("No expenses in this period.")
    
    with col2:
        st.markdown("### 💵 Income by Category")
        income_categories = get_category_totals(transactions, TransactionType.INCOME.value)
        
        if income_categories:
            import pandas as pd
            
            df = pd.DataFrame(
                list(income_categories.items()),
                columns=['Category', 'Amount']
            ).sort_values('Amount', ascending=False)
            
            st.bar_chart(df.set_index('Category'))
            
            # Show totals
            for cat, amount in sorted(income_categories.items(), key=lambda x: x[1], reverse=True):
                st.caption(f"**{cat}**: ${amount:,.2f}")
        else:
            st.info("No income in this period.")


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main page entry point."""
    # Initialize
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    render_header()
    st.divider()
    
    # Summary
    render_summary()
    st.divider()
    
    # Add transaction form
    render_add_transaction_form()
    st.divider()
    
    # Filters
    render_filters()
    st.divider()
    
    # Category breakdown
    render_category_breakdown()
    st.divider()
    
    # Transactions list
    render_transactions_list()


if __name__ == "__main__":
    main()