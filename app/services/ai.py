import json
import os
import re
from typing import Optional, Tuple
from datetime import datetime, timezone
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.config import settings
from app.schemas.ai import AIResult


SYSTEM_PROMPT = "You are a certified Indian fitness diet assistant. Keep replies short. Never give medical diagnosis. Respond ONLY with JSON: {intent:'log_meal|suggestion|progress',protein:number|null,carbs:number|null,fats:number|null,reply:string}"


def _extract_json(text: str) -> Optional[str]:
    m = re.search(r"\{.*\}", text, re.S)
    return m.group(0) if m else None


def parse_ai_result(text: str) -> Optional[AIResult]:
    raw = text
    try:
        data = json.loads(raw)
    except Exception:
        snippet = _extract_json(raw)
        if not snippet:
            return None
        try:
            data = json.loads(snippet)
        except Exception:
            return None
    try:
        return AIResult(**data)
    except Exception:
        return None


def _invoke_chat(client: OpenAI, message: str, model: str, json_mode: bool) -> str:
    if json_mode:
        chat = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
    else:
        chat = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            temperature=0.2,
        )
    return chat.choices[0].message.content or ""


def call_openai_with_retries(message: str, max_retries: int = 2) -> Tuple[Optional[AIResult], Optional[str]]:
    client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else OpenAI()
    model = settings.OPENAI_MODEL
    last_error: Optional[str] = None
    for _ in range(max_retries + 1):
        try:
            content = _invoke_chat(client, message, model, json_mode=True)
            result = parse_ai_result(content)
            if result:
                return result, None
            content = _invoke_chat(client, message, model, json_mode=False)
            result = parse_ai_result(content)
            if result:
                return result, None
        except (RateLimitError, APIConnectionError, APIError) as e:
            last_error = getattr(e, "message", str(e))
            continue
        except Exception as e:
            last_error = str(e)
            continue
    return None, last_error


def build_enhanced_system_prompt(user, db: Session) -> str:
    """Build personalized system prompt with user context"""
    from app.models.models import MealLog
    
    # Calculate level
    level = max(1, int((user.total_xp or 0) ** 0.5 / 10))
    
    # Get today's progress
    today = datetime.now(timezone.utc).date()
    meals = db.query(MealLog)\
        .filter(MealLog.user_id == user.id)\
        .filter(func.date(MealLog.created_at) == today)\
        .all()
    
    if meals:
        total_protein = sum(m.protein for m in meals)
        total_carbs = sum(m.carbs for m in meals)
        total_fats = sum(m.fats for m in meals)
        
        protein_pct = (total_protein / user.target_protein * 100) if user.target_protein else 0
        carbs_pct = (total_carbs / user.target_carbs * 100) if user.target_carbs else 0
        fats_pct = (total_fats / user.target_fats * 100) if user.target_fats else 0
        
        progress = f"""TODAY'S PROGRESS:
- Meals logged: {len(meals)}
- Protein: {total_protein}g / {user.target_protein}g ({protein_pct:.0f}%)
- Carbs: {total_carbs}g / {user.target_carbs}g ({carbs_pct:.0f}%)
- Fats: {total_fats}g / {user.target_fats}g ({fats_pct:.0f}%)"""
    else:
        progress = "TODAY'S PROGRESS:\n- No meals logged yet"
    
    return f"""You are a certified Indian fitness diet assistant.

USER PROFILE:
- Goal: {user.goal_type or 'Not set'}
- Daily Targets: {user.target_protein}g protein, {user.target_carbs}g carbs, {user.target_fats}g fats
- Level: {level}
- Current Streak: {user.current_streak} days
- Highest Streak: {user.highest_streak} days

{progress}

Keep replies short and motivating. Never give medical diagnosis.
Respond ONLY with JSON: {{intent:'log_meal|suggestion|progress',protein:number|null,carbs:number|null,fats:number|null,reply:string}}"""


def get_conversation_context(user_id: int, db: Session, limit: int = 5) -> list:
    """Get recent conversation history"""
    from app.models.models import ChatMessage
    
    messages = db.query(ChatMessage)\
        .filter(ChatMessage.user_id == user_id)\
        .order_by(ChatMessage.created_at.desc())\
        .limit(limit)\
        .all()
    
    # Reverse to get chronological order
    messages.reverse()
    
    context = []
    for msg in messages:
        role = "user" if msg.sender == "user" else "assistant"
        context.append({"role": role, "content": msg.message})
    
    return context


def call_openai_with_context(
    message: str, 
    user, 
    db: Session, 
    max_retries: int = 2
) -> Tuple[Optional[AIResult], Optional[str]]:
    """Call OpenAI with enhanced context (conversation history + user profile)"""
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else OpenAI()
    model = settings.OPENAI_MODEL
    
    # Build enhanced system prompt
    system_prompt = build_enhanced_system_prompt(user, db)
    
    # Get conversation history
    conversation_history = get_conversation_context(user.id, db, limit=5)
    
    # Build messages array
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": message})
    
    last_error: Optional[str] = None
    
    for _ in range(max_retries + 1):
        try:
            chat = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            content = chat.choices[0].message.content or ""
            result = parse_ai_result(content)
            
            if result:
                return result, None
                
        except (RateLimitError, APIConnectionError, APIError) as e:
            last_error = getattr(e, "message", str(e))
            continue
        except Exception as e:
            last_error = str(e)
            continue
    
    return None, last_error
