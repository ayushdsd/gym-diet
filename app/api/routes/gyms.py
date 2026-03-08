from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user, require_admin_in_same_gym
from app.models.models import Gym
from app.schemas.gym import GymCreate, GymOut

router = APIRouter()


@router.get("/locations", response_model=list[str])
def list_locations(db: Session = Depends(get_db)):
    """Public endpoint to list all unique gym locations"""
    locations = db.query(Gym.location).distinct().order_by(Gym.location).all()
    return [loc[0] for loc in locations]


@router.get("", response_model=list[GymOut])
def list_gyms(location: str = Query(None), db: Session = Depends(get_db)):
    """Public endpoint to list all gyms, optionally filtered by location"""
    query = db.query(Gym)
    if location:
        query = query.filter(func.lower(Gym.location) == func.lower(location))
    gyms = query.order_by(Gym.name).all()
    return gyms


@router.post("", response_model=GymOut, status_code=201)
def create_gym(payload: GymCreate, db: Session = Depends(get_db)):
    existing = db.query(Gym).filter(Gym.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    gym = Gym(name=payload.name)
    db.add(gym)
    db.commit()
    db.refresh(gym)
    return gym


@router.get("/me", response_model=GymOut)
def get_my_gym(db: Session = Depends(get_db), user=Depends(get_current_user)):
    gym = db.get(Gym, user.gym_id)
    if not gym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return gym


@router.get("/{gym_id}", response_model=GymOut)
def get_gym(gym_id: int, db: Session = Depends(get_db), user=Depends(require_admin_in_same_gym)):
    gym = db.get(Gym, gym_id)
    if not gym:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return gym
