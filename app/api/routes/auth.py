from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import exc as sa_exc
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.models import User, Gym
from app.schemas.user import UserCreate, UserOut, Token
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    gym = db.get(Gym, payload.gym_id)
    if not gym:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="gym_not_found")
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email_exists")
    hashed = get_password_hash(payload.password)
    user = User(email=payload.email, hashed_password=hashed, gym_id=payload.gym_id, role=payload.role)
    db.add(user)
    try:
        db.commit()
    except sa_exc.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="integrity_error")
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": str(user.id), "gym_id": user.gym_id, "role": user.role}, token_expires)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "onboarding_completed": bool(user.onboarding_completed)
    }
