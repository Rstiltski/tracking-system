"""
Veryfyn Tracking System - Main Streamlit Application

Main entry point for the Streamlit-based tracking application.
Uses Streamlit's native multi-page navigation.

Usage:
    streamlit run tracking_app/app.py
"""

import streamlit as st
from datetime import datetime
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import shared components
from tracking_app.components.sidebar import render_sidebar
from tracking_app.components.session import init_session_state
from tracking_app.design.theme import apply_design_system



# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Veryfyn - Personal Tracking System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Rstiltski/tracking-system',
        'Report a bug': 'https://github.com/Rstiltski/tracking-system/issues',
        'About': """
        # Veryfyn - Personal Tracking System
        
        A gamified personal tracking system for habits, finances, tasks, 
        health, time, and goals.
        
        Version: 2.0.0
        """
    }
)

# Reduce Streamlit blinking - hide loading spinner and make transitions smoother
st.markdown("""
<style>
    /* Hide the loading spinner during reruns */
    .stSpinner {
        display: none !important;
    }
    
    /* Make page transition smoother */
    .stApp {
        transition: opacity 0.1s ease-in-out;
    }
    
    /* Hide the running indicator */
    .stStatusWidget {
        opacity: 0.3 !important;
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Reduce animation flicker */
    .element-container {
        transition: all 0.1s ease;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """
    Main application entry point.
    
    Uses Streamlit's native multi-page navigation.
    The pages in tracking_app/pages/ appear in the sidebar automatically.
    """
    # Initialize session state
    init_session_state()
    
    # Apply design system (theme and styling)
    apply_design_system(theme=st.session_state.get('theme', 'dark'))
    
    # Render custom categorized sidebar
    render_sidebar()
    
    # Show welcome message on main page
    st.title("🎯 Veryfyn - Personal Tracking System")
    st.markdown("""
    Welcome to your personal tracking system!
    
    Use the **sidebar navigation** to access different features:
    
    - 📊 **Dashboard** - Overview of your progress
    - ✅ **Habits** - Track your daily habits  
    - 📝 **Tasks** - Manage your todo list
    - 💰 **Finances** - Track income and expenses
    - ❤️ **Health** - Monitor health metrics
    - 😊 **Emotional Health** - Track your emotional state
    - ⏰ **Time** - Track time spent on activities
    - 🎯 **Goals** - Set and track goals
    - 🏆 **Achievements** - View your achievements
    - 👥 **Friends** - Connect with friends
    - 📊 **Leaderboards** - Compete with friends
    - 🔬 **Habit Experiments** - Test habit variations
    - 📈 **Insights** - Analyze your data
    - 📓 **Journal** - Keep a daily journal
    - 🔒 **Private Todos** - Private notes and todos
    - ⚙️ **Settings** - Configure the app
    
    *Select a page from the sidebar to get started!*
    """)


if __name__ == "__main__":
    main()
