"""
StreakTracker Service

Handles daily streak tracking and freeze mechanics for the gamification system.
All streak calculations are timezone-aware using the user's gym location to
determine accurate day boundaries.

Always uses server time for calculations to prevent client time manipulation (Requirement 15.5).

References Requirements: 3.1, 3.2, 3.3, 3.7, 4.2, 4.3, 4.4, 15.5
"""

from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.models.models import User, StreakHistory
from app.services.timezone_utils import (
    get_user_timezone,
    get_user_date,
    get_day_boundary,
)


# Configure logging
logger = logging.getLogger(__name__)


class StreakUpdateResult:
    """Result of marking a day as active"""
    def __init__(
        self,
        current_streak: int,
        highest_streak: int,
        streak_incremented: bool,
        freeze_used: bool = False
    ):
        self.current_streak = current_streak
        self.highest_streak = highest_streak
        self.streak_incremented = streak_incremented
        self.freeze_used = freeze_used


class StreakBreakResult:
    """Result of checking for streak breaks"""
    def __init__(
        self,
        streak_broken: bool,
        freeze_consumed: bool,
        current_streak: int
    ):
        self.streak_broken = streak_broken
        self.freeze_consumed = freeze_consumed
        self.current_streak = current_streak


def mark_day_active(
    db: Session,
    user: User,
    timestamp: datetime = None
) -> StreakUpdateResult:
    """
    Mark a day as active and update the user's streak.
    
    This is called when a user logs their first meal of the day. It:
    1. Uses server time (ignores client-provided timestamp) for security (Requirement 15.5)
    2. Converts the timestamp to the user's local date
    3. Creates or updates a StreakHistory entry for that date
    4. Checks if this continues a streak from yesterday
    5. Updates current_streak and highest_streak accordingly
    
    Args:
        db: Database session
        user: User model instance (with gym relationship loaded)
        timestamp: IGNORED - server time is always used (Requirement 15.5)
        
    Returns:
        StreakUpdateResult with updated streak information
        
    References: Requirements 3.1, 3.2, 3.3, 3.7, 15.5
    """
    # ALWAYS use server time, ignore client-provided timestamp (Requirement 15.5)
    server_timestamp = datetime.utcnow()
    
    if timestamp is not None and timestamp != server_timestamp:
        logger.warning(
            f"Client-provided timestamp ignored for user {user.id}. "
            f"Using server time for streak calculation (security measure)."
        )
    
    # Get user's timezone and convert timestamp to local date
    timezone_str = get_user_timezone(user)
    local_date = get_user_date(server_timestamp, timezone_str)
    
    # Check if this date is already marked as active
    existing_entry = db.query(StreakHistory).filter(
        StreakHistory.user_id == user.id,
        StreakHistory.date == local_date
    ).first()
    
    if existing_entry and existing_entry.is_active:
        # Day already marked active, no streak change
        return StreakUpdateResult(
            current_streak=user.current_streak,
            highest_streak=user.highest_streak,
            streak_incremented=False
        )
    
    # Mark this day as active
    if existing_entry:
        existing_entry.is_active = True
    else:
        new_entry = StreakHistory(
            user_id=user.id,
            date=local_date,
            is_active=True,
            freeze_used=False
        )
        db.add(new_entry)
    
    # Check if this continues the streak
    streak_incremented = False
    if check_streak_continuation(db, user, local_date):
        # Yesterday was active, increment streak
        user.current_streak += 1
        streak_incremented = True
    else:
        # This is a new streak starting today
        user.current_streak = 1
        streak_incremented = True
    
    # Update highest streak if current exceeds it
    if user.current_streak > user.highest_streak:
        user.highest_streak = user.current_streak
    
    db.flush()
    
    return StreakUpdateResult(
        current_streak=user.current_streak,
        highest_streak=user.highest_streak,
        streak_incremented=streak_incremented
    )


def check_streak_continuation(
    db: Session,
    user: User,
    current_date: date
) -> bool:
    """
    Check if the current date continues the streak from yesterday.
    
    Args:
        db: Database session
        user: User model instance
        current_date: The date being checked (in user's local timezone)
        
    Returns:
        True if yesterday was active (or used a freeze), False otherwise
        
    References: Requirement 3.2
    """
    yesterday = current_date - timedelta(days=1)
    
    yesterday_entry = db.query(StreakHistory).filter(
        StreakHistory.user_id == user.id,
        StreakHistory.date == yesterday
    ).first()
    
    if not yesterday_entry:
        # No entry for yesterday means streak doesn't continue
        return False
    
    # Streak continues if yesterday was active OR a freeze was used
    return yesterday_entry.is_active or yesterday_entry.freeze_used


def check_for_streak_break(
    db: Session,
    user: User
) -> StreakBreakResult:
    """
    Check if the user missed a day and handle freeze consumption.
    
    This should be called by a scheduled job at the day boundary to check
    if the user was active yesterday. If not, it will:
    1. Try to consume a streak freeze if available
    2. Reset the streak to 0 if no freeze available
    
    Args:
        db: Database session
        user: User model instance (with gym relationship loaded)
        
    Returns:
        StreakBreakResult with information about what happened
        
    References: Requirements 3.3, 3.7, 4.2, 4.3
    """
    # Get user's timezone and yesterday's date
    timezone_str = get_user_timezone(user)
    today = datetime.now().astimezone().date()
    yesterday = today - timedelta(days=1)
    
    # Check if yesterday was active
    yesterday_entry = db.query(StreakHistory).filter(
        StreakHistory.user_id == user.id,
        StreakHistory.date == yesterday
    ).first()
    
    if yesterday_entry and (yesterday_entry.is_active or yesterday_entry.freeze_used):
        # Yesterday was covered, no break
        return StreakBreakResult(
            streak_broken=False,
            freeze_consumed=False,
            current_streak=user.current_streak
        )
    
    # User missed yesterday - try to consume a freeze
    if user.streak_freeze_count > 0:
        freeze_consumed = consume_streak_freeze(db, user, yesterday)
        return StreakBreakResult(
            streak_broken=False,
            freeze_consumed=freeze_consumed,
            current_streak=user.current_streak
        )
    
    # No freeze available, streak is broken
    user.current_streak = 0
    db.flush()
    
    return StreakBreakResult(
        streak_broken=True,
        freeze_consumed=False,
        current_streak=0
    )


def consume_streak_freeze(
    db: Session,
    user: User,
    date: date
) -> bool:
    """
    Consume a streak freeze to prevent streak loss for a specific date.
    
    Args:
        db: Database session
        user: User model instance
        date: The date to apply the freeze to (in user's local timezone)
        
    Returns:
        True if freeze was consumed successfully, False otherwise
        
    References: Requirements 4.2, 4.3, 4.4
    """
    if user.streak_freeze_count <= 0:
        return False
    
    # Check if freeze already used for this date
    existing_entry = db.query(StreakHistory).filter(
        StreakHistory.user_id == user.id,
        StreakHistory.date == date
    ).first()
    
    if existing_entry and existing_entry.freeze_used:
        # Freeze already consumed for this date (idempotent)
        return True
    
    # Create or update streak history entry
    if existing_entry:
        existing_entry.freeze_used = True
    else:
        new_entry = StreakHistory(
            user_id=user.id,
            date=date,
            is_active=False,
            freeze_used=True
        )
        db.add(new_entry)
    
    # Decrement freeze count
    user.streak_freeze_count -= 1
    db.flush()
    
    return True
