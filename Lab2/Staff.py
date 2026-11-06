"""
# Staff.py
# Represents general administrative or support staff in an office.
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


class Staff(Employee):
    """
    Staff subtype representing non-teaching operational staff.

    Parameters:
    -----------
    name : str
        Staff member's full name.
    phoneNumber : str
        Office phone or extension.
    position : str
        Job title (e.g. 'Lab Manager', 'Department Secretary').
    responsibilities : str
        Brief summary of primary duties.
    """

    def __init__(self, name, phoneNumber, position, responsibilities=""):
        super().__init__(name, phoneNumber, position)
        self._responsibilities = responsibilities

    def getResponsibilities(self):
        """Returns staff responsibilities."""
        return self._responsibilities

    def getDisplayPages(self):
        """
        Polymorphic display pages for Staff:
        Page 1: Name & Position
        Page 2: Key Responsibilities
        """
        return [
            (self._name[:16], self._position[:16]),
            ("Resp:", self._responsibilities[:16])
        ]


if __name__ == "__main__":
    Log.i("Testing Staff class...")
    staff = Staff("Bob Jones", "x2201", "Lab Coordinator", responsibilities="Hardware & Labs")
    assert staff.getName() == "Bob Jones"
    assert staff.getResponsibilities() == "Hardware & Labs"

    pages = staff.getDisplayPages()
    assert len(pages) == 2
    assert pages[0] == ("Bob Jones", "Lab Coordinator")
    assert pages[1] == ("Resp:", "Hardware & Labs")

    Log.i("Testing complete - Staff checks passed")
