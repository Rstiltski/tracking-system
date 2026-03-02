"""
UI components for the Time page.

Contains all render functions for the time tracking interface.
"""

import streamlit as st
from datetime import datetime, date, timedelta
import time as time_module
import pandas as pd

from .constants import TIME_CATEGORIES, TIMER_COLOR_RUNNING, TIMER_COLOR_PAUSED, MAX_ENTRIES_DISPLAY
from .helpers import (
    format_duration,
    format_hours,
    get_current_elapsed,
    calculate_xp,
    calculate_xp_for_hours,
    aggregate_daily_totals,
    aggregate_category_totals,
)
from .session_state import start_timer, pause_timer, reset_timer


def render_header():
    """Render page header."""
    st.title("⏱️ Time Tracking")
    st.markdown("Track your time with a built-in timer and categorize your activities.")


def render_timer():
    """Render the main timer interface."""
    st.subheader("⏱️ Timer")
    
    # Category selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        current_category = st.session_state.timer_category
        if current_category in TIME_CATEGORIES:
            current_index = TIME_CATEGORIES.index(current_category)
        else:
            current_index = 0
        
        st.session_state.timer_category = st.selectbox(
            "Category",
            TIME_CATEGORIES,
            index=current_index
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ New Category", use_container_width=True):
            st.info("Add custom categories in settings.")
    
    # Timer display
    elapsed = get_current_elapsed(
        st.session_state.timer_running,
        st.session_state.timer_start,
        st.session_state.timer_elapsed
    )
    
    # Large timer display
    timer_color = TIMER_COLOR_RUNNING if st.session_state.timer_running else TIMER_COLOR_PAUSED
    
    st.markdown(
        f"""
        <div style="
            text-align: center;
            font-size: 72px;
            font-family: monospace;
            padding: 20px;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border-radius: 15px;
            margin: 20px 0;
            color: {timer_color};
        ">
            {format_duration(elapsed)}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Timer controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not st.session_state.timer_running:
            if st.button("▶️ Start", use_container_width=True, type="primary"):
                start_timer()
                st.rerun()
        else:
            if st.button("⏸️ Pause", use_container_width=True, type="primary"):
                current_elapsed = get_current_elapsed(
                    st.session_state.timer_running,
                    st.session_state.timer_start,
                    st.session_state.timer_elapsed
                )
                pause_timer(current_elapsed)
                st.rerun()
    
    with col2:
        if st.session_state.timer_elapsed > 0 or st.session_state.timer_running:
            if st.button("⏹️ Stop & Save", use_container_width=True):
                final_elapsed = get_current_elapsed(
                    st.session_state.timer_running,
                    st.session_state.timer_start,
                    st.session_state.timer_elapsed
                )
                if final_elapsed > 0:
                    # Save time entry
                    entry = {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                        "date": date.today().isoformat(),
                        "category": st.session_state.timer_category,
                        "duration_hours": final_elapsed / 3600,
                        "duration_seconds": final_elapsed,
                        "timestamp": datetime.now().isoformat()
                    }
                    st.session_state.time_entries.append(entry)
                    
                    # Award XP
                    storage = st.session_state.storage
                    xp_earned = calculate_xp(final_elapsed)
                    storage.add_xp(xp_earned)
                    st.success(f"✅ Time entry saved! +{xp_earned} XP")
                
                # Reset timer
                reset_timer()
                st.rerun()
    
    with col3:
        if st.session_state.timer_elapsed > 0 or st.session_state.timer_running:
            if st.button("🔄 Reset", use_container_width=True):
                reset_timer()
                st.rerun()
    
    with col4:
        # Manual entry
        if st.button("📝 Manual Entry", use_container_width=True):
            st.session_state.show_manual_entry = True


def render_manual_entry():
    """Render manual time entry form."""
    if not st.session_state.get('show_manual_entry', False):
        return
    
    st.subheader("📝 Manual Time Entry")
    
    with st.form("manual_time_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            entry_date = st.date_input("Date", value=date.today())
            category = st.selectbox("Category", TIME_CATEGORIES)
        
        with col2:
            hours = st.number_input("Hours", min_value=0, max_value=24, value=0)
            minutes = st.number_input("Minutes", min_value=0, max_value=59, value=30)
        
        notes = st.text_input("Notes (optional)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("Save Entry", type="primary"):
                duration_hours = hours + (minutes / 60)
                if duration_hours > 0:
                    entry = {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                        "date": entry_date.isoformat(),
                        "category": category,
                        "duration_hours": duration_hours,
                        "duration_seconds": int(duration_hours * 3600),
                        "notes": notes,
                        "timestamp": datetime.now().isoformat(),
                        "manual": True
                    }
                    st.session_state.time_entries.append(entry)
                    
                    # Award XP
                    storage = st.session_state.storage
                    xp_earned = calculate_xp_for_hours(duration_hours)
                    storage.add_xp(xp_earned)
                    st.success(f"✅ Entry saved! +{xp_earned} XP")
                
                st.session_state.show_manual_entry = False
                st.rerun()
        
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.show_manual_entry = False
                st.rerun()


def render_daily_summary():
    """Render daily time summary."""
    st.subheader("📊 Today's Summary")
    
    today = date.today()
    today_entries = [
        e for e in st.session_state.time_entries 
        if e.get('date') == today.isoformat()
    ]
    
    if not today_entries:
        st.info("No time tracked today. Start the timer to begin!")
        return
    
    total_hours = sum(e['duration_hours'] for e in today_entries)
    
    # Summary by category
    category_totals = {}
    for entry in today_entries:
        cat = entry['category']
        if cat not in category_totals:
            category_totals[cat] = 0
        category_totals[cat] += entry['duration_hours']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Time Tracked", format_hours(total_hours))
    
    with col2:
        st.metric("Entries", len(today_entries))
    
    # Category breakdown
    st.markdown("#### By Category")
    
    for cat, hours in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (hours / total_hours * 100) if total_hours > 0 else 0
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.progress(percentage / 100)
        
        with col2:
            st.caption(f"{cat}")
        
        with col3:
            st.caption(f"{format_hours(hours)} ({percentage:.0f}%)")


def render_weekly_chart():
    """Render weekly time distribution chart."""
    st.subheader("📈 Weekly Overview")
    
    # Get entries from the past 7 days
    today = date.today()
    week_start = today - timedelta(days=6)
    
    # Aggregate data
    daily_totals = aggregate_daily_totals(st.session_state.time_entries, week_start, today)
    category_totals = aggregate_category_totals(st.session_state.time_entries, week_start, today)
    
    # Create chart
    df = pd.DataFrame([
        {'Date': d.strftime('%a'), 'Hours': h}
        for d, h in sorted(daily_totals.items())
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Daily Hours**")
        st.bar_chart(df.set_index('Date'))
    
    with col2:
        st.markdown("**By Category**")
        if category_totals:
            cat_df = pd.DataFrame([
                {'Category': cat, 'Hours': hours}
                for cat, hours in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            ])
            st.bar_chart(cat_df.set_index('Category'))
        else:
            st.info("No data yet")


def render_time_entries():
    """Render list of time entries."""
    st.subheader("📜 Recent Entries")
    
    if not st.session_state.time_entries:
        st.info("No time entries yet. Start tracking your time!")
        return
    
    # Sort by timestamp (newest first)
    entries = sorted(
        st.session_state.time_entries,
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )
    
    for entry in entries[:MAX_ENTRIES_DISPLAY]:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                entry_date = date.fromisoformat(entry['date'])
                st.markdown(f"**{entry_date.strftime('%b %d')}**")
            
            with col2:
                st.markdown(f"📁 {entry['category']}")
            
            with col3:
                st.markdown(f"⏱️ {format_hours(entry['duration_hours'])}")
            
            with col4:
                if st.button("🗑️", key=f"delete_time_{entry['id']}", help="Delete entry"):
                    st.session_state.time_entries.remove(entry)
                    st.rerun()
        
        st.divider()