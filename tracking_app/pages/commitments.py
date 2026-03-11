"""
Commitment Contracts Page

UI for creating and managing commitment contracts.

Based on Task 11.2.3 from PHASE_11_INTEGRATION_ROADMAP.md
"""

import streamlit as st
from datetime import datetime, timedelta


def render_commitments_page(engine, user_id: str) -> None:
    """
    Render the commitments page.
    
    Args:
        engine: CommitmentEngine instance
        user_id: User ID
    """
    st.markdown("🤝 Commitment Contracts")
    st.markdown("*Make promises you keep. Stakes make commitments real.*")
    
    # Summary
    summary = engine.get_contract_summary(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total", summary["total"])
    with col2:
        st.metric("Active", summary["active"])
    with col3:
        st.metric("Completed", summary["completed"])
    with col4:
        st.metric("Failed", summary["failed"])
    
    st.markdown("---")
    
    # Create new contract
    render_contract_creator(engine, user_id)
    
    st.markdown("---")
    
    # Show active contracts
    render_active_contracts(engine, user_id)
    
    st.markdown("---")
    
    # Show completed contracts
    render_contract_history(engine, user_id)


def render_contract_creator(engine, user_id: str) -> None:
    """Render contract creation form."""
    st.markdown("### ✨ Create Commitment Contract")
    
    from brain.models.commitment import StakeType
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Commitment Title", placeholder="e.g., Exercise daily for 30 days")
        target_days = st.number_input("Duration (days)", min_value=1, value=30)
    
    with col2:
        stake_type = st.selectbox(
            "Stake Type",
            [s.name for s in StakeType]
        )
        stake_desc = st.text_input(
            "Stake Description",
            placeholder="e.g., $100 to charity I hate"
        )
    
    description = st.text_area(
        "Description",
        placeholder="Why is this commitment important to you?"
    )
    
    accountability = st.text_input(
        "Accountability Partner (optional)",
        placeholder="Friend's name or email"
    )
    
    if st.button("Create Contract"):
        from brain.models.commitment import StakeType
        
        target_date = datetime.now() + timedelta(days=target_days)
        
        engine.create_contract(
            user_id=user_id,
            title=title,
            description=description,
            target_date=target_date,
            stake_type=StakeType[stake_type],
            stake_description=stake_desc,
            accountability_partner=accountability if accountability else None
        )
        
        st.success("Contract created! 🤞 Good luck!")
        st.balloons()


def render_active_contracts(engine, user_id: str) -> None:
    """Render active contracts with check-in."""
    from brain.models.commitment import ContractStatus
    
    contracts = engine.get_user_contracts(user_id, ContractStatus.ACTIVE)
    
    st.markdown(f"### 🔥 Active Contracts ({len(contracts)})")
    
    if not contracts:
        st.info("No active contracts. Create one above!")
        return
    
    for contract in contracts:
        with st.expander(f"📜 {contract.title}"):
            st.write(f"**{contract.description}**")
            
            # Days remaining
            days_left = (contract.target_date - datetime.now()).days
            if days_left > 0:
                st.info(f"⏳ {days_left} days remaining")
            else:
                st.warning("Past target date!")
            
            # Stake
            st.write(f"**Stake:** {contract.stake_description}")
            
            # Progress
            st.progress(
                contract.completed_check_ins / max(contract.total_check_ins, 1) 
                if contract.total_check_ins > 0 
                else 0
            )
            
            st.caption(f"Check-ins: {contract.completed_check_ins}")
            
            # Check-in form
            st.markdown("#### 📝 Check In")
            
            col1, col2 = st.columns(2)
            
            with col1:
                note = st.text_input("Progress Note", key=f"note_{contract.id}")
            
            with col2:
                mood = st.slider("Mood (1-10)", 1, 10, 7, key=f"mood_{contract.id}")
            
            on_track = st.checkbox("On Track", key=f"track_{contract.id}")
            
            if st.button("Check In", key=f"checkin_{contract.id}"):
                engine.check_in(
                    contract_id=contract.id,
                    progress_note=note,
                    on_track=on_track,
                    mood=mood
                )
                st.success("Check-in recorded! ✅")


def render_contract_history(engine, user_id: str) -> None:
    """Render contract history."""
    from brain.models.commitment import ContractStatus
    
    completed = engine.get_user_contracts(user_id, ContractStatus.COMPLETED)
    failed = engine.get_user_contracts(user_id, ContractStatus.FAILED)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Completed")
        if not completed:
            st.info("No completed contracts yet.")
        else:
            for c in completed:
                st.write(f"✅ {c.title}")
    
    with col2:
        st.markdown("### ❌ Failed")
        if not failed:
            st.info("No failed contracts. Keep it up!")
        else:
            for c in failed:
                st.write(f"❌ {c.title}")


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import streamlit as st
    from brain.models.commitment import create_engine, StakeType, ContractStatus
    from datetime import timedelta
    
    st.set_page_config(page_title="Commitment Contracts Test")
    
    st.title("🤝 Commitment Contracts Test")
    
    engine = create_engine()
    
    # Create test contract
    contract = engine.create_contract(
        user_id="test",
        title="Exercise daily for 30 days",
        description="Build consistent exercise habit",
        target_date=datetime.now() + timedelta(days=30),
        stake_type=StakeType.FINANCIAL,
        stake_description="$100 to least favorite charity",
        accountability_partner="John"
    )
    
    print(f"Created contract: {contract.title}")
    
    # Check in
    engine.check_in(
        contract_id=contract.id,
        progress_note="Did 20 pushups",
        on_track=True,
        mood=8
    )
    
    print(f"Check-ins: {len(engine.check_ins[contract.id])}")
    
    # Summary
    summary = engine.get_contract_summary("test")
    print(f"Summary: {summary}")
    
    st.write("Test passed!")
