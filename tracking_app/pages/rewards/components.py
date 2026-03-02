"""
UI components for the Rewards page.

Contains all render functions for the variable rewards interface.
"""

import time

import streamlit as st

from brain.behavioral.rewards import Rarity, RewardType

from .constants import (
    ROLL_ANIMATION_DELAY,
    TAB_INVENTORY,
    TAB_CATALOG,
    TAB_STATISTICS,
    DEFAULT_USER_ID,
)
from .helpers import (
    get_rarity_emoji,
    get_rarity_color,
    get_type_emoji,
    calculate_total_xp_from_history,
)
from .session_state import (
    get_reward_engine,
    get_storage,
    get_last_roll_result,
    set_last_roll_result,
    save_reward_history,
    update_user_xp,
    refresh_user_stats,
)


def render_header() -> None:
    """Render page header."""
    st.title("🎁 Variable Rewards")
    st.markdown("""
    **Earn random rewards through consistent habit tracking!**
    
    Based on the science of intermittent reinforcement, variable rewards keep 
    motivation high by providing unpredictable bonuses for your achievements.
    """)


def render_roll_section() -> None:
    """Render the reward roll section."""
    st.subheader("🎰 Roll for Rewards")
    
    engine = get_reward_engine()
    
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
            _handle_roll(engine)
    
    with col2:
        # Display last roll result
        result = get_last_roll_result()
        
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


def _handle_roll(engine) -> None:
    """
    Handle the roll button click.
    
    Args:
        engine: The reward engine instance
    """
    with st.spinner("Rolling..."):
        # Simulate roll animation delay
        time.sleep(ROLL_ANIMATION_DELAY)
        
        # Roll for reward
        result = engine.roll_for_user(
            user_id=DEFAULT_USER_ID,
            context={"source": "manual_roll"}
        )
        
        set_last_roll_result(result)
        save_reward_history(engine)
        
        # Add XP if rewarded
        if result.is_rewarded and result.reward:
            storage = get_storage()
            storage.add_xp(result.reward.value)
            update_user_xp(storage.get_xp())
        
        st.rerun()


def render_inventory() -> None:
    """Render reward inventory section."""
    st.subheader("📦 Your Inventory")
    
    engine = get_reward_engine()
    history = engine.get_user_history(DEFAULT_USER_ID)
    
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


def render_reward_catalog() -> None:
    """Render all available rewards."""
    st.subheader("📚 Reward Catalog")
    
    engine = get_reward_engine()
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


def render_stats() -> None:
    """Render reward statistics."""
    st.subheader("📊 Statistics")
    
    engine = get_reward_engine()
    stats = engine.get_user_stats(DEFAULT_USER_ID)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rolls", stats.get('total_rolls', 0))
    
    with col2:
        st.metric("Rewards Won", stats.get('total_rewards', 0))
    
    with col3:
        rate = stats.get('reward_rate', 0)
        st.metric("Win Rate", f"{rate:.1%}")
    
    with col4:
        history = engine.get_user_history(DEFAULT_USER_ID)
        total_xp = calculate_total_xp_from_history(history)
        st.metric("XP from Rewards", total_xp)


def render_science() -> None:
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