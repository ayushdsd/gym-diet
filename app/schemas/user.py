from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    gym_id: int
    role: str = "member"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    gym_id: int
    role: str = "member"


class UserOut(UserBase):
    id: int
    total_xp: int
    current_streak: int
    onboarding_completed: bool

    class Config:
        from_attributes = True


class OnboardingData(BaseModel):
    gender: str  # "male" or "female"
    age: int
    height: int  # cm
    weight: int  # kg
    goal_type: str  # "fat_loss", "maintenance", "muscle_gain"
    target_calories: int
    target_protein: int
    target_carbs: int
    target_fats: int


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    onboarding_completed: bool


class LoginIn(BaseModel):
    email: EmailStr
    password: str

