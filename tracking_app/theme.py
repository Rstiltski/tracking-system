"""
🎮 GAMEVIBE THEME ENGINE
Injects Cyberpunk/RPG aesthetics into Streamlit via CSS.
"""
import streamlit as st

def apply_gamevibe_theme():
    """
    Injects custom CSS to transform the app into a 'Life RPG' interface.
    Features: Dark mode, neon accents, glowing headers, arcade fonts.
    """
    st.markdown("""
        <style>
        /* --- 🌌 GLOBAL ATMOSPHERE --- */
        .stApp {
            background-color: #0d1117; /* Deep Void Blue */
            color: #c9d1d9;
            font-family: 'Courier New', Courier, monospace; /* Arcade Terminal */
        }
        
        /* Hide default footer header clutter */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* --- 🔮 TYPOGRAPHY & HEADERS --- */
        h1, h2, h3, h4, h5, h6 {
            color: #58a6ff !important; /* Neon Blue */
            font-family: 'Courier New', Courier, monospace;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            text-shadow: 0 0 10px rgba(88, 166, 255, 0.4);
            margin-bottom: 0.5em;
        }
        
        p, label, div.stMarkdown {
            color: #8b949e;
            font-size: 1.05rem;
        }

        /* --- 🃏 CARD CONTAINERS (Info, Success, Warning) --- */
        div[data-testid="stInfo"], 
        div[data-testid="stSuccess"], 
        div[data-testid="stWarning"], 
        div[data-testid="stError"] {
            background-color: rgba(22, 27, 34, 0.9) !important;
            border: 1px solid #30363d !important;
            border-left: 4px solid #58a6ff !important;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }

        div[data-testid="stInfo"]:hover,
        div[data-testid="stSuccess"]:hover,
        div[data-testid="stWarning"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 15px rgba(88, 166, 255, 0.25);
            border-color: #58a6ff !important;
        }

        /* Specific Colors for Status */
        div[data-testid="stSuccess"] { border-left-color: #3fb950 !important; } /* Green */
        div[data-testid="stSuccess"]:hover { box-shadow: 0 0 15px rgba(63, 185, 80, 0.25); }
        
        div[data-testid="stWarning"] { border-left-color: #d29922 !important; } /* Gold */
        div[data-testid="stWarning"]:hover { box-shadow: 0 0 15px rgba(210, 153, 34, 0.25); }

        /* --- 🔘 BUTTONS (Neon Arcade Style) --- */
        .stButton > button {
            background-color: transparent !important;
            color: #3fb950 !important; /* Neon Green Text */
            border: 2px solid #3fb950 !important;
            border-radius: 6px !important;
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 0.5em 1em;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 0 5px rgba(63, 185, 80, 0.2);
        }

        .stButton > button:hover {
            background-color: #3fb950 !important;
            color: #0d1117 !important; /* Black text on hover */
            box-shadow: 0 0 20px rgba(63, 185, 80, 0.6);
            transform: scale(1.05);
            cursor: pointer;
        }
        
        /* Secondary Button Style (Red/Danger) */
        .stButton > button[kind="secondary"] {
            color: #f85149 !important;
            border-color: #f85149 !important;
        }
        .stButton > button[kind="secondary"]:hover {
            background-color: #f85149 !important;
            box-shadow: 0 0 20px rgba(248, 81, 73, 0.6);
        }

        /* --- 📊 METRICS (Player Stats) --- */
        [data-testid="stMetricValue"] {
            color: #f0883e !important; /* Neon Orange */
            font-family: 'Courier New', Courier, monospace;
            font-size: 2.5rem;
            text-shadow: 0 0 8px rgba(240, 136, 62, 0.4);
        }
        [data-testid="stMetricLabel"] {
            color: #8b949e !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.9rem;
        }

        /* --- 📥 INPUT FIELDS --- */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #010409 !important;
            color: #c9d1d9 !important;
            border: 1px solid #30363d !important;
            border-radius: 6px;
        }
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: #58a6ff !important;
            box-shadow: 0 0 8px rgba(88, 166, 255, 0.3);
        }

        /* --- 📊 TABLES / DATAFRAMES --- */
        div[data-testid="stDataFrame"] {
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
        }
        table {
            background-color: #0d1117 !important;
            color: #c9d1d9 !important;
        }
        th {
            background-color: #161b22 !important;
            color: #58a6ff !important;
            text-transform: uppercase;
            font-size: 0.85rem;
        }
        tr:nth-child(even) {background-color: #010409 !important;}
        tr:hover {background-color: #161b22 !important;}

        /* --- 📌 SIDEBAR TWEAKS --- */
        section[data-testid="stSidebar"] {
            background-color: #010409 !important;
            border-right: 1px solid #30363d;
        }
        </style>
    """, unsafe_allow_html=True)
