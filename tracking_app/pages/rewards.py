"""
Rewards Page - Variable Rewards UI

Streamlit page for displaying and managing variable rewards using B.F. Skinner's 
Variable Ratio reinforcement schedule.

Features:
- View reward inventory
- Roll for rewards on habit completion
- View reward statistics
- Display rarity badges

Usage:
    streamlit run tracking_app/pages/rewards.py
"""
import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import sys
import os
import random

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage

# Import brain behavioral modules
from brain.behavioral.rewards import (
    RewardEngine, Reward, RewardType, Rarity,
    RewardResult, RewardHistory, DEFAULT_REWARDS, create_default_engine
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Rewards - Veryfyn",
    page_icon="🎁",
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
    
    if 'reward_engine' not in st.session_state:
        st.session_state.reward_engine = load_reward_engine()
    
    if 'last_roll_result' not in st.session_state:
        st.session_state.last_roll_result = None
    
    if 'rolling' not in st.session_state:
        st.session_state.rolling = False


def load_reward_engine() -> RewardEngine:
    """Load or create the reward engine."""
    engine = create_default_engine()
    
    # Load custom rewards from storage
    storage = st.session_state.storage
    custom_rewards = storage.get_user_data("custom_rewards", [])
    
    for reward_dict in custom_rewards:
        try:
            reward = Reward.from_dict(reward_dict)
            engine.add_reward(reward)
        except Exception:
            pass
    
    return engine


def save_reward_history(engine: RewardEngine) -> None:
    """Save reward history to storage."""
    storage = st.session_state.storage
    # Save histories
    for user_id, history in engine.histories.items():
        storage.set_user_data(f"reward_history_{user_id}", history.to_dict())


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_rarity_emoji(rarity: Rarity) -> str:
    """Get emoji for rarity level."""
    emojis = {
        Rarity.COMMON: "⚪",
        Rarity.UNCOMMON: "🟢",
        Rarity.RARE: "🔵",
        Rarity.LEGENDARY: "🟣"
    }
    return emojis.get(rarity, "⚪")


def get_rarity_color(rarity: Rarity) -> str:
    """Get color for rarity level."""
    colors = {
        Rarity.COMMON: "#9CA3AF",
        Rarity.UNCOMMON: "#10B981",
        Rarity.RARE: "#3B82F6",
        Rarity.LEGENDARY: "#8B5CF6"
    }
    return colors.get(rarity, "#9CA3AF")


def get_type_emoji(reward_type: RewardType) -> str:
    """Get emoji for reward type."""
    emojis = {
        RewardType.TRIBE: "👥",
        RewardType.HUNT: "💎",
        RewardType.SELF: "🌟"
    }
    return emojis.get(reward_type, "🎁")


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
        st.page_link("pages/rewards.py", label="🎁 Rewards", icon="🎁")


def render_header():
    """Render page header."""
    st.title("🎁 Variable Rewards")
    st.markdown("""
    **Earn random rewards through consistent habit tracking!**
    
    Based on the science of intermittent reinforcement, variable rewards keep 
    motivation high by providing unpredictable bonuses for your achievements.
    """)


def render_roll_section():
    """Render the reward roll section."""
    st.subheader("🎰 Roll for Rewards")
    
    engine = st.session_state.reward_engine
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **How it works:**
        - Complete habits to earn chances
        - Each roll has a 30% base chance
        - Rarer rewards are worth more XP!
        """)
        
        # Roll button
        if st.button("🎲 Roll for Reward", type="primary", use_container_width=True):
            with st.spinner("Rolling..."):
                # Simulate roll animation delay
                import time
                time.sleep(0.5)
                
                # Roll for reward
                result = engine.roll_for_user(
                    user_id="default",
                    context={"source": "manual_roll"}
                )
                
                st.session_state.last_roll_result = result
                save_reward_history(engine)
                
                # Add XP if rewarded
                if result.is_rewarded and result.reward:
                    storage = st.session_state.storage
                    storage.add_xp(result.reward.value)
                    st.session_state.user_xp = storage.get_xp()
                
                st.rerun()
    
    with col2:
        # Display last roll result
        result = st.session_state.last_roll_result
        
        if result:
            if result.is_rewarded and result.reward:
                st.success(f"🎉 **{result.reward.icon} {result.reward.name}**")
                st.markdown(f"*{result.reward.description}*")
                st.metric("XP Earned", f"+{result.reward.value}")
            elif result.near_miss:
                st.warning("😮 So close! Try again!")
            else:
                st.info("No reward this time. Keep going!")
        else:
            st.info("Roll to see what you get!")


def render_inventory():
    """Render reward inventory section."""
    st.subheader("📦 Your Inventory")
    
    engine = st.session_state.reward_engine
    history = engine.get_user_history("default")
    
    if not history.rewards_received:
        st.info("No rewards collected yet. Complete habits and roll for rewards!")
        return
    
    # Group by rarity
    by_rarity = {r: [] for r in Rarity}
    for record in history.rewards_received:
        rarity = Rarity(record['rarity'])
        by_rarity[rarity].append(record)
    
    # Display by rarity (rarest first)
    for rarity in [Rarity.LEGENDARY, Rarity.RARE, Rarity.UNCOMMON, Rarity.COMMON]:
        rewards = by_rarity[rarity]
        if rewards:
            with st.container():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    st.markdown(f"### {get_rarity_emoji(rarity)} {rarity.value.title()}")
                
                with col2:
                    st.caption(f"{len(rewards)} collected")
                
                # Show rewards
                for record in rewards[-5:]:  # Show last 5 of each rarity
                    st.markdown(f"- {record['reward_name']}")
                
                st.divider()


def render_reward_catalog():
    """Render all available rewards."""
    st.subheader("📚 Reward Catalog")
    
    engine = st.session_state.reward_engine
    rewards = engine.get_all_rewards()
    
    # Filter by rarity
    rarity_filter = st.selectbox(
        "Filter by Rarity",
        ["All"] + [r.value.title() for r in Rarity]
    )
    
    if rarity_filter != "All":
        rarity = Rarity(rarity_filter.lower())
        filtered = [r for r in rewards if r.rarity == rarity]
    else:
        filtered = rewards
    
    # Display rewards in grid
    cols = st.columns(3)
    
    for i, reward in enumerate(filtered):
        col = cols[i % 3]
        
        with col:
            rarity_emoji = get_rarity_emoji(reward.rarity)
            type_emoji = get_type_emoji(reward_type=reward.reward_type)
            
            st.markdown(f"""
            ### {reward.icon} {reward.name}
            
            {rarity_emoji} **{reward.rarity.value.title()}** | {type_emoji} {reward.reward_type.value.title()}
            
            *{reward.description}*
            
            💰 **Value:** {reward.value} XP
            """)
            st.divider()


def render_stats():
    """Render reward statistics."""
    st.subheader("📊 Statistics")
    
    engine = st.session_state.reward_engine
    stats = engine.get_user_stats("default")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rolls", stats.get('total_rolls', 0))
    
    with col2:
        st.metric("Rewards Won", stats.get('total_rewards', 0))
    
    with col3:
        rate = stats.get('reward_rate', 0)
        st.metric("Win Rate", f"{rate:.1%}")
    
    with col4:
        st.metric("XP from Rewards", sum(
            r['value'] if 'value' in r else 0 
            for r in engine.get_user_history("default").rewards_received
        ))


def render_science():
    """Render explanation of the science."""
    with st.expander("🔬 The Science of Variable Rewards"):
        st.markdown("""
        ### Why Variable Rewards Work
        
        Based on **B.F. Skinner's** research on **Variable Ratio reinforcement**, 
        this system uses intermittent reinforcement to maximize motivation.
        
        #### Key Principles:
        
        1. **Unpredictability** 🔮
           - Rewards are given after an unpredictable number of responses
           - This keeps dopamine response high
        
        2. **Dopamine Prediction Error** 🧠
           - Unexpected rewards trigger larger dopamine releases
           - This creates stronger habit reinforcement
        
        3. **Extinction Resistance** 💪
           - Behaviors rewarded variably persist longer when rewards stop
           - This builds lasting habits
        
        4. **Near-Miss Effect** 😮
           - "Almost winning" triggers similar dopamine response to winning
           - Makes the experience engaging even without rewards
        
        #### Reward Types (The Hook Model):
        
        | Type | Description | Examples |
        |------|-------------|----------|
        | 👥 **Tribe** | Social validation | Recognition, leaderboards |
        | 💎 **Hunt** | Material resources | XP, badges, points |
        | 🌟 **Self** | Mastery & competence | Leveling, streaks |
        
        #### Rarity Weights:
        
        | Rarity | Weight | Chance |
        |--------|--------|--------|
        | ⚪ Common | 60% | Most frequent |
        | 🟢 Uncommon | 25% | Medium |
        | 🔵 Rare | 12% | Low |
        | 🟣 Legendary | 3% | Very rare |
        
        ---
        
        *References:*
        - Skinner, B.F. (1953). "Science and Human Behavior"
        - Eyal, N. (2014). "Hooked: How to Build Habit-Forming Products"
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
    
    # Roll section
    render_roll_section()
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Inventory", "Catalog", "Statistics"])
    
    with tab1:
        render_inventory()
    
    with tab2:
        render_reward_catalog()
    
    with tab3:
        render_stats()
    
    st.divider()
    render_science()


if __name__ == "__main__":
    main()