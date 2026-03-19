"""
tracking_app/components/launchpad.py - Command Center Launchpad

Provides a visually stunning, glassmorphic grid navigation module for the Dashboard.
Instead of relying purely on the sidebar, users interact with these spatial tiles.
"""

import streamlit as st
import random

def render_glassmorphic_launchpad():
    """
    Renders a responsive, glass-styled grid of navigation tiles.
    Uses native anchor tags for seamless Streamlit multi-page routing.
    """
    
    # Generate some quick pseudo-metrics to make the tiles feel alive
    # (In a real scenario, we would pass these as arguments from database queries)
    active_tasks = random.randint(1, 5)
    
    css = """<style>
.launchpad-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-top: 16px; margin-bottom: 32px; }
.glass-tile { background: linear-gradient(145deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.4) 100%); border: 1px solid rgba(255, 255, 255, 0.05); border-top: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-radius: 24px; padding: 24px; text-align: center; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); cursor: pointer; text-decoration: none !important; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 160px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); }
.glass-tile:hover { transform: translateY(-8px) scale(1.02); background: linear-gradient(145deg, rgba(45, 55, 72, 0.8) 0%, rgba(30, 41, 59, 0.6) 100%); border: 1px solid rgba(99, 102, 241, 0.5); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1), 0 0 15px rgba(99, 102, 241, 0.3); }
.tile-icon { font-size: 48px; margin-bottom: 12px; filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.4)); transition: transform 0.3s ease; }
.glass-tile:hover .tile-icon { transform: scale(1.1); }
.tile-title { color: #F8FAFC !important; font-weight: 700; font-size: 18px; margin-bottom: 4px; font-family: 'Inter', system-ui, -apple-system, sans-serif; letter-spacing: -0.02em; }
.tile-subtitle { color: #94A3B8 !important; font-size: 13px; font-weight: 500; }
</style>"""
    
    html = f"""{css}
<div style="margin-bottom: 16px; margin-top: 16px;">
<h2 style="color: #F8FAFC; font-weight: 800; font-size: 28px; letter-spacing: -0.5px; margin: 0;">Command Center</h2>
<p style="color: #94A3B8; font-size: 16px; margin-top: 4px;">Where would you like to focus today?</p>
</div>
<div class="launchpad-grid">
<a href="habits" target="_self" class="glass-tile">
<div class="tile-icon">✅</div>
<div class="tile-title">Habits & Stacks</div>
<div class="tile-subtitle">Daily Mastery</div>
</a>
<a href="tasks" target="_self" class="glass-tile">
<div class="tile-icon">🎯</div>
<div class="tile-title">Tasks & Goals</div>
<div class="tile-subtitle">{active_tasks} Active High Priority</div>
</a>
<a href="health" target="_self" class="glass-tile">
<div class="tile-icon">❤️</div>
<div class="tile-title">Wellness</div>
<div class="tile-subtitle">Energy & Mood Log</div>
</a>
<a href="finances" target="_self" class="glass-tile">
<div class="tile-icon">💰</div>
<div class="tile-title">Finances</div>
<div class="tile-subtitle">Budget & Tracking</div>
</a>
</div>"""
    
    st.markdown(html, unsafe_allow_html=True)
    
