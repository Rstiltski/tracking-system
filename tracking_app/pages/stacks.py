"""
Habit Stacks Page - Habit Stacking UI

Streamlit page for creating and managing habit stacks using BJ Fogg's Tiny Habits methodology.

Features:
- Create habit stacks with anchors
- Add habits to stacks
- Track stack completion
- View stack analytics

Usage:
    streamlit run tracking_app/pages/stacks.py
"""
import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage
from tracking_app.models import Habit

# Import brain behavioral modules
from brain.behavioral.habit_stacking import (
    HabitStackingEngine, HabitStack, StackItem, AnchorPreset,
    AnchorCategory, DEFAULT_ANCHOR_PRESETS
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Habit Stacks - Veryfyn",
    page_icon="📚",
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
    
    if 'user_xp' not in st.session_state:
        st.session_state.user_xp = st.session_state.storage.get_xp()
    
    if 'user_level' not in st.session_state:
        st.session_state.user_level = st.session_state.storage.get_level()
    
    if 'stack_engine' not in st.session_state:
        st.session_state.stack_engine = load_stack_engine()
    
    if 'creating_stack' not in st.session_state:
        st.session_state.creating_stack = False


def load_stack_engine() -> HabitStackingEngine:
    """Load or create the habit stacking engine."""
    engine = HabitStackingEngine()
    
    # Load stacks from storage
    storage = st.session_state.storage
    stacks_data = storage.get_user_data("habit_stacks", [])
    
    for stack_dict in stacks_data:
        try:
            stack = HabitStack.from_dict(stack_dict)
            engine.stacks[stack.id] = stack
        except Exception:
            pass
    
    return engine


def save_stack_engine(engine: HabitStackingEngine) -> None:
    """Save stacks to storage."""
    storage = st.session_state.storage
    stacks_data = [stack.to_dict() for stack in engine.stacks.values()]
    storage.set_user_data("habit_stacks", stacks_data)


# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

def render_sidebar():
    """Render sidebar with navigation."""
    with st.sidebar:
        st.title("🎯 Veryfyn")
        st.caption("Personal Tracking System")
        st.divider()
        
        # User Stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Level", st.session_state.user_level)
        with col2:
            st.metric("XP", st.session_state.user_xp)
        
        st.divider()
        
        # Navigation
        st.subheader("📊 Tracking")
        st.page_link("pages/dashboard.py", label="🏠 Dashboard", icon="🏠")
        st.page_link("pages/habits.py", label="✅ Habits", icon="✅")
        st.page_link("pages/tasks.py", label="📋 Tasks", icon="📋")
        st.page_link("pages/finances.py", label="💰 Finances", icon="💰")
        st.page_link("pages/health.py", label="❤️ Health", icon="❤️")
        st.page_link("pages/emotional_health.py", label="🌈 Emotional Health", icon="🌈")
        st.page_link("pages/time.py", label="⏱️ Time", icon="⏱️")
        st.page_link("pages/goals.py", label="🎯 Goals", icon="🎯")
        st.page_link("pages/achievements.py", label="🏆 Achievements", icon="🏆")
        
        st.divider()
        st.page_link("pages/insights.py", label="🧠 Insights", icon="🧠")
        st.page_link("pages/stacks.py", label="📚 Stacks", icon="📚")


def render_header():
    """Render page header."""
    st.title("📚 Habit Stacks")
    st.markdown("""
    **Stack habits together using BJ Fogg's Tiny Habits methodology.**
    
    The formula: **After I [ANCHOR], I will [NEW HABIT]**
    
    By linking new habits to existing behaviors, you create automatic chains.
    """)


def render_create_stack_form():
    """Render form to create a new habit stack."""
    st.subheader("➕ Create New Stack")
    
    with st.form("create_stack_form", clear_on_submit=True):
        # Stack name
        name = st.text_input(
            "Stack Name",
            placeholder="e.g., Morning Routine, Evening Wind-down",
            help="Give your stack a memorable name"
        )
        
        # Anchor selection
        st.markdown("### Choose Your Anchor")
        st.caption("An anchor is an existing behavior that triggers your new habits")
        
        # Category filter
        categories = ["All"] + [c.value.title() for c in AnchorCategory]
        selected_category = st.selectbox("Filter by Category", categories)
        
        # Filter presets
        if selected_category == "All":
            filtered_presets = DEFAULT_ANCHOR_PRESETS
        else:
            category_enum = AnchorCategory(selected_category.lower())
            filtered_presets = [p for p in DEFAULT_ANCHOR_PRESETS if p.category == category_enum]
        
        # Display anchor options
        anchor_options = ["Custom (type your own)"] + [p.name for p in filtered_presets]
        selected_anchor = st.selectbox("Select Anchor", anchor_options)
        
        if selected_anchor == "Custom (type your own)":
            custom_anchor = st.text_input(
                "Custom Anchor",
                placeholder="e.g., After I finish my morning coffee"
            )
            trigger = custom_anchor
            category = AnchorCategory.CUSTOM
        else:
            preset = next(p for p in filtered_presets if p.name == selected_anchor)
            trigger = preset.example_trigger
            category = preset.category
            st.info(f"💡 {preset.description}")
        
        submitted = st.form_submit_button("Create Stack", type="primary")
        
        if submitted and name and trigger:
            engine = st.session_state.stack_engine
            stack = engine.create_stack(
                user_id="default",
                name=name,
                trigger=trigger,
                category=category
            )
            save_stack_engine(engine)
            st.success(f"✅ Created stack: {name}")
            st.rerun()


def render_add_habit_to_stack(stack: HabitStack):
    """Render form to add a habit to a stack."""
    storage = st.session_state.storage
    habits = [h for h in storage.get_habits() if not h.archived]
    
    if not habits:
        st.info("Create some habits first in the Habits page.")
        return
    
    with st.expander("➕ Add Habit to Stack", expanded=False):
        # Habit selection
        habit_options = {f"{h.icon} {h.name}": h.id for h in habits}
        selected = st.selectbox("Select Habit", list(habit_options.keys()), key=f"add_habit_{stack.id}")
        habit_id = habit_options[selected]
        
        # Tiny version toggle
        is_tiny = st.checkbox("This is a 'Tiny' version (< 30 seconds)", value=True)
        
        if is_tiny:
            # Suggest tiny version
            habit = next(h for h in habits if h.id == habit_id)
            suggested = st.session_state.stack_engine.suggest_tiny_version(habit.name)
            tiny_description = st.text_input(
                "Tiny Version Description",
                value=suggested,
                help="Describe the tiny version of this habit"
            )
        else:
            tiny_description = None
        
        # Position
        position = st.number_input(
            "Position in Stack",
            min_value=0,
            max_value=len(stack.items),
            value=len(stack.items),
            help="Position 0 = first habit after the anchor"
        )
        
        if st.button("Add to Stack", key=f"add_btn_{stack.id}"):
            engine = st.session_state.stack_engine
            try:
                engine.add_habit_to_stack(
                    stack_id=stack.id,
                    habit_id=habit_id,
                    position=position,
                    is_tiny=is_tiny,
                    tiny_description=tiny_description
                )
                save_stack_engine(engine)
                st.success("Habit added to stack!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


def render_stack_card(stack: HabitStack):
    """Render a single stack card."""
    storage = st.session_state.storage
    engine = st.session_state.stack_engine
    
    with st.container():
        # Stack header
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"### 📚 {stack.name}")
            st.caption(f"**Anchor:** {stack.trigger_description}")
        
        with col2:
            if st.button("🗑️", key=f"delete_stack_{stack.id}", help="Delete stack"):
                del engine.stacks[stack.id]
                save_stack_engine(engine)
                st.rerun()
        
        # Stack items
        if stack.items:
            st.markdown("**Chain:**")
            
            for item in sorted(stack.items, key=lambda x: x.position_index):
                habit = storage.get_habit(item.habit_id)
                if habit:
                    tiny_indicator = "🌱 " if item.is_tiny else ""
                    st.markdown(
                        f"{item.position_index + 1}. {tiny_indicator}{habit.icon} **{habit.name}**"
                    )
                    if item.is_tiny and item.tiny_version_description:
                        st.caption(f"   ↳ Tiny version: {item.tiny_version_description}")
        else:
            st.info("No habits in this stack yet. Add habits below.")
        
        # Add habit form
        render_add_habit_to_stack(stack)
        
        # Stack analytics
        if stack.items:
            analytics = engine.get_stack_analytics(stack.id)
            
            with st.expander("📊 View Analytics"):
                st.metric("Stack Depth", analytics.get('stack_depth', 0))
                st.metric("Conversion Rate", f"{analytics.get('conversion_rate', 0):.1%}")
                
                if analytics.get('weak_links'):
                    st.warning(f"⚠️ Weak links at positions: {analytics['weak_links']}")
        
        st.divider()


def render_stacks_list():
    """Render all user stacks."""
    st.subheader("📋 Your Stacks")
    
    engine = st.session_state.stack_engine
    stacks = list(engine.stacks.values())
    
    if not stacks:
        st.info("""
        No stacks yet. Create your first stack above!
        
        **Tip:** Start with a simple stack tied to a daily anchor like 
        "After I brush my teeth" or "After I pour my coffee".
        """)
        return
    
    for stack in stacks:
        render_stack_card(stack)


def render_tips():
    """Render habit stacking tips."""
    with st.expander("💡 Tips for Effective Habit Stacking"):
        st.markdown("""
        ### The Tiny Habits Formula
        
        **After I [ANCHOR], I will [NEW HABIT]**
        
        ### Key Principles
        
        1. **Start Tiny**: Make the new habit take < 30 seconds
           - Instead of "meditate 20 minutes", try "take 3 deep breaths"
           - Instead of "exercise for 30 minutes", try "do 2 pushups"
        
        2. **Choose Reliable Anchors**: Pick behaviors you do automatically
           - Brushing teeth, pouring coffee, getting into bed
        
        3. **One at a Time**: Add habits one at a time until automatic
        
        4. **Chain Formation**: Once Habit A is automatic, add Habit B
        
        ### Example Stacks
        
        **Morning Stack:**
        - After I brew coffee...
        - → I will drink a glass of water
        - → I will take my vitamins
        - → I will do 2 pushups
        
        **Evening Stack:**
        - After I put on pajamas...
        - → I will floss one tooth
        - → I will read one page
        - → I will take 3 deep breaths
        
        ### Based on BJ Fogg's Research
        
        > "The key to habit formation isn't willpower—it's design."
        > — BJ Fogg, *Tiny Habits*
        """)


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
    
    # Tips
    render_tips()
    st.divider()
    
    # Create stack form
    render_create_stack_form()
    st.divider()
    
    # Stacks list
    render_stacks_list()


if __name__ == "__main__":
    main()