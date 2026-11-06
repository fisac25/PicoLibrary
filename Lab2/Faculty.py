"""
# Faculty.py
# Represents a faculty member with teaching courses and office hours.
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


class Faculty(Employee):
    """
    Faculty subtype representing teaching staff.

    Parameters:
    -----------
    name : str
        Faculty member's name.
    phoneNumber : str
        Office phone or extension.
    position : str
        Academic title (e.g., 'Professor', 'Lecturer').
    courses : list of str
        List of course codes or titles being taught.
    officeHours : list of str
        List of office hour slots (e.g., ['MWF 10-11', 'TR 2-3']).
    """

    def __init__(self, name, phoneNumber, position, courses=None, officeHours=None):
        super().__init__(name, phoneNumber, position)
        self._courses = courses if courses is not None else []
        self._officeHours = officeHours if officeHours is not None else []

    def getCourses(self):
        """Returns the list of assigned courses."""
        return self._courses

    def getOfficeHours(self):
        """Returns the office hours list."""
        return self._officeHours

    def getDisplayPages(self):
        """
        Polymorphic display pages for Faculty:
        Page 1: Name & Position
        Page 2: Teaching Courses
        Page 3+: One page per office hours slot
        """
        pages = [(self._name[:16], self._position[:16])]

        courses_str = ", ".join(self._courses) if self._courses else "None"
        pages.append(("Courses:", courses_str[:16]))

        if self._officeHours:
            for i, slot in enumerate(self._officeHours):
                pages.append((f"Hours {i + 1}:", slot[:16]))
        else:
            pages.append(("Office Hours:", "By Appt"))

        return pages


if __name__ == "__main__":
    Log.i("Testing Faculty class...")
    prof = Faculty("Dr. Turing", "x4040", "Associate Prof",
                   courses=["CS101", "CS350"],
                   officeHours=["MWF 10-11", "T 14-15"])

    assert prof.getName() == "Dr. Turing"
    assert prof.getCourses() == ["CS101", "CS350"]
    pages = prof.getDisplayPages()
    assert len(pages) == 4                                      # Name + Courses + 2 hour slots
    assert pages[0] == ("Dr. Turing", "Associate Prof")
    assert pages[1] == ("Courses:", "CS101, CS350")
    assert pages[2] == ("Hours 1:", "MWF 10-11")
    assert pages[3] == ("Hours 2:", "T 14-15")

    Log.i("Testing complete - Faculty checks passed")
