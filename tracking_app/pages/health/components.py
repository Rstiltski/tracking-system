"""
UI components for the Health page.

Contains all render functions for the health tracking interface.
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from typing import List

from tracking_app.models import HealthEntry, Mood

from .constants import (
    MOOD_OPTIONS,
    MOOD_ICONS,
    MOOD_VALUES,
    DEFAULT_MOOD,
    WEIGHT_MIN,
    WEIGHT_MAX,
    SLEEP_MIN,
    SLEEP_MAX,
    HISTORY_LIMIT,
)
from .helpers import (
    get_mood_icon,
    get_mood_value,
    calculate_average,
    get_health_trend,
    get_most_common_mood,
    format_trend_icon,
)


def render_header():
    """Render page header."""
    st.title("❤️ Health")
    st.markdown("Track your weight, sleep, mood, and overall well-being.")


def render_quick_log():
    """Render quick logging form for today."""
    st.subheader("📝 Log Today's Health")
    
    storage = st.session_state.storage
    today = date.today()
    
    # Check if entry exists
    existing = storage.get_health_entry(today)
    
    with st.form("health_log_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            weight = st.number_input(
                "Weight (kg)",
                min_value=WEIGHT_MIN,
                max_value=WEIGHT_MAX,
                value=existing.weight if existing else None,
                step=0.1,
                format="%.1f"
            )
        
        with col2:
            sleep_hours = st.number_input(
                "Sleep (hours)",
                min_value=SLEEP_MIN,
                max_value=SLEEP_MAX,
                value=existing.sleep_hours if existing else None,
                step=0.5,
                format="%.1f"
            )
        
        with col3:
            default_mood = existing.mood if existing else DEFAULT_MOOD
            mood_index = list(MOOD_OPTIONS.keys()).index(default_mood) if default_mood in MOOD_OPTIONS else 1
            mood = st.selectbox(
                "Mood",
                options=list(MOOD_OPTIONS.keys()),
                format_func=lambda x: MOOD_OPTIONS[x],
                index=mood_index
            )
        
        notes = st.text_area(
            "Notes (optional)",
            value=existing.notes if existing else "",
            placeholder="How are you feeling today?"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 Save Entry", use_container_width=True, type="primary")
        
        with col2:
            clear = st.form_submit_button("🗑️ Clear", use_container_width=True)
        
        if submitted:
            storage.create_health_entry(
                entry_date=today,
                weight=weight if weight > 0 else None,
                sleep_hours=sleep_hours if sleep_hours > 0 else None,
                mood=mood,
                notes=notes
            )
            st.success("✅ Health entry saved!")
            st.rerun()
        
        if clear:
            storage.create_health_entry(
                entry_date=today,
                weight=None,
                sleep_hours=None,
                mood=DEFAULT_MOOD,
                notes=""
            )
            st.rerun()


def render_summary():
    """Render health summary for the past week."""
    st.subheader("📊 Weekly Summary")
    
    storage = st.session_state.storage
    entries = storage.get_health_entries(
        start_date=date.today() - timedelta(days=7),
        end_date=date.today()
    )
    
    if not entries:
        st.info("No health entries in the past week. Start logging to see your summary!")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_weight = calculate_average(entries, 'weight')
        if avg_weight:
            trend = get_health_trend(entries, 'weight')
            trend_icon = format_trend_icon(trend)
            st.metric(
                "Avg Weight",
                f"{avg_weight:.1f} kg",
                delta=trend_icon
            )
        else:
            st.metric("Avg Weight", "No data")
    
    with col2:
        avg_sleep = calculate_average(entries, 'sleep_hours')
        if avg_sleep:
            trend = get_health_trend(entries, 'sleep_hours')
            trend_icon = format_trend_icon(trend)
            st.metric(
                "Avg Sleep",
                f"{avg_sleep:.1f} hrs",
                delta=trend_icon
            )
        else:
            st.metric("Avg Sleep", "No data")
    
    with col3:
        # Most common mood
        most_common = get_most_common_mood(entries)
        if most_common:
            st.metric(
                "Most Common Mood",
                f"{get_mood_icon(most_common)} {most_common.title()}"
            )
        else:
            st.metric("Most Common Mood", "No data")


def render_charts():
    """Render health trend charts."""
    st.subheader("📈 Trends")
    
    storage = st.session_state.storage
    entries = storage.get_health_entries(
        start_date=date.today() - timedelta(days=30),
        end_date=date.today()
    )
    
    if not entries:
        st.info("No data to display. Start logging your health metrics!")
        return
    
    # Sort by date
    entries.sort(key=lambda e: e.entry_date)
    
    tab1, tab2, tab3 = st.tabs(["Weight", "Sleep", "Mood"])
    
    with tab1:
        weight_data = [(e.entry_date, e.weight) for e in entries if e.weight]
        if weight_data:
            df = pd.DataFrame(weight_data, columns=['Date', 'Weight'])
            df = df.set_index('Date')
            st.line_chart(df)
        else:
            st.info("No weight data available.")
    
    with tab2:
        sleep_data = [(e.entry_date, e.sleep_hours) for e in entries if e.sleep_hours]
        if sleep_data:
            df = pd.DataFrame(sleep_data, columns=['Date', 'Sleep Hours'])
            df = df.set_index('Date')
            st.line_chart(df)
        else:
            st.info("No sleep data available.")
    
    with tab3:
        # Mood over time as a bar chart
        mood_data = [(e.entry_date, e.mood) for e in entries if e.mood]
        if mood_data:
            # Convert mood to numeric
            df = pd.DataFrame(
                [(d, get_mood_value(m)) for d, m in mood_data],
                columns=['Date', 'Mood']
            )
            df = df.set_index('Date')
            st.bar_chart(df)
            
            # Legend
            st.caption("Mood Scale: 😊 Great (4) | 🙂 Good (3) | 😐 Okay (2) | 😔 Bad (1)")
        else:
            st.info("No mood data available.")


def render_history():
    """Render health entry history."""
    st.subheader("📜 History")
    
    storage = st.session_state.storage
    entries = storage.get_health_entries(
        start_date=date.today() - timedelta(days=30),
        end_date=date.today()
    )
    
    if not entries:
        st.info("No health entries yet. Start logging your health!")
        return
    
    # Sort by date (newest first)
    entries.sort(key=lambda e: e.entry_date, reverse=True)
    
    for entry in entries[:HISTORY_LIMIT]:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
            
            with col1:
                st.markdown(f"**{entry.entry_date.strftime('%b %d')}**")
            
            with col2:
                if entry.weight:
                    st.markdown(f"⚖️ {entry.weight:.1f} kg")
                else:
                    st.markdown("⚖️ --")
            
            with col3:
                if entry.sleep_hours:
                    st.markdown(f"😴 {entry.sleep_hours:.1f} hrs")
                else:
                    st.markdown("😴 --")
            
            with col4:
                st.markdown(f"{get_mood_icon(entry.mood)} {entry.mood.title()}")
                if entry.notes:
                    st.caption(entry.notes[:50] + "..." if len(entry.notes) > 50 else entry.notes)
        
        st.divider()