from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.models import User
from app.schemas.user import OnboardingData
from app.services.gamification import progress_snapshot

router = APIRouter()


@router.get("/progress")
def get_progress(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    data = progress_snapshot(db, user, now)
    return data


@router.get("/targets")
def get_user_targets(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Get user's personalized macro targets.
    Returns default values if onboarding not completed.
    """
    if user.onboarding_completed and user.target_calories:
        return {
            "calories": user.target_calories,
            "protein": user.target_protein,
            "carbs": user.target_carbs,
            "fats": user.target_fats,
            "has_custom_targets": True
        }
    else:
        # Return default targets if onboarding not completed
        return {
            "calories": 2000,
            "protein": 150,
            "carbs": 250,
            "fats": 60,
            "has_custom_targets": False
        }


@router.post("/onboarding")
def complete_onboarding(payload: OnboardingData, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Save user onboarding data and mark onboarding as completed.
    """
    user.gender = payload.gender
    user.age = payload.age
    user.height = payload.height
    user.weight = payload.weight
    user.goal_type = payload.goal_type
    user.target_calories = payload.target_calories
    user.target_protein = payload.target_protein
    user.target_carbs = payload.target_carbs
    user.target_fats = payload.target_fats
    user.onboarding_completed = 1  # SQLite uses 0/1 for boolean
    
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "message": "Onboarding completed successfully",
        "targets": {
            "calories": user.target_calories,
            "protein": user.target_protein,
            "carbs": user.target_carbs,
            "fats": user.target_fats
        }
    }


@router.get("/profile")
def get_user_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Get user profile information including email, gym, and goal.
    """
    goal_labels = {
        "fat_loss": "Fat Loss",
        "maintenance": "Maintenance",
        "muscle_gain": "Muscle Gain"
    }
    
    return {
        "id": user.id,
        "email": user.email,
        "goal": goal_labels.get(user.goal_type, user.goal_type or "Not set"),
        "gym": {
            "id": user.gym.id,
            "name": user.gym.name,
            "location": user.gym.location
        } if user.gym else None
    }
