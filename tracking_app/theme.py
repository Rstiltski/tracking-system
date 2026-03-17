"""
Gamevibe Theme Module - Gamified Streamlit UI
Phase 9: The Gamification & UI Overhaul (Gamevibe Protocol)
"""

import streamlit as st
from typing import Optional

THEME_COLORS = {
    "bg_primary": "#030712",
    "bg_secondary": "#111827",
    "bg_tertiary": "#1f2937",
    "bg_glass": "rgba(31, 41, 55, 0.7)",
    "primary": "#10b981",
    "neon_emerald": "#10b981",
    "neon_cyan": "#06b6d4",
    "neon_purple": "#a855f7",
    "neon_yellow": "#f59e0b",
    "text_primary": "#f9fafb",
    "text_secondary": "#9ca3af",
    "gradient_xp": "linear-gradient(90deg, #6366f1, #a855f7)",
}

THEME_CONFIG = {
    "radius_sm": "8px",
    "radius_md": "12px",
    "radius_lg": "16px",
    "radius_xl": "24px",
    "radius_full": "9999px",
    "transition_normal": "0.3s ease",
    "font_family": "'Poppins', -apple-system, sans-serif",
}

def apply_gamevibe_theme():
    """Inject the Gamevibe theme CSS into Streamlit."""
    c = THEME_COLORS
    cfg = THEME_CONFIG
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
:root {{
    --bg-primary: {c['bg_primary']};
    --neon-emerald: {c['neon_emerald']};
    --neon-cyan: {c['neon_cyan']};
    --neon-purple: {c['neon_purple']};
    --neon-yellow: {c['neon_yellow']};
    --text-primary: {c['text_primary']};
    --text-secondary: {c['text_secondary']};
}}
.stApp {{
    background-color: {c['bg_primary']};
    color: {c['text_primary']};
    font-family: {cfg['font_family']};
    background-image: radial-gradient(ellipse at top, rgba(16,185,129,0.05) 0%, transparent 50%), radial-gradient(ellipse at bottom right, rgba(99,102,241,0.05) 0%, transparent 50%);
}}
h1 {{ color: {c['neon_cyan']} !important; text-shadow: 0 0 20px rgba(6,182,212,0.4); font-weight: 800 !important; text-transform: uppercase; letter-spacing: 3px; }}
h2 {{ color: {c['neon_emerald']} !important; text-shadow: 0 0 10px rgba(16,185,129,0.3); font-weight: 700 !important; text-transform: uppercase; letter-spacing: 2px; }}
h3 {{ color: {c['neon_purple']} !important; text-shadow: 0 0 8px rgba(168,85,247,0.3); font-weight: 600 !important; }}
.stButton > button {{ background-color: transparent !important; color: {c['neon_emerald']} !important; border: 2px solid {c['neon_emerald']} !important; border-radius: {cfg['radius_md']} !important; font-weight: 700 !important; text-transform: uppercase; transition: all {cfg['transition_normal']} !important; box-shadow: 0 0 5px rgba(16,185,129,0.2); }}
.stButton > button:hover {{ background-color: rgba(16,185,129,0.15) !important; box-shadow: 0 0 20px rgba(16,185,129,0.5); transform: translateY(-2px) scale(1.02); }}
.stTextInput > div > div > input {{ background-color: {c['bg_secondary']} !important; color: {c['text_primary']} !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: {cfg['radius_md']} !important; }}
.stTextInput > div > div > input:focus {{ border-color: {c['neon_cyan']} !important; box-shadow: 0 0 10px rgba(6,182,212,0.3) !important; }}
.stCheckbox > label > div:first-child {{ width: 24px !important; height: 24px !important; border: 2px solid rgba(16,185,129,0.4) !important; border-radius: {cfg['radius_sm']} !important; background: rgba(16,185,129,0.1) !important; }}
[data-testid="stMetric"] {{ background: {c['bg_glass']}; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.05); border-radius: {cfg['radius_lg']}; padding: 1rem 1.25rem; transition: all {cfg['transition_normal']}; }}
[data-testid="stMetric"]:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.3), 0 0 15px rgba(16,185,129,0.2); }}
[data-testid="stMetricValue"] {{ color: {c['neon_yellow']} !important; font-size: 2rem !important; font-weight: 800 !important; text-shadow: 0 0 15px rgba(245,158,11,0.4); }}
[data-testid="stMetricLabel"] {{ color: {c['text_secondary']} !important; text-transform: uppercase; letter-spacing: 1px; }}
div[data-testid="stCard"] {{ background: {c['bg_glass']} !important; border: 1px solid rgba(255,255,255,0.05) !important; border-radius: {cfg['radius_xl']} !important; backdrop-filter: blur(10px); }}
div[data-testid="stProgress"] > div > div > div {{ background: {c['gradient_xp']} !important; border-radius: {cfg['radius_full']} !important; box-shadow: 0 0 10px rgba(99,102,241,0.5); }}
button[data-baseweb="tab"] {{ background: transparent !important; color: {c['text_secondary']} !important; font-weight: 600 !important; }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: {c['neon_emerald']} !important; box-shadow: 0 -2px 10px rgba(16,185,129,0.2); }}
section[data-testid="stSidebar"] {{ background: {c['bg_secondary']} !important; border-right: 1px solid rgba(255,255,255,0.05); }}
details > summary {{ background: {c['bg_secondary']} !important; border: 1px solid rgba(255,255,255,0.05) !important; border-radius: {cfg['radius_md']} !important; font-weight: 600 !important; }}
div.stSuccess {{ background: rgba(16,185,129,0.1) !important; border: 1px solid rgba(16,185,129,0.4) !important; border-radius: {cfg['radius_lg']} !important; box-shadow: 0 0 20px rgba(16,185,129,0.2); }}
#MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
::-webkit-scrollbar {{ width: 8px; }}
::-webkit-scrollbar-track {{ background: {c['bg_primary']}; }}
::-webkit-scrollbar-thumb {{ background: {c['bg_tertiary']}; border-radius: 4px; }}
@keyframes fireGlow {{ 0%, 100% {{ text-shadow: 0 0 5px #f59e0b; }} 50% {{ text-shadow: 0 0 15px #ef4444, 0 0 25px #f59e0b; }} }}
</style>""", unsafe_allow_html=True)

def render_player_card(level=1, xp_current=0, xp_max=100, streak=0):
    xp_pct = (xp_current / xp_max * 100) if xp_max > 0 else 0
    st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(17,24,39,0.9), rgba(31,41,55,0.8)); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; backdrop-filter: blur(10px);">
<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
<div style="width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#a855f7);display:flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:800;color:white;box-shadow:0 0 20px rgba(99,102,241,0.5);">{level}</div>
<div style="flex:1;"><div style="color:#9ca3af;font-size:0.85rem;text-transform:uppercase;letter-spacing:1px;">Player Level</div><div style="color:#f9fafb;font-size:1.25rem;font-weight:700;">Virtuoso</div></div>
<div style="text-align:right;"><div style="color:#f59e0b;font-size:1.5rem;font-weight:800;">{streak}</div><div style="color:#6b7280;font-size:0.75rem;text-transform:uppercase;">Streak</div></div></div>
<div style="margin-bottom:0.5rem;"><div style="display:flex;justify-content:space-between;margin-bottom:0.25rem;"><span style="color:#9ca3af;font-size:0.8rem;">XP</span><span style="color:#a855f7;font-size:0.8rem;font-weight:600;">{xp_current}/{xp_max}</span></div>
<div style="height:10px;background:#1f2937;border-radius:9999px;overflow:hidden;"><div style="height:100%;width:{xp_pct}%;background:linear-gradient(90deg,#6366f1,#a855f7);border-radius:9999px;box-shadow:0 0 10px rgba(168,85,247,0.5);"></div></div></div></div>""", unsafe_allow_html=True)

def render_streak_counter(days, max_streak=None):
    is_active = days > 0
    subtitle = f"Best: {max_streak} days" if max_streak else "Start your streak!"
    st.markdown(f"""<div style="text-align:center;padding:1rem;">
<div style="font-size:3rem;{'animation:fireGlow 1.5s ease-in-out infinite;' if is_active else ''}">{'🔥' if is_active else '💤'}</div>
<div style="font-size:2.5rem;font-weight:800;color:{'#f59e0b' if is_active else '#6b7280'};">{days}</div>
<div style="color:#9ca3af;font-size:0.85rem;text-transform:uppercase;letter-spacing:1px;">Day Streak</div>
<div style="color:#6b7280;font-size:0.75rem;margin-top:0.5rem;">{subtitle}</div></div>""", unsafe_allow_html=True)

def render_achievement_badge(title, description, icon="🏆", glow_color="#f59e0b"):
    st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(17,24,39,0.9),rgba(31,41,55,0.8));border:1px solid {glow_color}40;border-radius:12px;padding:1rem;display:flex;align-items:center;gap:1rem;backdrop-filter:blur(10px);box-shadow:0 0 15px {glow_color}20;">
<div style="font-size:2rem;filter:drop-shadow(0 0 8px {glow_color}80);">{icon}</div>
<div><div style="color:{glow_color};font-weight:700;font-size:1rem;">{title}</div><div style="color:#9ca3af;font-size:0.85rem;">{description}</div></div></div>""", unsafe_allow_html=True)

__all__ = ["apply_gamevibe_theme", "render_player_card", "render_streak_counter", "render_achievement_badge", "THEME_COLORS", "THEME_CONFIG"]
