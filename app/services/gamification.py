from datetime import datetime, timedelta, timezone, date
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from math import sqrt, floor

from app.core.config import settings
from app.models.models import MealLog, XPLog, User


def _day_bounds(dt: datetime):
    start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end


def _has_meal_on(db: Session, user: User, day: datetime) -> bool:
    start, end = _day_bounds(day)
    q = (
        db.query(MealLog.id)
        .filter(MealLog.user_id == user.id, MealLog.gym_id == user.gym_id, MealLog.created_at >= start, MealLog.created_at < end)
        .limit(1)
    )
    return db.query(q.exists()).scalar()


def _award_xp(db: Session, user: User, delta: int, reason: str):
    exists = db.query(XPLog.id).filter(XPLog.user_id == user.id, XPLog.gym_id == user.gym_id, XPLog.reason == reason).first()
    if exists:
        return
    log = XPLog(user_id=user.id, gym_id=user.gym_id, delta=delta, reason=reason)
    user.total_xp = (user.total_xp or 0) + delta
    db.add(log)


def on_meal_logged(db: Session, user: User, now: datetime):
    today_key = now.date().isoformat()
    _award_xp(db, user, 10, f"meal_logged:{today_key}")
    yesterday = now - timedelta(days=1)
    if _has_meal_on(db, user, yesterday):
        user.current_streak = (user.current_streak or 0) + 1
    else:
        user.current_streak = 1
    if user.current_streak % 7 == 0:
        _award_xp(db, user, 100, f"streak:{user.current_streak}")


def _targets():
    return {
        "protein": settings.DEFAULT_TARGET_PROTEIN,
        "carbs": settings.DEFAULT_TARGET_CARBS,
        "fats": settings.DEFAULT_TARGET_FATS,
        "calories": settings.DEFAULT_TARGET_CALORIES,
    }


def _totals_for_day(db: Session, user: User, day: datetime):
    start, end = _day_bounds(day)
    rows = (
        db.query(
            func.coalesce(func.sum(MealLog.protein), 0),
            func.coalesce(func.sum(MealLog.carbs), 0),
            func.coalesce(func.sum(MealLog.fats), 0),
            func.coalesce(func.sum(MealLog.calories), 0),
        )
        .filter(MealLog.user_id == user.id, MealLog.gym_id == user.gym_id, MealLog.created_at >= start, MealLog.created_at < end)
        .one()
    )
    return {"protein": int(rows[0]), "carbs": int(rows[1]), "fats": int(rows[2]), "calories": int(rows[3])}


def check_macro_target_and_award(db: Session, user: User, day: datetime):
    t = _targets()
    totals = _totals_for_day(db, user, day)
    ok = True
    for k in ["protein", "carbs", "fats"]:
        target = t[k]
        val = totals[k]
        low = target * 0.9
        high = target * 1.1
        if not (low <= val <= high):
            ok = False
            break
    if ok:
        _award_xp(db, user, 20, f"macro_target:{day.date().isoformat()}")


def level_from_xp(total_xp: int) -> int:
    return int(floor(sqrt((total_xp or 0) / 100)))


def progress_snapshot(db: Session, user: User, now: datetime):
    t = _targets()
    totals = _totals_for_day(db, user, now)
    today_pct = 0.0
    if t["calories"] > 0:
        today_pct = min(100.0, (totals["calories"] / t["calories"]) * 100.0)
    macro_parts = []
    for k in ["protein", "carbs", "fats"]:
        target = t[k] or 1
        pct = min(1.0, totals[k] / target) if target > 0 else 1.0
        macro_parts.append(pct)
    macro_completion = sum(macro_parts) / 3.0 * 100.0
    return {
        "total_xp": user.total_xp or 0,
        "level": level_from_xp(user.total_xp or 0),
        "streak_days": user.current_streak or 0,
        "today_progress_percentage": today_pct,
        "macro_completion_percentage": macro_completion,
    }

