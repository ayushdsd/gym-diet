"""
Timezone utilities for streak tracking.

This module provides timezone-aware date and time calculations for the gamification system.
Users in different locations should have streaks calculated based on their local midnight,
not UTC. The gym location determines the user's timezone.

Includes fallback handling for invalid timezones (Requirement 15.6).

References Requirements: 14.1, 14.2, 14.7, 14.8, 15.6
"""

from datetime import datetime, date, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import logging


# Configure logging
logger = logging.getLogger(__name__)


# Mapping of gym locations to IANA timezone identifiers
LOCATION_TIMEZONE_MAP = {
    "New York": "America/New_York",
    "Los Angeles": "America/Los_Angeles",
    "Chicago": "America/Chicago",
    "Houston": "America/Chicago",
    "Phoenix": "America/Phoenix",
    "Philadelphia": "America/New_York",
    "San Antonio": "America/Chicago",
    "San Diego": "America/Los_Angeles",
    "Dallas": "America/Chicago",
    "San Jose": "America/Los_Angeles",
    "Austin": "America/Chicago",
    "Jacksonville": "America/New_York",
    "Fort Worth": "America/Chicago",
    "Columbus": "America/New_York",
    "Charlotte": "America/New_York",
    "San Francisco": "America/Los_Angeles",
    "Indianapolis": "America/Indiana/Indianapolis",
    "Seattle": "America/Los_Angeles",
    "Denver": "America/Denver",
    "Boston": "America/New_York",
    "London": "Europe/London",
    "Paris": "Europe/Paris",
    "Berlin": "Europe/Berlin",
    "Tokyo": "Asia/Tokyo",
    "Sydney": "Australia/Sydney",
    "Toronto": "America/Toronto",
    "Vancouver": "America/Vancouver",
    "Mumbai": "Asia/Kolkata",
    "Singapore": "Asia/Singapore",
    "Dubai": "Asia/Dubai",
}


def get_user_timezone(user) -> str:
    """
    Get IANA timezone identifier from user's gym location.
    
    Includes fallback to UTC for invalid timezones (Requirement 15.6).
    
    Args:
        user: User model instance with gym relationship loaded
        
    Returns:
        IANA timezone identifier (e.g., 'America/New_York')
        Falls back to UTC if location not found in mapping
        
    References: Requirement 14.1, 14.8, 15.6
    """
    if not user.gym:
        logger.warning(f"User {user.id} has no gym, defaulting to UTC timezone")
        return "UTC"
    
    location = user.gym.location
    timezone = LOCATION_TIMEZONE_MAP.get(location, "UTC")
    
    if timezone == "UTC" and location not in ["UTC"]:
        logger.warning(
            f"No timezone mapping found for gym location '{location}' "
            f"(user {user.id}), defaulting to UTC"
        )
    
    return timezone


def convert_to_user_timezone(timestamp: datetime, timezone_str: str) -> datetime:
    """
    Convert UTC timestamp to user's timezone.
    
    Includes fallback to UTC for invalid timezone strings (Requirement 15.6).
    
    Args:
        timestamp: UTC datetime (should be timezone-aware)
        timezone_str: IANA timezone identifier (e.g., 'America/New_York')
        
    Returns:
        datetime object in the user's timezone (or UTC if timezone invalid)
        
    References: Requirement 14.2, 14.7, 15.6
    """
    # Ensure timestamp is timezone-aware (UTC)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=ZoneInfo("UTC"))
    
    # Convert to user's timezone with fallback
    try:
        user_tz = ZoneInfo(timezone_str)
        return timestamp.astimezone(user_tz)
    except ZoneInfoNotFoundError:
        logger.warning(
            f"Invalid timezone '{timezone_str}', falling back to UTC"
        )
        return timestamp.astimezone(ZoneInfo("UTC"))


def get_day_boundary(timezone_str: str, reference_date: date = None) -> datetime:
    """
    Get midnight (00:00:00) for a specific date in the given timezone, returned as UTC.
    
    This is used to determine when a new day starts for streak tracking purposes.
    For example, if a user is in New York (EST, UTC-5), their day boundary for
    January 15 would be at 05:00:00 UTC (which is midnight EST).
    
    Includes fallback to UTC for invalid timezone strings (Requirement 15.6).
    
    Args:
        timezone_str: IANA timezone identifier (e.g., 'America/New_York')
        reference_date: The date to get midnight for (defaults to today in that timezone)
        
    Returns:
        datetime object representing midnight in that timezone, converted to UTC
        
    References: Requirement 14.2, 14.7, 15.6
    """
    try:
        tz = ZoneInfo(timezone_str)
    except ZoneInfoNotFoundError:
        logger.warning(
            f"Invalid timezone '{timezone_str}' in get_day_boundary, falling back to UTC"
        )
        tz = ZoneInfo("UTC")
    
    # If no reference date provided, use today in that timezone
    if reference_date is None:
        now_in_tz = datetime.now(tz)
        reference_date = now_in_tz.date()
    
    # Create midnight in the user's timezone
    midnight_local = datetime.combine(reference_date, time(0, 0, 0))
    midnight_aware = midnight_local.replace(tzinfo=tz)
    
    # Convert to UTC for storage/comparison
    return midnight_aware.astimezone(ZoneInfo("UTC"))


def get_user_date(timestamp: datetime, timezone_str: str) -> date:
    """
    Convert UTC timestamp to user's local date.
    
    This is critical for streak tracking - a meal logged at 04:30 UTC might be
    on January 14 in New York (23:30 EST) but January 15 in UTC.
    
    Includes fallback to UTC for invalid timezone strings (Requirement 15.6).
    
    Args:
        timestamp: UTC datetime
        timezone_str: User's IANA timezone identifier
        
    Returns:
        date in user's timezone (or UTC if timezone invalid)
        
    References: Requirement 14.3, 14.7, 15.6
    """
    local_time = convert_to_user_timezone(timestamp, timezone_str)
    return local_time.date()
