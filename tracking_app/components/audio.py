"""
Audio Controls UI Component

Phase 7.3: Streamlit UI for audio preferences and controls.
Provides volume slider, mute toggle, and category settings.

Usage:
    from tracking_app.components.audio import render_audio_settings
    
    render_audio_settings()
"""

import streamlit as st
from typing import Optional, Any

from brain.audio import AudioManager, SoundEffect
from brain.audio.manager import AudioPreferences, get_audio_manager


def render_audio_settings(
    audio_manager: Optional[AudioManager] = None,
    show_category_settings: bool = True,
    show_test_button: bool = True,
) -> AudioPreferences:
    """
    Render audio settings panel.
    
    Args:
        audio_manager: AudioManager instance (uses singleton if not provided)
        show_category_settings: Whether to show category toggles
        show_test_button: Whether to show test sound button
    
    Returns:
        Current audio preferences
    """
    if audio_manager is None:
        audio_manager = get_audio_manager()
    
    st.subheader("🔊 Audio Settings")
    
    # Master enable/disable
    enabled = st.toggle(
        "Enable Sound Effects",
        value=audio_manager.preferences.enabled,
        key="audio_enabled_toggle",
        help="Toggle all sound effects on or off"
    )
    
    if enabled != audio_manager.preferences.enabled:
        if enabled:
            audio_manager.unmute()
        else:
            audio_manager.mute()
    
    if not enabled:
        st.caption("🔇 Sound effects are currently muted")
        return audio_manager.preferences
    
    # Volume control
    volume = st.slider(
        "Volume",
        min_value=0,
        max_value=100,
        value=int(audio_manager.preferences.volume * 100),
        key="audio_volume_slider",
        help="Adjust the master volume for all sound effects"
    )
    
    # Update volume if changed
    new_volume = volume / 100.0
    if abs(new_volume - audio_manager.preferences.volume) > 0.01:
        audio_manager.set_volume(new_volume)
    
    st.caption(f"🔊 Volume: {volume}%")
    
    # Category settings
    if show_category_settings:
        st.divider()
        st.markdown("**Sound Categories**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            habit_sounds = st.checkbox(
                "🎯 Habit Sounds",
                value=audio_manager.preferences.habit_sounds,
                key="audio_habit_sounds",
                help="Sounds for habit completion and streaks"
            )
            
            achievement_sounds = st.checkbox(
                "🏆 Achievement Sounds",
                value=audio_manager.preferences.achievement_sounds,
                key="audio_achievement_sounds",
                help="Sounds for achievement unlocks and level ups"
            )
        
        with col2:
            task_sounds = st.checkbox(
                "📋 Task Sounds",
                value=audio_manager.preferences.task_sounds,
                key="audio_task_sounds",
                help="Sounds for task completion"
            )
            
            system_sounds = st.checkbox(
                "⚙️ System Sounds",
                value=audio_manager.preferences.system_sounds,
                key="audio_system_sounds",
                help="System notifications and alerts"
            )
        
        # Update category settings if changed
        if habit_sounds != audio_manager.preferences.habit_sounds:
            audio_manager.set_category_enabled("habits", habit_sounds)
        if achievement_sounds != audio_manager.preferences.achievement_sounds:
            audio_manager.set_category_enabled("achievements", achievement_sounds)
        if task_sounds != audio_manager.preferences.task_sounds:
            audio_manager.set_category_enabled("tasks", task_sounds)
        if system_sounds != audio_manager.preferences.system_sounds:
            audio_manager.set_category_enabled("system", system_sounds)
    
    # Test sound button
    if show_test_button:
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔊 Test Sound", key="audio_test_button"):
                audio_manager.test_sound(SoundEffect.SUCCESS)
                st.toast("🔊 Test sound played!", icon="✅")
        
        with col2:
            # Sound selector for testing different sounds
            test_sound = st.selectbox(
                "Select Test Sound",
                options=[
                    ("Habit Complete", SoundEffect.HABIT_COMPLETE),
                    ("Achievement Unlock", SoundEffect.ACHIEVEMENT_UNLOCK),
                    ("Level Up", SoundEffect.LEVEL_UP),
                    ("Task Complete", SoundEffect.TASK_COMPLETE),
                    ("Success", SoundEffect.SUCCESS),
                    ("Notification", SoundEffect.NOTIFICATION),
                    ("Click", SoundEffect.CLICK),
                ],
                format_func=lambda x: x[0],
                key="audio_test_sound_select"
            )
    
    return audio_manager.preferences


def render_audio_toggle(
    audio_manager: Optional[AudioManager] = None
) -> bool:
    """
    Render a simple mute/unmute toggle button.
    
    Args:
        audio_manager: AudioManager instance
    
    Returns:
        Current mute state
    """
    if audio_manager is None:
        audio_manager = get_audio_manager()
    
    is_muted = audio_manager.is_muted()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if is_muted:
            st.markdown("🔇 Sound: **Muted**")
        else:
            volume = int(audio_manager.get_volume() * 100)
            st.markdown(f"🔊 Sound: **On** ({volume}%)")
    
    with col2:
        if st.button(
            "Unmute" if is_muted else "Mute",
            key="audio_quick_toggle"
        ):
            audio_manager.toggle_mute()
            st.rerun()
    
    return is_muted


def render_volume_slider(
    audio_manager: Optional[AudioManager] = None,
    label: str = "Volume"
) -> float:
    """
    Render a simple volume slider.
    
    Args:
        audio_manager: AudioManager instance
        label: Label for the slider
    
    Returns:
        Current volume (0.0 to 1.0)
    """
    if audio_manager is None:
        audio_manager = get_audio_manager()
    
    volume = st.slider(
        label,
        min_value=0,
        max_value=100,
        value=int(audio_manager.get_volume() * 100),
        key="audio_volume_simple"
    )
    
    new_volume = volume / 100.0
    if abs(new_volume - audio_manager.get_volume()) > 0.01:
        audio_manager.set_volume(new_volume)
    
    return new_volume


def play_sound(effect: SoundEffect) -> None:
    """
    Queue a sound for playback.
    
    This function queues a sound effect to be played via Web Audio API.
    The sound will be rendered as JavaScript in the next Streamlit render.
    
    Args:
        effect: The sound effect to play
    """
    audio_manager = get_audio_manager()
    audio_manager.play(effect)
    
    # Get queued sounds and render JavaScript
    sounds = audio_manager.get_queued_sounds()
    
    if sounds:
        for sound_data in sounds:
            _render_sound_js(sound_data)


def _render_sound_js(sound_data: dict) -> None:
    """
    Render JavaScript to play a synthesized sound.
    
    Uses Web Audio API to generate sounds without external files.
    
    Args:
        sound_data: Dictionary with sound parameters
    """
    import json
    
    # Create JavaScript for Web Audio API synthesis
    js_code = f"""
    <script>
    (function() {{
        try {{
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const masterVolume = {sound_data.get('master_volume', 0.7)};
            const volume = {sound_data.get('volume', 1.0)} * masterVolume;
            const duration = {sound_data.get('duration', 0.2)};
            const waveform = '{sound_data.get('waveform', 'sine')}';
            const frequencies = {json.dumps(sound_data.get('frequencies', [440]))};
            const attack = {sound_data.get('attack', 0.01)};
            const decay = {sound_data.get('decay', 0.1)};
            const sustain = {sound_data.get('sustain', 0.5)};
            const release = {sound_data.get('release', 0.1)};
            
            frequencies.forEach((freq, index) => {{
                const oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                
                oscillator.type = waveform;
                oscillator.frequency.setValueAtTime(freq, audioCtx.currentTime);
                
                // ADSR envelope
                const now = audioCtx.currentTime;
                gainNode.gain.setValueAtTime(0, now);
                gainNode.gain.linearRampToValueAtTime(volume, now + attack);
                gainNode.gain.linearRampToValueAtTime(volume * sustain, now + attack + decay);
                gainNode.gain.setValueAtTime(volume * sustain, now + duration - release);
                gainNode.gain.linearRampToValueAtTime(0, now + duration);
                
                oscillator.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                
                // Stagger multiple frequencies slightly for arpeggio effect
                oscillator.start(now + index * 0.05);
                oscillator.stop(now + duration + 0.1);
            }});
        }} catch (e) {{
            console.log('Audio playback error:', e);
        }}
    }})();
    </script>
    """
    
    st.components.v1.html(js_code, height=0)


def get_audio_js_for_sound(effect: SoundEffect) -> str:
    """
    Get JavaScript code for a sound effect.
    
    Useful for embedding sounds in custom components.
    
    Args:
        effect: The sound effect
    
    Returns:
        JavaScript code string
    """
    audio_manager = get_audio_manager()
    sound_data = audio_manager.get_sound_data(effect)
    
    if not sound_data:
        return ""
    
    import json
    
    return f"""
    (function() {{
        try {{
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const masterVolume = {sound_data.get('master_volume', 0.7)};
            const volume = {sound_data.get('volume', 1.0)} * masterVolume;
            const duration = {sound_data.get('duration', 0.2)};
            const waveform = '{sound_data.get('waveform', 'sine')}';
            const frequencies = {json.dumps(sound_data.get('frequencies', [440]))};
            const attack = {sound_data.get('attack', 0.01)};
            const decay = {sound_data.get('decay', 0.1)};
            const sustain = {sound_data.get('sustain', 0.5)};
            const release = {sound_data.get('release', 0.1)};
            
            frequencies.forEach((freq, index) => {{
                const oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                
                oscillator.type = waveform;
                oscillator.frequency.setValueAtTime(freq, audioCtx.currentTime);
                
                const now = audioCtx.currentTime;
                gainNode.gain.setValueAtTime(0, now);
                gainNode.gain.linearRampToValueAtTime(volume, now + attack);
                gainNode.gain.linearRampToValueAtTime(volume * sustain, now + attack + decay);
                gainNode.gain.setValueAtTime(volume * sustain, now + duration - release);
                gainNode.gain.linearRampToValueAtTime(0, now + duration);
                
                oscillator.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                
                oscillator.start(now + index * 0.05);
                oscillator.stop(now + duration + 0.1);
            }});
        }} catch (e) {{
            console.log('Audio playback error:', e);
        }}
    }})();
    """


__all__ = [
    "render_audio_settings",
    "render_audio_toggle",
    "render_volume_slider",
    "play_sound",
    "get_audio_js_for_sound",
]