"""
Template Sharing Page - Share and discover habit templates.

Usage:
    streamlit run tracking_app/pages/template_sharing.py
"""

# Conditional streamlit import for test compatibility
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None

from tracking_app.pages.template_sharing import (
    init_session_state,
    render_template_sharing_page,
    render_browse_templates,
    render_my_templates,
    render_share_template,
)


def main():
    """Main template sharing page."""
    if HAS_STREAMLIT:
        render_template_sharing_page()
    else:
        print("Streamlit not installed. Run: pip install streamlit")


if __name__ == "__main__":
    main()