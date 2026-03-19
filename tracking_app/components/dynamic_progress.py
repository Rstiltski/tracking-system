"""
tracking_app/components/dynamic_progress.py - Robo-Chickmini Progress Tracker

Provides a highly creative, animated replacement for the standard st.progress bar.
Features a character that moves along the track based on completion percentage.
"""

import streamlit as st

def render_chickmini_progress(completed: int, total: int):
    """
    Renders a dynamic, animated progress bar featuring a Robo-Chickmini.
    Preserves all existing logic; just replaces the visual representation.
    
    Args:
        completed: Number of completed items
        total: Total number of items
    """
    # Calculate percentage safely
    percentage = int((completed / total) * 100) if total > 0 else 0
    
    # Determine the character state
    if percentage == 0:
        character = "🥚"           # Starting out
    elif percentage < 100:
        character = "🐔"           # In progress/Walking
    else:
        character = "🐔💎"         # 100% complete: Lays a gem!
        
    # CSS for the animated glow effect when complete
    glow_css = "box-shadow: 0 0 15px rgba(99, 102, 241, 0.6);" if percentage == 100 else ""
    
    html_content = f"""<div style="margin: 16px 0 24px 0; font-family: 'Inter', system-ui, sans-serif;">
<div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
<span style="font-size: 14px; font-weight: 700; color: #E2E8F0;">Daily Progress</span>
<span style="font-size: 14px; font-weight: 600; color: #94A3B8;">{completed}/{total} ({percentage}%)</span>
</div>
<div style="width: 100%; background-color: rgba(30, 41, 59, 0.6); border-radius: 999px; height: 28px; position: relative; overflow: visible; border: 1px solid rgba(255, 255, 255, 0.05); box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);">
<div style="width: {percentage}%; {glow_css} background: linear-gradient(90deg, #10B981, #059669); height: 100%; border-radius: 999px; transition: width 1s cubic-bezier(0.34, 1.56, 0.64, 1);"></div>
<div style="position: absolute; left: calc({percentage}% - 14px); top: 50%; transform: translateY(-50%); font-size: 24px; transition: left 1s cubic-bezier(0.34, 1.56, 0.64, 1); z-index: 10; text-shadow: 0 4px 6px rgba(0,0,0,0.5);">
{character}
</div>
</div>
</div>"""
    
    st.markdown(html_content, unsafe_allow_html=True)

