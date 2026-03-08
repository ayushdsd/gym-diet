"""
Tests for gamification API routes.

Tests the gamification profile endpoint that provides user stats summary.

References Requirements: 11.4, 11.5
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.models import User, Gym, Badge, UserBadge
from app.api.routes.gamification import get_gamification_profile


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.db.base import Base
    
    # Create in-memory database
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
    db_session.refresh(gym)
    return gym


@pytest.fixture
def test_user(db_session: Session, test_gym: Gym):
    """Create a test user with gamification data"""
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        role="member",
        gym_id=test_gym.id,
        total_xp=2500,  # Level 5
        current_streak=8,
        streak_freeze_count=1,
        highest_streak=15,
        onboarding_completed=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def seed_badges(db_session: Session):
    """Seed badge data"""
    badges = [
        Badge(
            name="First Steps",
            description="Logged your first meal",
            tier="bronze",
            icon="🍽️",
            unlock_condition="meal_count >= 1",
            created_at=datetime.utcnow()
        ),
        Badge(
            name="Week Warrior",
            description="Maintained a 7-day streak",
            tier="silver",
            icon="🔥",
            unlock_condition="streak >= 7",
            created_at=datetime.utcnow()
        ),
        Badge(
            name="Level 10",
            description="Reached level 10",
            tier="silver",
            icon="⭐",
            unlock_condition="level >= 10",
            created_at=datetime.utcnow()
        ),
    ]
    for badge in badges:
        db_session.add(badge)
    db_session.commit()
    return badges


class TestGamificationProfile:
    """Test GET /gamification/profile endpoint"""
    
    def test_get_profile_basic_stats(self, db_session: Session, test_user: User, seed_badges):
        """Test that profile returns correct basic stats"""
        result = get_gamification_profile(db=db_session, user=test_user)
        
        assert result["user_id"] == test_user.id
        assert result["total_xp"] == 2500
        assert result["current_level"] == 5
        assert result["current_streak"] == 8
        assert result["highest_streak"] == 15
        assert result["streak_freeze_count"] == 1
    
    def test_get_profile_level_calculations(self, db_session: Session, test_user: User, seed_badges):
        """Test that level and XP calculations are correct"""
        result = get_gamification_profile(db=db_session, user=test_user)
        
        # Level 5 requires 2500 XP (5^2 * 100)
        # Level 6 requires 3600 XP (6^2 * 100)
        # So XP to next level should be 3600 - 2500 = 1100
        assert result["current_level"] == 5
        assert result["xp_to_next_level"] == 1100
    
    def test_get_profile_badge_counts(self, db_session: Session, test_user: User, seed_badges):
        """Test that badge counts are correct"""
        # Unlock one badge for the user
        user_badge = UserBadge(
            user_id=test_user.id,
            badge_id=seed_badges[0].id,
            unlocked_at=datetime.utcnow()
        )
        db_session.add(user_badge)
        db_session.commit()
        
        result = get_gamification_profile(db=db_session, user=test_user)
        
        assert result["badges_unlocked_count"] == 1
        assert result["total_badges"] == 3
    
    def test_get_profile_level_progress_percentage(self, db_session: Session, test_user: User, seed_badges):
        """Test that level progress percentage is calculated correctly"""
        result = get_gamification_profile(db=db_session, user=test_user)
        
        # User has 2500 XP (exactly at level 5 threshold)
        # Level 5 threshold: 2500 XP
        # Level 6 threshold: 3600 XP
        # Progress in level: 2500 - 2500 = 0
        # XP for level: 3600 - 2500 = 1100
        # Percentage: 0 / 1100 * 100 = 0%
        assert result["level_progress_percentage"] == 0.0
    
    def test_get_profile_with_progress(self, db_session: Session, test_gym: Gym, seed_badges):
        """Test level progress percentage with partial progress"""
        # Create user with 2800 XP (300 XP into level 5)
        user = User(
            email="progress@example.com",
            hashed_password="hashed",
            role="member",
            gym_id=test_gym.id,
            total_xp=2800,
            current_streak=5,
            streak_freeze_count=0,
            highest_streak=5,
            onboarding_completed=True,
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()
        
        result = get_gamification_profile(db=db_session, user=user)
        
        # Level 5 threshold: 2500 XP
        # Level 6 threshold: 3600 XP
        # Progress in level: 2800 - 2500 = 300
        # XP for level: 3600 - 2500 = 1100
        # Percentage: 300 / 1100 * 100 = 27.3%
        assert result["current_level"] == 5
        assert result["xp_to_next_level"] == 800
        assert result["level_progress_percentage"] == pytest.approx(27.3, rel=0.1)
    
    def test_get_profile_no_badges_unlocked(self, db_session: Session, test_user: User, seed_badges):
        """Test profile when user has no badges unlocked"""
        result = get_gamification_profile(db=db_session, user=test_user)
        
        assert result["badges_unlocked_count"] == 0
        assert result["total_badges"] == 3
    
    def test_get_profile_level_one_user(self, db_session: Session, test_gym: Gym, seed_badges):
        """Test profile for a new user at level 1"""
        user = User(
            email="newuser@example.com",
            hashed_password="hashed",
            role="member",
            gym_id=test_gym.id,
            total_xp=0,
            current_streak=0,
            streak_freeze_count=0,
            highest_streak=0,
            onboarding_completed=True,
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()
        
        result = get_gamification_profile(db=db_session, user=user)
        
        assert result["current_level"] == 1
        assert result["total_xp"] == 0
        assert result["xp_to_next_level"] == 400  # Level 2 requires 400 XP
        assert result["current_streak"] == 0
        assert result["highest_streak"] == 0
        assert result["streak_freeze_count"] == 0


class TestGetBadges:
    """Test GET /gamification/badges endpoint"""
    
    def test_get_badges_all_locked(self, db_session: Session, test_user: User, seed_badges):
        """Test getting badges when none are unlocked"""
        from app.api.routes.gamification import get_badges
        
        result = get_badges(db=db_session, user=test_user)
        
        assert "badges" in result
        assert len(result["badges"]) == 3
        
        # All badges should be locked
        for badge in result["badges"]:
            assert badge["unlocked"] is False
            assert badge["unlocked_at"] is None
            assert "id" in badge
            assert "name" in badge
            assert "description" in badge
            assert "tier" in badge
            assert "icon" in badge
    
    def test_get_badges_some_unlocked(self, db_session: Session, test_user: User, seed_badges):
        """Test getting badges when some are unlocked"""
        from app.api.routes.gamification import get_badges
        
        # Unlock first two badges
        unlock_time = datetime.utcnow()
        user_badge1 = UserBadge(
            user_id=test_user.id,
            badge_id=seed_badges[0].id,
            unlocked_at=unlock_time
        )
        user_badge2 = UserBadge(
            user_id=test_user.id,
            badge_id=seed_badges[1].id,
            unlocked_at=unlock_time
        )
        db_session.add(user_badge1)
        db_session.add(user_badge2)
        db_session.commit()
        
        result = get_badges(db=db_session, user=test_user)
        
        assert len(result["badges"]) == 3
        
        # First two should be unlocked
        unlocked_count = sum(1 for b in result["badges"] if b["unlocked"])
        assert unlocked_count == 2
        
        # Check that unlocked badges have timestamps
        for badge in result["badges"]:
            if badge["unlocked"]:
                assert badge["unlocked_at"] is not None
                assert isinstance(badge["unlocked_at"], str)  # ISO format string
            else:
                assert badge["unlocked_at"] is None
    
    def test_get_badges_ordered_by_tier(self, db_session: Session, test_user: User):
        """Test that badges are ordered by tier then by id"""
        from app.api.routes.gamification import get_badges
        
        # Create badges in mixed order
        badges = [
            Badge(
                name="Gold Badge 1",
                description="A gold badge",
                tier="gold",
                icon="🏆",
                unlock_condition="level >= 50",
                created_at=datetime.utcnow()
            ),
            Badge(
                name="Bronze Badge 1",
                description="A bronze badge",
                tier="bronze",
                icon="🥉",
                unlock_condition="meal_count >= 1",
                created_at=datetime.utcnow()
            ),
            Badge(
                name="Silver Badge 1",
                description="A silver badge",
                tier="silver",
                icon="🥈",
                unlock_condition="streak >= 7",
                created_at=datetime.utcnow()
            ),
            Badge(
                name="Bronze Badge 2",
                description="Another bronze badge",
                tier="bronze",
                icon="🍽️",
                unlock_condition="meal_count >= 10",
                created_at=datetime.utcnow()
            ),
        ]
        for badge in badges:
            db_session.add(badge)
        db_session.commit()
        
        result = get_badges(db=db_session, user=test_user)
        
        # Should be ordered: bronze, bronze, silver, gold
        assert result["badges"][0]["tier"] == "bronze"
        assert result["badges"][1]["tier"] == "bronze"
        assert result["badges"][2]["tier"] == "silver"
        assert result["badges"][3]["tier"] == "gold"
    
    def test_get_badges_includes_all_fields(self, db_session: Session, test_user: User, seed_badges):
        """Test that all required fields are present in response"""
        from app.api.routes.gamification import get_badges
        
        result = get_badges(db=db_session, user=test_user)
        
        required_fields = ["id", "name", "description", "tier", "icon", "unlocked", "unlocked_at"]
        
        for badge in result["badges"]:
            for field in required_fields:
                assert field in badge, f"Missing field: {field}"
    
    def test_get_badges_empty_database(self, db_session: Session, test_user: User):
        """Test getting badges when no badges exist in database"""
        from app.api.routes.gamification import get_badges
        
        result = get_badges(db=db_session, user=test_user)
        
        assert "badges" in result
        assert len(result["badges"]) == 0
    
    def test_get_badges_user_isolation(self, db_session: Session, test_gym: Gym, seed_badges):
        """Test that users only see their own unlocked badges"""
        from app.api.routes.gamification import get_badges
        
        # Create two users
        user1 = User(
            email="user1@example.com",
            hashed_password="hashed",
            role="member",
            gym_id=test_gym.id,
            total_xp=100,
            current_streak=0,
            streak_freeze_count=0,
            highest_streak=0,
            onboarding_completed=True,
            created_at=datetime.utcnow()
        )
        user2 = User(
            email="user2@example.com",
            hashed_password="hashed",
            role="member",
            gym_id=test_gym.id,
            total_xp=200,
            current_streak=0,
            streak_freeze_count=0,
            highest_streak=0,
            onboarding_completed=True,
            created_at=datetime.utcnow()
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        
        # Unlock badge for user1 only
        user_badge = UserBadge(
            user_id=user1.id,
            badge_id=seed_badges[0].id,
            unlocked_at=datetime.utcnow()
        )
        db_session.add(user_badge)
        db_session.commit()
        
        # Get badges for user1
        result1 = get_badges(db=db_session, user=user1)
        unlocked_count1 = sum(1 for b in result1["badges"] if b["unlocked"])
        assert unlocked_count1 == 1
        
        # Get badges for user2
        result2 = get_badges(db=db_session, user=user2)
        unlocked_count2 = sum(1 for b in result2["badges"] if b["unlocked"])
        assert unlocked_count2 == 0


class TestGetXPHistory:
    """Test GET /gamification/xp-history endpoint"""
    
    def test_get_xp_history_empty(self, db_session: Session, test_user: User):
        """Test XP history when user has no XP logs"""
        from app.api.routes.gamification import get_xp_history
        
        result = get_xp_history(days=30, db=db_session, user=test_user)
        
        assert "history" in result
        assert len(result["history"]) == 0

    
    def test_get_xp_history_single_day(self, db_session: Session, test_user: User):
        """Test XP history with logs from a single day"""
        from app.api.routes.gamification import get_xp_history
        from app.models.models import XPLog
        
        # Create XP logs for today
        now = datetime.utcnow()
        logs = [
            XPLog(
                user_id=test_user.id,
                gym_id=test_user.gym_id,
                delta=10,
                action_type="meal_logged",
                reason="Logged breakfast",
                created_at=now
            ),
            XPLog(
                user_id=test_user.id,
                gym_id=test_user.gym_id,
                delta=15,
                action_type="macro_goal",
                reason="Completed protein goal",
                created_at=now
            ),
        ]
        for log in logs:
            db_session.add(log)
        db_session.commit()
        
        result = get_xp_history(days=30, db=db_session, user=test_user)
        
        assert len(result["history"]) == 1
        day_data = result["history"][0]
        assert day_data["date"] == now.date().isoformat()
        assert day_data["total_xp"] == 25
        assert len(day_data["transactions"]) == 2

    
    def test_get_xp_history_multiple_days(self, db_session: Session, test_user: User):
        """Test XP history with logs from multiple days"""
        from app.api.routes.gamification import get_xp_history
        from app.models.models import XPLog
        from datetime import timedelta
        
        now = datetime.utcnow()
        
        # Create logs for 3 different days
        logs = [
            # Today
            XPLog(
                user_id=test_user.id,
                gym_id=test_user.gym_id,
                delta=10,
                action_type="meal_logged",
                reason="Today's meal",
                created_at=now
            ),
            # Yesterday
            XPLog(
                user_id=test_user.id,
                gym_id=test_user.gym_id,
                delta=20,
                action_type="daily_goal",
                reason="Yesterday's goal",
                created_at=now - timedelta(days=1)
            ),
            # 2 days ago
            XPLog(
                user_id=test_user.id,
                gym_id=test_user.gym_id,
                delta=30,
                action_type="meal_logged",
                reason="2 days ago meal",
                created_at=now - timedelta(days=2)
            ),
        ]
        for log in logs:
            db_session.add(log)
        db_session.commit()
        
        result = get_xp_history(days=30, db=db_session, user=test_user)
        
        assert len(result["history"]) == 3
        # Should be ordered by date descending (most recent first)
        assert result["history"][0]["date"] == now.date().isoformat()
        assert result["history"][1]["date"] == (now - timedelta(days=1)).date().isoformat()
        assert result["history"][2]["date"] == (now - timedelta(days=2)).date().isoformat()

    
    def test_get_xp_history_respects_days_parameter(self, db_session: Session, test_user: User):
        """Test that days parameter limits the date range"""
        from app.api.routes.gamification import get_xp_history
        from app.models.models import XPLog
        from datetime import timedelta
        
        now = datetime.utcnow()
        
        # Create logs for 40 days ago (outside default 30 day range)
        old_log = XPLog(
            user_id=test_user.id,
            gym_id=test_user.gym_id,
            delta=100,
            action_type="meal_logged",
            reason="Old meal",
            created_at=now - timedelta(days=40)
        )
        recent_log = XPLog(
            user_id=test_user.id,
            gym_id=test_user.gym_id,
            delta=50,
            action_type="meal_logged",
            reason="Recent meal",
            created_at=now - timedelta(days=5)
        )
        db_session.add(old_log)
        db_session.add(recent_log)
        db_session.commit()
        
        # Query with default 30 days
        result_30 = get_xp_history(days=30, db=db_session, user=test_user)
        assert len(result_30["history"]) == 1  # Only recent log
        
        # Query with 60 days
        result_60 = get_xp_history(days=60, db=db_session, user=test_user)
        assert len(result_60["history"]) == 2  # Both logs

    
    def test_get_xp_history_transaction_details(self, db_session: Session, test_user: User):
        """Test that transaction details are included correctly"""
        from app.api.routes.gamification import get_xp_history
        from app.models.models import XPLog
        
        now = datetime.utcnow()
        log = XPLog(
            user_id=test_user.id,
            gym_id=test_user.gym_id,
            delta=25,
            action_type="macro_goal",
            reason="Completed carbs goal",
            created_at=now
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)
        
        result = get_xp_history(days=30, db=db_session, user=test_user)
        
        transaction = result["history"][0]["transactions"][0]
        assert transaction["id"] == log.id
        assert transaction["delta"] == 25
        assert transaction["action_type"] == "macro_goal"
        assert transaction["reason"] == "Completed carbs goal"
        assert "created_at" in transaction

    
    def test_get_xp_history_aggregates_same_day(self, db_session: Session, test_user: User):
        """Test that multiple transactions on same day are aggregated"""
        from app.api.routes.gamification import get_xp_history
        from app.models.models import XPLog
        from datetime import timedelta
        
        # Use current time minus 1 day to ensure it's within the 30-day window
        now = datetime.utcnow()
        base_time = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Create multiple logs on the same day at different times
        logs = [
            XPLog(
                user_id=test_user.id,
                gym_id=test_user.gym_id,
                delta=10,
                action_type="meal_logged",
                reason="Breakfast",
                created_at=base_time + timedelta(hours=8)
            ),
            XPLog(
                user_id=test_user.id,
                gym_id=test_user.gym_id,
                delta=10,
                action_type="meal_logged",
                reason="Lunch",
                created_at=base_time + timedelta(hours=12)
            ),
            XPLog(
                user_id=test_user.id,
                gym_id=test_user.gym_id,
                delta=50,
                action_type="daily_goal",
                reason="Completed daily goal",
                created_at=base_time + timedelta(hours=20)
            ),
        ]
        for log in logs:
            db_session.add(log)
        db_session.commit()
        
        result = get_xp_history(days=30, db=db_session, user=test_user)
        
        assert len(result["history"]) == 1
        day_data = result["history"][0]
        assert day_data["total_xp"] == 70  # 10 + 10 + 50
        assert len(day_data["transactions"]) == 3

    
    def test_get_xp_history_user_isolation(self, db_session: Session, test_gym: Gym):
        """Test that users only see their own XP history"""
        from app.api.routes.gamification import get_xp_history
        from app.models.models import XPLog
        
        # Create two users
        user1 = User(
            email="user1@example.com",
            hashed_password="hashed",
            role="member",
            gym_id=test_gym.id,
            total_xp=100,
            current_streak=0,
            streak_freeze_count=0,
            highest_streak=0,
            onboarding_completed=True,
            created_at=datetime.utcnow()
        )
        user2 = User(
            email="user2@example.com",
            hashed_password="hashed",
            role="member",
            gym_id=test_gym.id,
            total_xp=200,
            current_streak=0,
            streak_freeze_count=0,
            highest_streak=0,
            onboarding_completed=True,
            created_at=datetime.utcnow()
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        
        # Create XP logs for both users
        now = datetime.utcnow()
        log1 = XPLog(
            user_id=user1.id,
            gym_id=test_gym.id,
            delta=50,
            action_type="meal_logged",
            reason="User 1 meal",
            created_at=now
        )
        log2 = XPLog(
            user_id=user2.id,
            gym_id=test_gym.id,
            delta=75,
            action_type="meal_logged",
            reason="User 2 meal",
            created_at=now
        )
        db_session.add(log1)
        db_session.add(log2)
        db_session.commit()
        
        # Get history for user1
        result1 = get_xp_history(days=30, db=db_session, user=user1)
        assert len(result1["history"]) == 1
        assert result1["history"][0]["total_xp"] == 50
        
        # Get history for user2
        result2 = get_xp_history(days=30, db=db_session, user=user2)
        assert len(result2["history"]) == 1
        assert result2["history"][0]["total_xp"] == 75
