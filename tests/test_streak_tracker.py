"""
Unit tests for StreakTracker service

Tests verify streak increment logic, streak reset on missed days, freeze consumption,
highest_streak tracking, timezone-aware day boundaries, and first meal marking.

**Validates: Requirements 18.3, 18.4, 18.8**
"""

import pytest
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.services.streak_tracker import (
    mark_day_active,
    check_streak_continuation,
    check_for_streak_break,
    consume_streak_freeze,
    StreakUpdateResult,
    StreakBreakResult,
)
from app.models.models import User, StreakHistory


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def mock_user():
    """Create a mock user with gym location."""
    user = Mock(spec=User)
    user.id = 1
    user.current_streak = 0
    user.highest_streak = 0
    user.streak_freeze_count = 0
    user.gym = Mock()
    user.gym.location = "New York"
    return user


class TestMarkDayActive:
    """Test mark_day_active function for streak increment logic."""
    
    def test_marks_first_day_active_starts_streak_at_one(self, mock_db, mock_user):
        """Test that marking the first day active starts streak at 1."""
        # User has no previous streak history
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # User logs meal on Jan 15, 2024 at 2 PM EST (7 PM UTC)
        timestamp = datetime(2024, 1, 15, 19, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        result = mark_day_active(mock_db, mock_user, timestamp)
        
        assert result.current_streak == 1
        assert result.streak_incremented is True
        assert mock_user.current_streak == 1
        assert mock_user.highest_streak == 1
    
    def test_consecutive_day_increments_streak(self, mock_db, mock_user):
        """Test that logging on consecutive days increments the streak."""
        mock_user.current_streak = 5
        mock_user.highest_streak = 5
        
        # Mock today's entry doesn't exist yet
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # User logs meal on Jan 15
        timestamp = datetime(2024, 1, 15, 19, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        with patch('app.services.streak_tracker.check_streak_continuation', return_value=True):
            result = mark_day_active(mock_db, mock_user, timestamp)
        
        assert result.current_streak == 6
        assert result.streak_incremented is True
        assert mock_user.current_streak == 6
        assert mock_user.highest_streak == 6
    
    def test_already_marked_day_does_not_increment_streak(self, mock_db, mock_user):
        """Test that marking an already active day doesn't increment streak."""
        mock_user.current_streak = 5
        mock_user.highest_streak = 5
        
        # Mock today's entry as already active
        today_entry = Mock(spec=StreakHistory)
        today_entry.is_active = True
        
        mock_db.query.return_value.filter.return_value.first.return_value = today_entry
        
        timestamp = datetime(2024, 1, 15, 19, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        result = mark_day_active(mock_db, mock_user, timestamp)
        
        assert result.current_streak == 5
        assert result.streak_incremented is False
        assert mock_user.current_streak == 5
    
    def test_updates_highest_streak_when_current_exceeds_it(self, mock_db, mock_user):
        """Test that highest_streak is updated when current_streak exceeds it."""
        mock_user.current_streak = 9
        mock_user.highest_streak = 9
        
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        timestamp = datetime(2024, 1, 15, 19, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        with patch('app.services.streak_tracker.check_streak_continuation', return_value=True):
            result = mark_day_active(mock_db, mock_user, timestamp)
        
        assert result.current_streak == 10
        assert result.highest_streak == 10
        assert mock_user.highest_streak == 10
    
    def test_does_not_update_highest_streak_when_below_it(self, mock_db, mock_user):
        """Test that highest_streak is not updated when current is below it."""
        mock_user.current_streak = 5
        mock_user.highest_streak = 20
        
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        timestamp = datetime(2024, 1, 15, 19, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        with patch('app.services.streak_tracker.check_streak_continuation', return_value=True):
            result = mark_day_active(mock_db, mock_user, timestamp)
        
        assert result.current_streak == 6
        assert result.highest_streak == 20
        assert mock_user.highest_streak == 20
    
    def test_timezone_aware_day_boundary_before_midnight(self, mock_db, mock_user):
        """Test that logging before local midnight counts for that day."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # 11:30 PM EST on Jan 14 = 4:30 AM UTC on Jan 15
        timestamp = datetime(2024, 1, 15, 4, 30, 0, tzinfo=ZoneInfo("UTC"))
        
        with patch('app.services.streak_tracker.get_user_date', return_value=date(2024, 1, 14)):
            result = mark_day_active(mock_db, mock_user, timestamp)
        
        # Should create entry for Jan 14, not Jan 15
        assert result.streak_incremented is True
    
    def test_timezone_aware_day_boundary_after_midnight(self, mock_db, mock_user):
        """Test that logging after local midnight counts for the new day."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # 12:30 AM EST on Jan 15 = 5:30 AM UTC on Jan 15
        timestamp = datetime(2024, 1, 15, 5, 30, 0, tzinfo=ZoneInfo("UTC"))
        
        with patch('app.services.streak_tracker.get_user_date', return_value=date(2024, 1, 15)):
            result = mark_day_active(mock_db, mock_user, timestamp)
        
        # Should create entry for Jan 15
        assert result.streak_incremented is True
    
    def test_gap_in_days_resets_streak_to_one(self, mock_db, mock_user):
        """Test that a gap in days resets the streak to 1."""
        mock_user.current_streak = 10
        mock_user.highest_streak = 15
        
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        timestamp = datetime(2024, 1, 15, 19, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        # Yesterday was not active
        with patch('app.services.streak_tracker.check_streak_continuation', return_value=False):
            result = mark_day_active(mock_db, mock_user, timestamp)
        
        assert result.current_streak == 1
        assert result.streak_incremented is True
        assert mock_user.current_streak == 1
        # Highest streak should remain unchanged
        assert mock_user.highest_streak == 15


class TestCheckStreakContinuation:
    """Test check_streak_continuation function."""
    
    def test_returns_true_when_yesterday_was_active(self, mock_db, mock_user):
        """Test that streak continues when yesterday was active."""
        yesterday_entry = Mock(spec=StreakHistory)
        yesterday_entry.is_active = True
        yesterday_entry.freeze_used = False
        
        mock_db.query.return_value.filter.return_value.first.return_value = yesterday_entry
        
        current_date = date(2024, 1, 15)
        result = check_streak_continuation(mock_db, mock_user, current_date)
        
        assert result is True
    
    def test_returns_true_when_yesterday_used_freeze(self, mock_db, mock_user):
        """Test that streak continues when yesterday used a freeze."""
        yesterday_entry = Mock(spec=StreakHistory)
        yesterday_entry.is_active = False
        yesterday_entry.freeze_used = True
        
        mock_db.query.return_value.filter.return_value.first.return_value = yesterday_entry
        
        current_date = date(2024, 1, 15)
        result = check_streak_continuation(mock_db, mock_user, current_date)
        
        assert result is True
    
    def test_returns_false_when_yesterday_has_no_entry(self, mock_db, mock_user):
        """Test that streak doesn't continue when yesterday has no entry."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        current_date = date(2024, 1, 15)
        result = check_streak_continuation(mock_db, mock_user, current_date)
        
        assert result is False
    
    def test_returns_false_when_yesterday_was_inactive_no_freeze(self, mock_db, mock_user):
        """Test that streak doesn't continue when yesterday was inactive with no freeze."""
        yesterday_entry = Mock(spec=StreakHistory)
        yesterday_entry.is_active = False
        yesterday_entry.freeze_used = False
        
        mock_db.query.return_value.filter.return_value.first.return_value = yesterday_entry
        
        current_date = date(2024, 1, 15)
        result = check_streak_continuation(mock_db, mock_user, current_date)
        
        assert result is False


class TestCheckForStreakBreak:
    """Test check_for_streak_break function for missed day handling."""
    
    def test_no_break_when_yesterday_was_active(self, mock_db, mock_user):
        """Test that no break occurs when yesterday was active."""
        mock_user.current_streak = 7
        
        yesterday_entry = Mock(spec=StreakHistory)
        yesterday_entry.is_active = True
        yesterday_entry.freeze_used = False
        
        mock_db.query.return_value.filter.return_value.first.return_value = yesterday_entry
        
        result = check_for_streak_break(mock_db, mock_user)
        
        assert result.streak_broken is False
        assert result.freeze_consumed is False
        assert result.current_streak == 7
    
    def test_no_break_when_yesterday_used_freeze(self, mock_db, mock_user):
        """Test that no break occurs when yesterday already used a freeze."""
        mock_user.current_streak = 7
        
        yesterday_entry = Mock(spec=StreakHistory)
        yesterday_entry.is_active = False
        yesterday_entry.freeze_used = True
        
        mock_db.query.return_value.filter.return_value.first.return_value = yesterday_entry
        
        result = check_for_streak_break(mock_db, mock_user)
        
        assert result.streak_broken is False
        assert result.freeze_consumed is False
        assert result.current_streak == 7
    
    def test_consumes_freeze_when_available_and_day_missed(self, mock_db, mock_user):
        """Test that freeze is consumed when user misses a day and has freezes."""
        mock_user.current_streak = 7
        mock_user.streak_freeze_count = 2
        
        # Yesterday has no entry (missed day)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with patch('app.services.streak_tracker.consume_streak_freeze', return_value=True) as mock_consume:
            result = check_for_streak_break(mock_db, mock_user)
        
        assert result.streak_broken is False
        assert result.freeze_consumed is True
        assert result.current_streak == 7
        mock_consume.assert_called_once()
    
    def test_resets_streak_when_no_freeze_available(self, mock_db, mock_user):
        """Test that streak resets to 0 when no freeze is available."""
        mock_user.current_streak = 7
        mock_user.streak_freeze_count = 0
        
        # Yesterday has no entry (missed day)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = check_for_streak_break(mock_db, mock_user)
        
        assert result.streak_broken is True
        assert result.freeze_consumed is False
        assert result.current_streak == 0
        assert mock_user.current_streak == 0


class TestConsumeStreakFreeze:
    """Test consume_streak_freeze function."""
    
    def test_consumes_freeze_successfully(self, mock_db, mock_user):
        """Test that freeze is consumed and count decremented."""
        mock_user.streak_freeze_count = 3
        
        # No existing entry for the date
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        target_date = date(2024, 1, 14)
        result = consume_streak_freeze(mock_db, mock_user, target_date)
        
        assert result is True
        assert mock_user.streak_freeze_count == 2
    
    def test_returns_false_when_no_freezes_available(self, mock_db, mock_user):
        """Test that freeze consumption fails when count is 0."""
        mock_user.streak_freeze_count = 0
        
        target_date = date(2024, 1, 14)
        result = consume_streak_freeze(mock_db, mock_user, target_date)
        
        assert result is False
        assert mock_user.streak_freeze_count == 0
    
    def test_idempotent_when_freeze_already_used(self, mock_db, mock_user):
        """Test that consuming freeze for same date is idempotent."""
        mock_user.streak_freeze_count = 3
        
        # Existing entry with freeze already used
        existing_entry = Mock(spec=StreakHistory)
        existing_entry.freeze_used = True
        
        mock_db.query.return_value.filter.return_value.first.return_value = existing_entry
        
        target_date = date(2024, 1, 14)
        result = consume_streak_freeze(mock_db, mock_user, target_date)
        
        assert result is True
        # Count should not be decremented again
        assert mock_user.streak_freeze_count == 3
    
    def test_updates_existing_entry_when_present(self, mock_db, mock_user):
        """Test that existing entry is updated when freeze is consumed."""
        mock_user.streak_freeze_count = 2
        
        # Existing entry without freeze
        existing_entry = Mock(spec=StreakHistory)
        existing_entry.freeze_used = False
        
        mock_db.query.return_value.filter.return_value.first.return_value = existing_entry
        
        target_date = date(2024, 1, 14)
        result = consume_streak_freeze(mock_db, mock_user, target_date)
        
        assert result is True
        assert existing_entry.freeze_used is True
        assert mock_user.streak_freeze_count == 1
    
    def test_creates_new_entry_when_none_exists(self, mock_db, mock_user):
        """Test that new StreakHistory entry is created when none exists."""
        mock_user.streak_freeze_count = 1
        
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        target_date = date(2024, 1, 14)
        result = consume_streak_freeze(mock_db, mock_user, target_date)
        
        assert result is True
        assert mock_user.streak_freeze_count == 0
        # Verify new entry was added
        mock_db.add.assert_called_once()


class TestStreakTrackerIntegration:
    """Integration tests for StreakTracker components working together."""
    
    def test_seven_day_streak_progression(self, mock_db, mock_user):
        """Test building a 7-day streak from scratch."""
        mock_user.current_streak = 0
        mock_user.highest_streak = 0
        
        # Simulate 7 consecutive days
        for day in range(1, 8):
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            timestamp = datetime(2024, 1, day, 19, 0, 0, tzinfo=ZoneInfo("UTC"))
            
            # Mock continuation check based on day
            with patch('app.services.streak_tracker.check_streak_continuation', return_value=(day > 1)):
                result = mark_day_active(mock_db, mock_user, timestamp)
            
            assert result.current_streak == day
            assert result.highest_streak == day
    
    def test_streak_break_and_recovery_with_freeze(self, mock_db, mock_user):
        """Test that streak is preserved when freeze is used."""
        mock_user.current_streak = 10
        mock_user.highest_streak = 10
        mock_user.streak_freeze_count = 1
        
        # User misses a day
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with patch('app.services.streak_tracker.consume_streak_freeze', return_value=True):
            result = check_for_streak_break(mock_db, mock_user)
        
        assert result.streak_broken is False
        assert result.freeze_consumed is True
        assert result.current_streak == 10
    
    def test_streak_break_without_freeze(self, mock_db, mock_user):
        """Test that streak resets when no freeze is available."""
        mock_user.current_streak = 10
        mock_user.highest_streak = 15
        mock_user.streak_freeze_count = 0
        
        # User misses a day
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = check_for_streak_break(mock_db, mock_user)
        
        assert result.streak_broken is True
        assert result.current_streak == 0
        # Highest streak should remain unchanged
        assert mock_user.highest_streak == 15
    
    def test_multiple_meals_same_day_only_counts_once(self, mock_db, mock_user):
        """Test that logging multiple meals on the same day doesn't increment streak multiple times."""
        mock_user.current_streak = 5
        mock_user.highest_streak = 5
        
        # First meal of the day
        mock_db.query.return_value.filter.return_value.first.return_value = None
        timestamp1 = datetime(2024, 1, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        with patch('app.services.streak_tracker.check_streak_continuation', return_value=True):
            result1 = mark_day_active(mock_db, mock_user, timestamp1)
        
        assert result1.current_streak == 6
        assert result1.streak_incremented is True
        
        # Second meal of the same day
        today_entry = Mock(spec=StreakHistory)
        today_entry.is_active = True
        mock_db.query.return_value.filter.return_value.first.return_value = today_entry
        
        timestamp2 = datetime(2024, 1, 15, 18, 0, 0, tzinfo=ZoneInfo("UTC"))
        result2 = mark_day_active(mock_db, mock_user, timestamp2)
        
        assert result2.current_streak == 6
        assert result2.streak_incremented is False
    
    def test_highest_streak_tracking_across_multiple_streaks(self, mock_db, mock_user):
        """Test that highest_streak tracks the maximum across multiple streak periods."""
        mock_user.current_streak = 0
        mock_user.highest_streak = 20
        
        # Build a new streak of 15 days
        for day in range(1, 16):
            mock_db.query.return_value.filter.return_value.first.return_value = None
            timestamp = datetime(2024, 1, day, 19, 0, 0, tzinfo=ZoneInfo("UTC"))
            
            with patch('app.services.streak_tracker.check_streak_continuation', return_value=(day > 1)):
                result = mark_day_active(mock_db, mock_user, timestamp)
        
        # Current streak is 15, but highest should still be 20
        assert result.current_streak == 15
        assert result.highest_streak == 20
        
        # Continue to 25 days
        for day in range(16, 26):
            mock_db.query.return_value.filter.return_value.first.return_value = None
            timestamp = datetime(2024, 1, day, 19, 0, 0, tzinfo=ZoneInfo("UTC"))
            
            with patch('app.services.streak_tracker.check_streak_continuation', return_value=True):
                result = mark_day_active(mock_db, mock_user, timestamp)
        
        # Now highest should be updated to 25
        assert result.current_streak == 25
        assert result.highest_streak == 25
