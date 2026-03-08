"""
Gamification API Routes

Provides endpoints for accessing user gamification data including:
- Profile summary (XP, level, streaks, badges)
- Badge collection
- XP history

References Requirements: 11.4, 11.5
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.models.models import User, UserBadge, Badge, XPLog
from app.services.level_system import calculate_level, calculate_xp_for_next_level

router = APIRouter()


@router.get("/profile")
def get_gamification_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get user's gamification profile summary.
    
    Returns:
        - user_id: User's ID
        - total_xp: Total experience points earned
        - current_level: Current level based on total XP
        - xp_to_next_level: XP needed to reach next level
        - current_streak: Current daily streak count
        - highest_streak: Highest streak ever achieved
        - streak_freeze_count: Number of available streak freezes
        - badges_unlocked_count: Number of badges unlocked
        - total_badges: Total number of badges available
        - level_progress_percentage: Progress to next level as percentage
    
    References Requirements: 11.4, 11.5
    """
    # Calculate current level and XP to next level
    current_level = calculate_level(user.total_xp)
    xp_to_next_level = calculate_xp_for_next_level(current_level, user.total_xp)
    
    # Query badge counts
    badges_unlocked_count = db.query(func.count(UserBadge.id)).filter(
        UserBadge.user_id == user.id
    ).scalar() or 0
    
    total_badges = db.query(func.count(Badge.id)).scalar() or 0
    
    # Calculate level progress percentage
    # XP needed for current level to next level
    next_level_threshold = (current_level + 1) ** 2 * 100
    current_level_threshold = current_level ** 2 * 100
    xp_for_current_level = next_level_threshold - current_level_threshold
    xp_progress_in_level = user.total_xp - current_level_threshold
    
    level_progress_percentage = (
        (xp_progress_in_level / xp_for_current_level * 100)
        if xp_for_current_level > 0
        else 0.0
    )
    
    return {
        "user_id": user.id,
        "total_xp": user.total_xp,
        "current_level": current_level,
        "xp_to_next_level": xp_to_next_level,
        "current_streak": user.current_streak,
        "highest_streak": user.highest_streak,
        "streak_freeze_count": user.streak_freeze_count,
        "badges_unlocked_count": badges_unlocked_count,
        "total_badges": total_badges,
        "level_progress_percentage": round(level_progress_percentage, 1)
    }


@router.get("/badges")
def get_badges(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get all badges with unlock status for the current user.
    
    Returns a list of all available badges, each with:
        - id: Badge ID
        - name: Badge name
        - description: Badge description
        - tier: Badge tier (bronze, silver, gold)
        - icon: Badge icon emoji
        - unlocked: Boolean indicating if user has unlocked this badge
        - unlocked_at: Timestamp when badge was unlocked (null if not unlocked)
    
    Badges are ordered by tier (bronze, silver, gold) then by id.
    
    References Requirements: 11.2, 11.3, 11.6
    """
    # Query all badges with left join to user_badges
    badges_query = (
        db.query(Badge, UserBadge.unlocked_at)
        .outerjoin(
            UserBadge,
            (UserBadge.badge_id == Badge.id) & (UserBadge.user_id == user.id)
        )
        .order_by(
            # Order by tier: bronze (1), silver (2), gold (3)
            case(
                (Badge.tier == "bronze", 1),
                (Badge.tier == "silver", 2),
                (Badge.tier == "gold", 3),
                else_=4
            ),
            Badge.id
        )
        .all()
    )
    
    # Format response
    badges = []
    for badge, unlocked_at in badges_query:
        badges.append({
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "tier": badge.tier,
            "icon": badge.icon,
            "unlocked": unlocked_at is not None,
            "unlocked_at": unlocked_at.isoformat() if unlocked_at else None
        })
    
    return {"badges": badges}


@router.get("/xp-history")
def get_xp_history(
    days: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get XP history for the user, grouped by date.
    
    Query Parameters:
        - days: Number of days to retrieve (default 30, max 90)
    
    Returns:
        - history: Array of daily XP summaries, each containing:
            - date: Date in YYYY-MM-DD format
            - total_xp: Total XP earned on that date
            - transactions: Array of XPLog entries for that date
    
    Results are ordered by date descending (most recent first).
    Limited to most recent 1000 entries for performance.
    
    References Requirements: 11.7, 17.8
    """
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query XP logs within date range, ordered by date descending
    # Limit to 1000 entries for performance
    xp_logs = (
        db.query(XPLog)
        .filter(
            XPLog.user_id == user.id,
            XPLog.created_at >= start_date,
            XPLog.created_at <= end_date
        )
        .order_by(XPLog.created_at.desc())
        .limit(1000)
        .all()
    )
    
    # Group by date and aggregate
    history_dict = {}
    for log in xp_logs:
        # Extract date from timestamp
        log_date = log.created_at.date().isoformat()
        
        if log_date not in history_dict:
            history_dict[log_date] = {
                "date": log_date,
                "total_xp": 0,
                "transactions": []
            }
        
        # Add to total XP for the day
        history_dict[log_date]["total_xp"] += log.delta
        
        # Add transaction details
        history_dict[log_date]["transactions"].append({
            "id": log.id,
            "delta": log.delta,
            "action_type": log.action_type,
            "reason": log.reason,
            "created_at": log.created_at.isoformat()
        })
    
    # Convert to list and sort by date descending
    history = sorted(
        history_dict.values(),
        key=lambda x: x["date"],
        reverse=True
    )
    
    return {"history": history}
