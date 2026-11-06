"""
# Availability.py
# Defines availability states for employees (Available, Away, Busy).
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


class Availability:
    """
    Availability enumeration representing employee status.
    
    Attributes:
    -----------
    AVAILABLE : str
        The employee is available in the office.
    AWAY : str
        The employee is temporarily away from the office.
    BUSY : str
        The employee is busy and should not be disturbed.
    """
    AVAILABLE = "Available"
    AWAY = "Away"
    BUSY = "Busy"

    _CYCLE_ORDER = [AVAILABLE, AWAY, BUSY]

    @classmethod
    def next(cls, current_status):
        """
        Cycle to the next availability state in order: Available -> Away -> Busy -> Available.

        Parameters:
        -----------
        current_status : str
            Current availability string.

        Returns:
        --------
        str
            The subsequent availability state.
        """
        try:
            idx = cls._CYCLE_ORDER.index(current_status)
            return cls._CYCLE_ORDER[(idx + 1) % len(cls._CYCLE_ORDER)]
        except ValueError:
            return cls.AVAILABLE


if __name__ == "__main__":
    Log.i("Testing Availability enumeration...")
    assert Availability.AVAILABLE == "Available"
    assert Availability.AWAY == "Away"
    assert Availability.BUSY == "Busy"

    # Test cycling
    curr = Availability.AVAILABLE
    curr = Availability.next(curr)
    assert curr == Availability.AWAY
    curr = Availability.next(curr)
    assert curr == Availability.BUSY
    curr = Availability.next(curr)
    assert curr == Availability.AVAILABLE

    Log.i("Testing complete - Availability checks passed")
