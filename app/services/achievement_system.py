"""
Achievement System Service

Manages achievement badges including unlock conditions, badge tracking,
and preventing duplicate unlocks. Badges are awarded based on user stats
like meal count, streak, level, and daily goal completion.

Includes retry logic for failed badge unlocks (Requirement 15.4).

References Requirements: 5.1, 5.2, 5.3, 5.4, 5.6, 15.4
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import logging

from app.models.models import Badge, UserBadge, User, MealLog, XPLog
from app.services.level_system import calculate_level


# Configure logging
logger = logging.getLogger(__name__)


# Badge definitions with unlock conditions
BADGE_DEFINITIONS = {
    "first_meal": {
        "name": "First Steps",
        "description": "Logged your first meal",
        "tier": "bronze",
        "icon": "🍽️",
        "condition": lambda db, user, context: context.get("meal_count", 0) >= 1
    },
    "consistent_logger": {
        "name": "Consistent Logger",
        "description": "Logged meals 7 days in a row",
        "tier": "silver",
        "icon": "📝",
        "condition": lambda db, user, context: user.current_streak >= 7
    },
    "macro_master": {
        "name": "Macro Master",
        "description": "Hit daily goal 10 times",
        "tier": "silver",
        "icon": "🎯",
        "condition": lambda db, user, context: _count_daily_goals_completed(db, user) >= 10
    },
    "week_warrior": {
        "name": "Week Warrior",
        "description": "Maintained a 7-day streak",
        "tier": "silver",
        "icon": "🔥",
        "condition": lambda db, user, context: user.current_streak >= 7
    },
    "month_champion": {
        "name": "Month Champion",
        "description": "Maintained a 30-day streak",
        "tier": "gold",
        "icon": "🏆",
        "condition": lambda db, user, context: user.current_streak >= 30
    },
    "century_club": {
        "name": "Century Club",
        "description": "Maintained a 100-day streak",
        "tier": "gold",
        "icon": "💯",
        "condition": lambda db, user, context: user.current_streak >= 100
    },
    "level_10": {
        "name": "Level 10",
        "description": "Reached level 10",
        "tier": "silver",
        "icon": "⭐",
        "condition": lambda db, user, context: calculate_level(user.total_xp) >= 10
    },
    "level_20": {
        "name": "Level 20",
        "description": "Reached level 20",
        "tier": "gold",
        "icon": "🌟",
        "condition": lambda db, user, context: calculate_level(user.total_xp) >= 20
    },
    "level_50": {
        "name": "Level 50",
        "description": "Reached level 50",
        "tier": "gold",
        "icon": "👑",
        "condition": lambda db, user, context: calculate_level(user.total_xp) >= 50
    }
}


def _count_daily_goals_completed(db: Session, user: User) -> int:
    """
    Count how many times the user has completed their daily goal.
    Daily goal completion is tracked via XP logs with action_type='daily_goal'.
    """
    count = db.query(func.count(XPLog.id)).filter(
        XPLog.user_id == user.id,
        XPLog.action_type == "daily_goal"
    ).scalar()
    return count or 0


def _get_meal_count(db: Session, user: User) -> int:
    """Get total number of meals logged by the user."""
    count = db.query(func.count(MealLog.id)).filter(
        MealLog.user_id == user.id
    ).scalar()
    return count or 0


def check_badge_unlocks(db: Session, user: User, context: dict) -> list[Badge]:
    """
    Check all badge conditions and return newly unlocked badges.
    
    Includes retry logic for previously failed badge unlocks (Requirement 15.4).
    
    Args:
        db: Database session
        user: User model instance
        context: Event context with additional data like meal_count, new_level, etc.
        
    Returns:
        List of newly unlocked Badge instances
        
    Examples:
        >>> context = {"meal_count": 1}
        >>> badges = check_badge_unlocks(db, user, context)
        >>> # Returns [first_meal_badge] if not already unlocked
    """
    newly_unlocked = []
    
    # Add meal_count to context if not provided
    if "meal_count" not in context:
        context["meal_count"] = _get_meal_count(db, user)
    
    # Check each badge definition
    for badge_key, badge_def in BADGE_DEFINITIONS.items():
        # Get the badge from database by name
        badge = db.query(Badge).filter(Badge.name == badge_def["name"]).first()
        
        if not badge:
            # Badge doesn't exist in database yet, skip
            logger.warning(f"Badge '{badge_def['name']}' not found in database")
            continue
        
        # Check if user already has this badge
        if is_badge_unlocked(db, user.id, badge.id):
            continue
        
        # Check if condition is met
        try:
            if badge_def["condition"](db, user, context):
                # Try to unlock the badge with retry logic (Requirement 15.4)
                user_badge = unlock_badge_with_retry(db, user.id, badge.id, max_retries=3)
                if user_badge:
                    newly_unlocked.append(badge)
                else:
                    logger.error(
                        f"Failed to unlock badge {badge_def['name']} for user {user.id} "
                        f"after retries. Will retry on next qualifying action."
                    )
        except Exception as e:
            # Log error but continue checking other badges
            logger.error(f"Error checking badge {badge_def['name']} for user {user.id}: {e}")
            continue
    
    return newly_unlocked


def unlock_badge(db: Session, user_id: int, badge_id: int) -> UserBadge | None:
    """
    Create UserBadge entry to unlock a badge for a user.
    
    Args:
        db: Database session
        user_id: User ID
        badge_id: Badge ID
        
    Returns:
        UserBadge instance if successfully unlocked, None if already unlocked
        
    Examples:
        >>> user_badge = unlock_badge(db, 1, 5)
        >>> # Returns UserBadge instance or None if duplicate
    """
    try:
        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge_id,
            unlocked_at=datetime.utcnow()
        )
        db.add(user_badge)
        db.flush()  # Flush to catch unique constraint violations
        return user_badge
    except IntegrityError:
        # Badge already unlocked (unique constraint violation)
        db.rollback()
        return None


def unlock_badge_with_retry(
    db: Session, 
    user_id: int, 
    badge_id: int, 
    max_retries: int = 3
) -> UserBadge | None:
    """
    Create UserBadge entry with retry logic for transient failures.
    
    Implements retry logic for badge unlock failures (Requirement 15.4).
    Retries on database errors but not on integrity errors (duplicate unlocks).
    
    Args:
        db: Database session
        user_id: User ID
        badge_id: Badge ID
        max_retries: Maximum number of retry attempts
        
    Returns:
        UserBadge instance if successfully unlocked, None if failed or already unlocked
        
    Examples:
        >>> user_badge = unlock_badge_with_retry(db, 1, 5, max_retries=3)
        >>> # Returns UserBadge instance or None
    """
    for attempt in range(max_retries):
        try:
            user_badge = UserBadge(
                user_id=user_id,
                badge_id=badge_id,
                unlocked_at=datetime.utcnow()
            )
            db.add(user_badge)
            db.flush()  # Flush to catch unique constraint violations
            logger.info(f"Badge {badge_id} unlocked for user {user_id}")
            return user_badge
        except IntegrityError:
            # Badge already unlocked (unique constraint violation)
            # Don't retry for this error
            db.rollback()
            logger.debug(f"Badge {badge_id} already unlocked for user {user_id}")
            return None
        except Exception as e:
            # Other database errors - retry
            db.rollback()
            logger.warning(
                f"Badge unlock attempt {attempt + 1}/{max_retries} failed "
                f"for user {user_id}, badge {badge_id}: {e}"
            )
            if attempt < max_retries - 1:
                # Wait before retrying (exponential backoff)
                import time
                time.sleep(0.1 * (2 ** attempt))
            else:
                # Final attempt failed
                logger.error(
                    f"Failed to unlock badge {badge_id} for user {user_id} "
                    f"after {max_retries} attempts"
                )
                return None
    
    return None


def get_user_badges(db: Session, user_id: int) -> list[dict]:
    """
    Get all badges with unlock status for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of badge dictionaries with unlock status
        
    Examples:
        >>> badges = get_user_badges(db, 1)
        >>> # Returns list of all badges with unlocked=True/False
    """
    # Get all badges
    all_badges = db.query(Badge).all()
    
    # Get user's unlocked badges
    unlocked_badge_ids = set(
        db.query(UserBadge.badge_id)
        .filter(UserBadge.user_id == user_id)
        .all()
    )
    unlocked_badge_ids = {badge_id for (badge_id,) in unlocked_badge_ids}
    
    # Get unlock timestamps
    unlock_times = {}
    user_badges = db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
    for ub in user_badges:
        unlock_times[ub.badge_id] = ub.unlocked_at
    
    # Build result list
    result = []
    for badge in all_badges:
        result.append({
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "tier": badge.tier,
            "icon": badge.icon,
            "unlocked": badge.id in unlocked_badge_ids,
            "unlocked_at": unlock_times.get(badge.id)
        })
    
    return result


def is_badge_unlocked(db: Session, user_id: int, badge_id: int) -> bool:
    """
    Check if a user has unlocked a specific badge.
    
    Args:
        db: Database session
        user_id: User ID
        badge_id: Badge ID
        
    Returns:
        True if badge is unlocked, False otherwise
        
    Examples:
        >>> is_unlocked = is_badge_unlocked(db, 1, 5)
        >>> # Returns True or False
    """
    exists = db.query(UserBadge).filter(
        UserBadge.user_id == user_id,
        UserBadge.badge_id == badge_id
    ).first()
    return exists is not None
