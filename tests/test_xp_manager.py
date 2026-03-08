"""
Unit tests for XPManager service.

Tests all XP calculation functions and the award_xp orchestration logic.

**Validates: Requirements 18.1**
"""

import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session
from app.services import xp_manager
from app.models.models import User, XPLog


@pytest.fixture
def db_session():
    """Create a mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def test_user():
    """Create a mock user for testing."""
    user = Mock(spec=User)
    user.id = 1
    user.gym_id = 1
    user.total_xp = 0
    user.current_streak = 0
    return user


class TestXPCalculations:
    """Test individual XP calculation functions"""
    
    def test_calculate_xp_for_meal(self):
        """Test that meal logging awards 10 XP"""
        xp = xp_manager.calculate_xp_for_meal()
        assert xp == 10
    
    def test_calculate_macro_goal_xp_single(self):
        """Test XP for completing one macro goal"""
        xp = xp_manager.calculate_macro_goal_xp(["protein"])
        assert xp == 15
    
    def test_calculate_macro_goal_xp_multiple(self):
        """Test XP for completing multiple macro goals"""
        xp = xp_manager.calculate_macro_goal_xp(["protein", "carbs"])
        assert xp == 30
    
    def test_calculate_macro_goal_xp_all_three(self):
        """Test XP for completing all three macro goals"""
        xp = xp_manager.calculate_macro_goal_xp(["protein", "carbs", "fats"])
        assert xp == 45
    
    def test_calculate_macro_goal_xp_empty(self):
        """Test XP for completing no macro goals"""
        xp = xp_manager.calculate_macro_goal_xp([])
        assert xp == 0
    
    def test_calculate_daily_goal_xp(self):
        """Test that daily goal completion awards 50 XP"""
        xp = xp_manager.calculate_daily_goal_xp()
        assert xp == 50


class TestStreakMultipliers:
    """Test streak multiplier application"""
    
    def test_no_multiplier_below_7_days(self):
        """Test no multiplier for streaks below 7 days"""
        base_xp = 100
        
        # Test various streak lengths below 7
        assert xp_manager.apply_streak_multiplier(base_xp, 0) == 100
        assert xp_manager.apply_streak_multiplier(base_xp, 1) == 100
        assert xp_manager.apply_streak_multiplier(base_xp, 3) == 100
        assert xp_manager.apply_streak_multiplier(base_xp, 6) == 100
    
    def test_1_5x_multiplier_at_7_days(self):
        """Test 1.5x multiplier for 7-day streak"""
        base_xp = 100
        result = xp_manager.apply_streak_multiplier(base_xp, 7)
        assert result == 150
    
    def test_1_5x_multiplier_between_7_and_29_days(self):
        """Test 1.5x multiplier for streaks between 7 and 29 days"""
        base_xp = 100
        
        assert xp_manager.apply_streak_multiplier(base_xp, 7) == 150
        assert xp_manager.apply_streak_multiplier(base_xp, 15) == 150
        assert xp_manager.apply_streak_multiplier(base_xp, 29) == 150
    
    def test_2x_multiplier_at_30_days(self):
        """Test 2.0x multiplier for 30-day streak"""
        base_xp = 100
        result = xp_manager.apply_streak_multiplier(base_xp, 30)
        assert result == 200
    
    def test_2x_multiplier_above_30_days(self):
        """Test 2.0x multiplier for streaks above 30 days"""
        base_xp = 100
        
        assert xp_manager.apply_streak_multiplier(base_xp, 30) == 200
        assert xp_manager.apply_streak_multiplier(base_xp, 50) == 200
        assert xp_manager.apply_streak_multiplier(base_xp, 100) == 200
    
    def test_multiplier_rounding(self):
        """Test that multiplier results are rounded correctly"""
        # 10 * 1.5 = 15 (exact)
        assert xp_manager.apply_streak_multiplier(10, 7) == 15
        
        # 11 * 1.5 = 16.5 -> rounds to 16 (banker's rounding)
        assert xp_manager.apply_streak_multiplier(11, 7) == 16
        
        # 13 * 1.5 = 19.5 -> rounds to 20
        assert xp_manager.apply_streak_multiplier(13, 7) == 20
        
        # 15 * 1.5 = 22.5 -> rounds to 22 (banker's rounding)
        assert xp_manager.apply_streak_multiplier(15, 7) == 22


class TestXPTransactionRecording:
    """Test XP transaction recording in XPLog"""
    
    def test_record_xp_transaction_creates_log_entry(self, db_session, test_user):
        """Test that recording XP creates an XPLog entry"""
        xp_log = xp_manager.record_xp_transaction(
            db=db_session,
            user_id=test_user.id,
            gym_id=test_user.gym_id,
            delta=50,
            action_type="meal_logged",
            reason="Logged breakfast"
        )
        
        assert xp_log is not None
        assert xp_log.user_id == test_user.id
        assert xp_log.gym_id == test_user.gym_id
        assert xp_log.delta == 50
        assert xp_log.action_type == "meal_logged"
        assert xp_log.reason == "Logged breakfast"
        assert xp_log.created_at is not None
    
    def test_record_xp_transaction_calls_db_add(self, db_session, test_user):
        """Test that XP transaction calls db.add to persist"""
        xp_log = xp_manager.record_xp_transaction(
            db=db_session,
            user_id=test_user.id,
            gym_id=test_user.gym_id,
            delta=75,
            action_type="daily_goal",
            reason="Completed daily goals"
        )
        
        # Verify db.add was called with the XPLog instance
        db_session.add.assert_called_once()
        db_session.flush.assert_called_once()
    
    def test_record_multiple_transactions(self, db_session, test_user):
        """Test recording multiple XP transactions"""
        # Record first transaction
        log1 = xp_manager.record_xp_transaction(
            db=db_session,
            user_id=test_user.id,
            gym_id=test_user.gym_id,
            delta=10,
            action_type="meal_logged",
            reason="Meal 1"
        )
        
        # Record second transaction
        log2 = xp_manager.record_xp_transaction(
            db=db_session,
            user_id=test_user.id,
            gym_id=test_user.gym_id,
            delta=15,
            action_type="macro_goal",
            reason="Protein goal"
        )
        
        # Verify both logs were created with correct values
        assert log1.delta == 10
        assert log2.delta == 15
        assert log1.action_type == "meal_logged"
        assert log2.action_type == "macro_goal"


class TestAwardXPOrchestration:
    """Test the award_xp orchestration function"""
    
    def test_award_xp_for_meal_logged(self, db_session, test_user):
        """Test awarding XP for meal logging"""
        initial_xp = test_user.total_xp or 0
        
        result = xp_manager.award_xp(
            db=db_session,
            user=test_user,
            action_type="meal_logged",
            context={}
        )
        
        assert result.total_xp_awarded == 10
        assert result.base_xp == 10
        assert result.multiplier == 1.0
        assert result.breakdown["meal_logged"] == 10
        assert result.breakdown["total_xp"] == 10
        
        # Verify user's total_xp was updated
        assert test_user.total_xp == initial_xp + 10
    
    def test_award_xp_for_macro_goal(self, db_session, test_user):
        """Test awarding XP for macro goal completion"""
        initial_xp = test_user.total_xp or 0
        
        result = xp_manager.award_xp(
            db=db_session,
            user=test_user,
            action_type="macro_goal",
            context={"completed_macros": ["protein", "carbs"]}
        )
        
        assert result.total_xp_awarded == 30
        assert result.base_xp == 30
        assert result.multiplier == 1.0
        assert result.breakdown["macro_goals_completed"] == ["protein", "carbs"]
        assert result.breakdown["macro_goal_xp"] == 30
        
        # Verify user's total_xp was updated
        assert test_user.total_xp == initial_xp + 30
    
    def test_award_xp_for_daily_goal(self, db_session, test_user):
        """Test awarding XP for daily goal completion"""
        initial_xp = test_user.total_xp or 0
        
        result = xp_manager.award_xp(
            db=db_session,
            user=test_user,
            action_type="daily_goal",
            context={}
        )
        
        assert result.total_xp_awarded == 50
        assert result.base_xp == 50
        assert result.multiplier == 1.0
        assert result.breakdown["daily_goal_completed"] is True
        assert result.breakdown["daily_goal_xp"] == 50
        
        # Verify user's total_xp was updated
        assert test_user.total_xp == initial_xp + 50
    
    def test_award_xp_with_7_day_streak_multiplier(self, db_session, test_user):
        """Test XP award with 7-day streak multiplier (1.5x)"""
        test_user.current_streak = 7
        initial_xp = test_user.total_xp or 0
        
        result = xp_manager.award_xp(
            db=db_session,
            user=test_user,
            action_type="meal_logged",
            context={}
        )
        
        # 10 base XP * 1.5 = 15 XP
        assert result.base_xp == 10
        assert result.multiplier == 1.5
        assert result.total_xp_awarded == 15
        assert result.breakdown["streak_multiplier"] == 1.5
        
        # Verify user's total_xp was updated with multiplied amount
        assert test_user.total_xp == initial_xp + 15
    
    def test_award_xp_with_30_day_streak_multiplier(self, db_session, test_user):
        """Test XP award with 30-day streak multiplier (2.0x)"""
        test_user.current_streak = 30
        initial_xp = test_user.total_xp or 0
        
        result = xp_manager.award_xp(
            db=db_session,
            user=test_user,
            action_type="daily_goal",
            context={}
        )
        
        # 50 base XP * 2.0 = 100 XP
        assert result.base_xp == 50
        assert result.multiplier == 2.0
        assert result.total_xp_awarded == 100
        assert result.breakdown["streak_multiplier"] == 2.0
        
        # Verify user's total_xp was updated with multiplied amount
        assert test_user.total_xp == initial_xp + 100
    
    def test_award_xp_creates_xp_log_entry(self, db_session, test_user):
        """Test that awarding XP creates an XPLog entry"""
        xp_manager.award_xp(
            db=db_session,
            user=test_user,
            action_type="meal_logged",
            context={}
        )
        
        # Verify db.add was called (which creates the XPLog entry)
        db_session.add.assert_called()
        db_session.flush.assert_called()
    
    def test_award_xp_handles_null_total_xp(self, db_session, test_user):
        """Test that awarding XP handles users with null total_xp"""
        test_user.total_xp = None
        
        result = xp_manager.award_xp(
            db=db_session,
            user=test_user,
            action_type="meal_logged",
            context={}
        )
        
        assert result.total_xp_awarded == 10
        assert test_user.total_xp == 10


class TestMultipleSimultaneousXPAwards:
    """Test multiple simultaneous XP awards"""
    
    def test_multiple_awards_accumulate_correctly(self, db_session, test_user):
        """Test that multiple XP awards accumulate correctly"""
        initial_xp = test_user.total_xp or 0
        
        # Award XP for meal logging
        result1 = xp_manager.award_xp(
            db=db_session,
            user=test_user,
            action_type="meal_logged",
            context={}
        )
        
        # Award XP for macro goal
        result2 = xp_manager.award_xp(
            db=db_session,
            user=test_user,
            action_type="macro_goal",
            context={"completed_macros": ["protein"]}
        )
        
        # Award XP for daily goal
        result3 = xp_manager.award_xp(
            db=db_session,
            user=test_user,
            action_type="daily_goal",
            context={}
        )
        
        # Verify each award
        assert result1.total_xp_awarded == 10
        assert result2.total_xp_awarded == 15
        assert result3.total_xp_awarded == 50
        
        # Verify total accumulation
        expected_total = initial_xp + 10 + 15 + 50
        assert test_user.total_xp == expected_total
    
    def test_multiple_awards_create_separate_log_entries(self, db_session, test_user):
        """Test that multiple XP awards create separate XPLog entries"""
        # Award XP three times
        xp_manager.award_xp(db=db_session, user=test_user, action_type="meal_logged", context={})
        xp_manager.award_xp(db=db_session, user=test_user, action_type="macro_goal", context={"completed_macros": ["protein"]})
        xp_manager.award_xp(db=db_session, user=test_user, action_type="daily_goal", context={})
        
        # Verify db.add was called three times (once per XP award for the XPLog entry)
        assert db_session.add.call_count == 3
    
    def test_multiple_awards_with_streak_multiplier(self, db_session, test_user):
        """Test that streak multiplier applies to all awards in a session"""
        test_user.current_streak = 7
        initial_xp = test_user.total_xp or 0
        
        # Award XP for meal (10 * 1.5 = 15)
        result1 = xp_manager.award_xp(
            db=db_session,
            user=test_user,
            action_type="meal_logged",
            context={}
        )
        
        # Award XP for macro goal (30 * 1.5 = 45)
        result2 = xp_manager.award_xp(
            db=db_session,
            user=test_user,
            action_type="macro_goal",
            context={"completed_macros": ["protein", "carbs"]}
        )
        
        # Verify multiplier was applied to both
        assert result1.total_xp_awarded == 15
        assert result1.multiplier == 1.5
        assert result2.total_xp_awarded == 45
        assert result2.multiplier == 1.5
        
        # Verify total accumulation with multipliers
        expected_total = initial_xp + 15 + 45
        assert test_user.total_xp == expected_total



class TestXPBatching:
    """Test XP award batching functionality"""
    
    def test_batch_collects_multiple_awards(self, db_session, test_user):
        """Test that batch collects multiple XP awards within 1 second"""
        import threading
        
        # Create a batch and add multiple awards quickly
        batch = xp_manager._batch_manager.get_or_create_batch(test_user.id)
        
        batch.add_award("meal_logged", {})
        batch.add_award("macro_goal", {"completed_macros": ["protein"]})
        batch.add_award("daily_goal", {})
        
        awards = batch.get_awards()
        
        assert len(awards) == 3
        assert awards[0]["action_type"] == "meal_logged"
        assert awards[1]["action_type"] == "macro_goal"
        assert awards[2]["action_type"] == "daily_goal"
        
        # Cleanup
        xp_manager._batch_manager.remove_batch(test_user.id)
    
    def test_batch_expires_after_1_second(self, db_session, test_user):
        """Test that batch expires after 1 second window"""
        import time
        
        batch = xp_manager._batch_manager.get_or_create_batch(test_user.id)
        
        # Initially not expired
        assert not batch.is_expired()
        
        # Wait for batch window to expire
        time.sleep(1.1)
        
        # Now should be expired
        assert batch.is_expired()
        
        # Cleanup
        xp_manager._batch_manager.remove_batch(test_user.id)
    
    def test_execute_batched_awards_combines_xp(self, db_session, test_user):
        """Test that batched awards are combined correctly"""
        awards = [
            {"action_type": "meal_logged", "context": {}},
            {"action_type": "macro_goal", "context": {"completed_macros": ["protein", "carbs"]}},
            {"action_type": "daily_goal", "context": {}}
        ]
        
        initial_xp = test_user.total_xp or 0
        
        result = xp_manager._execute_batched_awards(db_session, test_user, awards)
        
        # Expected: 10 (meal) + 30 (2 macros) + 50 (daily) = 90 XP
        assert result.base_xp == 90
        assert result.total_xp_awarded == 90
        assert result.multiplier == 1.0
        assert result.breakdown["total_awards"] == 3
        assert len(result.breakdown["awards"]) == 3
        
        # Verify user's total_xp was updated
        assert test_user.total_xp == initial_xp + 90
    
    def test_execute_batched_awards_applies_multiplier(self, db_session, test_user):
        """Test that streak multiplier applies to batched awards"""
        test_user.current_streak = 7
        
        awards = [
            {"action_type": "meal_logged", "context": {}},
            {"action_type": "meal_logged", "context": {}}
        ]
        
        initial_xp = test_user.total_xp or 0
        
        result = xp_manager._execute_batched_awards(db_session, test_user, awards)
        
        # Expected: (10 + 10) * 1.5 = 30 XP
        assert result.base_xp == 20
        assert result.total_xp_awarded == 30
        assert result.multiplier == 1.5
        
        # Verify user's total_xp was updated with multiplied amount
        assert test_user.total_xp == initial_xp + 30
    
    def test_execute_batched_awards_creates_single_log_entry(self, db_session, test_user):
        """Test that batched awards create only one XPLog entry"""
        awards = [
            {"action_type": "meal_logged", "context": {}},
            {"action_type": "macro_goal", "context": {"completed_macros": ["protein"]}},
            {"action_type": "daily_goal", "context": {}}
        ]
        
        xp_manager._execute_batched_awards(db_session, test_user, awards)
        
        # Verify db.add was called only once (for the single batched XPLog entry)
        assert db_session.add.call_count == 1
        # Flush is called twice: once in record_xp_transaction, once in _execute_batched_awards
        assert db_session.flush.call_count == 2
    
    def test_batched_awards_breakdown_includes_all_awards(self, db_session, test_user):
        """Test that breakdown includes details for all batched awards"""
        awards = [
            {"action_type": "meal_logged", "context": {}},
            {"action_type": "macro_goal", "context": {"completed_macros": ["protein", "carbs"]}},
        ]
        
        result = xp_manager._execute_batched_awards(db_session, test_user, awards)
        
        assert result.breakdown["total_awards"] == 2
        assert len(result.breakdown["awards"]) == 2
        
        # Check first award
        award1 = result.breakdown["awards"][0]
        assert award1["action_type"] == "meal_logged"
        assert award1["meal_logged"] == 10
        assert award1["base_xp"] == 10
        
        # Check second award
        award2 = result.breakdown["awards"][1]
        assert award2["action_type"] == "macro_goal"
        assert award2["macro_goals_completed"] == ["protein", "carbs"]
        assert award2["macro_goal_xp"] == 30
        assert award2["base_xp"] == 30
    
    def test_batch_manager_creates_new_batch_after_expiry(self, db_session, test_user):
        """Test that batch manager creates new batch after old one expires"""
        import time
        
        # Create first batch
        batch1 = xp_manager._batch_manager.get_or_create_batch(test_user.id)
        batch1.add_award("meal_logged", {})
        
        # Wait for expiry
        time.sleep(1.1)
        
        # Get batch again - should be a new one
        batch2 = xp_manager._batch_manager.get_or_create_batch(test_user.id)
        
        # Should be different batch (new instance)
        assert batch2 is not batch1
        assert len(batch2.get_awards()) == 0  # New batch is empty
        
        # Cleanup
        xp_manager._batch_manager.remove_batch(test_user.id)
    
    def test_batch_manager_reuses_unexpired_batch(self, db_session, test_user):
        """Test that batch manager reuses batch within window"""
        # Create first batch
        batch1 = xp_manager._batch_manager.get_or_create_batch(test_user.id)
        batch1.add_award("meal_logged", {})
        
        # Get batch again immediately - should be same batch
        batch2 = xp_manager._batch_manager.get_or_create_batch(test_user.id)
        
        # Should be same batch
        assert batch2 is batch1
        assert len(batch2.get_awards()) == 1  # Contains the award from batch1
        
        # Cleanup
        xp_manager._batch_manager.remove_batch(test_user.id)
    
    def test_batched_awards_with_30_day_streak(self, db_session, test_user):
        """Test batched awards with 30-day streak multiplier"""
        test_user.current_streak = 30
        
        awards = [
            {"action_type": "meal_logged", "context": {}},
            {"action_type": "daily_goal", "context": {}}
        ]
        
        initial_xp = test_user.total_xp or 0
        
        result = xp_manager._execute_batched_awards(db_session, test_user, awards)
        
        # Expected: (10 + 50) * 2.0 = 120 XP
        assert result.base_xp == 60
        assert result.total_xp_awarded == 120
        assert result.multiplier == 2.0
        
        # Verify user's total_xp was updated
        assert test_user.total_xp == initial_xp + 120
