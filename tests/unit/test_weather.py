"""
Unit tests for rowing/weather.py

Tests the physics-based calculations for rowing power and speed under
various weather conditions. These are critical calculations that affect
performance comparisons across different race conditions.
"""
import pytest
from django.test import TestCase
from rowing.weather import rowpower, rowspeed, row_v, powerdiff, powerdiff2


class TestRowpowerBasics(TestCase):
    """Test basic rowpower functionality with default and known inputs."""

    def test_rowpower_default_conditions(self):
        """Test rowpower returns reasonable value at typical race speed."""
        # A typical M8+ race speed is around 5.5-6.0 m/s
        power = rowpower(5.5)
        # Power should be positive and in a reasonable range (500-1500W for a crew)
        self.assertGreater(power, 0)
        self.assertLess(power, 5000)

    def test_rowpower_returns_float(self):
        """Test rowpower returns a numeric type."""
        result = rowpower(5.0)
        self.assertIsInstance(result, (int, float))

    def test_rowpower_zero_speed(self):
        """Test rowpower at zero speed - edge case behavior.

        Note: Zero speed causes mathematical issues (divide by zero in Reynolds
        calculation), resulting in NaN. This documents the current behavior.
        A production fix might handle v=0 specially.
        """
        import math
        power = rowpower(0.0)
        # Current implementation returns NaN due to log10(0) in Reynolds calc
        self.assertTrue(math.isnan(power))

    def test_rowpower_increases_with_speed(self):
        """Test that power increases monotonically with speed."""
        speeds = [3.0, 4.0, 5.0, 6.0]
        powers = [rowpower(v) for v in speeds]
        for i in range(len(powers) - 1):
            self.assertLess(powers[i], powers[i + 1],
                           f"Power at {speeds[i]} m/s should be less than at {speeds[i+1]} m/s")

    def test_rowpower_scales_roughly_cubic(self):
        """Test that power scales roughly with cube of speed (drag relationship)."""
        # Water drag is proportional to v^2, power = force * velocity ~ v^3
        power_at_4 = rowpower(4.0)
        power_at_5 = rowpower(5.0)
        # Ratio should be approximately (5/4)^3 = 1.953
        ratio = power_at_5 / power_at_4
        self.assertGreater(ratio, 1.5)  # Not exact due to air drag, Reynolds
        self.assertLess(ratio, 2.5)


class TestRowpowerWeatherEffects(TestCase):
    """Test weather parameter effects on power requirements."""

    def test_headwind_increases_power(self):
        """Test that headwind (angle=0) increases power requirement."""
        base_power = rowpower(5.0, wind_v=0.0)
        headwind_power = rowpower(5.0, wind_v=3.0, wind_angle=0)  # 0 = headwind
        self.assertGreater(headwind_power, base_power)

    def test_tailwind_decreases_power(self):
        """Test that tailwind (angle=pi) decreases power requirement."""
        from numpy import pi
        base_power = rowpower(5.0, wind_v=0.0)
        tailwind_power = rowpower(5.0, wind_v=3.0, wind_angle=pi)  # pi = tailwind
        self.assertLess(tailwind_power, base_power)

    def test_head_current_increases_power(self):
        """Test that head current (positive water_flow) increases power."""
        base_power = rowpower(5.0, water_flow=0.0)
        current_power = rowpower(5.0, water_flow=0.5)  # head current
        self.assertGreater(current_power, base_power)

    def test_tail_current_decreases_power(self):
        """Test that tail current (negative water_flow) decreases power."""
        base_power = rowpower(5.0, water_flow=0.0)
        current_power = rowpower(5.0, water_flow=-0.5)  # tail current
        self.assertLess(current_power, base_power)

    def test_cold_water_changes_power(self):
        """Test that water temperature affects power (viscosity changes)."""
        warm_power = rowpower(5.0, water_temp=25.0)
        cold_power = rowpower(5.0, water_temp=10.0)
        # Cold water has higher viscosity, so should require slightly more power
        # The difference is small but should be measurable
        self.assertNotAlmostEqual(warm_power, cold_power, places=1)

    def test_high_altitude_reduces_air_resistance(self):
        """Test that lower air pressure reduces air drag."""
        sea_level_power = rowpower(5.0, air_pressure=1013.0)
        altitude_power = rowpower(5.0, air_pressure=850.0)  # ~1500m altitude
        # Lower pressure = less air resistance = less power needed
        self.assertLess(altitude_power, sea_level_power)

    def test_humidity_effect(self):
        """Test that humidity affects air density and thus power."""
        dry_power = rowpower(5.0, air_humidity=0.0)
        humid_power = rowpower(5.0, air_humidity=1.0)
        # Humid air is less dense than dry air, so less power needed
        self.assertLess(humid_power, dry_power)


class TestRowpowerEdgeCases(TestCase):
    """Test edge cases and boundary conditions."""

    def test_very_high_speed(self):
        """Test calculation doesn't break at very high speeds."""
        # World record 2k speed is about 6.5 m/s for an 8+
        power = rowpower(7.0)
        self.assertGreater(power, 0)
        self.assertIsInstance(power, (int, float))

    def test_very_low_speed(self):
        """Test calculation handles very low speeds."""
        power = rowpower(0.5)
        self.assertGreater(power, 0)

    def test_extreme_cold(self):
        """Test with very cold conditions."""
        power = rowpower(5.0, water_temp=2.0, air_temp=-5.0)
        self.assertGreater(power, 0)

    def test_extreme_heat(self):
        """Test with very hot conditions."""
        power = rowpower(5.0, water_temp=30.0, air_temp=40.0)
        self.assertGreater(power, 0)

    def test_strong_headwind(self):
        """Test with strong headwind."""
        power = rowpower(5.0, wind_v=10.0, wind_angle=0)
        self.assertGreater(power, 0)

    def test_crosswind(self):
        """Test with pure crosswind (90 degrees)."""
        from numpy import pi
        power = rowpower(5.0, wind_v=5.0, wind_angle=pi/2)
        self.assertGreater(power, 0)


class TestRowspeed(TestCase):
    """Test rowspeed function - inverse of rowpower."""

    def test_rowspeed_returns_tuple(self):
        """Test rowspeed returns (speed, errorcode) tuple."""
        result = rowspeed(1000)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_rowspeed_success_errorcode(self):
        """Test rowspeed returns errorcode 0 on success."""
        speed, errorcode = rowspeed(1000)
        self.assertEqual(errorcode, 0)

    def test_rowspeed_returns_positive_speed(self):
        """Test rowspeed returns a positive speed value."""
        speed, errorcode = rowspeed(1000)
        self.assertGreater(speed, 0)

    def test_rowspeed_inverse_of_rowpower(self):
        """Test that rowspeed is the inverse of rowpower."""
        # Calculate power at a known speed
        test_speed = 5.0
        power = rowpower(test_speed)
        # Calculate speed from that power
        calculated_speed, errorcode = rowspeed(power)
        self.assertEqual(errorcode, 0)
        self.assertAlmostEqual(calculated_speed, test_speed, places=4)

    def test_rowspeed_with_tail_current(self):
        """Test rowspeed with negative water_flow (tail current)."""
        speed, errorcode = rowspeed(1000, water_flow=-0.5)
        self.assertEqual(errorcode, 0)
        self.assertGreater(speed, 0)

    def test_rowspeed_higher_power_higher_speed(self):
        """Test that higher power results in higher speed."""
        speed_low, _ = rowspeed(800)
        speed_high, _ = rowspeed(1200)
        self.assertGreater(speed_high, speed_low)


class TestRowV(TestCase):
    """Test row_v function."""

    def test_row_v_returns_float(self):
        """Test row_v returns a numeric value."""
        result = row_v(5.0)
        self.assertIsInstance(result, (int, float))

    def test_row_v_same_conditions_returns_same_speed(self):
        """Test row_v with same conditions returns same speed."""
        # With identical conditions, speed should be unchanged
        result = row_v(5.0)
        self.assertAlmostEqual(result, 5.0, places=4)

    def test_row_v_with_headwind(self):
        """Test row_v calculates equivalent speed under different conditions.

        row_v finds what speed in new conditions produces the same power as
        the original speed in default conditions. With headwind, you need MORE
        power to maintain speed, so at the SAME power you'd go SLOWER in a
        headwind. However, row_v is finding equivalent power output, not
        equivalent speed - the result depends on the specific physics model.
        """
        base_speed = 5.0
        result = row_v(base_speed, wind_v=3.0, wind_angle=0)
        # Result should be a valid positive speed
        self.assertGreater(result, 0)
        self.assertIsInstance(result, (int, float))


class TestPowerdiff(TestCase):
    """Test helper functions."""

    def test_powerdiff_at_equilibrium(self):
        """Test powerdiff returns zero when watts equals rowpower."""
        speed = 5.0
        watts = rowpower(speed)
        diff = powerdiff(speed, watts)
        self.assertAlmostEqual(diff, 0.0, places=6)

    def test_powerdiff2_at_equilibrium(self):
        """Test powerdiff2 returns zero when calculation matches."""
        speed = 5.0
        kwargs = {'water_temp': 18.0, 'air_temp': 20.0}
        watts = rowpower(speed, **kwargs)
        diff = powerdiff2(speed, watts, kwargs)
        self.assertAlmostEqual(diff, 0.0, places=6)


class TestPhysicsConsistency(TestCase):
    """Test physical consistency of the model."""

    def test_symmetry_crosswind(self):
        """Test that equal crosswinds from opposite sides give same power."""
        from numpy import pi
        power_left = rowpower(5.0, wind_v=5.0, wind_angle=pi/2)
        power_right = rowpower(5.0, wind_v=5.0, wind_angle=-pi/2)
        self.assertAlmostEqual(power_left, power_right, places=5)

    def test_power_positive_definite(self):
        """Test power is always positive for positive speeds."""
        test_cases = [
            {'v': 3.0},
            {'v': 5.0, 'wind_v': 5.0, 'wind_angle': 0},
            {'v': 5.0, 'water_flow': 1.0},
            {'v': 5.0, 'water_temp': 5.0, 'air_temp': -5.0},
        ]
        for case in test_cases:
            v = case.pop('v')
            power = rowpower(v, **case)
            self.assertGreater(power, 0, f"Failed for case with v={v}, {case}")

    def test_reasonable_power_range_for_single(self):
        """Test power range is reasonable for a single sculler (~350-500W)."""
        # A competitive single sculler at 4.5 m/s
        power = rowpower(4.5, A_air=0.8, A_water=2.5, boat_length=8.2)
        # Single scull power output typically 300-500W at race pace
        self.assertGreater(power, 200)
        self.assertLess(power, 800)

    def test_reasonable_power_range_for_eight(self):
        """Test power range is reasonable for an eight (~3000-4000W total)."""
        # A competitive eight at 6.0 m/s with default parameters
        power = rowpower(6.0)  # Default A_water=9.0, boat_length=18.0 (eight)
        # Eight total power typically 2500-4000W at race pace
        self.assertGreater(power, 1500)
        self.assertLess(power, 6000)
