import json
import os
import re
from typing import Optional, Tuple
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
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
