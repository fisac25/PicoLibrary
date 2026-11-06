"""
# Employee.py
# Abstract base class representing an employee in the office nameplate system.
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


class Employee:
    """
    Abstract base class for all employee subtypes.
    Encapsulates core information: name, phone number, position, and availability.

    Parameters:
    -----------
    name : str
        The full name of the employee.
    phoneNumber : str
        The office extension or phone number.
    position : str
        The job title / role of the employee.
    """

    def __init__(self, name, phoneNumber, position):
        self._name = name
        self._phoneNumber = phoneNumber
        self._position = position
        self._availability = Availability.AVAILABLE

    def getName(self):
        """Returns the employee's name."""
        return self._name

    def getPhoneNumber(self):
        """Returns the employee's phone number."""
        return self._phoneNumber

    def getPosition(self):
        """Returns the employee's position title."""
        return self._position

    def getAvailability(self, now=None):
        """
        Returns the current availability status.

        Parameters:
        -----------
        now : int, optional
            Reference timestamp (used by automated subclasses like Administrator).

        Returns:
        --------
        str
            Availability status (Available, Away, or Busy).
        """
        return self._availability

    def cycleAvailability(self):
        """
        Cycles manually through Available -> Away -> Busy -> Available.
        """
        old_status = self._availability
        self._availability = Availability.next(self._availability)
        Log.i(f"{self._name} availability changed: {old_status} -> {self._availability}")

    def getDisplayPages(self):
        """
        Polymorphic method returning a list of 2-line display pages for the 16x2 LCD.
        Each page is represented as a tuple of strings: (line1, line2).

        Returns:
        --------
        list of tuple of (str, str)
        """
        return [
            (self._name[:16], self._position[:16]),
            ("Phone:", self._phoneNumber[:16])
        ]


if __name__ == "__main__":
    Log.i("Testing Employee base class...")
    emp = Employee("Alice Smith", "x1234", "General Staff")
    assert emp.getName() == "Alice Smith"
    assert emp.getPhoneNumber() == "x1234"
    assert emp.getPosition() == "General Staff"
    assert emp.getAvailability() == Availability.AVAILABLE

    # Test cycling availability
    emp.cycleAvailability()
    assert emp.getAvailability() == Availability.AWAY
    emp.cycleAvailability()
    assert emp.getAvailability() == Availability.BUSY
    emp.cycleAvailability()
    assert emp.getAvailability() == Availability.AVAILABLE

    # Test default display pages
    pages = emp.getDisplayPages()
    assert len(pages) == 2
    assert pages[0] == ("Alice Smith", "General Staff")
    assert pages[1] == ("Phone:", "x1234")

    Log.i("Testing complete - Employee checks passed")
