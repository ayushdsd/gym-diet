"""
Level System Service

Handles all level progression calculations for the gamification system.
The level formula ensures smooth progression where each level requires 
progressively more XP. Milestone levels (5, 10, 20, 50, 100) award streak freezes.

References Requirements: 2.1, 2.2, 2.3, 2.6, 2.7, 17.3
"""

from functools import lru_cache
from math import sqrt, floor


# Milestone levels that award streak freezes
MILESTONE_LEVELS = [5, 10, 20, 50, 100]


@lru_cache(maxsize=1024)
def calculate_level(total_xp: int) -> int:
    """
    Calculate user level from total XP with caching.
    
    Formula: level = floor(sqrt(total_xp / 100))
    Minimum level is 1.
    
    Uses LRU cache to avoid repeated square root calculations for the same XP values.
    Cache size of 1024 entries is sufficient for typical usage patterns.
    
    Args:
        total_xp: Total experience points earned by the user
        
    Returns:
        Current level (minimum 1)
        
    Examples:
        >>> calculate_level(0)
        1
        >>> calculate_level(100)
        1
        >>> calculate_level(400)
        2
        >>> calculate_level(900)
        3
        >>> calculate_level(10000)
        10
    """
    if total_xp < 0:
        total_xp = 0
    
    level = floor(sqrt(total_xp / 100))
    return max(1, level)


@lru_cache(maxsize=256)
def get_level_threshold(level: int) -> int:
    """
    Get total XP required to reach a specific level with caching.
    
    Formula: level² × 100
    
    Uses LRU cache for frequently accessed level thresholds.
    Cache size of 256 entries covers levels 1-256.
    
    Args:
        level: Target level
        
    Returns:
        Total XP required to reach that level
        
    Examples:
        >>> get_level_threshold(1)
        100
        >>> get_level_threshold(2)
        400
        >>> get_level_threshold(5)
        2500
        >>> get_level_threshold(10)
        10000
    """
    return level * level * 100


def calculate_xp_for_next_level(current_level: int, total_xp: int) -> int:
    """
    Calculate XP needed to reach the next level.
    
    Formula: (level + 1)² × 100 - total_xp
    
    Args:
        current_level: User's current level
        total_xp: User's current total XP
        
    Returns:
        XP needed for next level (0 if already at or above threshold)
        
    Examples:
        >>> calculate_xp_for_next_level(1, 100)
        300
        >>> calculate_xp_for_next_level(2, 400)
        500
        >>> calculate_xp_for_next_level(5, 2000)
        1600
    """
    next_level_threshold = get_level_threshold(current_level + 1)
    xp_needed = next_level_threshold - total_xp
    return max(0, xp_needed)


def is_milestone_level(level: int) -> bool:
    """
    Check if a level is a milestone level.
    
    Milestone levels (5, 10, 20, 50, 100) award streak freezes.
    
    Args:
        level: Level to check
        
    Returns:
        True if level is a milestone, False otherwise
        
    Examples:
        >>> is_milestone_level(5)
        True
        >>> is_milestone_level(10)
        True
        >>> is_milestone_level(7)
        False
        >>> is_milestone_level(100)
        True
    """
    return level in MILESTONE_LEVELS


def check_level_up(old_xp: int, new_xp: int) -> tuple[bool, int, int]:
    """
    Check if XP gain caused a level up.
    
    Args:
        old_xp: XP before the gain
        new_xp: XP after the gain
        
    Returns:
        Tuple of (level_up_occurred, old_level, new_level)
        
    Examples:
        >>> check_level_up(300, 350)
        (False, 1, 1)
        >>> check_level_up(350, 400)
        (True, 1, 2)
        >>> check_level_up(2400, 2600)
        (True, 4, 5)
        >>> check_level_up(2400, 10000)
        (True, 4, 10)
    """
    old_level = calculate_level(old_xp)
    new_level = calculate_level(new_xp)
    level_up_occurred = new_level > old_level
    
    return (level_up_occurred, old_level, new_level)
