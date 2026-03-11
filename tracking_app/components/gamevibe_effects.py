"""
🎉 GAMEVIBE VISUAL EFFECTS
Lottie animations and visual feedback for achievements and interactions.
"""
import streamlit as st

try:
    from lottie import from_json
    import json
    LOTTY_AVAILABLE = True
except ImportError:
    LOTTY_AVAILABLE = False


def get_celebration_animation():
    """Returns Lottie JSON data for celebration confetti."""
    # Simple confetti animation data (inline to avoid external file dependency)
    return {
        "v": "5.5.7",
        "fr": 30,
        "ip": 0,
        "op": 60,
        "w": 400,
        "h": 400,
        "nm": "Confetti Celebration",
        "ddd": 0,
        "assets": [],
        "layers": []
    }


def render_confetti():
    """Displays a confetti celebration animation."""
    if LOTTY_AVAILABLE:
        try:
            from streamlit_lottie import st_lottie
            st_lottie(
                get_celebration_animation(),
                height=200,
                key="confetti"
            )
        except Exception:
            # Fallback if lottie fails
            st.success("🎉 **LEVEL UP!** 🎉")
    else:
        # Text-based fallback
        st.success("🎉 **CELEBRATION!** 🎊✨🚀")


def render_level_up_effect():
    """Displays a level-up visual effect."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 20px; 
                    background: linear-gradient(45deg, #3fb950, #58a6ff);
                    border-radius: 15px; margin: 10px 0;'>
            <h2 style='color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>
                ⬆️ LEVEL UP! ⬆️
            </h2>
        </div>
        """, unsafe_allow_html=True)


def render_streak_fire():
    """Returns fire emoji animation for streaks."""
    return "🔥"


def render_achievement_badge(icon: str = "🏆", title: str = "Achievement Unlocked"):
    """Displays an achievement badge with styling."""
    st.markdown(f"""
    <div style='display: inline-block; 
                padding: 15px 25px; 
                background: linear-gradient(135deg, #d29922, #f0883e);
                border-radius: 50px; 
                box-shadow: 0 4px 15px rgba(240, 136, 62, 0.4);
                margin: 10px 0;
                text-align: center;'>
        <span style='font-size: 2em;'>{icon}</span>
        <div style='color: white; font-weight: bold; font-size: 1.1em; 
                    text-transform: uppercase; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>
            {title}
        </div>
    </div>
    """, unsafe_allow_html=True)
