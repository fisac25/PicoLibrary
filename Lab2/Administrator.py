"""
# Administrator.py
# Represents an office administrator with automated calendar-based availability.
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
from Employee import Employee
from Calendar import Calendar, CalendarEvent
from Availability import Availability


class Administrator(Employee):
    """
    Administrator subtype with automated availability driven by a Calendar.

    Parameters:
    -----------
    name : str
        Administrator's name.
    phoneNumber : str
        Direct phone or office extension.
    position : str
        Administrative title (e.g., 'Department Chair', 'Dean').
    calendar : Calendar, optional
        A Calendar instance holding scheduled events.
    """

    def __init__(self, name, phoneNumber, position, calendar=None):
        super().__init__(name, phoneNumber, position)
        self._calendar = calendar if calendar is not None else Calendar()

    def getCalendar(self):
        """Returns the administrator's Calendar instance."""
        return self._calendar

    def getAvailability(self, now=None):
        """
        Polymorphic availability determination:
        Automated via Calendar lookup if a reference time 'now' is provided.

        Parameters:
        -----------
        now : int, optional
            Current time used to evaluate schedule events.

        Returns:
        --------
        str
            Availability state from calendar.
        """
        if now is not None:
            return self._calendar.getAvailability(now)
        return self._availability

    def cycleAvailability(self):
        """
        Administrators have automated calendar availability, so manual cycling
        is ignored or restricted.
        """
        Log.i(f"Manual availability cycling is disabled for Administrator ({self._name}) - managed by Calendar.")

    def getDisplayPages(self):
        """
        Polymorphic display pages for Administrator:
        Page 1: Name & Position
        Page 2: Auto Calendar Status
        """
        return [
            (self._name[:16], self._position[:16]),
            ("Availability:", "Auto (Calendar)")
        ]


if __name__ == "__main__":
    Log.i("Testing Administrator class...")
    cal = Calendar()
    cal.addEvent(CalendarEvent(900, 1100, Availability.BUSY))

    admin = Administrator("Dr. Hamilton", "x5500", "Department Chair", calendar=cal)
    assert admin.getName() == "Dr. Hamilton"
    assert admin.getPosition() == "Department Chair"

    # Automated calendar lookup
    assert admin.getAvailability(now=930) == Availability.BUSY
    assert admin.getAvailability(now=1130) == Availability.AVAILABLE

    # Manual cycling should not alter automated availability
    admin.cycleAvailability()
    assert admin.getAvailability(now=930) == Availability.BUSY

    pages = admin.getDisplayPages()
    assert len(pages) == 2
    assert pages[0] == ("Dr. Hamilton", "Department Chair")
    assert pages[1] == ("Availability:", "Auto (Calendar)")

    Log.i("Testing complete - Administrator checks passed")
