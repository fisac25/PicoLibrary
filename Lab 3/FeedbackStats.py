"""
# FeedbackStats.py
# Business model class tracking customer satisfaction feedback statistics.
# Author: fisac25
"""

import sys
for _p in [".", ".."]:
    if _p not in sys.path:
        sys.path.append(_p)

try:
    from Log import *
except ImportError:
    class Log:
        @classmethod
        def i(cls, msg): print(f"[INFO] {msg}")
        @classmethod
        def d(cls, msg): print(f"[DEBUG] {msg}")
        @classmethod
        def w(cls, msg): print(f"[WARN] {msg}")
        @classmethod
        def e(cls, msg): print(f"[ERROR] {msg}")


class FeedbackStats:
    """
    Manages customer satisfaction metrics for the kiosk system.
    Tracks happy and unhappy counts, calculates satisfaction percentages,
    and determines lighting levels for visual feedback.

    Examples:
    ---------
    1. stats = FeedbackStats()
       stats.add_happy()
       stats.add_unhappy()
       pct = stats.calculate_percentage()
    """

    def __init__(self, num_leds: int = 16):
        """
        Initialize the feedback counters.

        Parameters:
        ----------
        num_leds : int, optional
            Number of LEDs on the indicator light strip (default: 16)
        """
        Log.i("FeedbackStats initialized")
        self._happy_count = 0
        self._unhappy_count = 0
        self._num_leds = num_leds

    def add_happy(self) -> None:
        """Increment the positive feedback count by 1."""
        self._happy_count += 1
        Log.i(f"FeedbackStats: Happy feedback recorded (total happy: {self._happy_count})")

    def add_unhappy(self) -> None:
        """Increment the negative feedback count by 1."""
        self._unhappy_count += 1
        Log.i(f"FeedbackStats: Unhappy feedback recorded (total unhappy: {self._unhappy_count})")

    def get_total_count(self) -> int:
        """
        Get the total number of feedback responses received.

        Returns:
        --------
        int
            Sum of happy and unhappy feedback counts.
        """
        return self._happy_count + self._unhappy_count

    def calculate_percentage(self) -> float:
        """
        Calculate the ratio of positive feedback to total feedback.

        Returns:
        --------
        float
            Satisfaction percentage as a float between 0.0 and 1.0.
            Defaults to 1.0 (100%) when no feedback has been recorded yet.
        """
        total = self.get_total_count()
        if total == 0:
            return 1.0
        return self._happy_count / total

    def get_light_level(self) -> int:
        """
        Calculate the number of LEDs to illuminate based on satisfaction percentage.

        Returns:
        --------
        int
            Number of active LEDs (from 0 up to num_leds).
        """
        ratio = self.calculate_percentage()
        level = int(round(ratio * self._num_leds))
        return max(0, min(self._num_leds, level))

    def reset(self) -> None:
        """Reset all feedback statistics back to zero."""
        self._happy_count = 0
        self._unhappy_count = 0
        Log.i("FeedbackStats: Statistics reset to zero")


if __name__ == "__main__":
    Log.i("Starting FeedbackStats self-test...")
    stats = FeedbackStats(num_leds=8)

    # Initial state
    assert stats.get_total_count() == 0, "Initial total should be 0"
    assert stats.calculate_percentage() == 1.0, "Initial percentage should be 1.0"
    assert stats.get_light_level() == 8, "Initial light level should be 8"

    # Add 1 happy
    stats.add_happy()
    assert stats.get_total_count() == 1, "Total should be 1"
    assert stats.calculate_percentage() == 1.0, "Percentage should be 1.0"

    # Add 3 unhappy -> total 4, 1 happy, 3 unhappy = 25% (0.25)
    stats.add_unhappy()
    stats.add_unhappy()
    stats.add_unhappy()
    assert stats.get_total_count() == 4, "Total should be 4"
    pct = stats.calculate_percentage()
    assert abs(pct - 0.25) < 0.001, f"Expected 0.25, got {pct}"
    assert stats.get_light_level() == 2, f"Expected 2 LEDs, got {stats.get_light_level()}"

    # Reset
    stats.reset()
    assert stats.get_total_count() == 0, "Total should be 0 after reset"
    assert stats.calculate_percentage() == 1.0, "Percentage should be 1.0 after reset"

    Log.i("Testing complete - all checks passed!")
