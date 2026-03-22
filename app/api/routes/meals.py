from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user
from app.models.models import MealLog, User
from app.schemas.meal import MealCreate, MealOut
from app.services.nutrition import sanitize_meal_input, sum_macros, weekly_averages
from app.services.xp_manager import award_xp
from app.services.level_system import check_level_up, is_milestone_level
from app.services.streak_tracker import mark_day_active
from app.services.achievement_system import check_badge_unlocks

router = APIRouter()


def _get_user_targets(user: User) -> dict:
    """Get user's macro targets (personalized or defaults)"""
    if user.onboarding_completed and user.target_protein:
        return {
            "protein": user.target_protein,
            "carbs": user.target_carbs,
            "fats": user.target_fats,
        }
    else:
        return {
            "protein": 150,
            "carbs": 250,
            "fats": 60,
        }


def _get_daily_totals(db: Session, user: User, now: datetime) -> dict:
    """Get total macros for the current day"""
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    
    rows = db.query(
        func.coalesce(func.sum(MealLog.protein), 0),
        func.coalesce(func.sum(MealLog.carbs), 0),
        func.coalesce(func.sum(MealLog.fats), 0),
    ).filter(
        MealLog.user_id == user.id,
        MealLog.gym_id == user.gym_id,
        MealLog.created_at >= start,
        MealLog.created_at < end
    ).one()
    
    return {
        "protein": int(rows[0]),
        "carbs": int(rows[1]),
        "fats": int(rows[2]),
    }


def _check_macro_goals(totals: dict, targets: dict) -> list[str]:
    """Check which macro goals are completed (within ±10% of target)"""
    completed = []
    for macro in ["protein", "carbs", "fats"]:
        target = targets[macro]
        actual = totals[macro]
        if abs(actual - target) <= target * 0.1:
            completed.append(macro)
    return completed


def _check_daily_goal(totals: dict, targets: dict) -> bool:
    """Check if all macro goals are completed"""
    for macro in ["protein", "carbs", "fats"]:
        target = targets[macro]
        actual = totals[macro]
        if abs(actual - target) > target * 0.1:
            return False
    return True


@router.post("", status_code=201)
def create_meal(payload: MealCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        normalized = sanitize_meal_input(payload.protein, payload.carbs, payload.fats, payload.calories)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Save meal
    meal = MealLog(
        user_id=user.id,
        gym_id=user.gym_id,
        protein=normalized["protein"],
        carbs=normalized["carbs"],
        fats=normalized["fats"],
        calories=normalized["calories"],
        description=payload.description,
    )
    db.add(meal)
    
    try:
        db.flush()
    except Exception as e:
        db.rollback()
        print(f"Database error saving meal: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Initialize gamification response
    gamification_data = {
        "xp_awarded": 0,
        "xp_breakdown": {},
        "new_total_xp": user.total_xp,
        "level_up": False,
        "old_level": 0,
        "new_level": 0,
        "current_streak": user.current_streak,
        "streak_freeze_earned": False,
        "badges_unlocked": []
    }
    
    try:
        now = datetime.now(timezone.utc)
        old_xp = user.total_xp
        
        # 1. Award XP for meal logging
        meal_xp_result = award_xp(db, user, "meal_logged", {})
        gamification_data["xp_awarded"] += meal_xp_result.total_xp_awarded
        gamification_data["xp_breakdown"].update(meal_xp_result.breakdown)
        
        # 2. Update streak
        streak_result = mark_day_active(db, user, now)
        gamification_data["current_streak"] = streak_result.current_streak
        
        # 3. Check macro goals and daily goal completion
        targets = _get_user_targets(user)
        totals = _get_daily_totals(db, user, now)
        completed_macros = _check_macro_goals(totals, targets)
        daily_goal_completed = _check_daily_goal(totals, targets)
        
        # Award XP for macro goals
        if completed_macros:
            macro_xp_result = award_xp(db, user, "macro_goal", {"completed_macros": completed_macros})
            gamification_data["xp_awarded"] += macro_xp_result.total_xp_awarded
            gamification_data["xp_breakdown"]["macro_goals_completed"] = completed_macros
            gamification_data["xp_breakdown"]["macro_goal_xp"] = macro_xp_result.total_xp_awarded
        
        # Award XP for daily goal
        if daily_goal_completed:
            daily_xp_result = award_xp(db, user, "daily_goal", {})
            gamification_data["xp_awarded"] += daily_xp_result.total_xp_awarded
            gamification_data["xp_breakdown"]["daily_goal_completed"] = True
            gamification_data["xp_breakdown"]["daily_goal_xp"] = daily_xp_result.total_xp_awarded
        
        # 4. Check for level up
        new_xp = user.total_xp
        level_up_occurred, old_level, new_level = check_level_up(old_xp, new_xp)
        gamification_data["level_up"] = level_up_occurred
        gamification_data["old_level"] = old_level
        gamification_data["new_level"] = new_level
        gamification_data["new_total_xp"] = new_xp
        
        # 5. Award streak freeze if milestone level reached
        if level_up_occurred and is_milestone_level(new_level):
            user.streak_freeze_count += 1
            gamification_data["streak_freeze_earned"] = True
        
        # 6. Check for badge unlocks
        context = {
            "meal_count": db.query(func.count(MealLog.id)).filter(MealLog.user_id == user.id).scalar(),
            "new_level": new_level,
            "level_up": level_up_occurred,
        }
        newly_unlocked_badges = check_badge_unlocks(db, user, context)
        gamification_data["badges_unlocked"] = [
            {
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "tier": badge.tier,
                "icon": badge.icon
            }
            for badge in newly_unlocked_badges
        ]
        
    except Exception as e:
        # Log error but don't fail meal logging
        print(f"Gamification error: {e}")
        import traceback
        traceback.print_exc()
    
    # Commit everything
    db.commit()
    db.refresh(meal)
    
    # Return meal with gamification data
    return {
        "meal": {
            "id": meal.id,
            "description": meal.description,
            "protein": meal.protein,
            "carbs": meal.carbs,
            "fats": meal.fats,
            "calories": meal.calories,
            "created_at": meal.created_at.isoformat(),
            "user_id": meal.user_id,
            "gym_id": meal.gym_id,
        },
        "gamification": gamification_data
    }


@router.get("/today", response_model=list[MealOut])
def get_today_meals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    rows = (
        db.query(MealLog)
        .filter(MealLog.user_id == user.id, MealLog.gym_id == user.gym_id, MealLog.created_at >= start, MealLog.created_at < end)
        .order_by(MealLog.created_at.desc())
        .all()
    )
    return rows


@router.get("/weekly", response_model=list[MealOut])
def get_weekly_meals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)
    rows = (
        db.query(MealLog)
        .filter(MealLog.user_id == user.id, MealLog.gym_id == user.gym_id, MealLog.created_at >= start, MealLog.created_at <= now)
        .order_by(MealLog.created_at.desc())
        .all()
    )
    return rows


@router.get("/totals/daily")
def get_daily_totals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    rows = (
        db.query(MealLog)
        .filter(MealLog.user_id == user.id, MealLog.gym_id == user.gym_id, MealLog.created_at >= start, MealLog.created_at < end)
        .all()
    )
    totals = sum_macros(rows)
    return {"date": start.date().isoformat(), "totals": totals}


@router.get("/averages/weekly")
def get_weekly_averages(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)
    rows = (
        db.query(MealLog)
        .filter(MealLog.user_id == user.id, MealLog.gym_id == user.gym_id, MealLog.created_at >= start, MealLog.created_at <= now)
        .all()
    )
    avg = weekly_averages(rows, days=7)
    return {"start": start.date().isoformat(), "end": now.date().isoformat(), "averages": avg}


@router.get("/monthly-goals")
def get_monthly_goals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Returns monthly goal completion data for the current month.
    Each day is marked as:
    - completed: macros within ±10% of target
    - missed: has data but didn't meet goals
    - no_data: no meals logged
    """
    now = datetime.now(timezone.utc)
    # Get first day of current month
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Get first day of next month
    if now.month == 12:
        end_of_month = start_of_month.replace(year=now.year + 1, month=1)
    else:
        end_of_month = start_of_month.replace(month=now.month + 1)
    
    # Use user's personalized targets if available, otherwise use defaults
    if user.onboarding_completed and user.target_protein:
        TARGETS = {
            "protein": user.target_protein,
            "carbs": user.target_carbs,
            "fats": user.target_fats,
        }
    else:
        # Default targets
        TARGETS = {
            "protein": 150,
            "carbs": 250,
            "fats": 60,
        }
    
    # Query all meals for the month
    meals = (
        db.query(MealLog)
        .filter(
            MealLog.user_id == user.id,
            MealLog.gym_id == user.gym_id,
            MealLog.created_at >= start_of_month,
            MealLog.created_at < end_of_month
        )
        .all()
    )
    
    # Group meals by day
    daily_totals = {}
    for meal in meals:
        day_key = meal.created_at.date().isoformat()
        if day_key not in daily_totals:
            daily_totals[day_key] = {"protein": 0, "carbs": 0, "fats": 0, "calories": 0}
        daily_totals[day_key]["protein"] += meal.protein
        daily_totals[day_key]["carbs"] += meal.carbs
        daily_totals[day_key]["fats"] += meal.fats
        daily_totals[day_key]["calories"] += meal.calories
    
    # Build response for each day of the month
    days_data = []
    completed_count = 0
    total_days_with_data = 0
    
    current_day = start_of_month
    while current_day < end_of_month and current_day <= now:
        day_str = current_day.date().isoformat()
        
        if day_str in daily_totals:
            totals = daily_totals[day_str]
            total_days_with_data += 1
            
            # Check if within ±10% of targets
            protein_ok = abs(totals["protein"] - TARGETS["protein"]) <= TARGETS["protein"] * 0.1
            carbs_ok = abs(totals["carbs"] - TARGETS["carbs"]) <= TARGETS["carbs"] * 0.1
            fats_ok = abs(totals["fats"] - TARGETS["fats"]) <= TARGETS["fats"] * 0.1
            
            goal_completed = protein_ok and carbs_ok and fats_ok
            
            if goal_completed:
                completed_count += 1
            
            days_data.append({
                "date": day_str,
                "status": "completed" if goal_completed else "missed",
                "totals": totals
            })
        else:
            days_data.append({
                "date": day_str,
                "status": "no_data",
                "totals": None
            })
        
        current_day += timedelta(days=1)
    
    # Calculate completion rate
    completion_rate = (completed_count / total_days_with_data * 100) if total_days_with_data > 0 else 0
    
    return {
        "month": start_of_month.strftime("%B %Y"),
        "days": days_data,
        "completed_count": completed_count,
        "total_days": len(days_data),
        "completion_rate": round(completion_rate, 1)
    }


@router.delete("/{meal_id}", status_code=204)
def delete_meal(meal_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Delete a meal by ID"""
    meal = db.query(MealLog).filter(
        MealLog.id == meal_id,
        MealLog.user_id == user.id,
        MealLog.gym_id == user.gym_id
    ).first()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    db.delete(meal)
    db.commit()
    
    return None
