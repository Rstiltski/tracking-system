"""
Health Page - Health Metrics Tracking

Streamlit page for tracking weight, sleep, mood, and other health metrics.

Usage:
    streamlit run tracking_app/pages/health.py
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage
from tracking_app.models import HealthEntry, Mood
from tracking_app.components.sidebar import render_sidebar


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Health - Veryfyn",
    page_icon="❤️",
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
    
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = date.today()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_mood_icon(mood: str) -> str:
    """Get emoji for mood."""
    icons = {
        Mood.GREAT.value: "😊",
        Mood.GOOD.value: "🙂",
        Mood.OKAY.value: "😐",
        Mood.BAD.value: "😔"
    }
    return icons.get(mood, "😐")


def get_mood_color(mood: str) -> str:
    """Get color for mood."""
    colors = {
        Mood.GREAT.value: "#10b981",
        Mood.GOOD.value: "#6366f1",
        Mood.OKAY.value: "#f59e0b",
        Mood.BAD.value: "#ef4444"
    }
    return colors.get(mood, "#6b7280")


def calculate_average(entries: List[HealthEntry], field: str) -> Optional[float]:
    """Calculate average for a field."""
    values = [getattr(e, field) for e in entries if getattr(e, field) is not None]
    if not values:
        return None
    return sum(values) / len(values)


def get_health_trend(entries: List[HealthEntry], field: str) -> str:
    """Get trend direction for a health metric."""
    if len(entries) < 2:
        return "neutral"
    
    values = [(e.entry_date, getattr(e, field)) for e in entries if getattr(e, field) is not None]
    values.sort(key=lambda x: x[0])
    
    if len(values) < 2:
        return "neutral"
    
    recent = values[-1][1]
    previous = values[-2][1]
    
    if recent > previous:
        return "up"
    elif recent < previous:
        return "down"
    return "stable"


# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

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
                min_value=0.0,
                max_value=500.0,
                value=existing.weight if existing else None,
                step=0.1,
                format="%.1f"
            )
        
        with col2:
            sleep_hours = st.number_input(
                "Sleep (hours)",
                min_value=0.0,
                max_value=24.0,
                value=existing.sleep_hours if existing else None,
                step=0.5,
                format="%.1f"
            )
        
        with col3:
            mood_options = {
                Mood.GREAT.value: "😊 Great",
                Mood.GOOD.value: "🙂 Good",
                Mood.OKAY.value: "😐 Okay",
                Mood.BAD.value: "😔 Bad"
            }
            default_mood = existing.mood if existing else Mood.GOOD.value
            mood_index = list(mood_options.keys()).index(default_mood) if default_mood in mood_options else 1
            mood = st.selectbox(
                "Mood",
                options=list(mood_options.keys()),
                format_func=lambda x: mood_options[x],
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
                mood=Mood.GOOD.value,
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
            trend_icon = "📈" if trend == "up" else "📉" if trend == "down" else "➡️"
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
            trend_icon = "📈" if trend == "up" else "📉" if trend == "down" else "➡️"
            st.metric(
                "Avg Sleep",
                f"{avg_sleep:.1f} hrs",
                delta=trend_icon
            )
        else:
            st.metric("Avg Sleep", "No data")
    
    with col3:
        # Most common mood
        moods = [e.mood for e in entries if e.mood]
        if moods:
            from collections import Counter
            most_common = Counter(moods).most_common(1)[0][0]
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
            import pandas as pd
            
            df = pd.DataFrame(weight_data, columns=['Date', 'Weight'])
            df = df.set_index('Date')
            st.line_chart(df)
        else:
            st.info("No weight data available.")
    
    with tab2:
        sleep_data = [(e.entry_date, e.sleep_hours) for e in entries if e.sleep_hours]
        if sleep_data:
            import pandas as pd
            
            df = pd.DataFrame(sleep_data, columns=['Date', 'Sleep Hours'])
            df = df.set_index('Date')
            st.line_chart(df)
        else:
            st.info("No sleep data available.")
    
    with tab3:
        # Mood over time as a scatter plot or bar chart
        mood_data = [(e.entry_date, e.mood) for e in entries if e.mood]
        if mood_data:
            import pandas as pd
            
            # Convert mood to numeric
            mood_values = {
                Mood.GREAT.value: 4,
                Mood.GOOD.value: 3,
                Mood.OKAY.value: 2,
                Mood.BAD.value: 1
            }
            
            df = pd.DataFrame(
                [(d, mood_values.get(m, 2)) for d, m in mood_data],
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
    
    for entry in entries[:10]:  # Show last 10 entries
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
    
    # Quick log
    render_quick_log()
    st.divider()
    
    # Summary
    render_summary()
    st.divider()
    
    # Charts
    render_charts()
    st.divider()
    
    # History
    render_history()


if __name__ == "__main__":
    main()