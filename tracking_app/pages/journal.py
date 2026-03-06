"""Journal Page - Personal Journaling"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import get_storage
from tracking_app.components.sidebar import render_sidebar
from tracking_app.pages.journal import init_session_state, render_header, render_add_entry_form, render_entry_list, render_search, render_edit_form

st.set_page_config(page_title="Journal - Veryfyn", page_icon="📓", layout="wide")

def main():
    init_session_state()
    render_sidebar()
    render_header()
    st.divider()
    
    storage = st.session_state.storage
    
    if st.session_state.journal_editing_entry:
        entry = storage.get_journal_entry(st.session_state.journal_editing_entry)
        if entry:
            render_edit_form(storage, entry)
            return
        st.session_state.journal_editing_entry = None
    
    query, category = render_search(storage)
    st.divider()
    
    with st.expander("✨ Add New Entry", expanded=False):
        render_add_entry_form(storage)
    st.divider()
    
    if query:
        entries = storage.search_journal_entries(query)
    elif category:
        entries = storage.get_journal_entries(category=category)
    else:
        entries = storage.get_journal_entries()
    
    render_entry_list(storage, entries)

if __name__ == "__main__":
    main()