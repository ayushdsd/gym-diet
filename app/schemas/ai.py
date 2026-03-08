from typing import Optional, Literal
from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    message: str = Field(min_length=1)


class AIResult(BaseModel):
    intent: Literal["log_meal", "suggestion", "progress"]
    protein: Optional[int] = None
    carbs: Optional[int] = None
    fats: Optional[int] = None
    reply: str

