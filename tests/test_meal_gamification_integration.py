"""
Integration tests for meal logging with gamification.

Tests the complete flow of logging a meal and receiving gamification rewards.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.models import User, Gym, MealLog, Badge
from app.api.routes.meals import create_meal
from app.schemas.meal import MealCreate


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
        onboarding_completed=True,
        target_protein=150,
        target_carbs=250,
        target_fats=60,
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
    ]
    for badge in badges:
        db_session.add(badge)
    db_session.commit()


class TestMealLoggingWithGamification:
    """Test meal logging with gamification integration"""
    
    def test_log_first_meal_awards_xp_and_badge(self, db_session: Session, test_user: User, seed_badges):
        """Test that logging first meal awards XP and unlocks First Steps badge"""
        # Create meal payload
        meal_data = MealCreate(
            description="Chicken and rice",
            protein=45,
            carbs=60,
            fats=15,
            calories=540
        )
        
        # Log meal
        result = create_meal(meal_data, db_session, test_user)
        
        # Verify meal was created
        assert result["meal"]["description"] == "Chicken and rice"
        assert result["meal"]["protein"] == 45
        
        # Verify gamification data
        gamification = result["gamification"]
        assert gamification["xp_awarded"] == 10  # Base meal XP
        assert gamification["new_total_xp"] == 10
        assert gamification["current_streak"] == 1
        assert len(gamification["badges_unlocked"]) == 1
        assert gamification["badges_unlocked"][0]["name"] == "First Steps"
    
    def test_log_meal_completing_daily_goal_awards_bonus_xp(self, db_session: Session, test_user: User, seed_badges):
        """Test that completing daily goal awards bonus XP"""
        # Log meals to complete daily goal (within 10% of targets)
        # Target: protein=150, carbs=250, fats=60
        
        # First meal
        meal1 = MealCreate(
            description="Breakfast",
            protein=50,
            carbs=80,
            fats=20,
            calories=680
        )
        result1 = create_meal(meal1, db_session, test_user)
        
        # Second meal
        meal2 = MealCreate(
            description="Lunch",
            protein=50,
            carbs=85,
            fats=20,
            calories=700
        )
        result2 = create_meal(meal2, db_session, test_user)
        
        # Third meal - completes daily goal
        meal3 = MealCreate(
            description="Dinner",
            protein=50,
            carbs=85,
            fats=20,
            calories=700
        )
        result3 = create_meal(meal3, db_session, test_user)
        
        # Verify gamification data from third meal
        gamification = result3["gamification"]
        
        # Should have meal XP (10) + macro goal XP (15*3=45) + daily goal XP (50) = 105
        assert gamification["xp_awarded"] >= 10  # At least meal XP
        assert "daily_goal_completed" in gamification["xp_breakdown"]
        assert gamification["xp_breakdown"]["daily_goal_completed"] == True
    
    def test_level_up_awards_streak_freeze_at_milestone(self, db_session: Session, test_user: User, seed_badges):
        """Test that reaching milestone level awards streak freeze"""
        # Set user to just below level 5 threshold
        # Level 5 requires 2500 XP (5^2 * 100)
        test_user.total_xp = 2490
        db_session.commit()
        
        # Log meal to push over level 5
        meal = MealCreate(
            description="Milestone meal",
            protein=45,
            carbs=60,
            fats=15,
            calories=540
        )
        result = create_meal(meal, db_session, test_user)
        
        # Verify level up occurred
        gamification = result["gamification"]
        assert gamification["level_up"] == True
        assert gamification["new_level"] == 5
        assert gamification["streak_freeze_earned"] == True
        
        # Verify user has streak freeze
        db_session.refresh(test_user)
        assert test_user.streak_freeze_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
