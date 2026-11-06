"""
# NamePlateView.py
# Presentation/View layer for the office nameplate system (LCD, LightStrip, Buzzer).
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


class NamePlateView:
    """
    View class encapsulating the physical and simulated output hardware:
    1. 16x2 LCD Display (shows employee details & polymorphic pages).
    2. NeoPixel LightStrip (shows availability color code).
    3. Passive Buzzer (provides audible navigation feedback).

    Parameters:
    -----------
    lcd : object, optional
        LCDDisplay instance providing clear() and showText(text, row, col).
    lightStrip : object, optional
        LightStrip instance providing setColor(color) or show().
    buzzer : object, optional
        PassiveBuzzer instance providing beep(tone, duration) or play(tone)/stop().
    """

    COLOR_AVAILABLE = (0, 255, 0)      # Green
    COLOR_AWAY      = (255, 180, 0)    # Amber / Yellow
    COLOR_BUSY      = (255, 0, 0)      # Red
    COLOR_OFF       = (0, 0, 0)

    def __init__(self, lcd=None, lightStrip=None, buzzer=None):
        self._lcd = lcd
        self._lightStrip = lightStrip
        self._buzzer = buzzer

    def showPage(self, employee, pageIndex=0):
        """
        Renders a specific display page for the given employee on the LCD.

        Parameters:
        -----------
        employee : Employee
            The employee whose page is being displayed.
        pageIndex : int
            The index of the page to render.
        """
        if not employee:
            return

        pages = employee.getDisplayPages()
        if not pages:
            return

        idx = pageIndex % len(pages)
        line1, line2 = pages[idx]

        Log.i(f"[View LCD Page {idx + 1}/{len(pages)}]: Line 1='{line1}' | Line 2='{line2}'")
        if self._lcd:
            try:
                self._lcd.clear()
                self._lcd.showText(line1[:16], row=0, col=0)
                self._lcd.showText(line2[:16], row=1, col=0)
            except Exception as e:
                Log.e(f"Error updating LCD: {e}")

    def showAvailability(self, status, updateLCD=False):
        """
        Updates the LightStrip LEDs to reflect the employee's availability.
        Optionally also writes the status to the LCD (useful on button press).

        Parameters:
        -----------
        status : str
            Availability status string ('Available', 'Away', or 'Busy').
        updateLCD : bool
            If True, also writes the status to the LCD display.
        """
        if status == Availability.AVAILABLE:
            color = self.COLOR_AVAILABLE
        elif status == Availability.AWAY:
            color = self.COLOR_AWAY
        elif status == Availability.BUSY:
            color = self.COLOR_BUSY
        else:
            color = self.COLOR_OFF

        Log.i(f"[View LightStrip]: Availability '{status}' -> RGB {color}")
        if self._lightStrip:
            try:
                if hasattr(self._lightStrip, "setColor"):
                    self._lightStrip.setColor(color)
                elif hasattr(self._lightStrip, "setPixel"):
                    for i in range(getattr(self._lightStrip, "_numleds", 8)):
                        self._lightStrip.setPixel(i, color, show=False)
                    if hasattr(self._lightStrip, "show"):
                        self._lightStrip.show()
            except Exception as e:
                Log.e(f"Error updating LightStrip: {e}")

        if updateLCD and self._lcd:
            try:
                self._lcd.clear()
                self._lcd.showText("Status:", row=0, col=0)
                self._lcd.showText(status[:16], row=1, col=0)
                Log.i(f"[View LCD Status]: {status}")
            except Exception as e:
                Log.e(f"Error writing status to LCD: {e}")

    def playNavigationSound(self, forward=True):
        """
        Emits an audible feedback tone when navigating between employees.

        Parameters:
        -----------
        forward : bool
            True if navigating to the next employee (higher pitch),
            False if navigating to the previous employee (lower pitch).
        """
        tone = 880 if forward else 440
        duration_ms = 60
        direction = "Forward" if forward else "Backward"
        Log.i(f"[View Buzzer]: Navigation sound ({direction}) -> {tone} Hz for {duration_ms} ms")

        if self._buzzer:
            try:
                if hasattr(self._buzzer, "beep"):
                    self._buzzer.beep(tone, duration_ms)
                elif hasattr(self._buzzer, "play") and hasattr(self._buzzer, "stop"):
                    self._buzzer.play(tone)
                    self._buzzer.stop()
            except Exception as e:
                Log.e(f"Error playing sound: {e}")


# ==============================================================================
# Self-contained Test Block
# ==============================================================================
if __name__ == "__main__":
    Log.i("Testing NamePlateView class with mock peripherals...")

    class MockLCD:
        def __init__(self):
            self.lines = ["", ""]
        def clear(self):
            self.lines = ["", ""]
        def showText(self, text, row=0, col=0):
            self.lines[row] = text

    class MockLightStrip:
        def __init__(self):
            self.color = (0, 0, 0)
        def setColor(self, color):
            self.color = color

    class MockBuzzer:
        def __init__(self):
            self.last_tone = 0
            self.last_duration = 0
        def beep(self, tone, duration):
            self.last_tone = tone
            self.last_duration = duration

    from Faculty import Faculty
    prof = Faculty("Dr. Turing", "x4040", "Professor", courses=["CS101"], officeHours=["MWF 10-11"])

    lcd = MockLCD()
    strip = MockLightStrip()
    buz = MockBuzzer()
    view = NamePlateView(lcd=lcd, lightStrip=strip, buzzer=buz)

    # Test LCD page rendering
    view.showPage(prof, 0)
    assert lcd.lines[0] == "Dr. Turing"
    assert lcd.lines[1] == "Professor"

    view.showPage(prof, 1)
    assert lcd.lines[0] == "Courses:"
    assert lcd.lines[1] == "CS101"

    # Test LightStrip status colors
    view.showAvailability(Availability.AVAILABLE)
    assert strip.color == (0, 255, 0)
    view.showAvailability(Availability.AWAY)
    assert strip.color == (255, 180, 0)
    view.showAvailability(Availability.BUSY)
    assert strip.color == (255, 0, 0)

    # Test LCD availability display on button press (updateLCD=True)
    view.showAvailability(Availability.AWAY, updateLCD=True)
    assert strip.color == (255, 180, 0)
    assert lcd.lines[0] == "Status:"
    assert lcd.lines[1] == "Away"

    # Test Buzzer tones
    view.playNavigationSound(forward=True)
    assert buz.last_tone == 880
    view.playNavigationSound(forward=False)
    assert buz.last_tone == 440

    Log.i("Testing complete - NamePlateView checks passed")
