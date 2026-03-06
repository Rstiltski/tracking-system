"""
UI components for the Diary page.

Renders various components for diary entry management.
"""

import streamlit as st
from datetime import date, datetime, timedelta
import calendar
from typing import List, Optional
import random

from tracking_app.models import DiaryEntry
from .constants import DIARY_MOODS, DIARY_MOOD_EMOJIS, DIARY_PROMPTS, DEFAULT_DIARY_TAGS
from .helpers import get_mood_emoji, get_mood_color, format_entry_date, truncate_text, get_word_count


def render_header():
    """Render the diary page header."""
    st.title("📔 Private Diary")
    st.markdown("*Your personal space for thoughts, reflections, and memories*")
    st.caption("🔒 All entries are private and stored locally")


def render_add_entry_form(storage):
    """
    Render the form for adding a new diary entry.

    Args:
        storage: Storage instance for saving entries
    """
    st.subheader("✨ New Entry")

    # Random prompt suggestion
    if st.button("💡 Get a writing prompt", type="secondary"):
        st.session_state.diary_prompt = random.choice(DIARY_PROMPTS)

    if 'diary_prompt' in st.session_state:
        st.info(f"💡 **Prompt:** {st.session_state.diary_prompt}")

    # Entry form
    col1, col2 = st.columns([3, 1])

    with col1:
        entry_title = st.text_input(
            "Title",
            placeholder="Give your entry a title...",
            key="diary_new_title"
        )

    with col2:
        entry_date = st.date_input(
            "Date",
            value=st.session_state.get('diary_selected_date', date.today()),
            key="diary_new_date"
        )

    # Mood selector with emojis
    st.markdown("**How are you feeling?**")
    mood_cols = st.columns(len(DIARY_MOODS))
    selected_mood = st.session_state.get('diary_new_mood', 'good')

    for i, mood in enumerate(DIARY_MOODS):
        with mood_cols[i]:
            emoji = get_mood_emoji(mood)
            is_selected = selected_mood == mood
            button_type = "primary" if is_selected else "secondary"
            if st.button(
                f"{emoji}",
                key=f"mood_{mood}",
                type=button_type,
                use_container_width=True
            ):
                st.session_state.diary_new_mood = mood
                st.rerun()

    # Content textarea
    content = st.text_area(
        "What's on your mind?",
        height=200,
        placeholder="Write your thoughts here...",
        key="diary_new_content"
    )

    # Tags
    col_tag1, col_tag2 = st.columns([3, 1])
    with col_tag1:
        custom_tags = st.text_input(
            "Tags (comma-separated)",
            placeholder="personal, reflection, goals...",
            key="diary_new_tags"
        )

    with col_tag2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Add Entry", type="primary", use_container_width=True):
            if content.strip():
                # Parse tags
                tags = [t.strip() for t in custom_tags.split(',') if t.strip()] if custom_tags else []

                # Create entry
                mood = st.session_state.get('diary_new_mood', 'good')
                entry = storage.create_diary_entry(
                    title=entry_title or format_entry_date(entry_date),
                    content=content,
                    entry_date=entry_date,
                    mood=mood,
                    tags=tags
                )

                st.success("✅ Entry saved!")

                # Clear form
                st.session_state.diary_new_title = ""
                st.session_state.diary_new_content = ""
                st.session_state.diary_new_tags = ""
                if 'diary_prompt' in st.session_state:
                    del st.session_state.diary_prompt

                st.rerun()
            else:
                st.warning("Please write something in your entry.")

    # Word count
    if content:
        st.caption(f"📝 {get_word_count(content)} words")


def render_entry_card(entry: DiaryEntry, storage):
    """
    Render a single diary entry card.

    Args:
        entry: DiaryEntry to render
        storage: Storage instance for actions
    """
    mood_emoji = get_mood_emoji(entry.mood)
    mood_color = get_mood_color(entry.mood)

    with st.container():
        # Entry header
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"### {entry.title}")

        with col2:
            st.markdown(f"<span style='font-size: 1.5rem;'>{mood_emoji}</span>", unsafe_allow_html=True)

        with col3:
            st.caption(format_entry_date(entry.entry_date))

        # Content preview
        st.markdown(entry.content)

        # Tags
        if entry.tags:
            tag_str = " ".join([f"`{tag}`" for tag in entry.tags])
            st.markdown(f"<small>{tag_str}</small>", unsafe_allow_html=True)

        # Actions
        col_action1, col_action2, col_action3 = st.columns([1, 1, 4])

        with col_action1:
            if st.button("✏️ Edit", key=f"edit_entry_{entry.id}"):
                st.session_state.diary_editing_entry = entry.id
                st.rerun()

        with col_action2:
            if st.button("🗑️ Delete", key=f"del_entry_{entry.id}"):
                storage.delete_diary_entry(entry.id)
                st.success("Entry deleted")
                st.rerun()

        st.divider()


def render_entry_list(storage, entries: List[DiaryEntry]):
    """
    Render a list of diary entries.

    Args:
        storage: Storage instance
        entries: List of DiaryEntry objects to display
    """
    if not entries:
        st.info("📝 No diary entries yet. Start writing your first entry above!")
        return

    st.markdown(f"**{len(entries)} entries**")

    for entry in entries:
        render_entry_card(entry, storage)


def render_calendar_view(storage, year: int, month: int):
    """
    Render a calendar view for diary entries.

    Args:
        storage: Storage instance
        year: Year to display
        month: Month to display (1-12)
    """
    # Get entries for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    entries = storage.get_diary_entries(start_date=start_date, end_date=end_date)

    # Create a lookup for entries by date
    entries_by_date = {e.entry_date: e for e in entries}

    # Calendar header
    month_name = calendar.month_name[month]
    st.subheader(f"📅 {month_name} {year}")

    # Navigation
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if st.button("◀ Previous"):
            new_month = month - 1
            new_year = year
            if new_month < 1:
                new_month = 12
                new_year = year - 1
            st.session_state.diary_calendar_month = new_month
            st.session_state.diary_calendar_year = new_year
            st.rerun()

    with col_next:
        if st.button("Next ▶"):
            new_month = month + 1
            new_year = year
            if new_month > 12:
                new_month = 1
                new_year = year + 1
            st.session_state.diary_calendar_month = new_month
            st.session_state.diary_calendar_year = new_year
            st.rerun()

    # Calendar grid
    cal = calendar.Calendar(firstweekday=6)  # Sunday first
    weeks = cal.monthdayscalendar(year, month)

    # Day headers
    header_cols = st.columns(7)
    day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    for i, day_name in enumerate(day_names):
        with header_cols[i]:
            st.markdown(f"**{day_name}**")

    # Days
    for week in weeks:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day > 0:
                    current_date = date(year, month, day)
                    has_entry = current_date in entries_by_date

                    if has_entry:
                        entry = entries_by_date[current_date]
                        mood_emoji = get_mood_emoji(entry.mood)
                        st.markdown(
                            f"<div style='text-align: center; padding: 5px; background-color: {get_mood_color(entry.mood)}20; border-radius: 5px;'>"
                            f"<strong>{day}</strong><br>{mood_emoji}</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(f"<div style='text-align: center; padding: 5px;'><strong>{day}</strong></div>", unsafe_allow_html=True)


def render_search(storage):
    """
    Render search and filter controls.

    Args:
        storage: Storage instance
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        search_query = st.text_input(
            "🔍 Search entries",
            placeholder="Search by title or content...",
            key="diary_search_input"
        )

    with col2:
        mood_filter = st.selectbox(
            "Filter by mood",
            ["All"] + DIARY_MOODS,
            key="diary_mood_filter"
        )

    return search_query, None if mood_filter == "All" else mood_filter


def render_edit_form(storage, entry: DiaryEntry):
    """
    Render the edit form for a diary entry.

    Args:
        storage: Storage instance
        entry: DiaryEntry to edit
    """
    st.subheader("✏️ Edit Entry")

    # Pre-populate form with existing data
    title = st.text_input("Title", value=entry.title, key=f"edit_title_{entry.id}")
    entry_date = st.date_input("Date", value=entry.entry_date, key=f"edit_date_{entry.id}")

    # Mood selector
    st.markdown("**How are you feeling?**")
    mood_cols = st.columns(len(DIARY_MOODS))
    selected_mood = st.session_state.get(f'edit_mood_{entry.id}', entry.mood)

    for i, mood in enumerate(DIARY_MOODS):
        with mood_cols[i]:
            emoji = get_mood_emoji(mood)
            is_selected = selected_mood == mood
            button_type = "primary" if is_selected else "secondary"
            if st.button(
                f"{emoji}",
                key=f"edit_mood_btn_{mood}_{entry.id}",
                type=button_type,
                use_container_width=True
            ):
                st.session_state[f'edit_mood_{entry.id}'] = mood
                st.rerun()

    content = st.text_area(
        "Content",
        value=entry.content,
        height=200,
        key=f"edit_content_{entry.id}"
    )

    tags_str = ", ".join(entry.tags) if entry.tags else ""
    tags = st.text_input("Tags (comma-separated)", value=tags_str, key=f"edit_tags_{entry.id}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Changes", type="primary", use_container_width=True):
            parsed_tags = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
            mood = st.session_state.get(f'edit_mood_{entry.id}', entry.mood)

            storage.update_diary_entry(
                entry.id,
                title=title,
                content=content,
                entry_date=entry_date,
                mood=mood,
                tags=parsed_tags
            )

            st.session_state.diary_editing_entry = None
            st.success("✅ Entry updated!")
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.diary_editing_entry = None
            st.rerun()