from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MealCreate(BaseModel):
    protein: int = Field(ge=0)
    carbs: int = Field(ge=0)
    fats: int = Field(ge=0)
    calories: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = None


class MealOut(BaseModel):
    id: int
    user_id: int
    gym_id: int
    protein: int
    carbs: int
    fats: int
    calories: int
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
