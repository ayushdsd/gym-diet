"""
XPManager Service

Orchestrates all XP calculations and awards for the gamification system.
This service calculates base XP for different actions, applies streak multipliers,
records transactions in XPLog, and updates the user's total_xp.

References Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 17.5
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional
import threading
import time
import logging

from app.models.models import User, XPLog


# Configure logging
logger = logging.getLogger(__name__)

# XP Constants
XP_PER_MEAL = 10
XP_PER_MACRO_GOAL = 15
XP_DAILY_GOAL = 50

# Streak multipliers
STREAK_MULTIPLIER_7_DAYS = 1.5
STREAK_MULTIPLIER_30_DAYS = 2.0

# Batching configuration
BATCH_WINDOW_SECONDS = 1.0

# XP overflow protection (Requirement 15.3)
MAX_XP = 2**31 - 1  # Maximum 32-bit signed integer


class XPBatch:
    """Represents a batch of XP awards to be executed together"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.awards = []
        self.created_at = time.time()
        self.lock = threading.Lock()
    
    def add_award(self, action_type: str, context: dict):
        """Add an XP award to the batch"""
        with self.lock:
            self.awards.append({
                "action_type": action_type,
                "context": context,
                "timestamp": time.time()
            })
    
    def is_expired(self) -> bool:
        """Check if batch window has expired"""
        return (time.time() - self.created_at) >= BATCH_WINDOW_SECONDS
    
    def get_awards(self):
        """Get all awards in the batch"""
        with self.lock:
            return self.awards.copy()


class XPBatchManager:
    """Manages batching of XP awards within time windows"""
    def __init__(self):
        self.batches = {}  # user_id -> XPBatch
        self.lock = threading.Lock()
    
    def get_or_create_batch(self, user_id: int) -> XPBatch:
        """Get existing batch or create new one for user"""
        with self.lock:
            # Check if existing batch exists and is not expired
            if user_id in self.batches:
                batch = self.batches[user_id]
                if not batch.is_expired():
                    return batch
                else:
                    # Remove expired batch
                    del self.batches[user_id]
            
            # Create new batch
            batch = XPBatch(user_id)
            self.batches[user_id] = batch
            return batch
    
    def remove_batch(self, user_id: int):
        """Remove batch after processing"""
        with self.lock:
            if user_id in self.batches:
                del self.batches[user_id]


# Global batch manager instance
_batch_manager = XPBatchManager()


class XPAwardResult:
    """Result of awarding XP to a user"""
    def __init__(
        self,
        total_xp_awarded: int,
        base_xp: int,
        multiplier: float,
        breakdown: dict
    ):
        self.total_xp_awarded = total_xp_awarded
        self.base_xp = base_xp
        self.multiplier = multiplier
        self.breakdown = breakdown


def calculate_xp_for_meal() -> int:
    """
    Calculate base XP for logging a meal.
    
    Returns:
        10 XP for logging a meal
        
    References: Requirement 1.1
    """
    return XP_PER_MEAL


def calculate_macro_goal_xp(completed_macros: list[str]) -> int:
    """
    Calculate XP for completing macro goals.
    
    Args:
        completed_macros: List of macro names that were completed
                         (e.g., ["protein", "carbs"])
    
    Returns:
        15 XP per completed macro goal
        
    References: Requirement 1.3
    """
    return len(completed_macros) * XP_PER_MACRO_GOAL


def calculate_daily_goal_xp() -> int:
    """
    Calculate XP for completing the daily goal (all macros).
    
    Returns:
        50 XP for completing daily goal
        
    References: Requirement 1.2
    """
    return XP_DAILY_GOAL


def apply_streak_multiplier(base_xp: int, streak_days: int) -> int:
    """
    Apply streak multiplier to base XP.
    
    Multipliers:
    - 7+ days: 1.5x
    - 30+ days: 2.0x
    - Less than 7 days: 1.0x (no multiplier)
    
    Args:
        base_xp: Base XP before multiplier
        streak_days: Current streak count
        
    Returns:
        XP after applying multiplier (rounded to nearest integer)
        
    References: Requirements 1.4, 1.5
    """
    if streak_days >= 30:
        multiplier = STREAK_MULTIPLIER_30_DAYS
    elif streak_days >= 7:
        multiplier = STREAK_MULTIPLIER_7_DAYS
    else:
        multiplier = 1.0
    
    return round(base_xp * multiplier)


def record_xp_transaction(
    db: Session,
    user_id: int,
    gym_id: int,
    delta: int,
    action_type: str,
    reason: str,
    source: str = "meal_log",
    reference_id: int | None = None
) -> XPLog:
    """
    Create an XPLog entry to record an XP transaction.
    
    Args:
        db: Database session
        user_id: ID of the user receiving XP
        gym_id: ID of the user's gym
        delta: Amount of XP awarded (can be negative for penalties)
        action_type: Type of action (e.g., "meal_logged", "macro_goal", "daily_goal")
        reason: Human-readable description of why XP was awarded
        source: Source of the XP (e.g., "meal_log", "achievement")
        reference_id: ID of the related entity (e.g., meal_id for meal_logged)
        
    Returns:
        Created XPLog instance
        
    References: Requirement 1.6
    """
    xp_log = XPLog(
        user_id=user_id,
        gym_id=gym_id,
        delta=delta,
        action_type=action_type,
        reason=reason,
        source=source,
        reference_id=reference_id,
        created_at=datetime.utcnow()
    )
    db.add(xp_log)
    db.flush()
    
    return xp_log


def award_xp(
    db: Session,
    user: User,
    action_type: str,
    context: dict
) -> XPAwardResult:
    """
    Orchestrate XP calculation and awarding for a user action.
    
    This is the main entry point for awarding XP. It:
    1. Calculates base XP based on action type and context
    2. Applies streak multipliers
    3. Records the transaction in XPLog
    4. Updates the user's total_xp field
    
    Args:
        db: Database session
        user: User model instance
        action_type: Type of action triggering XP award
                    ("meal_logged", "macro_goal", "daily_goal")
        context: Additional context for XP calculation
                - For "meal_logged": {"meal_id": int}
                - For "macro_goal": {"completed_macros": ["protein", "carbs"]}
                - For "daily_goal": {}
                
    Returns:
        XPAwardResult with details about the XP awarded
        
    References: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8
    """
    # Calculate base XP based on action type
    base_xp = 0
    breakdown = {}
    reference_id = None
    source = "meal_log"
    
    if action_type == "meal_logged":
        meal_xp = calculate_xp_for_meal()
        base_xp += meal_xp
        breakdown["meal_logged"] = meal_xp
        reference_id = context.get("meal_id")
        
    elif action_type == "macro_goal":
        completed_macros = context.get("completed_macros", [])
        macro_xp = calculate_macro_goal_xp(completed_macros)
        base_xp += macro_xp
        breakdown["macro_goals_completed"] = completed_macros
        breakdown["macro_goal_xp"] = macro_xp
        
    elif action_type == "daily_goal":
        daily_xp = calculate_daily_goal_xp()
        base_xp += daily_xp
        breakdown["daily_goal_completed"] = True
        breakdown["daily_goal_xp"] = daily_xp
    
    # Apply streak multiplier
    streak_days = user.current_streak or 0
    total_xp = apply_streak_multiplier(base_xp, streak_days)
    
    # Determine multiplier for breakdown
    if streak_days >= 30:
        multiplier = STREAK_MULTIPLIER_30_DAYS
    elif streak_days >= 7:
        multiplier = STREAK_MULTIPLIER_7_DAYS
    else:
        multiplier = 1.0
    
    breakdown["streak_multiplier"] = multiplier
    breakdown["base_xp"] = base_xp
    breakdown["total_xp"] = total_xp
    
    # Record XP transaction with unique reason
    # Add timestamp to make reason unique for multiple meals per day
    timestamp = datetime.utcnow().isoformat()
    
    if action_type == "meal_logged":
        # Include timestamp to allow multiple meals per day
        reason = f"Meal logged at {timestamp}"
    elif action_type == "macro_goal":
        completed = context.get("completed_macros", [])
        # Include date to allow one macro goal award per day
        date_str = datetime.utcnow().date().isoformat()
        reason = f"Macro goals ({', '.join(completed)}) on {date_str}"
    elif action_type == "daily_goal":
        # Include date to allow one daily goal award per day
        date_str = datetime.utcnow().date().isoformat()
        reason = f"Daily goal completed on {date_str}"
    else:
        reason = f"{action_type} at {timestamp}"
    
    record_xp_transaction(
        db=db,
        user_id=user.id,
        gym_id=user.gym_id,
        delta=total_xp,
        action_type=action_type,
        reason=reason,
        source=source,
        reference_id=reference_id
    )
    
    # Update user's total XP with overflow protection (Requirement 15.3)
    current_xp = user.total_xp or 0
    new_total_xp = current_xp + total_xp
    
    # Check for overflow
    if new_total_xp > MAX_XP:
        logger.warning(
            f"XP overflow detected for user {user.id}: "
            f"current={current_xp}, award={total_xp}, would be={new_total_xp}. "
            f"Capping at {MAX_XP}"
        )
        user.total_xp = MAX_XP
    else:
        user.total_xp = new_total_xp
    
    db.flush()
    
    return XPAwardResult(
        total_xp_awarded=total_xp,
        base_xp=base_xp,
        multiplier=multiplier,
        breakdown=breakdown
    )


def award_xp_batched(
    db: Session,
    user: User,
    action_type: str,
    context: dict
) -> XPAwardResult:
    """
    Award XP with batching support.
    
    Collects multiple XP awards within 1 second and executes them
    as a single database transaction for improved performance.
    
    This function:
    1. Adds the award to a batch for the user
    2. Waits for the batch window to expire (1 second)
    3. Processes all awards in the batch as a single transaction
    4. Returns combined result
    
    Args:
        db: Database session
        user: User model instance
        action_type: Type of action triggering XP award
        context: Additional context for XP calculation
        
    Returns:
        XPAwardResult with combined totals from all batched awards
        
    References: Requirement 17.5
    """
    batch = _batch_manager.get_or_create_batch(user.id)
    batch.add_award(action_type, context)
    
    # Wait for batch window to expire
    while not batch.is_expired():
        time.sleep(0.1)
    
    # Process the batch
    awards = batch.get_awards()
    _batch_manager.remove_batch(user.id)
    
    # Execute all awards in a single transaction
    return _execute_batched_awards(db, user, awards)


def _execute_batched_awards(
    db: Session,
    user: User,
    awards: list[dict]
) -> XPAwardResult:
    """
    Execute multiple XP awards in a single database transaction.
    
    Args:
        db: Database session
        user: User model instance
        awards: List of award dictionaries with action_type and context
        
    Returns:
        XPAwardResult with combined totals
    """
    total_xp_awarded = 0
    total_base_xp = 0
    combined_breakdown = {
        "awards": [],
        "total_awards": len(awards)
    }
    
    # Calculate XP for each award
    for award in awards:
        action_type = award["action_type"]
        context = award["context"]
        
        # Calculate base XP
        base_xp = 0
        award_breakdown = {"action_type": action_type}
        
        if action_type == "meal_logged":
            meal_xp = calculate_xp_for_meal()
            base_xp += meal_xp
            award_breakdown["meal_logged"] = meal_xp
            
        elif action_type == "macro_goal":
            completed_macros = context.get("completed_macros", [])
            macro_xp = calculate_macro_goal_xp(completed_macros)
            base_xp += macro_xp
            award_breakdown["macro_goals_completed"] = completed_macros
            award_breakdown["macro_goal_xp"] = macro_xp
            
        elif action_type == "daily_goal":
            daily_xp = calculate_daily_goal_xp()
            base_xp += daily_xp
            award_breakdown["daily_goal_completed"] = True
            award_breakdown["daily_goal_xp"] = daily_xp
        
        total_base_xp += base_xp
        award_breakdown["base_xp"] = base_xp
        combined_breakdown["awards"].append(award_breakdown)
    
    # Apply streak multiplier to total base XP
    streak_days = user.current_streak or 0
    total_xp_awarded = apply_streak_multiplier(total_base_xp, streak_days)
    
    # Determine multiplier
    if streak_days >= 30:
        multiplier = STREAK_MULTIPLIER_30_DAYS
    elif streak_days >= 7:
        multiplier = STREAK_MULTIPLIER_7_DAYS
    else:
        multiplier = 1.0
    
    combined_breakdown["streak_multiplier"] = multiplier
    combined_breakdown["total_base_xp"] = total_base_xp
    combined_breakdown["total_xp"] = total_xp_awarded
    
    # Record single XP transaction for the batch
    reason = f"Batched {len(awards)} XP awards: {total_xp_awarded} total XP"
    record_xp_transaction(
        db=db,
        user_id=user.id,
        gym_id=user.gym_id,
        delta=total_xp_awarded,
        action_type="batched",
        reason=reason
    )
    
    # Update user's total XP once
    user.total_xp = (user.total_xp or 0) + total_xp_awarded
    db.flush()
    
    return XPAwardResult(
        total_xp_awarded=total_xp_awarded,
        base_xp=total_base_xp,
        multiplier=multiplier,
        breakdown=combined_breakdown
    )
