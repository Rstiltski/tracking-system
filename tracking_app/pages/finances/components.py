"""
UI components for the Finances page.

Contains all render functions for the financial tracking interface.
"""

import streamlit as st
import pandas as pd
from datetime import date
from typing import List

from tracking_app.models import Transaction, TransactionType

from .constants import (
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    PERIOD_OPTIONS,
    TYPE_OPTIONS,
    INCOME_ICON,
    EXPENSE_ICON,
    BALANCE_ICON,
)
from .helpers import (
    get_date_range,
    calculate_totals,
    get_category_totals,
    format_currency,
)


def render_header():
    """Render page header."""
    st.title("💰 Finances")
    st.markdown("Track your income, expenses, and monitor your budget.")


def render_summary():
    """Render financial summary metrics."""
    storage = st.session_state.storage
    start_date, end_date = get_date_range(st.session_state.filter_period)
    
    transactions = storage.get_transactions(start_date=start_date, end_date=end_date)
    totals = calculate_totals(transactions)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            f"{INCOME_ICON} Income",
            format_currency(totals['income']),
            delta=None
        )
    
    with col2:
        st.metric(
            f"{EXPENSE_ICON} Expenses",
            format_currency(totals['expenses']),
            delta=None
        )
    
    with col3:
        st.metric(
            f"{BALANCE_ICON} Balance",
            format_currency(totals['balance']),
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
                format_func=lambda x: f"{EXPENSE_ICON} Expense" if x == "expense" else f"{INCOME_ICON} Income"
            )
        
        with col2:
            # Category based on type
            if trans_type == "expense":
                categories = EXPENSE_CATEGORIES
            else:
                categories = INCOME_CATEGORIES
            
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
            st.success(f"✅ Added: {transaction.description} ({format_currency(transaction.amount)})")
            st.rerun()


def render_filters():
    """Render filter controls."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.filter_period = st.selectbox(
            "Time Period",
            options=list(PERIOD_OPTIONS.keys()),
            format_func=lambda x: PERIOD_OPTIONS[x]
        )
    
    with col2:
        st.session_state.filter_type = st.selectbox(
            "Transaction Type",
            options=list(TYPE_OPTIONS.keys()),
            format_func=lambda x: TYPE_OPTIONS[x]
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
    """
    Render a single transaction card.
    
    Args:
        trans: Transaction object to render
    """
    storage = st.session_state.storage
    
    with st.container():
        col1, col2, col3, col4 = st.columns([1, 4, 2, 1])
        
        with col1:
            icon = INCOME_ICON if trans.type == TransactionType.INCOME.value else EXPENSE_ICON
            st.markdown(f"### {icon}")
        
        with col2:
            st.markdown(f"**{trans.description}**")
            st.caption(f"📁 {trans.category} • 📅 {trans.trans_date.strftime('%b %d, %Y')}")
        
        with col3:
            prefix = "+" if trans.type == TransactionType.INCOME.value else "-"
            st.markdown(f"**{prefix}{format_currency(trans.amount)}**")
        
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
        st.markdown(f"### {EXPENSE_ICON} Expenses by Category")
        expense_categories = get_category_totals(transactions, TransactionType.EXPENSE.value)
        
        if expense_categories:
            df = pd.DataFrame(
                list(expense_categories.items()),
                columns=['Category', 'Amount']
            ).sort_values('Amount', ascending=False)
            
            st.bar_chart(df.set_index('Category'))
            
            # Show totals
            for cat, amount in sorted(expense_categories.items(), key=lambda x: x[1], reverse=True):
                st.caption(f"**{cat}**: {format_currency(amount)}")
        else:
            st.info("No expenses in this period.")
    
    with col2:
        st.markdown(f"### {INCOME_ICON} Income by Category")
        income_categories = get_category_totals(transactions, TransactionType.INCOME.value)
        
        if income_categories:
            df = pd.DataFrame(
                list(income_categories.items()),
                columns=['Category', 'Amount']
            ).sort_values('Amount', ascending=False)
            
            st.bar_chart(df.set_index('Category'))
            
            # Show totals
            for cat, amount in sorted(income_categories.items(), key=lambda x: x[1], reverse=True):
                st.caption(f"**{cat}**: {format_currency(amount)}")
        else:
            st.info("No income in this period.")