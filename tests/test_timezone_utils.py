"""
Unit tests for timezone utilities.

Tests timezone-aware date and time calculations for streak tracking.
"""

import pytest
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from unittest.mock import Mock

from app.services.timezone_utils import (
    get_user_timezone,
    convert_to_user_timezone,
    get_day_boundary,
    get_user_date,
    LOCATION_TIMEZONE_MAP,
)


class TestGetUserTimezone:
    """Test get_user_timezone function."""
    
    def test_returns_timezone_for_known_location(self):
        """Should return correct timezone for known gym location."""
        user = Mock()
        user.gym = Mock()
        user.gym.location = "New York"
        
        result = get_user_timezone(user)
        
        assert result == "America/New_York"
    
    def test_returns_utc_for_unknown_location(self):
        """Should return UTC for unknown gym location."""
        user = Mock()
        user.gym = Mock()
        user.gym.location = "Unknown City"
        
        result = get_user_timezone(user)
        
        assert result == "UTC"
    
    def test_returns_utc_when_no_gym(self):
        """Should return UTC when user has no gym."""
        user = Mock()
        user.gym = None
        
        result = get_user_timezone(user)
        
        assert result == "UTC"
    
    def test_all_mapped_locations_are_valid_timezones(self):
        """All timezone strings in the mapping should be valid IANA identifiers."""
        for location, tz_str in LOCATION_TIMEZONE_MAP.items():
            # This will raise an exception if timezone is invalid
            ZoneInfo(tz_str)
    
    def test_handles_case_sensitive_location(self):
        """Should handle exact case matching for location names."""
        user = Mock()
        user.gym = Mock()
        user.gym.location = "new york"  # lowercase
        
        result = get_user_timezone(user)
        
        # Should return UTC since case doesn't match
        assert result == "UTC"


class TestConvertToUserTimezone:
    """Test convert_to_user_timezone function."""
    
    def test_converts_utc_to_eastern_time(self):
        """Should correctly convert UTC to Eastern time."""
        # 5 PM UTC = 12 PM EST (UTC-5)
        utc_time = datetime(2024, 1, 15, 17, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        result = convert_to_user_timezone(utc_time, "America/New_York")
        
        assert result.hour == 12
        assert result.day == 15
        assert result.tzinfo == ZoneInfo("America/New_York")
    
    def test_converts_utc_to_pacific_time(self):
        """Should correctly convert UTC to Pacific time."""
        # 5 PM UTC = 9 AM PST (UTC-8)
        utc_time = datetime(2024, 1, 15, 17, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        result = convert_to_user_timezone(utc_time, "America/Los_Angeles")
        
        assert result.hour == 9
        assert result.day == 15
        assert result.tzinfo == ZoneInfo("America/Los_Angeles")
    
    def test_handles_naive_datetime(self):
        """Should handle naive datetime by assuming UTC."""
        naive_time = datetime(2024, 1, 15, 17, 0, 0)
        
        result = convert_to_user_timezone(naive_time, "America/New_York")
        
        assert result.hour == 12
        assert result.day == 15
    
    def test_handles_day_boundary_crossing(self):
        """Should correctly handle when conversion crosses day boundary."""
        # 2 AM UTC = 9 PM previous day EST
        utc_time = datetime(2024, 1, 15, 2, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        result = convert_to_user_timezone(utc_time, "America/New_York")
        
        assert result.hour == 21  # 9 PM
        assert result.day == 14  # Previous day
    
    def test_handles_utc_timezone_string(self):
        """Should handle UTC timezone string correctly."""
        utc_time = datetime(2024, 1, 15, 17, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        result = convert_to_user_timezone(utc_time, "UTC")
        
        assert result.hour == 17
        assert result.day == 15
        assert result.tzinfo == ZoneInfo("UTC")


class TestGetDayBoundary:
    """Test get_day_boundary function."""
    
    def test_returns_midnight_in_utc_for_eastern_timezone(self):
        """Should return midnight EST as UTC datetime."""
        # Midnight on Jan 15 EST = 5 AM UTC
        reference = date(2024, 1, 15)
        
        result = get_day_boundary("America/New_York", reference)
        
        assert result.hour == 5
        assert result.day == 15
        assert result.tzinfo == ZoneInfo("UTC")
    
    def test_returns_midnight_in_utc_for_pacific_timezone(self):
        """Should return midnight PST as UTC datetime."""
        # Midnight on Jan 15 PST = 8 AM UTC
        reference = date(2024, 1, 15)
        
        result = get_day_boundary("America/Los_Angeles", reference)
        
        assert result.hour == 8
        assert result.day == 15
        assert result.tzinfo == ZoneInfo("UTC")
    
    def test_uses_current_date_when_no_reference_provided(self):
        """Should use current date in timezone when reference_date is None."""
        result = get_day_boundary("America/New_York")
        
        # Should be a valid UTC datetime
        assert result.tzinfo == ZoneInfo("UTC")
        assert isinstance(result, datetime)
    
    def test_handles_utc_timezone(self):
        """Should handle UTC timezone correctly."""
        reference = date(2024, 1, 15)
        
        result = get_day_boundary("UTC", reference)
        
        assert result.hour == 0
        assert result.day == 15
        assert result.tzinfo == ZoneInfo("UTC")
    
    def test_handles_daylight_saving_time(self):
        """Should correctly handle DST transitions."""
        # Summer date when DST is active (EDT = UTC-4)
        summer_date = date(2024, 7, 15)
        
        result = get_day_boundary("America/New_York", summer_date)
        
        # Midnight EDT = 4 AM UTC (not 5 AM like EST)
        assert result.hour == 4
        assert result.day == 15


class TestGetUserDate:
    """Test get_user_date function."""
    
    def test_returns_correct_date_in_user_timezone(self):
        """Should return date in user's timezone, not UTC."""
        # 2 AM UTC on Jan 15 = 9 PM EST on Jan 14
        utc_time = datetime(2024, 1, 15, 2, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        result = get_user_date(utc_time, "America/New_York")
        
        assert result == date(2024, 1, 14)
    
    def test_returns_same_date_when_no_boundary_crossing(self):
        """Should return same date when conversion doesn't cross day boundary."""
        # 5 PM UTC on Jan 15 = 12 PM EST on Jan 15
        utc_time = datetime(2024, 1, 15, 17, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        result = get_user_date(utc_time, "America/New_York")
        
        assert result == date(2024, 1, 15)
    
    def test_handles_pacific_timezone(self):
        """Should correctly handle Pacific timezone."""
        # 5 AM UTC on Jan 15 = 9 PM PST on Jan 14
        utc_time = datetime(2024, 1, 15, 5, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        result = get_user_date(utc_time, "America/Los_Angeles")
        
        assert result == date(2024, 1, 14)
    
    def test_handles_utc_timezone(self):
        """Should handle UTC timezone correctly."""
        utc_time = datetime(2024, 1, 15, 2, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        result = get_user_date(utc_time, "UTC")
        
        assert result == date(2024, 1, 15)


class TestTimezoneIntegration:
    """Integration tests for timezone utilities working together."""
    
    def test_streak_scenario_before_midnight_local(self):
        """
        Test realistic streak scenario: user logs meal before local midnight.
        
        User in New York logs meal at 11:30 PM EST on Jan 14.
        This is 4:30 AM UTC on Jan 15.
        Should count as activity for Jan 14 in user's timezone.
        """
        # 4:30 AM UTC on Jan 15
        utc_timestamp = datetime(2024, 1, 15, 4, 30, 0, tzinfo=ZoneInfo("UTC"))
        timezone = "America/New_York"
        
        # Get user's local date
        user_date = get_user_date(utc_timestamp, timezone)
        
        # Should be Jan 14 (11:30 PM EST)
        assert user_date == date(2024, 1, 14)
        
        # Get day boundary for Jan 15
        next_day_boundary = get_day_boundary(timezone, date(2024, 1, 15))
        
        # User's action was before the Jan 15 boundary
        assert utc_timestamp < next_day_boundary
    
    def test_streak_scenario_after_midnight_local(self):
        """
        Test realistic streak scenario: user logs meal after local midnight.
        
        User in New York logs meal at 12:30 AM EST on Jan 15.
        This is 5:30 AM UTC on Jan 15.
        Should count as activity for Jan 15 in user's timezone.
        """
        # 5:30 AM UTC on Jan 15
        utc_timestamp = datetime(2024, 1, 15, 5, 30, 0, tzinfo=ZoneInfo("UTC"))
        timezone = "America/New_York"
        
        # Get user's local date
        user_date = get_user_date(utc_timestamp, timezone)
        
        # Should be Jan 15 (12:30 AM EST)
        assert user_date == date(2024, 1, 15)
        
        # Get day boundary for Jan 15
        day_boundary = get_day_boundary(timezone, date(2024, 1, 15))
        
        # User's action was after the Jan 15 boundary
        assert utc_timestamp > day_boundary
    
    def test_cross_timezone_comparison(self):
        """
        Test that same UTC time results in different dates for different timezones.
        """
        # 3 AM UTC on Jan 15
        utc_timestamp = datetime(2024, 1, 15, 3, 0, 0, tzinfo=ZoneInfo("UTC"))
        
        # New York: 10 PM EST on Jan 14
        ny_date = get_user_date(utc_timestamp, "America/New_York")
        assert ny_date == date(2024, 1, 14)
        
        # Los Angeles: 7 PM PST on Jan 14
        la_date = get_user_date(utc_timestamp, "America/Los_Angeles")
        assert la_date == date(2024, 1, 14)
        
        # Tokyo: 12 PM JST on Jan 15
        tokyo_date = get_user_date(utc_timestamp, "Asia/Tokyo")
        assert tokyo_date == date(2024, 1, 15)
    
    def test_dst_transition_spring_forward(self):
        """
        Test DST transition when clocks spring forward (2 AM -> 3 AM).
        
        In 2024, DST starts on March 10 at 2:00 AM EST -> 3:00 AM EDT.
        Verify day boundary calculation handles the missing hour correctly.
        """
        # Day before DST transition
        before_dst = date(2024, 3, 9)
        boundary_before = get_day_boundary("America/New_York", before_dst)
        # Midnight EST = 5 AM UTC
        assert boundary_before.hour == 5
        
        # Day of DST transition
        dst_day = date(2024, 3, 10)
        boundary_dst = get_day_boundary("America/New_York", dst_day)
        # Midnight EST = 5 AM UTC (still EST at midnight)
        assert boundary_dst.hour == 5
        
        # Day after DST transition
        after_dst = date(2024, 3, 11)
        boundary_after = get_day_boundary("America/New_York", after_dst)
        # Midnight EDT = 4 AM UTC
        assert boundary_after.hour == 4
    
    def test_dst_transition_fall_back(self):
        """
        Test DST transition when clocks fall back (2 AM -> 1 AM).
        
        In 2024, DST ends on November 3 at 2:00 AM EDT -> 1:00 AM EST.
        Verify day boundary calculation handles the repeated hour correctly.
        """
        # Day before DST ends
        before_dst = date(2024, 11, 2)
        boundary_before = get_day_boundary("America/New_York", before_dst)
        # Midnight EDT = 4 AM UTC
        assert boundary_before.hour == 4
        
        # Day DST ends
        dst_end_day = date(2024, 11, 3)
        boundary_dst = get_day_boundary("America/New_York", dst_end_day)
        # Midnight EDT = 4 AM UTC (still EDT at midnight)
        assert boundary_dst.hour == 4
        
        # Day after DST ends
        after_dst = date(2024, 11, 4)
        boundary_after = get_day_boundary("America/New_York", after_dst)
        # Midnight EST = 5 AM UTC
        assert boundary_after.hour == 5
    
    def test_multiple_timezone_day_boundaries_same_date(self):
        """
        Test that day boundaries for the same date differ across timezones.
        
        Midnight on Jan 15 occurs at different UTC times in different locations.
        """
        reference = date(2024, 1, 15)
        
        # Get midnight for Jan 15 in different timezones (as UTC)
        ny_boundary = get_day_boundary("America/New_York", reference)
        la_boundary = get_day_boundary("America/Los_Angeles", reference)
        london_boundary = get_day_boundary("Europe/London", reference)
        tokyo_boundary = get_day_boundary("Asia/Tokyo", reference)
        
        # All should be different UTC times
        assert ny_boundary != la_boundary
        assert ny_boundary != london_boundary
        assert ny_boundary != tokyo_boundary
        
        # New York midnight (EST) = 5 AM UTC
        assert ny_boundary.hour == 5
        
        # Los Angeles midnight (PST) = 8 AM UTC
        assert la_boundary.hour == 8
        
        # London midnight (GMT) = 0 AM UTC
        assert london_boundary.hour == 0
        
        # Tokyo midnight (JST) = 3 PM previous day UTC
        assert tokyo_boundary.day == 14
        assert tokyo_boundary.hour == 15
