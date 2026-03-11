"""
Privacy Dashboard Page

Streamlit interface for privacy controls and consent management.
Shows what data is collected and allows granular consent management.

Based on Task 11.1.2 from PHASE_11_INTEGRATION_ROADMAP.md

Features:
- Data category dashboard (required vs optional)
- Granular consent (opt-in per category)
- Data export (full JSON/CSV)
- Selective deletion
- Scheduled deletion
- Quarterly privacy review flow
"""

import streamlit as st
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
import json

# Import privacy models
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from brain.models.privacy_preferences import (
    PrivacyPreferences,
    ConsentRecord,
    ConsentStatus,
    DataCategory,
    DataSensitivity,
    DATA_CATEGORIES,
    get_category_info,
    calculate_privacy_score,
    should_show_quarterly_review,
    create_privacy_preferences,
)


# =============================================================================
# SESSION STATE
# =============================================================================

def init_privacy_session():
    """Initialize privacy-related session state."""
    if "privacy_preferences" not in st.session_state:
        st.session_state.privacy_preferences = create_privacy_preferences(
            st.session_state.get("user_id", "default_user")
        )


def get_preferences() -> PrivacyPreferences:
    """Get privacy preferences from session state."""
    init_privacy_session()
    return st.session_state.privacy_preferences


def save_preferences(prefs: PrivacyPreferences):
    """Save privacy preferences to session state."""
    st.session_state.privacy_preferences = prefs


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Privacy Dashboard",
    page_icon="🔒",
    layout="wide"
)


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_header():
    """Render the page header."""
    st.title("🔒 Privacy Dashboard")
    st.markdown("""
    Control your data privacy settings. See what we collect, why, and manage your consent.
    
    **Your data is yours.** We believe in transparent data practices.
    """)


def render_privacy_score(prefs: PrivacyPreferences):
    """Render privacy score overview."""
    score = calculate_privacy_score(prefs)
    score_percent = int(score * 100)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Privacy Score",
            f"{score_percent}%",
            delta="Higher = More Private" if score > 0.5 else None,
            delta_color="normal"
        )
    
    with col2:
        pending = len(prefs.get_pending_categories())
        st.metric("Pending Decisions", str(pending))
    
    with col3:
        if prefs.last_review:
            days_since = (date.today() - prefs.last_review).days
            st.metric("Last Review", f"{days_since} days ago")
        else:
            st.metric("Last Review", "Never")


def render_category_card(category: DataCategory, prefs: PrivacyPreferences):
    """Render a single data category card with consent controls."""
    info = get_category_info(category)
    record = prefs.get_consent_record(category)
    is_required = info["sensitivity"] == DataSensitivity.REQUIRED
    
    with st.container():
        # Category header
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"**{info['name']}**")
            st.caption(info["description"])
            
            # Show what's required
            if is_required:
                st.caption(f"🔴 Required for: {info['required_for']}")
            else:
                st.caption(f"🟢 Optional: {info['required_for']}")
        
        with col2:
            # Consent status badge
            if record.status == ConsentStatus.GRANTED:
                st.success("✅ Granted")
            elif record.status == ConsentStatus.WITHDRAWN:
                st.warning("❌ Withdrawn")
            else:
                st.info("⏳ Pending")
        
        with col3:
            # Consent toggle
            if is_required:
                st.caption("Cannot be disabled")
                st.caption("(Required)")
            else:
                if record.status == ConsentStatus.GRANTED:
                    if st.button(
                        "Withdraw",
                        key=f"withdraw_{category.value}",
                        help="Withdraw consent for this data category"
                    ):
                        prefs.withdraw_consent(category, "User withdrew via privacy dashboard")
                        save_preferences(prefs)
                        st.rerun()
                else:
                    if st.button(
                        "Enable",
                        key=f"grant_{category.value}",
                        help="Grant consent for this data category"
                    ):
                        prefs.grant_consent(category, "User granted via privacy dashboard")
                        save_preferences(prefs)
                        st.rerun()
        
        st.divider()


def render_consent_section(prefs: PrivacyPreferences):
    """Render the consent management section."""
    st.subheader("📋 Data Categories & Consent")
    
    # Required categories first
    st.markdown("### Required Data")
    st.caption("These are necessary for core app functionality and cannot be disabled.")
    
    required_cats = prefs.get_required_categories()
    for cat in required_cats:
        render_category_card(cat, prefs)
    
    # Optional categories
    st.markdown("### Optional Data")
    st.caption("You can enable or disable these at any time.")
    
    optional_cats = prefs.get_optional_categories()
    for cat in optional_cats:
        render_category_card(cat, prefs)


def render_export_section(prefs: PrivacyPreferences):
    """Render the data export section."""
    st.subheader("📤 Export Your Data")
    st.markdown("Download a copy of all your data.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "Export Format",
            ["JSON", "CSV"],
            help="JSON for full data, CSV for spreadsheet compatibility"
        )
    
    with col2:
        include_options = st.multiselect(
            "Include Categories",
            [cat.value for cat in DataCategory],
            default=[cat.value for cat in prefs.consents if prefs.is_consent_granted(cat)],
            help="Select which data categories to include"
        )
    
    if st.button("Prepare Export", type="primary"):
        with st.spinner("Preparing your data export..."):
            # Simulated export (in production, this would generate actual files)
            export_data = {
                "user_id": prefs.user_id,
                "export_date": datetime.now().isoformat(),
                "categories": include_options,
                "format": export_format,
                "note": "Full export would include actual data here"
            }
            
            st.success("✅ Export ready!")
            st.json(export_data)
            
            # In production, provide actual download
            if export_format == "JSON":
                st.download_button(
                    "Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"veryfyn_export_{date.today()}.json",
                    mime="application/json"
                )
            else:
                st.download_button(
                    "Download CSV",
                    data="category,data\nhabits,placeholder\n",
                    file_name=f"veryfyn_export_{date.today()}.csv",
                    mime="text/csv"
                )


def render_deletion_section(prefs: PrivacyPreferences):
    """Render the data deletion section."""
    st.subheader("🗑️ Delete Your Data")
    st.warning("⚠️ These actions are permanent and cannot be undone.")
    
    # Selective deletion
    st.markdown("#### Selective Deletion")
    st.caption("Delete specific categories of data.")
    
    delete_category = st.selectbox(
        "Select category to delete",
        [cat.value for cat in DataCategory if cat != DataCategory.HABITS],  # Can't delete habits completely
        format_func=lambda x: DATA_CATEGORIES[DataCategory(x)]["name"]
    )
    
    if st.button("Delete Selected Data", type="secondary"):
        st.error("This would delete all data for the selected category. Confirmation required in production.")
    
    # Scheduled deletion
    st.markdown("#### Scheduled Deletion")
    st.caption("Automatically delete old data after a certain period.")
    
    retention_options = [
        (0, "Keep forever"),
        (30, "30 days"),
        (90, "90 days"),
        (180, "6 months"),
        (365, "1 year"),
    ]
    
    current_retention = st.selectbox(
        "Data Retention Period",
        options=[opt[0] for opt in retention_options],
        index=0,
        format_func=lambda x: next(opt[1] for opt in retention_options if opt[0] == x),
        help="How long to keep your data before automatic deletion"
    )
    
    if prefs.data_retention_days != current_retention:
        prefs.data_retention_days = current_retention
        save_preferences(prefs)
        if current_retention > 0:
            st.success(f"Data will be automatically deleted after {current_retention} days.")
        else:
            st.info("Data will be kept forever.")
    
    # Delete all data
    st.markdown("#### Delete All Data")
    if st.button("Delete All My Data", type="secondary"):
        st.error("This would permanently delete ALL your data. This action is irreversible.")


def render_quarterly_review(prefs: PrivacyPreferences):
    """Render the quarterly privacy review section."""
    st.subheader("📅 Quarterly Privacy Review")
    
    if should_show_quarterly_review(prefs):
        st.info("""
        ### ⏰ Time for Your Quarterly Privacy Review
        
        It's been over 90 days since you last reviewed your privacy settings.
        Please take a moment to:
        
        1. Review which data categories you have enabled
        2. Check if you're still comfortable with the data collected
        3. Consider withdrawing consent for any categories you no longer use
        """)
        
        if st.button("I Have Reviewed My Settings", type="primary"):
            prefs.mark_reviewed()
            save_preferences(prefs)
            st.rerun()
    else:
        if prefs.last_review:
            days_until_review = 90 - (date.today() - prefs.last_review).days
            st.success(f"✅ Privacy settings reviewed. Next review in {days_until_review} days.")
        else:
            st.success("✅ Privacy settings reviewed.")


def render_transparency_section():
    """Render the transparency/privacy calculus section."""
    st.subheader("📊 Privacy Transparency")
    
    st.markdown("""
    ### How We Use Your Data
    
    | Category | How We Use It | Your Control |
    |----------|---------------|---------------|
    | Habits | To track your daily progress and calculate streaks | Grant/Withdraw |
    | Tasks | To manage your todo list | Grant/Withdraw |
    | Finances | To track income and expenses (encrypted) | Grant/Withdraw |
    | Health | To log health metrics | Grant/Withdraw |
    | Emotional | To track mood and wellbeing | Grant/Withdraw |
    | Time | To log time spent on activities | Grant/Withdraw |
    | Goals | To track goal progress | Grant/Withdraw |
    | Achievements | To display XP, badges, and gamification | Grant/Withdraw |
    | Analytics | Anonymous usage data to improve the app | Grant/Withdraw |
    | AI Suggestions | Personalized habit recommendations | Grant/Withdraw |
    
    ### Your Rights
    
    - **Access**: Download all your data at any time
    - **Rectification**: Correct inaccurate data
    - **Erasure**: Delete specific or all data
    - **Portability**: Export data in machine-readable format
    - **Object**: Opt out of specific data collection
    """)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main privacy dashboard page."""
    # Initialize
    init_privacy_session()
    prefs = get_preferences()
    
    # Header
    render_header()
    
    # Privacy score overview
    render_privacy_score(prefs)
    st.divider()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Consent",
        "📤 Export",
        "🗑️ Deletion",
        "📅 Review",
        "📊 Transparency"
    ])
    
    with tab1:
        render_consent_section(prefs)
    
    with tab2:
        render_export_section(prefs)
    
    with tab3:
        render_deletion_section(prefs)
    
    with tab4:
        render_quarterly_review(prefs)
    
    with tab5:
        render_transparency_section()


if __name__ == "__main__":
    main()
