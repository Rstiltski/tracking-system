"""
Habits Page - Bento Earth Theme (Phase 12 Design System v2)

Streamlit page for creating, tracking, and managing daily habits with the
Bento Earth theme - warm earthy palette with elegant bento grid layout.

Features:
- ✅ Bento grid layout with warm earthy colors
- ✅ Progress ring with completion percentage
- ✅ Habit cards with score tracking
- ✅ Streak tracking with visual indicators
- ✅ Quick complete functionality
- ✅ Add/Edit habit modals
- ✅ Motivational quote section
- ✅ Responsive design

Theme: Bento Earth
- Warm paper background: #f2ece4
- Card background: #faf6f0
- Primary accent: #a47764 (mocha)
- Action color: #b17a50 (wood)
- Text: #2d1f14 (ink)
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Phase 12 Design System
from tracking_app.design.theme import apply_design_system, get_current_theme
from tracking_app.design.tokens import COLORS
from tracking_app.storage import get_storage
from tracking_app.components.session import init_session_state, add_xp

# Import habits components
from tracking_app.pages.habits import (
    init_session_state as init_habits_session_state,
    render_habit_header,
    render_edit_habit_modal,
)


# =============================================================================
# BENTO EARTH THEME COLORS
# =============================================================================

EARTH = {
    "bg": "#f2ece4",
    "card": "#faf6f0",
    "mocha": "#a47764",
    "clay": "#c99383",
    "wood": "#b17a50",
    "ink": "#2d1f14",
    "muted": "#9a8070",
    "soft": "#e8ddd4",
    "green": "#5a7a5c",
    "amber": "#c8842a",
    "border": "#dfd3c6",
}


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Habits - Veryfyn",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Bento Earth theme
apply_design_system(theme="bento_earth")


# =============================================================================
# CUSTOM CSS FOR BENTO EARTH THEME
# =============================================================================

def render_bento_earth_styles():
    """Render Bento Earth specific styles."""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Instrument+Serif:wght@400&display=swap');
    
    /* Bento Earth Theme Overrides */
    .theme-bento-earth {{
        font-family: 'Georgia', 'Palatino', serif !important;
    }}
    
    .theme-bento-earth h1 {{
        font-family: 'Georgia', serif !important;
        letter-spacing: -2px !important;
    }}
    
    .theme-bento-earth .stButton > button {{
        font-family: 'Poppins', sans-serif !important;
        border-radius: 12px !important;
    }}
    
    /* Bento Grid */
    .bento-grid {{
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 14px;
        margin-bottom: 20px;
    }}
    
    .bento-cell {{
        background: {EARTH["card"]};
        border: 1.5px solid {EARTH["border"]};
        border-radius: 20px;
        padding: 20px;
        transition: box-shadow 0.25s ease, transform 0.25s ease !important;
    }}
    
    .bento-cell:hover {{
        box-shadow: 0 12px 40px rgba(45,31,20,0.14);
        transform: translateY(-3px);
    }}
    
    /* Progress Ring */
    .progress-ring-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    
    /* Habit Row */
    .habit-row {{
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 14px 24px;
        border-bottom: 1px solid {EARTH["border"]};
        cursor: pointer;
        transition: all 0.2s;
    }}
    
    .habit-row:hover {{
        background: #f0e6d8;
    }}
    
    .habit-row:last-child {{
        border-bottom: none;
    }}
    
    /* Custom Checkbox */
    .habit-checkbox {{
        width: 26px;
        height: 26px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        transition: all 0.2s;
        flex-shrink: 0;
    }}
    
    .habit-checkbox.completed {{
        background: {EARTH["wood"]};
        border: 2px solid {EARTH["wood"]};
        color: #fff;
        box-shadow: 0 0 0 4px rgba(177,122,80,0.15);
    }}
    
    .habit-checkbox.incomplete {{
        background: transparent;
        border: 2px solid {EARTH["border"]};
        color: transparent;
    }}
    
    /* Score Badge */
    .score-badge {{
        font-family: 'Poppins', sans-serif;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 100px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .score-badge.excellent {{
        background: #e8f5e9;
        color: {EARTH["green"]};
    }}
    
    .score-badge.strong {{
        background: #fff8e1;
        color: {EARTH["amber"]};
    }}
    
    .score-badge.building {{
        background: #fce4ec;
        color: #c62828;
    }}
    
    /* Progress Bar */
    .habit-progress {{
        height: 3px;
        background: {EARTH["soft"]};
        border-radius: 2px;
        margin-top: 6px;
    }}
    
    .habit-progress-fill {{
        height: 100%;
        background: linear-gradient(90deg, {EARTH["clay"]}, {EARTH["wood"]});
        border-radius: 2px;
        transition: width 1s ease;
    }}
    
    /* Stat Card */
    .stat-card {{
        background: {EARTH["card"]};
        border: 1.5px solid {EARTH["border"]};
        border-radius: 18px;
        padding: 20px 22px;
        transition: all 0.25s;
    }}
    
    .stat-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(45,31,20,0.1);
    }}
    
    /* Buttons */
    .earth-btn-primary {{
        background: {EARTH["wood"]};
        border: none;
        color: #fff;
        padding: 10px 20px;
        border-radius: 12px;
        font-size: 13px;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 4px 16px rgba(177,122,80,0.35);
    }}
    
    .earth-btn-primary:hover {{
        background: #8a5e3e;
        transform: translateY(-1px);
    }}
    
    .earth-btn-ghost {{
        background: transparent;
        border: 1.5px solid {EARTH["border"]};
        color: {EARTH["muted"]};
        padding: 10px 18px;
        border-radius: 12px;
        font-size: 13px;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }}
    
    .earth-btn-ghost:hover {{
        background: {EARTH["soft"]};
    }}
    
    /* Quote Block */
    .quote-block {{
        background: linear-gradient(145deg, {EARTH["wood"]}, {EARTH["mocha"]});
        border-radius: 20px;
        padding: 28px;
        color: #fff;
    }}
    
    /* Responsive */
    @media (max-width: 768px) {{
        .bento-grid {{
            grid-template-columns: 1fr;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# COMPONENT FUNCTIONS
# =============================================================================

def render_page_header_bento():
    """Render Bento Earth styled page header."""
    storage = get_storage()
    today = datetime.now().date()
    
    # Get habits data
    habits = storage.get_habits()
    completed_today = sum(1 for h in habits if storage.is_habit_completed_on_date(h.id, today))
    total_habits = len(habits)
    completion_rate = (completed_today / total_habits * 100) if total_habits > 0 else 0
    
    # Get user stats
    level = st.session_state.get('user_level', 1)
    streak = st.session_state.get('user_streak', 0)
    
    # Format date
    date_str = today.strftime('%A, %B %d')
    
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <div style="font-family: 'Poppins', sans-serif; font-size: 11px; font-weight: 600; letter-spacing: 3px; color: {EARTH["mocha"]}; text-transform: uppercase; margin-bottom: 8px;">
            Daily Practice
        </div>
        <h1 style="font-size: 46px; margin: 0 0 6px; font-weight: normal; letter-spacing: -2px; line-height: 1; font-family: 'Georgia', serif;">
            Your Habits
        </h1>
        <p style="margin: 0; color: {EARTH["muted"]}; font-size: 15px; font-style: italic;">
            {date_str} • Level {level} Virtuoso • {streak} day streak
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh", key="refresh_habits", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("➕ Add New Habit", key="add_habit", use_container_width=True):
            st.session_state.show_add_habit = True


def render_progress_ring_bento(completion_rate: float, completed: int, total: int):
    """Render Bento Earth styled progress ring."""
    st.markdown(f"""
    <div style="
        background: {EARTH["mocha"]};
        border-radius: 20px;
        padding: 24px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #fff;
    ">
        <svg width="90" height="90" viewBox="0 0 90 90">
            <circle cx="45" cy="45" r="35" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="8"/>
            <circle cx="45" cy="45" r="35" fill="none" stroke="#fff" strokeWidth="8"
                stroke-linecap="round"
                stroke-dasharray="220"
                stroke-dashoffset="{220 - (220 * completion_rate / 100)}"
                transform="rotate(-90 45 45)"
                style="transition: stroke-dashoffset 1s cubic-bezier(0.34,1.56,0.64,1)"
            />
            <text x="45" y="50" text-anchor="middle" fill="#fff" font-size="20" font-weight="bold" font-family="Georgia">{completion_rate:.0f}%</text>
        </svg>
        <div style="font-family: 'Poppins', sans-serif; font-size: 12px; margin-top: 8px; opacity: 0.8; letter-spacing: 1px; text-transform: uppercase;">
            Today
        </div>
        <div style="font-size: 13px; opacity: 0.7; margin-top: 2px;">
            {completed} of {total} done
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stat_card_bento(label: str, value: str, icon: str, col_span: str = "3", bg: str = None, accent: str = None):
    """Render Bento Earth styled stat card."""
    if bg is None:
        bg = EARTH["card"]
    if accent is None:
        accent = EARTH["mocha"]
    
    text_color = "#fff" if bg == EARTH["clay"] else accent
    
    st.markdown(f"""
    <div class="stat-card" style="
        grid-column: span {col_span};
        background: {bg};
    ">
        <div style="font-size: 22px; margin-bottom: 8px;">{icon}</div>
        <div style="font-size: 28px; font-weight: bold; color: {text_color}; line-height: 1;">{value}</div>
        <div style="font-family: 'Poppins', sans-serif; font-size: 11px; color: {EARTH['muted']}; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px;">
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_habits_list_bento():
    """Render Bento Earth styled habits list."""
    storage = get_storage()
    today = datetime.now().date()
    habits = storage.get_habits()
    
    if not habits:
        st.markdown(f"""
        <div style="
            background: {EARTH["card"]};
            border: 1.5px solid {EARTH["border"]};
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            color: {EARTH["muted"]};
        ">
            <div style="font-size: 48px; margin-bottom: 16px;">🌱</div>
            <h3 style="color: {EARTH["ink"]}; margin-bottom: 8px;">No habits yet</h3>
            <p>Click 'Add New Habit' to create your first habit and start building better routines!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Sort habits by score (highest first)
    sorted_habits = sorted(habits, key=lambda h: storage.get_habit_score(h.id), reverse=True)
    
    st.markdown(f"""
    <div style="
        background: {EARTH["card"]};
        border: 1.5px solid {EARTH["border"]};
        border-radius: 20px;
        overflow: hidden;
    ">
        <div style="padding: 20px 24px 12px; border-bottom: 1px solid {EARTH["border"]}; display: flex; justify-content: space-between;">
            <span style="font-family: 'Poppins', sans-serif; font-size: 12px; font-weight: 700; color: {EARTH["muted"]}; text-transform: uppercase; letter-spacing: 2px;">
                Habits
            </span>
            <span style="font-family: 'Poppins', sans-serif; font-size: 12px; color: {EARTH["border"]};">
                Sorted by score
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    for habit in sorted_habits:
        is_completed = storage.is_habit_completed_on_date(habit.id, today)
        score = storage.get_habit_score(habit.id)
        streak = storage.get_habit_streak(habit.id)
        
        # Determine score category
        if score > 80:
            category = "Excellent"
            badge_class = "excellent"
            badge_bg = "#e8f5e9"
            badge_color = EARTH["green"]
        elif score > 65:
            category = "Strong"
            badge_class = "strong"
            badge_bg = "#fff8e1"
            badge_color = EARTH["amber"]
        else:
            category = "Building"
            badge_class = "building"
            badge_bg = "#fce4ec"
            badge_color = "#c62828"
        
        # Create unique key for this habit's checkbox
        checkbox_key = f"habit_complete_{habit.id}"
        
        # Use Streamlit columns for the habit row
        cols = st.columns([0.5, 3, 1, 1])
        
        with cols[0]:
            # Custom checkbox
            if st.button(
                "✓" if is_completed else "○",
                key=checkbox_key,
                use_container_width=True,
            ):
                if is_completed:
                    storage.unmark_habit_complete(habit.id, today)
                else:
                    storage.mark_habit_complete(habit.id, today)
                    add_xp(10)
                    st.toast(f"✅ {habit.name} completed! +10 XP", icon="⭐")
                st.rerun()
        
        with cols[1]:
            st.markdown(f"""
            <div style="flex: 1;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <span style="font-size: 15px; color: {EARTH['ink'] if is_completed else EARTH['muted']}; font-style: {'normal' if is_completed else 'italic'};">
                        {habit.name}
                    </span>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="score-badge {badge_class}" style="background: {badge_bg}; color: {badge_color};">
                            {category}
                        </span>
                        <span style="font-size: 15px; font-weight: bold; color: {EARTH['mocha']};">
                            {score}%
                        </span>
                    </div>
                </div>
                <div class="habit-progress">
                    <div class="habit-progress-fill" style="width: {score}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[2]:
            st.caption(f"🔥 {streak}d")
        
        with cols[3]:
            # Edit button
            if st.button("✏️", key=f"edit_habit_{habit.id}", help="Edit habit"):
                st.session_state.editing_habit = habit.id
                st.session_state.show_edit_habit = True


def render_quote_block_bento():
    """Render motivational quote block."""
    today = datetime.now().date()
    storage = get_storage()
    habits = storage.get_habits()
    completed = sum(1 for h in habits if storage.is_habit_completed_on_date(h.id, today))
    total = len(habits)
    rate = (completed / total * 100) if total > 0 else 0
    
    quotes = [
        ("We are what we repeatedly do. Excellence is not an act, but a habit.", "Aristotle"),
        ("The secret of getting ahead is getting started.", "Mark Twain"),
        ("It's not about having time. It's about making time.", "Unknown"),
        ("Small daily improvements are the key to staggering long-term results.", "Unknown"),
    ]
    
    # Select quote based on day of week
    quote_idx = today.weekday() % len(quotes)
    quote, author = quotes[quote_idx]
    
    st.markdown(f"""
    <div class="quote-block">
        <div style="font-size: 36px; margin-bottom: 16px;">🌱</div>
        <p style="font-size: 17px; line-height: 1.6; margin: 0 0 12px; font-style: italic;">
            "{quote}"
        </p>
        <div style="font-family: 'Poppins', sans-serif; font-size: 11px; opacity: 0.7; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px;">
            — {author}
        </div>
        <div style="background: rgba(255,255,255,0.15); border-radius: 12px; padding: 12px 16px; font-family: 'Poppins', sans-serif; font-size: 13px;">
            🎉 {completed}/{total} habits done · {rate:.0f}% complete
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main page entry point."""
    # Initialize session state
    init_session_state()
    init_habits_session_state()
    
    # Render custom styles
    render_bento_earth_styles()
    
    # Render sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 20px 10px;">
            <div style="font-family: 'Poppins', sans-serif; font-size: 11px; font-weight: 600; letter-spacing: 2px; color: {EARTH['mocha']}; text-transform: uppercase; margin-bottom: 12px;">
                Veryfyn
            </div>
            <div style="font-size: 24px; font-weight: bold; color: {EARTH['ink']}; margin-bottom: 8px;">
                ⚔️ Virtuoso
            </div>
            <div style="font-size: 13px; color: {EARTH['muted']};">
                Level {st.session_state.get('user_level', 1)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Theme info
        st.caption("🎨 Bento Earth Theme")
    
    # Render page header
    render_page_header_bento()
    
    # Get habits data
    storage = get_storage()
    habits = storage.get_habits()
    today = datetime.now().date()
    completed = sum(1 for h in habits if storage.is_habit_completed_on_date(h.id, today))
    total = len(habits)
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    # Get user stats
    level = st.session_state.get('user_level', 1)
    streak = st.session_state.get('user_streak', 0)
    xp = st.session_state.get('user_xp', 0)
    
    # Calculate best streak
    best_streak = max((storage.get_habit_streak(h.id) for h in habits), default=0)
    
    # Render Bento Grid
    st.markdown('<div class="bento-grid">', unsafe_allow_html=True)
    
    # Row 1: Title block (8 cols) + Progress ring (4 cols)
    col1, col2 = st.columns([8, 4])
    
    with col1:
        # Empty container - title is rendered above the grid
        pass
    
    with col2:
        render_progress_ring_bento(completion_rate, completed, total)
    
    # Row 2: Stat cards (4 cards, 3 cols each)
    stat_cols = st.columns(4)
    
    with stat_cols[0]:
        # Calculate current max streak
        current_streak = max((storage.get_habit_streak(h.id) for h in habits), default=0)
        render_stat_card_bento("Streak", f"{current_streak}d", "🔥", "3", EARTH["card"], EARTH["amber"])
    
    with stat_cols[1]:
        render_stat_card_bento("Best Record", f"{best_streak}d", "🏆", "3", EARTH["card"], EARTH["green"])
    
    with stat_cols[2]:
        render_stat_card_bento("Total Habits", str(total), "📋", "3", EARTH["card"], EARTH["mocha"])
    
    with stat_cols[3]:
        render_stat_card_bento("Level", str(level), "⚡", "3", EARTH["clay"], "#fff")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 3: Habits list (8 cols) + Quote block (4 cols)
    col3, col4 = st.columns([8, 4])
    
    with col3:
        render_habits_list_bento()
    
    with col4:
        render_quote_block_bento()
    
    # Render edit modal if editing
    if st.session_state.get('show_edit_habit', False):
        render_edit_habit_modal()
    
    # Handle add habit
    if st.session_state.get('show_add_habit', False):
        from tracking_app.pages.habits import render_add_habit_form
        with st.form("add_habit_form"):
            st.subheader("Add New Habit")
            name = st.text_input("Habit Name")
            category = st.selectbox("Category", ["Health", "Growth", "Wellness", "Finance", "Other"])
            
            if st.form_submit_button("Create Habit"):
                if name:
                    storage.add_habit(name=name, category=category.lower())
                    st.success(f"✅ Created habit: {name}")
                    st.session_state.show_add_habit = False
                    st.rerun()
        
        if st.button("Cancel"):
            st.session_state.show_add_habit = False
            st.rerun()


if __name__ == "__main__":
    main()
