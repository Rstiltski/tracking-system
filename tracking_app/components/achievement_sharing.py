"""
Achievement Sharing Component

Phase 7.2: Achievement sharing functionality for text export.
Provides shareable achievement summaries and progress reports.

Usage:
    from tracking_app.components.achievement_sharing import (
        generate_achievement_share_text,
        export_achievements_text,
        render_share_button,
    )
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional


def generate_achievement_share_text(
    achievement: Dict[str, Any],
    user_level: int = 1,
    user_xp: int = 0,
    include_timestamp: bool = True
) -> str:
    """
    Generate shareable text for a single achievement.
    
    Args:
        achievement: Achievement dictionary
        user_level: Current user level
        user_xp: Current user XP
        include_timestamp: Whether to include timestamp
    
    Returns:
        Formatted shareable text
    """
    tier_emojis = {
        "bronze": "🥉",
        "silver": "🥈",
        "gold": "🥇",
        "platinum": "💎",
        "diamond": "💠",
    }
    
    tier = achievement.get('tier', 'bronze')
    tier_emoji = tier_emojis.get(tier, "🥉")
    
    lines = [
        "🏆 ACHIEVEMENT UNLOCKED! 🏆",
        "",
        f"{tier_emoji} {tier.upper()}: {achievement.get('name', 'Unknown')}",
        "",
        f"📝 {achievement.get('description', '')}",
        "",
        f"💰 +{achievement.get('xp_reward', 50)} XP",
        "",
        f"📊 Level {user_level} | {user_xp:,} XP",
    ]
    
    if include_timestamp:
        lines.extend([
            "",
            f"📅 Unlocked: {datetime.now().strftime('%B %d, %Y')}",
        ])
    
    lines.extend([
        "",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "Veryfyn - Personal Growth Tracker",
        "#Veryfyn #AchievementUnlocked",
    ])
    
    return "\n".join(lines)


def export_achievements_text(
    unlocked_achievements: List[Dict[str, Any]],
    user_level: int = 1,
    user_xp: int = 0,
    stats: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate full achievement export text.
    
    Args:
        unlocked_achievements: List of unlocked achievements
        user_level: Current user level
        user_xp: Current user XP
        stats: Optional stats dictionary
    
    Returns:
        Formatted export text
    """
    tier_emojis = {
        "bronze": "🥉",
        "silver": "🥈",
        "gold": "🥇",
        "platinum": "💎",
        "diamond": "💠",
    }
    
    lines = [
        "╔══════════════════════════════════════╗",
        "║      VERYFYN ACHIEVEMENT REPORT      ║",
        "╚══════════════════════════════════════╝",
        "",
        f"📊 Level: {user_level}",
        f"💰 Total XP: {user_xp:,}",
        f"🏅 Achievements Unlocked: {len(unlocked_achievements)}",
    ]
    
    if stats:
        lines.extend([
            "",
            "─── STATISTICS ───",
        ])
        if 'total_habits' in stats:
            lines.append(f"📋 Total Habits Tracked: {stats['total_habits']}")
        if 'best_streak' in stats:
            lines.append(f"🔥 Best Streak: {stats['best_streak']} days")
        if 'completion_rate' in stats:
            lines.append(f"✅ Completion Rate: {stats['completion_rate']:.1f}%")
    
    lines.extend([
        "",
        "─── ACHIEVEMENTS ───",
        "",
    ])
    
    # Group by tier
    by_tier: Dict[str, List[Dict]] = {}
    for ach in unlocked_achievements:
        tier = ach.get('tier', 'bronze')
        if tier not in by_tier:
            by_tier[tier] = []
        by_tier[tier].append(ach)
    
    # Display by tier (highest first)
    tier_order = ['diamond', 'platinum', 'gold', 'silver', 'bronze']
    
    for tier in tier_order:
        if tier in by_tier:
            emoji = tier_emojis.get(tier, "🥉")
            lines.append(f"{emoji} {tier.upper()} ({len(by_tier[tier])})")
            
            for ach in by_tier[tier]:
                lines.append(f"   ✓ {ach.get('name', 'Unknown')} (+{ach.get('xp_reward', 50)} XP)")
            
            lines.append("")
    
    lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📅 Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        "",
        "Veryfyn - Personal Growth Tracker",
        "Track habits. Achieve goals. Grow daily.",
    ])
    
    return "\n".join(lines)


def render_share_button(
    achievement: Dict[str, Any],
    user_level: int = 1,
    user_xp: int = 0,
    button_text: str = "📤 Share Achievement"
) -> None:
    """
    Render a share button for an achievement.
    
    Args:
        achievement: Achievement dictionary
        user_level: Current user level
        user_xp: Current user XP
        button_text: Button text
    """
    if st.button(button_text, key=f"share_{achievement.get('id', 'unknown')}"):
        share_text = generate_achievement_share_text(
            achievement, user_level, user_xp
        )
        
        # Show in a text area for copying
        st.text_area(
            "Copy this text to share:",
            value=share_text,
            height=200,
            key=f"share_text_{achievement.get('id', 'unknown')}"
        )
        
        st.info("📋 Select the text above and copy to share on social media!")


def render_export_button(
    unlocked_achievements: List[Dict[str, Any]],
    user_level: int = 1,
    user_xp: int = 0,
    stats: Optional[Dict[str, Any]] = None
) -> None:
    """
    Render an export button for all achievements.
    
    Args:
        unlocked_achievements: List of unlocked achievements
        user_level: Current user level
        user_xp: Current user XP
        stats: Optional stats dictionary
    """
    if st.button("📄 Export All Achievements"):
        export_text = export_achievements_text(
            unlocked_achievements, user_level, user_xp, stats
        )
        
        # Show in a text area for copying
        st.text_area(
            "Copy your achievement report:",
            value=export_text,
            height=400,
            key="export_text_area"
        )
        
        # Also provide download
        st.download_button(
            label="📥 Download as Text File",
            data=export_text,
            file_name=f"veryfyn_achievements_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )


def generate_progress_share_text(
    progress_data: Dict[str, Any]
) -> str:
    """
    Generate shareable progress summary text.
    
    Args:
        progress_data: Dictionary with progress information
    
    Returns:
        Formatted progress text
    """
    lines = [
        "📊 MY PROGRESS REPORT 📊",
        "",
    ]
    
    if 'habits_completed' in progress_data:
        lines.append(f"✅ Habits Completed Today: {progress_data['habits_completed']}")
    
    if 'current_streak' in progress_data:
        lines.append(f"🔥 Current Streak: {progress_data['current_streak']} days")
    
    if 'weekly_score' in progress_data:
        lines.append(f"📈 Weekly Score: {progress_data['weekly_score']:.1f}%")
    
    if 'level' in progress_data:
        lines.append(f"🎖️ Level: {progress_data['level']}")
    
    if 'xp' in progress_data:
        lines.append(f"💰 Total XP: {progress_data['xp']:,}")
    
    if 'achievements_count' in progress_data:
        lines.append(f"🏆 Achievements: {progress_data['achievements_count']}")
    
    lines.extend([
        "",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "Veryfyn - Personal Growth Tracker",
        "#Veryfyn #ProgressUpdate",
    ])
    
    return "\n".join(lines)


__all__ = [
    "generate_achievement_share_text",
    "export_achievements_text",
    "render_share_button",
    "render_export_button",
    "generate_progress_share_text",
]