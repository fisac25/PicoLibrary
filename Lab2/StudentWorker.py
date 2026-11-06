"""
# StudentWorker.py
# Represents a student employee working part-time in the office.
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


class StudentWorker(Employee):
    """
    StudentWorker subtype representing part-time student staff.

    Parameters:
    -----------
    name : str
        Student's full name.
    phoneNumber : str
        Desk phone or supervisor contact number.
    position : str
        Role title (e.g. 'Lab Assistant', 'Student Aide').
    workSchedule : str
        Weekly working hours description (e.g. 'MW 13:00-17:00').
    """

    def __init__(self, name, phoneNumber, position, workSchedule=""):
        super().__init__(name, phoneNumber, position)
        self._workSchedule = workSchedule

    def getWorkSchedule(self):
        """Returns student work schedule."""
        return self._workSchedule

    def getDisplayPages(self):
        """
        Polymorphic display pages for StudentWorker:
        Page 1: Name & Position
        Page 2: Working Hours / Schedule
        """
        return [
            (self._name[:16], self._position[:16]),
            ("Schedule:", self._workSchedule[:16])
        ]


if __name__ == "__main__":
    Log.i("Testing StudentWorker class...")
    student = StudentWorker("Charlie Brown", "x9911", "Peer Tutor", workSchedule="TR 14:00-18:00")
    assert student.getName() == "Charlie Brown"
    assert student.getWorkSchedule() == "TR 14:00-18:00"

    pages = student.getDisplayPages()
    assert len(pages) == 2
    assert pages[0] == ("Charlie Brown", "Peer Tutor")
    assert pages[1] == ("Schedule:", "TR 14:00-18:00")

    Log.i("Testing complete - StudentWorker checks passed")
