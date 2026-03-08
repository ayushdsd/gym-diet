"""
Unit tests for LevelSystem service

Tests verify the level progression formula, XP calculations, milestone detection,
and level-up logic as specified in Requirements 18.2.

**Validates: Requirements 18.2**
"""

import pytest
from app.services.level_system import (
    calculate_level,
    get_level_threshold,
    calculate_xp_for_next_level,
    is_milestone_level,
    check_level_up,
    MILESTONE_LEVELS
)


class TestCalculateLevel:
    """Test level calculation from total XP"""
    
    def test_level_calculation_for_zero_xp(self):
        """Test that 0 XP returns level 1 (minimum level)"""
        assert calculate_level(0) == 1
    
    def test_level_calculation_for_100_xp(self):
        """Test that 100 XP returns level 1"""
        assert calculate_level(100) == 1
    
    def test_level_calculation_for_400_xp(self):
        """Test that 400 XP returns level 2"""
        assert calculate_level(400) == 2
    
    def test_level_calculation_for_10000_xp(self):
        """Test that 10000 XP returns level 10"""
        assert calculate_level(10000) == 10
    
    def test_minimum_level_is_one_for_all_positive_xp(self):
        """Test that minimum level is 1 for all XP >= 0"""
        assert calculate_level(0) == 1
        assert calculate_level(1) == 1
        assert calculate_level(50) == 1
        assert calculate_level(99) == 1
    
    def test_negative_xp_returns_level_one(self):
        """Test that negative XP is treated as 0 and returns level 1"""
        assert calculate_level(-100) == 1
        assert calculate_level(-1) == 1
    
    def test_level_progression_sequence(self):
        """Test level progression at key thresholds"""
        # Level 1: 0-399 XP
        assert calculate_level(0) == 1
        assert calculate_level(399) == 1
        
        # Level 2: 400-899 XP
        assert calculate_level(400) == 2
        assert calculate_level(899) == 2
        
        # Level 3: 900-1599 XP
        assert calculate_level(900) == 3
        assert calculate_level(1599) == 3
        
        # Level 5: 2500-3599 XP
        assert calculate_level(2500) == 5
        assert calculate_level(3599) == 5
        
        # Level 10: 10000-12099 XP
        assert calculate_level(10000) == 10
        assert calculate_level(12099) == 10


class TestGetLevelThreshold:
    """Test XP threshold calculation for levels"""
    
    def test_threshold_for_level_1(self):
        """Test that level 1 requires 100 XP"""
        assert get_level_threshold(1) == 100
    
    def test_threshold_for_level_2(self):
        """Test that level 2 requires 400 XP"""
        assert get_level_threshold(2) == 400
    
    def test_threshold_for_level_5(self):
        """Test that level 5 requires 2500 XP"""
        assert get_level_threshold(5) == 2500
    
    def test_threshold_for_level_10(self):
        """Test that level 10 requires 10000 XP"""
        assert get_level_threshold(10) == 10000
    
    def test_threshold_for_milestone_levels(self):
        """Test thresholds for all milestone levels"""
        assert get_level_threshold(5) == 2500
        assert get_level_threshold(10) == 10000
        assert get_level_threshold(20) == 40000
        assert get_level_threshold(50) == 250000
        assert get_level_threshold(100) == 1000000


class TestCalculateXpForNextLevel:
    """Test XP needed for next level calculation"""
    
    def test_xp_for_next_level_at_threshold(self):
        """Test XP needed when exactly at level threshold"""
        # At level 1 (100 XP), need 300 more for level 2 (400 XP)
        assert calculate_xp_for_next_level(1, 100) == 300
        
        # At level 2 (400 XP), need 500 more for level 3 (900 XP)
        assert calculate_xp_for_next_level(2, 400) == 500
    
    def test_xp_for_next_level_mid_progress(self):
        """Test XP needed when in the middle of a level"""
        # At level 5 with 2000 XP, need 1600 more for level 6 (3600 XP)
        assert calculate_xp_for_next_level(5, 2000) == 1600
        
        # At level 1 with 200 XP, need 200 more for level 2 (400 XP)
        assert calculate_xp_for_next_level(1, 200) == 200
    
    def test_xp_for_next_level_returns_zero_when_above_threshold(self):
        """Test that XP needed is 0 when already at or above next level threshold"""
        # If somehow at level 1 but with 500 XP (level 2 threshold is 400)
        assert calculate_xp_for_next_level(1, 500) == 0
    
    def test_xp_for_next_level_various_scenarios(self):
        """Test XP calculations for various level/XP combinations"""
        # Level 3 (900 XP threshold) with 1000 XP, need 600 for level 4 (1600 XP)
        assert calculate_xp_for_next_level(3, 1000) == 600
        
        # Level 10 (10000 XP threshold) with 10500 XP, need 1600 for level 11 (12100 XP)
        assert calculate_xp_for_next_level(10, 10500) == 1600


class TestIsMilestoneLevel:
    """Test milestone level detection"""
    
    def test_milestone_levels_are_detected(self):
        """Test that all milestone levels (5, 10, 20, 50, 100) are detected"""
        assert is_milestone_level(5) is True
        assert is_milestone_level(10) is True
        assert is_milestone_level(20) is True
        assert is_milestone_level(50) is True
        assert is_milestone_level(100) is True
    
    def test_non_milestone_levels_are_not_detected(self):
        """Test that non-milestone levels return False"""
        assert is_milestone_level(1) is False
        assert is_milestone_level(2) is False
        assert is_milestone_level(7) is False
        assert is_milestone_level(15) is False
        assert is_milestone_level(25) is False
        assert is_milestone_level(99) is False
        assert is_milestone_level(101) is False
    
    def test_milestone_levels_constant(self):
        """Test that MILESTONE_LEVELS constant is correct"""
        assert MILESTONE_LEVELS == [5, 10, 20, 50, 100]


class TestCheckLevelUp:
    """Test level-up detection across XP boundaries"""
    
    def test_no_level_up_within_same_level(self):
        """Test that no level-up occurs when staying within the same level"""
        level_up, old_level, new_level = check_level_up(300, 350)
        assert level_up is False
        assert old_level == 1
        assert new_level == 1
    
    def test_level_up_at_exact_boundary(self):
        """Test level-up when crossing exact level boundary"""
        # From 350 XP (level 1) to 400 XP (level 2)
        level_up, old_level, new_level = check_level_up(350, 400)
        assert level_up is True
        assert old_level == 1
        assert new_level == 2
    
    def test_level_up_crossing_boundary(self):
        """Test level-up when crossing level boundary"""
        # From 2400 XP (level 4) to 2600 XP (level 5)
        level_up, old_level, new_level = check_level_up(2400, 2600)
        assert level_up is True
        assert old_level == 4
        assert new_level == 5
    
    def test_multiple_level_ups_in_single_gain(self):
        """Test multiple level-ups in a single XP gain"""
        # From 2400 XP (level 4) to 10000 XP (level 10)
        level_up, old_level, new_level = check_level_up(2400, 10000)
        assert level_up is True
        assert old_level == 4
        assert new_level == 10
    
    def test_level_up_from_zero_xp(self):
        """Test level-up detection starting from 0 XP"""
        # From 0 XP (level 1) to 100 XP (still level 1)
        level_up, old_level, new_level = check_level_up(0, 100)
        assert level_up is False
        assert old_level == 1
        assert new_level == 1
        
        # From 0 XP (level 1) to 400 XP (level 2)
        level_up, old_level, new_level = check_level_up(0, 400)
        assert level_up is True
        assert old_level == 1
        assert new_level == 2
    
    def test_level_up_to_milestone_levels(self):
        """Test level-up detection when reaching milestone levels"""
        # To level 5 (milestone)
        level_up, old_level, new_level = check_level_up(2400, 2500)
        assert level_up is True
        assert old_level == 4
        assert new_level == 5
        
        # To level 10 (milestone)
        level_up, old_level, new_level = check_level_up(9900, 10000)
        assert level_up is True
        assert old_level == 9
        assert new_level == 10
        
        # To level 20 (milestone)
        level_up, old_level, new_level = check_level_up(39900, 40000)
        assert level_up is True
        assert old_level == 19
        assert new_level == 20


class TestLevelSystemIntegration:
    """Integration tests for level system components working together"""
    
    def test_level_progression_consistency(self):
        """Test that level calculations are consistent across functions"""
        xp = 2500
        level = calculate_level(xp)
        threshold = get_level_threshold(level)
        
        # The threshold for the calculated level should be <= current XP
        assert threshold <= xp
        
        # The threshold for next level should be > current XP
        next_threshold = get_level_threshold(level + 1)
        assert next_threshold > xp
    
    def test_xp_for_next_level_matches_threshold_difference(self):
        """Test that XP for next level matches the difference in thresholds"""
        current_level = 5
        total_xp = 3000
        
        xp_needed = calculate_xp_for_next_level(current_level, total_xp)
        next_threshold = get_level_threshold(current_level + 1)
        
        assert xp_needed == next_threshold - total_xp
    
    def test_level_up_detection_matches_calculate_level(self):
        """Test that check_level_up results match calculate_level"""
        old_xp = 2400
        new_xp = 2600
        
        level_up, old_level, new_level = check_level_up(old_xp, new_xp)
        
        assert old_level == calculate_level(old_xp)
        assert new_level == calculate_level(new_xp)
        assert level_up == (new_level > old_level)


class TestLevelSystemCaching:
    """Tests for level calculation caching functionality"""
    
    def test_calculate_level_caching_returns_same_result(self):
        """Test that cached results match uncached results"""
        # Clear cache before test
        calculate_level.cache_clear()
        
        # First call - cache miss
        result1 = calculate_level(2500)
        
        # Second call - cache hit
        result2 = calculate_level(2500)
        
        # Results should be identical
        assert result1 == result2
        assert result1 == 5
    
    def test_calculate_level_cache_info(self):
        """Test that caching is actually working by checking cache stats"""
        # Clear cache before test
        calculate_level.cache_clear()
        
        # First call - cache miss
        calculate_level(1000)
        info1 = calculate_level.cache_info()
        assert info1.hits == 0
        assert info1.misses == 1
        
        # Second call with same value - cache hit
        calculate_level(1000)
        info2 = calculate_level.cache_info()
        assert info2.hits == 1
        assert info2.misses == 1
        
        # Third call with different value - cache miss
        calculate_level(2000)
        info3 = calculate_level.cache_info()
        assert info3.hits == 1
        assert info3.misses == 2
        
        # Fourth call with first value - cache hit
        calculate_level(1000)
        info4 = calculate_level.cache_info()
        assert info4.hits == 2
        assert info4.misses == 2
    
    def test_get_level_threshold_caching_returns_same_result(self):
        """Test that cached threshold results match uncached results"""
        # Clear cache before test
        get_level_threshold.cache_clear()
        
        # First call - cache miss
        result1 = get_level_threshold(10)
        
        # Second call - cache hit
        result2 = get_level_threshold(10)
        
        # Results should be identical
        assert result1 == result2
        assert result1 == 10000
    
    def test_get_level_threshold_cache_info(self):
        """Test that threshold caching is working by checking cache stats"""
        # Clear cache before test
        get_level_threshold.cache_clear()
        
        # First call - cache miss
        get_level_threshold(5)
        info1 = get_level_threshold.cache_info()
        assert info1.hits == 0
        assert info1.misses == 1
        
        # Second call with same value - cache hit
        get_level_threshold(5)
        info2 = get_level_threshold.cache_info()
        assert info2.hits == 1
        assert info2.misses == 1
    
    def test_cache_improves_performance_for_repeated_calls(self):
        """Test that caching provides performance benefit for repeated calculations"""
        import time
        
        # Clear cache
        calculate_level.cache_clear()
        
        # Measure time for first 100 calls (cache misses)
        start1 = time.perf_counter()
        for i in range(100):
            calculate_level(i * 100)
        time1 = time.perf_counter() - start1
        
        # Measure time for same 100 calls (cache hits)
        start2 = time.perf_counter()
        for i in range(100):
            calculate_level(i * 100)
        time2 = time.perf_counter() - start2
        
        # Cached calls should be significantly faster
        # We expect at least 2x speedup, but allow for some variance
        assert time2 < time1, f"Cached calls ({time2:.6f}s) should be faster than uncached ({time1:.6f}s)"
    
    def test_cache_handles_edge_cases(self):
        """Test that caching works correctly for edge cases"""
        # Clear cache
        calculate_level.cache_clear()
        
        # Test with 0 XP
        assert calculate_level(0) == 1
        assert calculate_level(0) == 1  # Cache hit
        
        # Test with negative XP
        assert calculate_level(-100) == 1
        assert calculate_level(-100) == 1  # Cache hit
        
        # Test with very large XP
        large_xp = 1000000
        level1 = calculate_level(large_xp)
        level2 = calculate_level(large_xp)
        assert level1 == level2
        assert level1 == 100
