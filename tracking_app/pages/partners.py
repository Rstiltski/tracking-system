"""
Couples/Partners Tracking Page

UI for tracking habits together.

Based on Task 11.2.9 from PHASE_11_INTEGRATION_ROADMAP.md
"""

import streamlit as st


def render_partners_page(engine, user_id: str) -> None:
    """
    Render the couples tracking page.
    
    Args:
        engine: DyadicEngine instance
        user_id: User ID
    """
    st.markdown("💑 Partner Tracking")
    st.markdown("*Track habits together. Build stronger relationships.*")
    
    # Get partners
    partners = engine.get_user_partners(user_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_partner_adder(engine, user_id)
    
    with col2:
        if partners:
            selected_partner = st.selectbox(
                "Select Partner",
                [p.name for p in partners]
            )
            
            # Get partner
            partner = next(p for p in partners if p.name == selected_partner)
            
            # Stats
            stats = engine.get_partner_stats(partner.id)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Shared Activities", stats["total_activities"])
            with col_b:
                st.metric("🔥 Streak", f"{stats['avg_streak']:.0f} days")
    
    st.markdown("---")
    
    # Shared activities
    if partners:
        render_activity_manager(engine, partners)
        
        st.markdown("---")
        
        # Activity tracking
        render_activity_tracker(engine, partners)


def render_partner_adder(engine, user_id: str) -> None:
    """Render partner adding form."""
    st.markdown("### 👤 Add Partner")
    
    from brain.models.dyadic import RelationshipType
    
    name = st.text_input("Partner Name")
    
    rel_type = st.selectbox(
        "Relationship Type",
        [r.name for r in RelationshipType]
    )
    
    if st.button("Add Partner"):
        from brain.models.dyadic import RelationshipType
        
        engine.add_partner(
            user_id=user_id,
            name=name,
            relationship_type=RelationshipType[rel_type]
        )
        
        st.success(f"Partner {name} added! 💑")


def render_activity_manager(engine, partners) -> None:
    """Render shared activity manager."""
    st.markdown("### 🎯 Shared Activities")
    
    # Select partners for activity
    selected_partners = st.multiselect(
        "Select Partners",
        [p.name for p in partners]
    )
    
    from brain.models.dyadic import ActivityCategory
    
    col1, col2 = st.columns(2)
    
    with col1:
        activity_name = st.text_input("Activity Name")
    
    with col2:
        category = st.selectbox(
            "Category",
            [c.name for c in ActivityCategory]
        )
    
    frequency = st.selectbox(
        "Frequency",
        ["daily", "weekly", "bi-weekly", "monthly"]
    )
    
    if st.button("Create Activity") and selected_partners:
        # Get partner IDs
        partner_objs = [p for p in partners if p.name in selected_partners]
        partner_ids = [p.id for p in partner_objs]
        
        from brain.models.dyadic import ActivityCategory
        
        engine.create_shared_activity(
            partner_ids=partner_ids,
            activity_name=activity_name,
            category=ActivityCategory[category],
            frequency=frequency
        )
        
        st.success(f"Activity '{activity_name}' created! 🎯")


def render_activity_tracker(engine, partners) -> None:
    """Render activity tracking."""
    st.markdown("### ✅ Track Activity")
    
    if not partners:
        return
    
    # Select partner
    selected = st.selectbox("Partner", [p.name for p in partners])
    partner = next(p for p in partners if p.name == selected)
    
    # Get activities
    activities = engine.get_shared_activities(partner.id)
    
    if not activities:
        st.info("No shared activities yet. Create one above!")
        return
    
    for activity in activities:
        with st.expander(f"🎯 {activity.activity_name} ({activity.category.value})"):
            st.write(f"**Frequency:** {activity.frequency}")
            st.write(f"**Completions:** {activity.total_completions}")
            st.write(f"**🔥 Streak:** {activity.streak} days")
            
            # Log completion
            note = st.text_input("Note (optional)", key=f"note_{activity.id}")
            
            if st.button("Mark Complete", key=f"complete_{activity.id}"):
                engine.log_completion(
                    activity_id=activity.id,
                    partner_id=partner.id,
                    note=note
                )
                
                st.success("Completed! 🎉")
                st.balloons()


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import streamlit as st
    from brain.models.dyadic import create_engine, RelationshipType, ActivityCategory
    
    st.set_page_config(page_title="Couples Test")
    
    st.title("💑 Couples Tracking Test")
    
    engine = create_engine()
    
    # Add partner
    partner = engine.add_partner(
        user_id="user1",
        name="Alex",
        relationship_type=RelationshipType.PARTNER
    )
    print(f"Added partner: {partner.name}")
    
    # Create activity
    activity = engine.create_shared_activity(
        partner_ids=[partner.id],
        activity_name="Morning walks",
        category=ActivityCategory.HEALTH,
        frequency="daily"
    )
    print(f"Created activity: {activity.activity_name}")
    
    # Log completion
    engine.log_completion(
        activity_id=activity.id,
        partner_id=partner.id,
        note="Great walk!"
    )
    
    # Stats
    stats = engine.get_partner_stats(partner.id)
    print(f"Stats: {stats}")
    
    st.write("Test passed!")
