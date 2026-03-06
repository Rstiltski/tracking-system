"""
Trial Tests for Phase 7.2 Achievement System Enhancement

Tests the new achievement notification and sharing components.
Run with: python -m pytest tests/test_phase_7_2_achievements.py -v
"""

import pytest
from datetime import datetime


class TestAchievementNotifications:
    """Tests for achievement notification functions."""
    
    def test_show_achievement_unlocked_import(self):
        """Test that show_achievement_unlocked can be imported."""
        from tracking_app.components.achievement_notifications import show_achievement_unlocked
        assert callable(show_achievement_unlocked)
    
    def test_show_level_up_import(self):
        """Test that show_level_up can be imported."""
        from tracking_app.components.achievement_notifications import show_level_up
        assert callable(show_level_up)
    
    def test_show_streak_milestone_import(self):
        """Test that show_streak_milestone can be imported."""
        from tracking_app.components.achievement_notifications import show_streak_milestone
        assert callable(show_streak_milestone)


class TestAchievementSharing:
    """Tests for achievement sharing functions."""
    
    def test_generate_achievement_share_text(self):
        """Test generating shareable text for an achievement."""
        from tracking_app.components.achievement_sharing import generate_achievement_share_text
        
        achievement = {
            'id': 'test_achievement',
            'name': 'Test Achievement',
            'description': 'A test achievement for testing',
            'tier': 'gold',
            'xp_reward': 100,
        }
        
        result = generate_achievement_share_text(
            achievement=achievement,
            user_level=5,
            user_xp=500
        )
        
        assert 'Test Achievement' in result
        assert '+100 XP' in result
        assert 'Level 5' in result
        assert 'GOLD' in result
    
    def test_export_achievements_text(self):
        """Test exporting all achievements as text."""
        from tracking_app.components.achievement_sharing import export_achievements_text
        
        achievements = [
            {'id': 'ach1', 'name': 'First Steps', 'tier': 'bronze', 'xp_reward': 50},
            {'id': 'ach2', 'name': 'Getting Better', 'tier': 'silver', 'xp_reward': 100},
            {'id': 'ach3', 'name': 'Expert', 'tier': 'gold', 'xp_reward': 200},
        ]
        
        result = export_achievements_text(
            unlocked_achievements=achievements,
            user_level=10,
            user_xp=1000
        )
        
        assert 'Level: 10' in result
        assert 'Total XP: 1,000' in result
        assert 'First Steps' in result
        assert 'Getting Better' in result
        assert 'Expert' in result
    
    def test_generate_progress_share_text(self):
        """Test generating progress share text."""
        from tracking_app.components.achievement_sharing import generate_progress_share_text
        
        progress_data = {
            'habits_completed': 5,
            'current_streak': 14,
            'weekly_score': 85.5,
            'level': 7,
            'xp': 750,
            'achievements_count': 12,
        }
        
        result = generate_progress_share_text(progress_data)
        
        assert '5' in result
        assert '14' in result
        assert 'Level:' in result or 'Level' in result
        assert 'PROGRESS REPORT' in result


class TestAchievementConstants:
    """Tests for achievement constants."""
    
    def test_tier_colors_exist(self):
        """Test that tier colors are defined."""
        from tracking_app.pages.achievements.constants import TIER_COLORS
        
        assert 'bronze' in TIER_COLORS
        assert 'silver' in TIER_COLORS
        assert 'gold' in TIER_COLORS
        assert 'platinum' in TIER_COLORS
        assert 'diamond' in TIER_COLORS
    
    def test_tier_emojis_exist(self):
        """Test that tier emojis are defined."""
        from tracking_app.pages.achievements.constants import TIER_EMOJIS
        
        assert 'bronze' in TIER_EMOJIS
        assert 'silver' in TIER_EMOJIS
        assert 'gold' in TIER_EMOJIS
        assert 'platinum' in TIER_EMOJIS
        assert 'diamond' in TIER_EMOJIS
    
    def test_default_achievements_count(self):
        """Test that default achievements exist."""
        from tracking_app.pages.achievements.constants import DEFAULT_ACHIEVEMENTS
        
        assert len(DEFAULT_ACHIEVEMENTS) >= 25  # Should have 29 achievements


class TestAchievementModels:
    """Tests for achievement model definitions."""
    
    def test_achievement_tier_enum(self):
        """Test that AchievementTier enum exists."""
        from brain.models.achievement import AchievementTier
        
        assert AchievementTier.BRONZE.value == 'bronze'
        assert AchievementTier.SILVER.value == 'silver'
        assert AchievementTier.GOLD.value == 'gold'
        assert AchievementTier.PLATINUM.value == 'platinum'
        assert AchievementTier.DIAMOND.value == 'diamond'
    
    def test_default_achievements_exist(self):
        """Test that default achievements are defined."""
        from brain.models.achievement import DEFAULT_ACHIEVEMENTS
        
        achievement_ids = [a.id for a in DEFAULT_ACHIEVEMENTS]
        
        # Check for some of the new achievements
        assert any('unbreakable' in aid for aid in achievement_ids)
        assert any('variety' in aid for aid in achievement_ids)
        assert any('dawn_patrol' in aid for aid in achievement_ids)
    
    def test_hidden_achievements_exist(self):
        """Test that hidden achievements are defined."""
        from brain.models.achievement import DEFAULT_ACHIEVEMENTS
        
        hidden = [a for a in DEFAULT_ACHIEVEMENTS if a.is_hidden]
        assert len(hidden) >= 2  # Should have at least 2 hidden achievements
    
    def test_achievement_count(self):
        """Test that we have enough achievements."""
        from brain.models.achievement import DEFAULT_ACHIEVEMENTS
        
        # Should have at least 25 achievements (original + new)
        assert len(DEFAULT_ACHIEVEMENTS) >= 25


if __name__ == '__main__':
    pytest.main([__file__, '-v'])