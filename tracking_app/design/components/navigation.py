"""
Navigation Components - Consistent Navigation Patterns

Phase 12: UI/UX Redesign - Component Layer

Provides reusable navigation components for page headers, breadcrumbs,
tabs, and section navigation with consistent styling.

Usage:
    from tracking_app.design.components.navigation import (
        render_page_header,
        render_breadcrumbs,
        render_tabs,
        render_section_header,
    )
"""

import streamlit as st
from typing import List, Optional, Dict, Any, Literal
from ...design.tokens import COLORS, SPACING, RADIUS, TRANSITION

TabStyle = Literal["underline", "pills", "boxed"]


def render_page_header(
    title: str,
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
    actions: Optional[List[Dict[str, Any]]] = None,
    show_divider: bool = True,
):
    """
    Render a page header with title, subtitle, and optional actions.
    
    Args:
        title: Page title
        subtitle: Optional subtitle/description
        icon: Optional emoji icon
        actions: Optional list of action buttons
        show_divider: Whether to show divider line
    
    Example:
        >>> render_page_header(
        ...     title="Dashboard",
        ...     subtitle="Overview of your progress",
        ...     icon="🏠",
        ...     actions=[
        ...         {"label": "Refresh", "icon": "🔄", "key": "refresh"}
        ...     ]
        ... )
    """
    
    # Build header HTML
    icon_html = f'<span style="font-size: 2rem; margin-right: 0.75rem;">{icon}</span>' if icon else ''
    
    subtitle_html = ""
    if subtitle:
        subtitle_html = f'<p style="color: var(--text-secondary); font-size: 1rem; margin: 0.5rem 0 0 0;">{subtitle}</p>'
    
    # Build action buttons
    actions_html = ""
    if actions:
        actions_html = '<div style="display: flex; gap: 0.5rem; margin-left: auto;">'
        for action in actions:
            actions_html += f'''
            <button 
                id="{action.get('key', 'action')}"
                style="
                    background: var(--bg-tertiary);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-md);
                    padding: 0.5rem 1rem;
                    color: var(--text-primary);
                    cursor: pointer;
                    transition: var(--transition-fast);
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    font-weight: 500;
                "
                onmouseover="this.style.background='var(--bg-secondary)'; this.style.borderColor='var(--primary)'"
                onmouseout="this.style.background='var(--bg-tertiary)'; this.style.borderColor='var(--border)'"
            >
                {action.get('icon', '')} {action.get('label', 'Action')}
            </button>
            '''
        actions_html += '</div>'
    
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        padding: {'1.5rem 0' if show_divider else '1rem 0'};
        {'border-bottom: 1px solid var(--border);' if show_divider else ''}
        margin-bottom: {'1.5rem' if show_divider else '1rem'};
    ">
        {icon_html}
        <div style="flex: 1;">
            <h1 style="margin: 0; font-size: clamp(1.875rem, 5vw, 2.5rem); font-weight: 800; color: var(--text-primary); line-height: 1.1;">
                {title}
            </h1>
            {subtitle_html}
        </div>
        {actions_html}
    </div>
    """, unsafe_allow_html=True)


def render_breadcrumbs(items: List[Dict[str, str]], separator: str = "›"):
    """
    Render breadcrumb navigation.
    
    Args:
        items: List of breadcrumb items with 'label' and optional 'href'
        separator: Separator character
    
    Example:
        >>> render_breadcrumbs([
        ...     {"label": "Home", "href": "/"},
        ...     {"label": "Habits", "href": "/habits"},
        ...     {"label": "Create New"}
        ... ])
    """
    
    breadcrumbs_html = ""
    for i, item in enumerate(items):
        label = item.get("label", "Link")
        href = item.get("href")
        
        if href and i < len(items) - 1:
            breadcrumbs_html += f'''
            <a href="{href}" style="
                color: var(--primary);
                text-decoration: none;
                font-weight: 500;
                transition: var(--transition-fast);
            " onmouseover="this.style.color='var(--primary-hover)'" onmouseout="this.style.color='var(--primary)'">
                {label}
            </a>
            '''
        else:
            breadcrumbs_html += f'''
            <span style="color: var(--text-secondary); font-weight: 500;">{label}</span>
            '''
        
        if i < len(items) - 1:
            breadcrumbs_html += f'''
            <span style="color: var(--text-disabled); margin: 0 0.5rem;">{separator}</span>
            '''
    
    st.markdown(f"""
    <nav style="
        display: flex;
        align-items: center;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    " aria-label="Breadcrumb">
        {breadcrumbs_html}
    </nav>
    """, unsafe_allow_html=True)


def render_tabs(
    tabs: List[str],
    active_tab: int = 0,
    style: TabStyle = "underline",
    key_prefix: str = "tab",
) -> int:
    """
    Render tab navigation.
    
    Args:
        tabs: List of tab labels
        active_tab: Index of currently active tab
        style: Tab style (underline, pills, boxed)
        key_prefix: Prefix for tab keys
    
    Returns:
        Index of selected tab
    
    Example:
        >>> selected = render_tabs(
        ...     tabs=["Overview", "Details", "Settings"],
        ...     active_tab=0,
        ...     style="pills"
        ... )
    """
    
    # Create columns for tabs
    cols = st.columns(len(tabs))
    
    for i, tab_label in enumerate(tabs):
        with cols[i]:
            # Determine if this tab is active
            is_active = (i == active_tab)
            
            # Style based on tab type and active state
            if style == "underline":
                if is_active:
                    st.markdown(f"""
                    <div style="
                        padding: 0.75rem 1rem;
                        border-bottom: 3px solid var(--primary);
                        color: var(--primary);
                        font-weight: 600;
                        cursor: pointer;
                        transition: var(--transition-fast);
                    " onmouseover="this.style.background='rgba(99, 102, 241, 0.05)'">
                        {tab_label}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        padding: 0.75rem 1rem;
                        border-bottom: 3px solid transparent;
                        color: var(--text-secondary);
                        font-weight: 500;
                        cursor: pointer;
                        transition: var(--transition-fast);
                    " onmouseover="this.style.background='rgba(99, 102, 241, 0.05)'; this.style.color='var(--text-primary)'">
                        {tab_label}
                    </div>
                    """, unsafe_allow_html=True)
            
            elif style == "pills":
                if is_active:
                    st.markdown(f"""
                    <div style="
                        padding: 0.5rem 1rem;
                        background: var(--primary);
                        color: white;
                        border-radius: var(--radius-full);
                        font-weight: 600;
                        cursor: pointer;
                        transition: var(--transition-fast);
                        text-align: center;
                    " onmouseover="this.style.background='var(--primary-hover)'">
                        {tab_label}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        padding: 0.5rem 1rem;
                        background: var(--bg-tertiary);
                        color: var(--text-secondary);
                        border-radius: var(--radius-full);
                        font-weight: 500;
                        cursor: pointer;
                        transition: var(--transition-fast);
                        text-align: center;
                    " onmouseover="this.style.background='var(--bg-secondary)'; this.style.color='var(--text-primary)'">
                        {tab_label}
                    </div>
                    """, unsafe_allow_html=True)
            
            elif style == "boxed":
                if is_active:
                    st.markdown(f"""
                    <div style="
                        padding: 0.75rem 1rem;
                        background: var(--bg-secondary);
                        border: 1px solid var(--primary);
                        color: var(--primary);
                        border-radius: var(--radius-md);
                        font-weight: 600;
                        cursor: pointer;
                        transition: var(--transition-fast);
                        text-align: center;
                        box-shadow: var(--shadow-sm);
                    " onmouseover="this.style.boxShadow='var(--shadow-md)'">
                        {tab_label}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        padding: 0.75rem 1rem;
                        background: transparent;
                        border: 1px solid var(--border);
                        color: var(--text-secondary);
                        border-radius: var(--radius-md);
                        font-weight: 500;
                        cursor: pointer;
                        transition: var(--transition-fast);
                        text-align: center;
                    " onmouseover="this.style.background='var(--bg-tertiary)'; this.style.color='var(--text-primary)'">
                        {tab_label}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Handle tab click (simplified - in production use session state)
            if st.button(f"Select {tab_label}", key=f"{key_prefix}_{i}", style_args={"display": "none"}):
                return i
    
    return active_tab


def render_section_header(
    title: str,
    icon: Optional[str] = None,
    subtitle: Optional[str] = None,
    action_label: Optional[str] = None,
    action_key: Optional[str] = None,
    on_action: Optional[str] = None,
    show_divider: bool = True,
):
    """
    Render a section header within a page.
    
    Args:
        title: Section title
        icon: Optional emoji icon
        subtitle: Optional subtitle
        action_label: Optional action button label
        action_key: Optional action button key
        on_action: Optional onclick handler
        show_divider: Whether to show divider line
    
    Example:
        >>> render_section_header(
        ...     title="Today's Habits",
        ...     icon="✅",
        ...     subtitle="5 habits to complete",
        ...     action_label="+ Add Habit",
        ...     action_key="add_habit_btn"
        ... )
    """
    
    icon_html = f'<span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>' if icon else ''
    
    subtitle_html = f'<p style="color: var(--text-secondary); font-size: 0.875rem; margin: 0.25rem 0 0 0;">{subtitle}</p>' if subtitle else ''
    
    action_html = ""
    if action_label and action_key:
        action_html = f'''
        <button 
            id="{action_key}"
            style="
                background: var(--primary);
                color: white;
                border: none;
                border-radius: var(--radius-md);
                padding: 0.5rem 1rem;
                font-weight: 600;
                font-size: 0.875rem;
                cursor: pointer;
                transition: var(--transition-fast);
                white-space: nowrap;
            "
            onmouseover="this.style.background='var(--primary-hover)'"
            onmouseout="this.style.background='var(--primary)'"
            {f'onclick="{on_action}"' if on_action else ''}
        >
            {action_label}
        </button>
        '''
    
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        padding: {'1rem 0' if show_divider else '0.75rem 0'};
        {'border-bottom: 1px solid var(--border);' if show_divider else ''}
        margin-bottom: {'1rem' if show_divider else '0.75rem'};
    ">
        <div style="display: flex; align-items: center; flex: 1;">
            {icon_html}
            <div>
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 600; color: var(--text-primary); line-height: 1.3;">
                    {title}
                </h3>
                {subtitle_html}
            </div>
        </div>
        {action_html}
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_section(
    title: str,
    icon: Optional[str] = None,
    items: Optional[List[Dict[str, Any]]] = None,
    expanded: bool = True,
    key: Optional[str] = None,
):
    """
    Render a collapsible sidebar section.
    
    Args:
        title: Section title
        icon: Optional emoji icon
        items: List of sidebar items with 'label', 'icon', 'page_path'
        expanded: Whether section is expanded by default
        key: Unique key for the section
    
    Example:
        >>> render_sidebar_section(
        ...     title="Mastery",
        ...     icon="✅",
        ...     items=[
        ...         {"label": "Habits", "icon": "✅", "page_path": "habits"},
        ...         {"label": "Stacks", "icon": "🔗", "page_path": "stacks"},
        ...     ]
        ... )
    """
    
    # Use Streamlit's native expander for sidebar sections
    section_title = f"{icon} {title}" if icon else title
    
    with st.sidebar.expander(section_title, expanded=expanded):
        if items:
            for item in items:
                label = item.get("label", "Item")
                item_icon = item.get("icon", "📄")
                page_path = item.get("page_path", "")
                
                # Use Streamlit's page_link
                if page_path:
                    st.page_link(
                        f"pages/{page_path}.py",
                        label=f"{item_icon} {label}",
                    )


def render_pagination(
    current_page: int,
    total_pages: int,
    key_prefix: str = "page",
) -> int:
    """
    Render pagination controls.
    
    Args:
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages
        key_prefix: Prefix for button keys
    
    Returns:
        Selected page number
    
    Example:
        >>> page = render_pagination(current_page=3, total_pages=10)
    """
    
    cols = st.columns([1, 4, 1])
    
    with cols[0]:
        prev_disabled = current_page <= 1
        if st.button("← Previous", key=f"{key_prefix}_prev", disabled=prev_disabled):
            return current_page - 1
    
    with cols[1]:
        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 0.75rem;
            color: var(--text-primary);
            font-weight: 600;
        ">
            Page {current_page} of {total_pages}
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        next_disabled = current_page >= total_pages
        if st.button("Next →", key=f"{key_prefix}_next", disabled=next_disabled):
            return current_page + 1
    
    return current_page


def render_quick_links(
    title: str,
    links: List[Dict[str, str]],
    icon: Optional[str] = None,
):
    """
    Render a quick links section.
    
    Args:
        title: Section title
        links: List of links with 'label', 'url', optional 'description'
        icon: Optional emoji icon
    
    Example:
        >>> render_quick_links(
        ...     title="Resources",
        ...     icon="🔗",
        ...     links=[
        ...         {"label": "Documentation", "url": "/docs", "description": "User guide"},
        ...         {"label": "Support", "url": "/support", "description": "Get help"},
        ...     ]
        ... )
    """
    
    icon_html = f'<span style="font-size: 1.25rem; margin-right: 0.5rem;">{icon}</span>' if icon else ''
    
    links_html = ""
    for link in links:
        label = link.get("label", "Link")
        url = link.get("url", "#")
        description = link.get("description", "")
        
        links_html += f'''
        <a href="{url}" style="
            display: block;
            padding: 0.75rem;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            text-decoration: none;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            transition: var(--transition-fast);
        " onmouseover="this.style.borderColor='var(--primary)'; this.style.background='var(--bg-secondary)'" onmouseout="this.style.borderColor='var(--border)'; this.style.background='var(--bg-tertiary)'">
            <div style="font-weight: 600; margin-bottom: 0.25rem;">{label}</div>
            {f'<div style="font-size: 0.875rem; color: var(--text-secondary);">{description}</div>' if description else ''}
        </a>
        '''
    
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <div style="
            display: flex;
            align-items: center;
            margin-bottom: 0.75rem;
            font-weight: 600;
            color: var(--text-primary);
        ">
            {icon_html}
            <span>{title}</span>
        </div>
        {links_html}
    </div>
    """, unsafe_allow_html=True)


def render_search_bar(
    placeholder: str = "Search...",
    key: str = "search",
    on_search: Optional[str] = None,
) -> Optional[str]:
    """
    Render a search bar.
    
    Args:
        placeholder: Placeholder text
        key: Unique key
        on_search: Optional JavaScript search handler
    
    Returns:
        Search query (if using form submit)
    
    Example:
        >>> query = render_search_bar(
        ...     placeholder="Search habits...",
        ...     key="habit_search"
        ... )
    """
    
    # Use Streamlit's text_input for search
    query = st.text_input(
        label="Search",
        placeholder=placeholder,
        key=key,
        label_visibility="collapsed",
    )
    
    return query


__all__ = [
    "render_page_header",
    "render_breadcrumbs",
    "render_tabs",
    "render_section_header",
    "render_sidebar_section",
    "render_pagination",
    "render_quick_links",
    "render_search_bar",
    "TabStyle",
]
