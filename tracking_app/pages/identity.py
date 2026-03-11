"""
Identity Dashboard Page

Track "who am I becoming?" not just "what did I do?"

Based on Task 11.2.1 from PHASE_11_INTEGRATION_ROADMAP.md
"""

import streamlit as st
from typing import Optional


def render_identity_dashboard(tracker, user_id: str) -> None:
    """
    Render the full identity dashboard.
    
    Args:
        tracker: IdentityTracker instance
        user_id: User ID
    """
    st.markdown("# 🪞 Identity Tracker")
    st.markdown("*Who am I becoming? Not just what did I do.*")
    
    # Get summary
    summary = tracker.get_dashboard_summary()
    
    # Overall alignment score
    st.markdown("### 🌟 Overall Identity Alignment")
    
    avg_alignment = summary["avg_alignment"]
    
    # Color based on alignment
    if avg_alignment >= 70:
        st.success(f"**{avg_alignment:.1f}%** - Strong identity alignment!")
    elif avg_alignment >= 40:
        st.info(f"**{avg_alignment:.1f}%** - Building your identity")
    else:
        st.warning(f"**{avg_alignment:.1f}%** - Just getting started")
    
    st.progress(avg_alignment / 100)
    
    st.markdown("---")
    
    # Dimension breakdown
    st.markdown("### 📊 Identity Dimensions")
    
    for dim in summary["dimensions"]:
        with st.expander(f"{dim['name']} ({dim['alignment']:.0f}% aligned)"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Current Self**")
                st.progress(dim["current"] / 100)
                st.caption(f"{dim['current']:.0f}/100")
            
            with col2:
                st.write("**Ideal Self**")
                st.progress(dim["ideal"] / 100)
                st.caption(f"{dim['ideal']:.0f}/100")
    
    st.markdown("---")
    
    # Add new identity section
    render_identity_creator(tracker)
    
    st.markdown("---")
    
    # Evidence section
    render_evidence_adder(tracker)
    
    st.markdown("---")
    
    # Conflicts section
    render_conflicts(tracker)


def render_identity_creator(tracker) -> None:
    """Render the identity statement creator."""
    st.markdown("### ✨ Create Identity Statement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dimension = st.selectbox(
            "Life Dimension",
            [
                "Health & Fitness",
                "Career & Work",
                "Relationships",
                "Creativity",
                "Spirituality",
                "Finances",
                "Personal Growth",
                "Community",
                "Fun & Adventure",
                "Physical Environment",
            ]
        )
    
    with col2:
        identity_type = st.selectbox(
            "Identity Type",
            ["Current (who I am now)", "Ideal (who I want to become)", "Feared (who I fear becoming)"]
        )
    
    statement = st.text_input(
        "Identity Statement",
        placeholder="e.g., I am someone who exercises daily"
    )
    
    if st.button("Create Identity Statement"):
        from brain.models.identity import IdentityType
        
        type_map = {
            "Current (who I am now)": IdentityType.CURRENT,
            "Ideal (who I want to become)": IdentityType.IDEAL,
            "Feared (who I fear becoming)": IdentityType.FEARED
        }
        
        tracker.create_identity_statement(
            dimension=dimension,
            statement=statement,
            identity_type=type_map[identity_type]
        )
        
        st.success("Identity statement created! 🎉")


def render_evidence_adder(tracker) -> None:
    """Render the evidence adder."""
    st.markdown("### 📝 Add Identity Evidence")
    
    if not tracker.identity_statements:
        st.info("Create identity statements first to add evidence!")
        return
    
    # Select identity
    options = [
        f"{s.statement} ({s.dimension})"
        for s in tracker.identity_statements.values()
    ]
    
    selected = st.selectbox("Which identity does this support?", options)
    
    if selected:
        # Find matching statement
        stmt = None
        for s in tracker.identity_statements.values():
            if f"{s.statement} ({s.dimension})" == selected:
                stmt = s
                break
        
        if stmt:
            evidence_desc = st.text_input(
                "What did you do?",
                placeholder="e.g., Went for a 30-minute run this morning"
            )
            
            impact = st.slider("Impact on identity (1-5)", 1, 5, 3)
            
            if st.button("Add Evidence"):
                tracker.add_evidence(
                    identity_statement_id=stmt.id,
                    description=evidence_desc,
                    impact_score=float(impact)
                )
                
                st.success("Evidence added! Your identity is strengthening. 💪")


def render_conflicts(tracker) -> None:
    """Render detected conflicts."""
    st.markdown("### ⚠️ Identity Conflicts")
    
    if not tracker.conflicts:
        st.success("No conflicts detected! Keep building your identity. ✨")
        return
    
    for conflict in tracker.conflicts[-5:]:  # Last 5
        with st.expander(f"{conflict.dimension} - {conflict.severity}/5 severity"):
            st.write(f"**Ideal:** {conflict.identity_statement}")
            st.write(f"**Behavior:** {conflict.conflicting_behavior}")
            
            st.caption(f"Detected: {conflict.detected_at.strftime('%Y-%m-%d %H:%M')}")


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import streamlit as st
    from brain.models.identity import create_tracker, IdentityType
    
    st.set_page_config(page_title="Identity Tracker Test")
    
    st.title("🪞 Identity Tracker Test")
    
    tracker = create_tracker()
    
    # Create some test identities
    tracker.create_identity_statement(
        dimension="Health & Fitness",
        statement="I am a runner",
        identity_type=IdentityType.IDEAL
    )
    
    # Add evidence
    identities = list(tracker.identity_statements.values())
    if identities:
        tracker.add_evidence(
            identity_statement_id=identities[0].id,
            description="Ran 5k this morning"
        )
    
    # Show dashboard
    render_identity_dashboard(tracker, "test_user")
