"""
# Calendar.py
# Models schedule events and calendar availability for administrators.
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
from Availability import Availability


class CalendarEvent:
    """
    Represents a discrete time interval with an associated availability state.

    Parameters:
    -----------
    startTime : int
        Start time of the event (e.g. integer timestamp or minute of the day).
    endTime : int
        End time of the event.
    status : str
        The availability status during this event (from Availability).
    """

    def __init__(self, startTime, endTime, status):
        self.startTime = startTime
        self.endTime = endTime
        self.status = status

    def contains(self, now):
        """
        Check if the given time falls within the event window [startTime, endTime).

        Parameters:
        -----------
        now : int
            Current time.

        Returns:
        --------
        bool
            True if now is within the event interval, False otherwise.
        """
        return self.startTime <= now < self.endTime

    def getStatus(self):
        """
        Returns the availability status of this event.

        Returns:
        --------
        str
            Availability state.
        """
        return self.status


class Calendar:
    """
    Manages a collection of CalendarEvents to determine automated availability.
    """

    def __init__(self):
        self.events = []

    def addEvent(self, event):
        """
        Adds a calendar event to the schedule.

        Parameters:
        -----------
        event : CalendarEvent
            The event to register.
        """
        self.events.append(event)
        Log.i(f"Added CalendarEvent: [{event.startTime} - {event.endTime}] -> {event.status}")

    def getAvailability(self, now):
        """
        Determines the availability based on scheduled events for the given time.
        Defaults to Availability.AVAILABLE if no active event is found.

        Parameters:
        -----------
        now : int
            The current reference time.

        Returns:
        --------
        str
            Availability status (Available, Away, or Busy).
        """
        for event in self.events:
            if event.contains(now):
                return event.getStatus()
        return Availability.AVAILABLE


if __name__ == "__main__":
    Log.i("Testing Calendar and CalendarEvent...")

    cal = Calendar()
    # Meeting from 900 to 1000: Busy
    cal.addEvent(CalendarEvent(900, 1000, Availability.BUSY))
    # Lunch from 1200 to 1300: Away
    cal.addEvent(CalendarEvent(1200, 1300, Availability.AWAY))

    # Before meeting
    assert cal.getAvailability(830) == Availability.AVAILABLE
    # In meeting
    assert cal.getAvailability(915) == Availability.BUSY
    # Between events
    assert cal.getAvailability(1100) == Availability.AVAILABLE
    # At lunch
    assert cal.getAvailability(1230) == Availability.AWAY
    # After lunch
    assert cal.getAvailability(1400) == Availability.AVAILABLE

    Log.i("Testing complete - Calendar checks passed")
