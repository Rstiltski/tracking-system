"""
Weekly Review Page - Streamlit page for weekly habit reviews.

Provides a comprehensive weekly review interface with:
- Completion metrics
- Streak milestones
- Habit performance
- Actionable insights

Usage:
    streamlit run tracking_app/pages/weekly_review.py
"""

# Conditional streamlit import for test compatibility
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None

from tracking_app.pages.weekly_review import (
    init_session_state,
    render_weekly_review_page,
    display_review,
    display_historical_comparison,
)


def main():
    """Main review page."""
    if HAS_STREAMLIT:
        render_weekly_review_page()
    else:
        print("Streamlit not installed. Run: pip install streamlit")


if __name__ == "__main__":
    main()