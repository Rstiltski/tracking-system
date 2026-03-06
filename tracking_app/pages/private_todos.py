"""Private Todos Page - Personal Todo List"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import get_storage
from tracking_app.components.sidebar import render_sidebar
from datetime import datetime

st.set_page_config(page_title="Private Todos - Veryfyn", page_icon="🔒", layout="wide")

def main():
    render_sidebar()
    st.title("🔒 Private Todos")
    st.markdown("*Your personal todo list - separate from your main tasks*")
    st.caption("🔐 These todos are private and not shared")
    st.divider()
    
    storage = st.session_state.storage
    
    # Add new todo form
    with st.expander("➕ Add New Todo", expanded=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            title = st.text_input("Title", placeholder="What do you need to do?", key="private_todo_title")
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], key="private_todo_priority")
        
        description = st.text_area("Description (optional)", key="private_todo_desc")
        due_date = st.date_input("Due Date (optional)", value=None, key="private_todo_due")
        category = st.text_input("Category (optional)", placeholder="personal, work, etc.", key="private_todo_cat")
        
        if st.button("Add Todo", type="primary"):
            if title.strip():
                due = datetime.combine(due_date, datetime.min.time()) if due_date else None
                storage.create_private_todo(
                    title=title,
                    description=description,
                    priority=priority,
                    category=category,
                    due_date=due
                )
                st.success("✅ Todo added!")
                st.rerun()
            else:
                st.warning("Please enter a title.")
    
    st.divider()
    
    # Filter
    show_completed = st.checkbox("Show completed todos", value=False)
    
    # Get todos
    todos = storage.get_private_todos(include_completed=show_completed)
    
    if not todos:
        st.info("📝 No private todos yet. Add your first one above!")
    else:
        for todo in todos:
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                is_complete = st.checkbox("", value=todo.completed, key=f"complete_private_{todo.id}")
                if is_complete != todo.completed:
                    storage.update_private_todo(todo.id, completed=is_complete)
                    st.rerun()
            
            with col2:
                title_text = f"~~{todo.title}~~" if todo.completed else f"**{todo.title}**"
                st.markdown(title_text)
                if todo.description:
                    st.caption(todo.description)
                if todo.due_date:
                    st.caption(f"📅 Due: {todo.due_date.strftime('%b %d, %Y')}")
            
            with col3:
                priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                st.markdown(priority_color.get(todo.priority, "⚪"))
                
                if st.button("🗑️", key=f"del_private_{todo.id}"):
                    storage.delete_private_todo(todo.id)
                    st.rerun()
            
            st.divider()

if __name__ == "__main__":
    main()