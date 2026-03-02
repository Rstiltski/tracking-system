"""
Component render functions for the Template Sharing page.
"""

import streamlit as st
from typing import List, Any, Optional

from .constants import (
    PAGE_TITLE,
    PAGE_ICON,
    PAGE_LAYOUT,
    INITIAL_SIDEBAR_STATE,
    DEFAULT_USER_ID,
    SEARCH_PLACEHOLDER,
    ALL_CATEGORIES,
    TAB_BROWSE,
    TAB_MINE,
    TAB_CREATE,
    FORM_TITLE_LABEL,
    FORM_DESCRIPTION_LABEL,
    FORM_PUBLIC_LABEL,
    SUCCESS_CLONE,
    SUCCESS_SHARE,
    INFO_SAVED,
    INFO_NO_TEMPLATES,
    INFO_NO_SHARED,
    INFO_NO_CLONED,
    BTN_USE_TEMPLATE,
    BTN_SHARE_FIRST,
    BTN_SHARE_TEMPLATE,
)
from .helpers import (
    filter_templates_by_search,
    filter_templates_by_category,
    get_template_options,
    format_template_header,
    format_habit_list,
    create_mock_shared_template,
)
from .session_state import (
    init_session_state,
    get_user_id,
    add_cloned_template,
    add_shared_template,
    get_shared_templates,
)


def render_browse_templates() -> None:
    """Render browse templates tab."""
    st.markdown("**🌍 Community Templates**")
    
    # Search and filter
    col1, col2 = st.columns(2)
    
    with col1:
        search = st.text_input("Search templates", placeholder=SEARCH_PLACEHOLDER)
    
    with col2:
        # Import here to avoid circular imports
        from brain.models.habit_template import TemplateCategory
        category = st.selectbox(
            "Category",
            options=[ALL_CATEGORIES] + [c.value for c in TemplateCategory]
        )
    
    # Get templates
    from brain.models.habit_template import DEFAULT_TEMPLATES
    templates = DEFAULT_TEMPLATES
    
    # Apply filters
    templates = filter_templates_by_search(templates, search)
    templates = filter_templates_by_category(templates, category)
    
    if not templates:
        st.info(INFO_NO_TEMPLATES)
        return
    
    # Display templates
    for template in templates:
        with st.expander(format_template_header(template)):
            st.markdown(f"*{template.description}*")
            
            # Show habits
            st.markdown("**Habits:**")
            for habit_line in format_habit_list(template.habits):
                st.markdown(habit_line)
            
            # Clone button
            if st.button(BTN_USE_TEMPLATE, key=f"use_{template.id}"):
                add_cloned_template(template.id)
                st.success(SUCCESS_CLONE.format(template.name))
                st.rerun()
            
            st.divider()


def render_my_templates() -> None:
    """Render my templates tab."""
    st.markdown("**📚 My Shared Templates**")
    
    shared_templates = get_shared_templates()
    
    if not shared_templates:
        st.info(INFO_NO_SHARED)
        
        if st.button(BTN_SHARE_FIRST):
            st.session_state.selected_tab = TAB_CREATE
            st.rerun()
    else:
        for template in shared_templates:
            with st.expander(f"**{template['title']}**"):
                st.markdown(f"*{template['description']}*")
                st.caption(f"Public: {'Yes' if template['is_public'] else 'No'}")
    
    st.divider()
    
    st.markdown("**📥 Cloned Templates**")
    st.info(INFO_NO_CLONED)


def render_share_template() -> None:
    """Render share template tab."""
    st.markdown("**➕ Share Your Template**")
    
    # Get templates for selection
    from brain.models.habit_template import DEFAULT_TEMPLATES
    template_options = get_template_options(DEFAULT_TEMPLATES)
    
    with st.form("share_template_form"):
        # Select template to share
        selected = st.selectbox(
            "Select a template to share",
            options=list(template_options.keys())
        )
        
        selected_template = template_options[selected]
        
        title = st.text_input(FORM_TITLE_LABEL, value=selected_template.name)
        description = st.text_area(
            FORM_DESCRIPTION_LABEL,
            value=selected_template.description,
            help="Describe why this template works for you"
        )
        
        is_public = st.checkbox(FORM_PUBLIC_LABEL, value=True)
        
        submitted = st.form_submit_button(BTN_SHARE_TEMPLATE, type="primary")
        
        if submitted:
            user_id = get_user_id()
            new_shared = create_mock_shared_template(
                template_id=selected_template.id,
                title=title,
                description=description,
                user_id=user_id,
                is_public=is_public
            )
            add_shared_template(new_shared)
            st.success(SUCCESS_SHARE.format(title))
            st.info(INFO_SAVED)
            st.rerun()


def render_template_sharing_page() -> None:
    """Render the complete template sharing page."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=PAGE_LAYOUT,
        initial_sidebar_state=INITIAL_SIDEBAR_STATE
    )
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.title(f"{PAGE_ICON} Template Sharing")
    st.markdown("Share your successful habit templates with the community!")
    
    # Tabs
    tab_browse, tab_mine, tab_create = st.tabs([
        TAB_BROWSE,
        TAB_MINE,
        TAB_CREATE
    ])
    
    with tab_browse:
        render_browse_templates()
    
    with tab_mine:
        render_my_templates()
    
    with tab_create:
        render_share_template()