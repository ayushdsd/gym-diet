"""
Unit tests for AchievementSystem service

Tests verify badge unlock conditions, duplicate prevention, badge tracking,
and unlock status checking as specified in Requirements 18.7.

**Validates: Requirements 18.7**
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.base import Base
from app.models.models import User, Gym, Badge, UserBadge, MealLog, XPLog
from app.services.achievement_system import (
    check_badge_unlocks,
    unlock_badge,
    get_user_badges,
    is_badge_unlocked,
    BADGE_DEFINITIONS
)


# Test database setup
@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def test_gym(db_session: Session):
    """Create a test gym"""
    gym = Gym(
        name="Test Gym",
        location="New York",
        created_at=datetime.utcnow()
    )
    db_session.add(gym)
    db_session.commit()
    return gym


@pytest.fixture
def test_user(db_session: Session, test_gym: Gym):
    """Create a test user"""
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        role="member",
        gym_id=test_gym.id,
        total_xp=0,
        current_streak=0,
        streak_freeze_count=0,
        highest_streak=0,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_badges(db_session: Session):
    """Create test badges in database"""
    badges = []
    for badge_key, badge_def in BADGE_DEFINITIONS.items():
        badge = Badge(
            name=badge_def["name"],
            description=badge_def["description"],
            tier=badge_def["tier"],
            icon=badge_def["icon"],
            unlock_condition=badge_key,
            created_at=datetime.utcnow()
        )
        db_session.add(badge)
        badges.append(badge)
    
    db_session.commit()
    return badges


class TestUnlockBadge:
    """Test badge unlocking functionality"""
    
    def test_unlock_badge_creates_user_badge_entry(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that unlocking a badge creates a UserBadge entry"""
        badge = test_badges[0]
        
        user_badge = unlock_badge(db_session, test_user.id, badge.id)
        
        assert user_badge is not None
        assert user_badge.user_id == test_user.id
        assert user_badge.badge_id == badge.id
        assert user_badge.unlocked_at is not None
    
    def test_unlock_badge_prevents_duplicates(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that unlocking the same badge twice returns None (duplicate prevention)"""
        badge = test_badges[0]
        
        # First unlock should succeed
        user_badge1 = unlock_badge(db_session, test_user.id, badge.id)
        assert user_badge1 is not None
        
        # Second unlock should return None (duplicate)
        user_badge2 = unlock_badge(db_session, test_user.id, badge.id)
        assert user_badge2 is None
    
    def test_unlock_badge_sets_timestamp(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that unlocking a badge sets the unlocked_at timestamp"""
        badge = test_badges[0]
        before = datetime.utcnow()
        
        user_badge = unlock_badge(db_session, test_user.id, badge.id)
        
        after = datetime.utcnow()
        assert user_badge.unlocked_at >= before
        assert user_badge.unlocked_at <= after


class TestIsBadgeUnlocked:
    """Test badge unlock status checking"""
    
    def test_is_badge_unlocked_returns_false_for_locked_badge(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that is_badge_unlocked returns False for a badge that hasn't been unlocked"""
        badge = test_badges[0]
        
        is_unlocked = is_badge_unlocked(db_session, test_user.id, badge.id)
        
        assert is_unlocked is False
    
    def test_is_badge_unlocked_returns_true_for_unlocked_badge(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that is_badge_unlocked returns True for an unlocked badge"""
        badge = test_badges[0]
        unlock_badge(db_session, test_user.id, badge.id)
        
        is_unlocked = is_badge_unlocked(db_session, test_user.id, badge.id)
        
        assert is_unlocked is True
    
    def test_is_badge_unlocked_is_user_specific(self, db_session: Session, test_gym: Gym, test_badges: list[Badge]):
        """Test that badge unlock status is specific to each user"""
        # Create two users
        user1 = User(
            email="user1@example.com",
            hashed_password="hashed",
            role="member",
            gym_id=test_gym.id,
            total_xp=0,
            current_streak=0,
            created_at=datetime.utcnow()
        )
        user2 = User(
            email="user2@example.com",
            hashed_password="hashed",
            role="member",
            gym_id=test_gym.id,
            total_xp=0,
            current_streak=0,
            created_at=datetime.utcnow()
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        badge = test_badges[0]
        
        # Unlock badge for user1 only
        unlock_badge(db_session, user1.id, badge.id)
        
        # Check that only user1 has the badge
        assert is_badge_unlocked(db_session, user1.id, badge.id) is True
        assert is_badge_unlocked(db_session, user2.id, badge.id) is False


class TestGetUserBadges:
    """Test retrieving all badges with unlock status"""
    
    def test_get_user_badges_returns_all_badges(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that get_user_badges returns all badges"""
        badges = get_user_badges(db_session, test_user.id)
        
        assert len(badges) == len(test_badges)
    
    def test_get_user_badges_includes_unlock_status(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that get_user_badges includes unlock status for each badge"""
        # Unlock first badge
        unlock_badge(db_session, test_user.id, test_badges[0].id)
        
        badges = get_user_badges(db_session, test_user.id)
        
        # Find the unlocked badge in results
        unlocked_badge = next(b for b in badges if b["id"] == test_badges[0].id)
        assert unlocked_badge["unlocked"] is True
        assert unlocked_badge["unlocked_at"] is not None
        
        # Check that other badges are locked
        locked_badges = [b for b in badges if b["id"] != test_badges[0].id]
        for badge in locked_badges:
            assert badge["unlocked"] is False
            assert badge["unlocked_at"] is None
    
    def test_get_user_badges_includes_badge_details(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that get_user_badges includes all badge details"""
        badges = get_user_badges(db_session, test_user.id)
        
        for badge in badges:
            assert "id" in badge
            assert "name" in badge
            assert "description" in badge
            assert "tier" in badge
            assert "icon" in badge
            assert "unlocked" in badge
            assert "unlocked_at" in badge


class TestCheckBadgeUnlocks:
    """Test badge unlock condition checking"""
    
    def test_check_badge_unlocks_first_meal(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that first meal badge is unlocked when meal_count >= 1"""
        # Create a meal log
        meal = MealLog(
            user_id=test_user.id,
            gym_id=test_user.gym_id,
            description="Test meal",
            protein=30,
            carbs=40,
            fats=10,
            calories=350,
            created_at=datetime.utcnow()
        )
        db_session.add(meal)
        db_session.commit()
        
        context = {"meal_count": 1}
        newly_unlocked = check_badge_unlocks(db_session, test_user, context)
        
        # Should unlock "First Steps" badge
        assert len(newly_unlocked) > 0
        assert any(badge.name == "First Steps" for badge in newly_unlocked)
    
    def test_check_badge_unlocks_streak_badges(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that streak badges are unlocked at correct thresholds"""
        # Set user streak to 7
        test_user.current_streak = 7
        db_session.commit()
        
        context = {}
        newly_unlocked = check_badge_unlocks(db_session, test_user, context)
        
        # Should unlock "Week Warrior" and "Consistent Logger" badges
        unlocked_names = [badge.name for badge in newly_unlocked]
        assert "Week Warrior" in unlocked_names or "Consistent Logger" in unlocked_names
    
    def test_check_badge_unlocks_level_badges(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that level badges are unlocked at correct levels"""
        # Set user XP to level 10 (10000 XP)
        test_user.total_xp = 10000
        db_session.commit()
        
        context = {}
        newly_unlocked = check_badge_unlocks(db_session, test_user, context)
        
        # Should unlock "Level 10" badge
        assert any(badge.name == "Level 10" for badge in newly_unlocked)
    
    def test_check_badge_unlocks_skips_already_unlocked(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that check_badge_unlocks skips badges that are already unlocked"""
        # Create a meal and unlock first meal badge
        meal = MealLog(
            user_id=test_user.id,
            gym_id=test_user.gym_id,
            description="Test meal",
            protein=30,
            carbs=40,
            fats=10,
            calories=350,
            created_at=datetime.utcnow()
        )
        db_session.add(meal)
        db_session.commit()
        
        # First check should unlock the badge
        context = {"meal_count": 1}
        newly_unlocked1 = check_badge_unlocks(db_session, test_user, context)
        assert len(newly_unlocked1) > 0
        
        # Second check should not unlock it again
        newly_unlocked2 = check_badge_unlocks(db_session, test_user, context)
        first_steps_badges = [b for b in newly_unlocked2 if b.name == "First Steps"]
        assert len(first_steps_badges) == 0
    
    def test_check_badge_unlocks_returns_empty_list_when_no_conditions_met(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that check_badge_unlocks returns empty list when no conditions are met"""
        # User has no XP, no streak, no meals
        context = {"meal_count": 0}
        newly_unlocked = check_badge_unlocks(db_session, test_user, context)
        
        assert len(newly_unlocked) == 0
    
    def test_check_badge_unlocks_macro_master(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that Macro Master badge is unlocked after 10 daily goals"""
        # Create 10 daily_goal XP logs
        for i in range(10):
            xp_log = XPLog(
                user_id=test_user.id,
                gym_id=test_user.gym_id,
                delta=50,
                action_type="daily_goal",
                reason=f"Daily goal {i+1}",
                created_at=datetime.utcnow()
            )
            db_session.add(xp_log)
        db_session.commit()
        
        context = {}
        newly_unlocked = check_badge_unlocks(db_session, test_user, context)
        
        # Should unlock "Macro Master" badge
        assert any(badge.name == "Macro Master" for badge in newly_unlocked)


class TestBadgeDefinitions:
    """Test badge definition structure"""
    
    def test_all_badge_definitions_have_required_fields(self):
        """Test that all badge definitions have required fields"""
        required_fields = ["name", "description", "tier", "icon", "condition"]
        
        for badge_key, badge_def in BADGE_DEFINITIONS.items():
            for field in required_fields:
                assert field in badge_def, f"Badge {badge_key} missing field {field}"
    
    def test_badge_tiers_are_valid(self):
        """Test that all badge tiers are bronze, silver, or gold"""
        valid_tiers = ["bronze", "silver", "gold"]
        
        for badge_key, badge_def in BADGE_DEFINITIONS.items():
            assert badge_def["tier"] in valid_tiers, f"Badge {badge_key} has invalid tier {badge_def['tier']}"
    
    def test_badge_conditions_are_callable(self):
        """Test that all badge conditions are callable functions"""
        for badge_key, badge_def in BADGE_DEFINITIONS.items():
            assert callable(badge_def["condition"]), f"Badge {badge_key} condition is not callable"


class TestAchievementSystemIntegration:
    """Integration tests for achievement system components"""
    
    def test_full_badge_unlock_flow(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test complete flow from checking conditions to unlocking badge"""
        # Create a meal
        meal = MealLog(
            user_id=test_user.id,
            gym_id=test_user.gym_id,
            description="Test meal",
            protein=30,
            carbs=40,
            fats=10,
            calories=350,
            created_at=datetime.utcnow()
        )
        db_session.add(meal)
        db_session.commit()
        
        # Check badge unlocks
        context = {"meal_count": 1}
        newly_unlocked = check_badge_unlocks(db_session, test_user, context)
        
        # Verify badge was unlocked
        assert len(newly_unlocked) > 0
        first_steps = next((b for b in newly_unlocked if b.name == "First Steps"), None)
        assert first_steps is not None
        
        # Verify badge appears in user's badge list
        user_badges = get_user_badges(db_session, test_user.id)
        first_steps_status = next(b for b in user_badges if b["name"] == "First Steps")
        assert first_steps_status["unlocked"] is True
        
        # Verify is_badge_unlocked returns True
        assert is_badge_unlocked(db_session, test_user.id, first_steps.id) is True
    
    def test_multiple_badges_unlock_simultaneously(self, db_session: Session, test_user: User, test_badges: list[Badge]):
        """Test that multiple badges can be unlocked in a single check"""
        # Set up conditions for multiple badges
        test_user.current_streak = 7
        test_user.total_xp = 10000
        db_session.commit()
        
        # Create a meal
        meal = MealLog(
            user_id=test_user.id,
            gym_id=test_user.gym_id,
            description="Test meal",
            protein=30,
            carbs=40,
            fats=10,
            calories=350,
            created_at=datetime.utcnow()
        )
        db_session.add(meal)
        db_session.commit()
        
        context = {"meal_count": 1}
        newly_unlocked = check_badge_unlocks(db_session, test_user, context)
        
        # Should unlock multiple badges
        assert len(newly_unlocked) >= 2
