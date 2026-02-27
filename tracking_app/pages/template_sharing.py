"""
Template Sharing Page - Share and discover habit templates.

Usage:
    streamlit run tracking_app/pages/template_sharing.py
"""
import streamlit as st

from brain.models.habit_template import DEFAULT_TEMPLATES, TemplateCategory


# Page configuration
st.set_page_config(
    page_title="Template Sharing - Veryfyn",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main template sharing page."""
    # Initialize
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()

    if 'user_id' not in st.session_state:
        st.session_state.user_id = "user-123"  # Demo user ID

    # Header
    st.title("📋 Template Sharing")
    st.markdown("Share your successful habit templates with the community!")

    # Tabs
    tab_browse, tab_mine, tab_create = st.tabs([
        "🌍 Browse Templates",
        "📚 My Templates",
        "➕ Share Template"
    ])

    with tab_browse:
        render_browse_templates()

    with tab_mine:
        render_my_templates()

    with tab_create:
        render_share_template()


def render_browse_templates() -> None:
    """Render browse templates tab."""
    st.markdown("**🌍 Community Templates**")

    # Search and filter
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("Search templates", placeholder="Search by name or tag...")
    with col2:
        category = st.selectbox(
            "Category",
            options=["All"] + [c.value for c in TemplateCategory]
        )

    # Show templates
    templates = DEFAULT_TEMPLATES

    if search:
        templates = [t for t in templates if search.lower() in t.name.lower()]

    if category != "All":
        templates = [t for t in templates if t.category.value == category]

    if not templates:
        st.info("No templates found")
        return

    # Display templates
    for template in templates:
        with st.expander(
            f"**{template.name}** - {template.difficulty.value.title()} ({template.total_duration} min)"
        ):
            st.markdown(f"*{template.description}*")

            # Show habits
            st.markdown("**Habits:**")
            for i, habit in enumerate(template.habits, 1):
                st.markdown(f"{i}. {habit.icon} {habit.name} ({habit.duration_minutes} min)")

            # Clone button
            if st.button("📋 Use This Template", key=f"use_{template.id}"):
                st.success(f"✅ Template '{template.name}' added to your habits!")
                st.rerun()

            st.divider()


def render_my_templates() -> None:
    """Render my templates tab."""
    st.markdown("**📚 My Shared Templates**")

    # In production, get user's shared templates
    st.info("You haven't shared any templates yet")

    if st.button("Share Your First Template"):
        st.session_state.selected_tab = "➕ Share Template"
        st.rerun()

    st.divider()

    st.markdown("**📥 Cloned Templates**")
    st.info("Templates you've cloned will appear here")


def render_share_template() -> None:
    """Render share template tab."""
    st.markdown("**➕ Share Your Template**")

    with st.form("share_template_form"):
        # Select template to share
        template_options = {t.name: t for t in DEFAULT_TEMPLATES}
        selected = st.selectbox(
            "Select a template to share",
            options=list(template_options.keys())
        )

        title = st.text_input("Title", value=template_options[selected].name)
        description = st.text_area(
            "Description",
            value=template_options[selected].description,
            help="Describe why this template works for you"
        )

        is_public = st.checkbox("Make public", value=True)

        submitted = st.form_submit_button("Share Template", type="primary")

        if submitted:
            st.success(f"✅ Template '{title}' shared successfully!")
            st.info("In production, this would save to the database")
            st.rerun()


if __name__ == "__main__":
    main()
