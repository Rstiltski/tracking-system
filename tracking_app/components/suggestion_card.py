"""
Suggestion Card - Display smart habit suggestions.

Provides UI components for:
- Suggestion display with priority
- Action buttons
- Feedback collection

Usage:
    from tracking_app.components.suggestion_card import render_suggestion_card
    
    render_suggestion_card(storage, suggestion, user_id)
"""
import streamlit as st
from typing import Dict, Optional, Any, List
from brain.models.suggestion import (
    Suggestion,
    SuggestionType,
    SuggestionPriority,
)


# Type emojis
TYPE_EMOJIS = {
    SuggestionType.PATTERN: "📊",
    SuggestionType.PREDICTIVE: "🔮",
    SuggestionType.GAP: "🧩",
    SuggestionType.OPTIMIZATION: "⚡",
    SuggestionType.ENCOURAGEMENT: "🌟",
}


def render_suggestion_card(
    storage: Any,
    suggestion: Dict[str, Any],
    user_id: str = "",
    show_dismiss: bool = True
) -> None:
    """
    Render a suggestion card.

    Args:
        storage: Storage instance
        suggestion: Suggestion data dict
        user_id: User ID
        show_dismiss: Whether to show dismiss button
    """
    # Get type emoji
    suggestion_type = SuggestionType(suggestion.get("suggestion_type", "pattern"))
    emoji = TYPE_EMOJIS.get(suggestion_type, "💡")

    # Get priority color
    priority = suggestion.get("priority", "medium")
    color = {
        "high": "#F44336",
        "medium": "#FF9800",
        "low": "#4CAF50",
    }.get(priority, "#808080")

    with st.container():
        # Header with priority indicator
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(
                f"""
                <div style="
                    padding: 1rem;
                    border-radius: 0.5rem;
                    border-left: 5px solid {color};
                    background: rgba(255,255,255,0.05);
                    margin: 0.5rem 0;
                ">
                    <div style="font-size: 1.1rem; font-weight: bold;">
                        {emoji} {suggestion.get('title', 'Suggestion')}
                    </div>
                    <div style="font-size: 0.9rem; color: gray; margin: 0.5rem 0;">
                        {suggestion.get('description', '')}
                    </div>
                    <div style="font-size: 0.85rem; color: {color};">
                        💡 Action: {suggestion.get('action', '')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            if show_dismiss:
                if st.button("✕", key=f"dismiss_{suggestion.get('id', '')}", help="Dismiss"):
                    storage.dismiss_suggestion(suggestion.get('id', ''))
                    st.rerun()

        # Action buttons
        col_action1, col_action2 = st.columns(2)

        with col_action1:
            if st.button(
                "✓ Do It",
                key=f"do_{suggestion.get('id', '')}",
                type="primary",
                use_container_width=True
            ):
                storage.record_suggestion_action(suggestion.get('id', ''))
                st.success("✅ Great! Take action on this suggestion.")
                storage.dismiss_suggestion(suggestion.get('id', ''))
                st.rerun()

        with col_action2:
            if st.button(
                "👍 Helpful",
                key=f"helpful_{suggestion.get('id', '')}",
                use_container_width=True
            ):
                storage.save_suggestion_feedback({
                    "suggestion_id": suggestion.get('id', ''),
                    "user_id": user_id,
                    "helpful": True
                })
                st.success("👍 Thanks for the feedback!")
                storage.dismiss_suggestion(suggestion.get('id', ''))
                st.rerun()


def render_suggestions_section(
    storage: Any,
    user_id: str = "",
    limit: int = 3,
    key_prefix: str = ""
) -> None:
    """
    Render suggestions section.

    Args:
        storage: Storage instance
        user_id: User ID
        limit: Number of suggestions to show
        key_prefix: Prefix for unique element keys
    """
    from brain.ai.suggestion_engine import SuggestionEngine

    # Get suggestions
    engine = SuggestionEngine(storage, user_id)
    suggestions = engine.get_suggestions(limit=limit)

    if not suggestions:
        return

    st.divider()
    st.markdown("**💡 Smart Suggestions**")

    # Show suggestions
    for idx, suggestion in enumerate(suggestions):
        # Convert to dict if object
        suggestion_dict: Dict[str, Any]
        if hasattr(suggestion, 'to_dict'):
            suggestion_dict = suggestion.to_dict()
        elif isinstance(suggestion, dict):
            suggestion_dict = suggestion
        else:
            suggestion_dict = {'id': f'{idx}', 'title': str(suggestion)}
        
        # Add prefix to suggestion ID for unique keys
        suggestion_id = suggestion_dict.get('id', f'{idx}')
        suggestion_with_prefix = {
            **suggestion_dict,
            'id': f"{key_prefix}_{suggestion_id}"
        }
        render_suggestion_card(storage, suggestion_with_prefix, user_id)

    # View all button
    if len(suggestions) >= limit:
        button_key = f"{key_prefix}_view_all_suggestions" if key_prefix else "view_all_suggestions"
        if st.button("📋 View All Suggestions", key=button_key):
            st.session_state.show_all_suggestions = True


def render_all_suggestions(
    storage: Any,
    user_id: str = ""
) -> None:
    """
    Render all suggestions.

    Args:
        storage: Storage instance
        user_id: User ID
    """
    st.markdown("**📋 All Suggestions**")

    # Get all suggestions
    suggestions = storage.get_suggestions(user_id, limit=20, active_only=True)

    if not suggestions:
        st.info("No suggestions at this time")
        return

    for suggestion in suggestions:
        render_suggestion_card(storage, suggestion, user_id)


def render_suggestion_stats(
    storage: Any,
    user_id: str = ""
) -> None:
    """
    Render suggestion statistics.

    Args:
        storage: Storage instance
        user_id: User ID
    """
    # Get suggestions
    all_suggestions = storage.get_suggestions(user_id, limit=100, active_only=False)

    if not all_suggestions:
        return

    acted_upon = sum(1 for s in all_suggestions if s.get('acted_upon', False))
    dismissed = sum(1 for s in all_suggestions if s.get('dismissed', False))

    st.markdown("**📊 Suggestion Stats**")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", len(all_suggestions))
    with col2:
        st.metric("Acted Upon", acted_upon)
    with col3:
        st.metric("Dismissed", dismissed)


__all__ = [
    "render_suggestion_card",
    "render_suggestions_section",
    "render_all_suggestions",
    "render_suggestion_stats",
]
