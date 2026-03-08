from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.ai import AIRequest, AIResult
from app.services.ai import call_openai_with_retries
from app.services.nutrition import sanitize_meal_input, sum_macros, weekly_averages
from app.models.models import MealLog, User, ChatMessage

router = APIRouter()


@router.get("/history")
def get_chat_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get last 50 chat messages for the current user"""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(50)
        .all()
    )
    # Reverse to get chronological order (oldest first)
    messages.reverse()
    return {
        "messages": [
            {
                "id": msg.id,
                "sender": msg.sender,
                "message": msg.message,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]
    }


@router.post("/message")
def ai_message(payload: AIRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Save user message to database
    user_msg = ChatMessage(
        user_id=user.id,
        message=payload.message,
        sender="user",
    )
    db.add(user_msg)
    db.commit()
    
    # Get AI response
    result, err = call_openai_with_retries(payload.message)
    if not result:
        raise HTTPException(status_code=502, detail=f"openai_error: {err or 'unknown'}")
    
    # Save AI response to database
    ai_msg = ChatMessage(
        user_id=user.id,
        message=result.reply,
        sender="ai",
    )
    db.add(ai_msg)
    db.commit()
    
    # Handle meal logging
    if result.intent == "log_meal":
        if result.protein is None or result.carbs is None or result.fats is None:
            return {"reply": result.reply, "status": "need_macros"}
        try:
            normalized = sanitize_meal_input(int(result.protein), int(result.carbs), int(result.fats), None)
        except ValueError:
            raise HTTPException(status_code=400)
        meal = MealLog(
            user_id=user.id,
            gym_id=user.gym_id,
            protein=normalized["protein"],
            carbs=normalized["carbs"],
            fats=normalized["fats"],
            calories=normalized["calories"],
            description=None,
        )
        db.add(meal)
        db.commit()
        db.refresh(meal)
        return {
            "reply": result.reply,
            "intent": result.intent,
            "meal": {
                "id": meal.id,
                "protein": meal.protein,
                "carbs": meal.carbs,
                "fats": meal.fats,
                "calories": meal.calories,
                "description": meal.description,
                "created_at": meal.created_at.isoformat(),
            }
        }
    
    # Handle progress request
    if result.intent == "progress":
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=7)
        rows = (
            db.query(MealLog)
            .filter(MealLog.user_id == user.id, MealLog.gym_id == user.gym_id, MealLog.created_at >= start, MealLog.created_at <= now)
            .all()
        )
        avg = weekly_averages(rows, days=7)
        return {"reply": result.reply, "intent": result.intent, "averages": avg}
    
    return {"reply": result.reply, "intent": result.intent}
