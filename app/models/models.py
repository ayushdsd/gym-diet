from datetime import datetime, date
from sqlalchemy import Integer, String, DateTime, Date, ForeignKey, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Gym(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    users: Mapped[list["User"]] = relationship(back_populates="gym", cascade="all, delete-orphan")


class User(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")
    total_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    streak_freeze_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    highest_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gym_id: Mapped[int] = mapped_column(ForeignKey("gym.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Onboarding fields
    onboarding_completed: Mapped[bool] = mapped_column(Integer, nullable=False, default=0)  # SQLite uses 0/1 for boolean
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)  # in cm
    weight: Mapped[int | None] = mapped_column(Integer, nullable=True)  # in kg
    goal_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # fat_loss, maintenance, muscle_gain
    target_calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_protein: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_carbs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_fats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    gym: Mapped[Gym] = relationship(back_populates="users")
    meal_logs: Mapped[list["MealLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    xp_logs: Mapped[list["XPLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    chat_messages: Mapped[list["ChatMessage"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    streak_history: Mapped[list["StreakHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    user_badges: Mapped[list["UserBadge"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class MealLog(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    gym_id: Mapped[int] = mapped_column(ForeignKey("gym.id", ondelete="CASCADE"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    protein: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    carbs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fats: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    calories: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    user: Mapped[User] = relationship(back_populates="meal_logs")


class XPLog(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    gym_id: Mapped[int] = mapped_column(ForeignKey("gym.id", ondelete="CASCADE"), nullable=False, index=True)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, default='meal_logged', index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default='meal_log', index=True)
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    user: Mapped[User] = relationship(back_populates="xp_logs")


class ChatMessage(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sender: Mapped[str] = mapped_column(String(10), nullable=False)  # "user" or "ai"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="chat_messages")


class Badge(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tier: Mapped[str] = mapped_column(String(20), nullable=False)
    icon: Mapped[str] = mapped_column(String(10), nullable=False)
    unlock_condition: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    user_badges: Mapped[list["UserBadge"]] = relationship(back_populates="badge", cascade="all, delete-orphan")


class UserBadge(Base):
    __tablename__ = "user_badge"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    badge_id: Mapped[int] = mapped_column(ForeignKey("badge.id", ondelete="CASCADE"), nullable=False, index=True)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'badge_id', name='uq_user_badge'),
    )
    
    user: Mapped[User] = relationship(back_populates="user_badges")
    badge: Mapped[Badge] = relationship(back_populates="user_badges")


class StreakHistory(Base):
    __tablename__ = "streak_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    freeze_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_user_date'),
    )
    
    user: Mapped[User] = relationship(back_populates="streak_history")
