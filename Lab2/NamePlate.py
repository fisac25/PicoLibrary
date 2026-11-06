"""
# NamePlate.py
# Controller class managing state, button inputs, employee roster, and auto-paging.
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


class NamePlate:
    """
    Controller coordinating employee domain models, hardware inputs (buttons),
    and the output view (LCD, LightStrip, Buzzer).

    Parameters:
    -----------
    employees : list of Employee
        List of employee instances managed by this nameplate.
    view : NamePlateView
        The presentation view object.
    previousButton : Button, optional
        Button for navigating backward.
    nextButton : Button, optional
        Button for navigating forward.
    availabilityButton : Button, optional
        Button for cycling availability.
    pageIntervalMs : int, optional
        Milliseconds between automatic display page rotations (default 5000ms).
    """

    def __init__(self, employees, view, previousButton=None, nextButton=None,
                 availabilityButton=None, pageIntervalMs=5000):
        self._employees = employees if employees else []
        self._view = view
        self._currentEmployeeIndex = 0
        self._currentPageIndex = 0
        self._pageIntervalMs = pageIntervalMs
        self._lastPageChangeMs = None  # Set on first update() call to avoid instant page flip at boot
        self._lastAvailability = None

        self._previousButton = previousButton
        self._nextButton = nextButton
        self._availabilityButton = availabilityButton

        # Register this controller as handler for buttons if provided
        for btn in [self._previousButton, self._nextButton, self._availabilityButton]:
            if btn and hasattr(btn, "setHandler"):
                btn.setHandler(self)

        Log.i(f"NamePlate controller initialized with {len(self._employees)} employees.")
        self._refreshDisplay()

    def getCurrentEmployee(self):
        """Returns the currently active Employee object, or None if roster is empty."""
        if not self._employees:
            return None
        return self._employees[self._currentEmployeeIndex % len(self._employees)]

    def previousEmployee(self):
        """Navigates to the previous employee in the list (wraps around)."""
        if not self._employees:
            return
        self._currentEmployeeIndex = (self._currentEmployeeIndex - 1) % len(self._employees)
        self._currentPageIndex = 0
        self._lastPageChangeMs = None
        Log.i(f"Navigated to previous employee (Index: {self._currentEmployeeIndex})")
        if self._view:
            self._view.playNavigationSound(forward=False)
        self._refreshDisplay()

    def nextEmployee(self):
        """Navigates to the next employee in the list (wraps around)."""
        if not self._employees:
            return
        self._currentEmployeeIndex = (self._currentEmployeeIndex + 1) % len(self._employees)
        self._currentPageIndex = 0
        self._lastPageChangeMs = None
        Log.i(f"Navigated to next employee (Index: {self._currentEmployeeIndex})")
        if self._view:
            self._view.playNavigationSound(forward=True)
        self._refreshDisplay()

    def cycleAvailability(self):
        """Cycles availability for the current employee (if permitted) and updates LCD."""
        emp = self.getCurrentEmployee()
        if not emp:
            return
        emp.cycleAvailability()
        self._lastPageChangeMs = None
        if self._view:
            self._view.showAvailability(emp.getAvailability(), updateLCD=True)

    def buttonPressed(self, name):
        """
        Callback triggered when any registered button is pressed.

        Parameters:
        -----------
        name : str
            The name identifier of the pressed button.
        """
        Log.i(f"NamePlate buttonPressed event received from: '{name}'")
        btn_name = str(name).lower()
        if "prev" in btn_name:
            self.previousEmployee()
        elif "next" in btn_name:
            self.nextEmployee()
        elif "avail" in btn_name:
            self.cycleAvailability()
        else:
            Log.w(f"Unrecognized button pressed: '{name}'")

    def buttonReleased(self, name):
        """Callback triggered when a button is released."""
        Log.i(f"NamePlate buttonReleased event from: '{name}'")

    def update(self, now):
        """
        Periodic update method to be called from the main loop.
        Handles auto-rotation of multi-page employee info and schedule-driven availability.

        Parameters:
        -----------
        now : int
            Current time in milliseconds.
        """
        emp = self.getCurrentEmployee()
        if not emp:
            return

        # Check if availability has changed (e.g. Administrator schedule transitions)
        curr_avail = emp.getAvailability(now)
        if curr_avail != self._lastAvailability:
            self._lastAvailability = curr_avail
            if self._view:
                self._view.showAvailability(curr_avail)

        # Check if it is time to flip to the next display page
        if self._lastPageChangeMs is None:
            self._lastPageChangeMs = now  # Anchor the timer to the first loop tick
            return

        if (now - self._lastPageChangeMs) >= self._pageIntervalMs:
            pages = emp.getDisplayPages()
            if pages:
                self._currentPageIndex = (self._currentPageIndex + 1) % len(pages)
                if self._view:
                    self._view.showPage(emp, self._currentPageIndex)
            self._lastPageChangeMs = now

    def _refreshDisplay(self, now=None):
        """Internal helper to refresh both LCD text and LightStrip availability indicator."""
        emp = self.getCurrentEmployee()
        if not emp or not self._view:
            return
        self._view.showPage(emp, self._currentPageIndex)
        curr_avail = emp.getAvailability(now)
        self._lastAvailability = curr_avail
        self._view.showAvailability(curr_avail)


# ==============================================================================
# Self-contained Test Block
# ==============================================================================
if __name__ == "__main__":
    Log.i("Testing NamePlate controller...")

    class MockView:
        def __init__(self):
            self.last_page = None
            self.last_status = None
            self.last_sound = None

        def showPage(self, employee, pageIndex):
            self.last_page = (employee.getName(), pageIndex)

        def showAvailability(self, status, updateLCD=False):
            self.last_status = status

        def playNavigationSound(self, forward):
            self.last_sound = forward

    from Faculty import Faculty
    from Staff import Staff

    emp1 = Faculty("Prof. Alan", "x1111", "Professor", courses=["CS101"], officeHours=["MWF 10-11"])
    emp2 = Staff("Grace Hopper", "x2222", "Director", responsibilities="Systems Architecture")

    view = MockView()
    controller = NamePlate([emp1, emp2], view, pageIntervalMs=2000)

    # Initial check
    assert controller.getCurrentEmployee().getName() == "Prof. Alan"
    assert view.last_page == ("Prof. Alan", 0)
    assert view.last_status == Availability.AVAILABLE

    # Next employee
    controller.buttonPressed("btn_next")
    assert controller.getCurrentEmployee().getName() == "Grace Hopper"
    assert view.last_sound is True
    assert view.last_page == ("Grace Hopper", 0)

    # Previous employee
    controller.buttonPressed("btn_previous")
    assert controller.getCurrentEmployee().getName() == "Prof. Alan"
    assert view.last_sound is False

    # Cycle availability
    controller.buttonPressed("btn_availability")
    assert controller.getCurrentEmployee().getAvailability() == Availability.AWAY
    assert view.last_status == Availability.AWAY

    # Test auto-page advance via update(now)
    # First update call anchors the timer at t=1000
    controller.update(1000)
    assert controller._currentPageIndex == 0

    # At t=2500 (1500ms elapsed < 2000ms), page should remain 0
    controller.update(2500)
    assert controller._currentPageIndex == 0

    # At t=3100 (2100ms elapsed >= 2000ms), page should advance to 1
    controller.update(3100)
    assert controller._currentPageIndex == 1
    assert view.last_page == ("Prof. Alan", 1)

    Log.i("Testing complete - NamePlate checks passed")
