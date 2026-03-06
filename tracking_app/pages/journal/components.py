"""UI components for the Journal page."""

import streamlit as st
from datetime import datetime
from typing import List
import random

from tracking_app.models import JournalEntry
from .constants import JOURNAL_CATEGORIES, JOURNAL_CATEGORY_EMOJIS, JOURNAL_PROMPTS, JOURNAL_CATEGORY_COLORS
from .helpers import get_category_emoji, get_category_color

def render_header():
    st.title("📓 Journal")
    st.markdown("*Capture your thoughts, ideas, and reflections*")

def render_add_entry_form(storage):
    st.subheader("✨ New Entry")
    
    # Category selector
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Title", placeholder="Entry title...", key="journal_new_title")
    with col2:
        category = st.selectbox(
            "Category",
            JOURNAL_CATEGORIES,
            format_func=lambda x: f"{get_category_emoji(x)} {x.replace('_', ' ').title()}",
            key="journal_new_category"
        )
    
    # Prompt suggestion
    if st.button("💡 Get a prompt", type="secondary"):
        prompts = JOURNAL_PROMPTS.get(category, JOURNAL_PROMPTS["free_write"])
        st.session_state.journal_prompt = random.choice(prompts)
    
    if 'journal_prompt' in st.session_state:
        st.info(f"💡 **Prompt:** {st.session_state.journal_prompt}")
    
    content = st.text_area("Content", height=200, placeholder="Write your thoughts...", key="journal_new_content")
    tags = st.text_input("Tags (comma-separated)", placeholder="tag1, tag2...", key="journal_new_tags")
    
    if st.button("Save Entry", type="primary"):
        if content.strip():
            parsed_tags = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
            storage.create_journal_entry(title=title or "Untitled", content=content, category=category, tags=parsed_tags)
            st.success("✅ Entry saved!")
            st.rerun()
        else:
            st.warning("Please write something.")

def render_entry_card(entry: JournalEntry, storage):
    emoji = get_category_emoji(entry.category)
    color = get_category_color(entry.category)
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### {emoji} {entry.title}")
        with col2:
            st.caption(entry.created_at.strftime("%b %d, %Y") if entry.created_at else "")
        
        st.markdown(entry.content)
        
        if entry.tags:
            st.markdown(" ".join([f"`{tag}`" for tag in entry.tags]), unsafe_allow_html=True)
        
        col_a, col_b = st.columns([1, 4])
        with col_a:
            if st.button("🗑️", key=f"del_journal_{entry.id}"):
                storage.delete_journal_entry(entry.id)
                st.rerun()
        st.divider()

def render_entry_list(storage, entries: List[JournalEntry]):
    if not entries:
        st.info("📝 No journal entries yet. Start writing above!")
        return
    for entry in entries:
        render_entry_card(entry, storage)

def render_search(storage):
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("🔍 Search", placeholder="Search entries...", key="journal_search")
    with col2:
        category = st.selectbox("Category", ["All"] + JOURNAL_CATEGORIES, key="journal_cat_filter")
    return query, None if category == "All" else category

def render_edit_form(storage, entry: JournalEntry):
    st.subheader("✏️ Edit Entry")
    title = st.text_input("Title", value=entry.title, key=f"edit_journal_title_{entry.id}")
    category = st.selectbox("Category", JOURNAL_CATEGORIES, index=JOURNAL_CATEGORIES.index(entry.category) if entry.category in JOURNAL_CATEGORIES else 0, key=f"edit_journal_cat_{entry.id}")
    content = st.text_area("Content", value=entry.content, height=200, key=f"edit_journal_content_{entry.id}")
    tags = st.text_input("Tags", value=", ".join(entry.tags) if entry.tags else "", key=f"edit_journal_tags_{entry.id}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save", type="primary"):
            parsed_tags = [t.strip() for t in tags.split(',') if t.strip()]
            storage.update_journal_entry(entry.id, title=title, content=content, category=category, tags=parsed_tags)
            st.session_state.journal_editing_entry = None
            st.rerun()
    with col2:
        if st.button("Cancel"):
            st.session_state.journal_editing_entry = None
            st.rerun()