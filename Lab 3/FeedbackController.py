"""
# FeedbackController.py
# State model controller coordinating sensors, buttons, display, audio, and lights
# for the customer satisfaction kiosk.
# Author: fisac25
"""

import sys
import time

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

from FeedbackStats import FeedbackStats

# Lazy / Safe imports for PicoLibrary components
try:
    from StateModel import StateModel
except ImportError:
    StateModel = None

try:
    from Counters import SoftwareTimer
except ImportError:
    SoftwareTimer = None

try:
    from Button import Button
except ImportError:
    Button = None

try:
    from Displays import LCDDisplay
except ImportError:
    LCDDisplay = None

try:
    from LightStrip import LightStrip, RED, GREEN, BLACK
except ImportError:
    LightStrip = None
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLACK = (0, 0, 0)

try:
    from Buzzer import PassiveBuzzer
except ImportError:
    PassiveBuzzer = None

try:
    from Sensors_advanced import UltrasonicSensor
except ImportError:
    UltrasonicSensor = None


class FeedbackController:
    """
    Main controller for the satisfaction kiosk.
    Implements a 5-state UML statechart managing proximity detection,
    customer voting, audio/visual cues, low-feedback alarm triggers,
    and manager administrative resets.

    States:
    -------
    0: Welcome (Idle)
    1: Selection (Rating prompt active)
    2: Happy (Positive feedback recorded)
    3: Unhappy (Negative feedback recorded)
    4: Alarm (Emergency manager alert if feedback < 30%)

    Examples:
    ---------
    1. controller = FeedbackController()
       controller.run()
    """

    STATE_WELCOME = 0
    STATE_SELECTION = 1
    STATE_HAPPY = 2
    STATE_UNHAPPY = 3
    STATE_ALARM = 4

    def __init__(self, lcd=None, lights=None, buzzer=None, uss=None,
                 green_btn=None, red_btn=None, manager_btn=None, timer=None,
                 stats=None, model=None):
        """
        Initialize controller components, hardware references, and state transitions.

        Parameters:
        ----------
        lcd : LCDDisplay, optional
            Display driver for showing kiosk text.
        lights : LightStrip, optional
            NeoPixel LED strip for visual progress and alarms.
        buzzer : PassiveBuzzer, optional
            Buzzer for sound feedback and alarms.
        uss : UltrasonicSensor, optional
            Proximity sensor detecting customer approach.
        green_btn : Button, optional
            Green positive rating button.
        red_btn : Button, optional
            Red negative rating button.
        manager_btn : Button, optional
            Manager silence and reset button.
        timer : SoftwareTimer, optional
            Timer used for kiosk timeouts.
        stats : FeedbackStats, optional
            Feedback statistics aggregator.
        model : StateModel, optional
            Underlying state machine model.
        """
        Log.i("FeedbackController: Initializing controller...")

        self._stats = stats if stats is not None else FeedbackStats(num_leds=8)
        self._lcd = lcd
        self._lights = lights
        self._buzzer = buzzer
        self._uss = uss
        self._green_btn = green_btn
        self._red_btn = red_btn
        self._manager_btn = manager_btn
        self._timer = timer
        self._alarm_active = False
        self._alarm_tone_toggle = False
        self._last_alarm_toggle = 0

        # Configure the StateModel
        self._model = model
        self.configure_states()

    def configure_states(self) -> None:
        """
        Configure the 5 states, input events, and transitions in the StateModel.
        """
        if StateModel is None:
            Log.w("FeedbackController: StateModel library not loaded, skipping model configuration.")
            return

        if self._model is None:
            self._model = StateModel(5, self, debug=True)

        # Register buttons if provided
        if self._green_btn:
            self._model.addButton(self._green_btn)
        if self._red_btn:
            self._model.addButton(self._red_btn)
        if self._manager_btn:
            self._model.addButton(self._manager_btn)

        # Register proximity sensor
        if self._uss:
            self._model.addSensor(self._uss)

        # Register timer
        if self._timer:
            self._model.addTimer(self._timer)

        # Register custom threshold event
        self._model.addCustomEvent("feedback_below_threshold")

        # Define Transitions as per the UML Statechart:
        # State 0 (Welcome) -> State 1 on customer arrival within 10cm
        self._model.addTransition(self.STATE_WELCOME, ["uss_trip"], self.STATE_SELECTION)

        # State 1 (Selection) transitions
        self._model.addTransition(self.STATE_SELECTION, ["timer_timeout"], self.STATE_WELCOME)
        self._model.addTransition(self.STATE_SELECTION, ["green_press"], self.STATE_HAPPY)
        self._model.addTransition(self.STATE_SELECTION, ["red_press"], self.STATE_UNHAPPY)

        # State 2 (Happy) transitions
        self._model.addTransition(self.STATE_HAPPY, ["timer_timeout"], self.STATE_WELCOME)

        # State 3 (Unhappy) transitions
        self._model.addTransition(self.STATE_UNHAPPY, ["timer_timeout"], self.STATE_WELCOME)
        self._model.addTransition(self.STATE_UNHAPPY, ["feedback_below_threshold"], self.STATE_ALARM)

        # State 4 (Alarm) transition on manager button press
        self._model.addTransition(self.STATE_ALARM, ["manager_press"], self.STATE_WELCOME)

        Log.i("FeedbackController: States and transitions configured successfully.")

    # =========================================================================
    # State Lifecycle Actions
    # =========================================================================

    def enter_welcome(self) -> None:
        """Entry action for State 0 (Welcome / Idle)."""
        Log.i("FeedbackController: Entering Welcome state (Idle)")
        self._alarm_active = False

        if self._timer:
            self._timer.cancel()

        if self._buzzer and hasattr(self._buzzer, "stop"):
            self._buzzer.stop()

        if self._lights:
            if hasattr(self._lights, "clear"):
                self._lights.clear()
            elif hasattr(self._lights, "off"):
                self._lights.off()

        if self._lcd:
            self._show_display("Welcome to Ikea", "Please step near")

    def enter_selection(self) -> None:
        """Entry action for State 1 (Selection / Rating prompt)."""
        Log.i("FeedbackController: Entering Selection state")
        if self._lcd:
            self._show_display("How was visit?", "G=Good  R=Bad")

        # Start 5 second inactivity timer
        if self._timer:
            self._timer.start(5)

        # Indicate active kiosk with neutral/warm lights if available
        if self._lights and hasattr(self._lights, "on"):
            self._lights.on()

    def enter_happy(self) -> None:
        """Entry action for State 2 (Happy feedback recorded)."""
        Log.i("FeedbackController: Entering Happy state")
        self._stats.add_happy()
        pct = int(self._stats.calculate_percentage() * 100)

        if self._lcd:
            self._show_display("Thank you!", f"Score: {pct}% Good")

        # Visual progress on light strip
        if self._lights:
            self._update_light_strip()

        # Play cheerful tone
        if self._buzzer and hasattr(self._buzzer, "play"):
            self._buzzer.play(880)

        # Start 5-second return timer
        if self._timer:
            self._timer.start(5)

    def enter_unhappy(self) -> None:
        """Entry action for State 3 (Unhappy feedback recorded)."""
        Log.i("FeedbackController: Entering Unhappy state")
        self._stats.add_unhappy()
        pct = self._stats.calculate_percentage()
        pct_int = int(pct * 100)

        if self._lcd:
            self._show_display("Sorry to hear!", f"Score: {pct_int}% Good")

        # Visual progress on light strip
        if self._lights:
            self._update_light_strip()

        # Play sad tone
        if self._buzzer and hasattr(self._buzzer, "play"):
            self._buzzer.play(260)

        # Check threshold (< 30%)
        if pct < 0.3:
            Log.w(f"FeedbackController: Feedback dropped below 30% ({pct_int}%)! Triggering alarm.")
            if self._model:
                self._model.processEvent("feedback_below_threshold")
        else:
            # Normal return to idle after 5 seconds
            if self._timer:
                self._timer.start(5)

    def enter_alarm(self) -> None:
        """Entry action for State 4 (Alarm mode)."""
        Log.w("FeedbackController: Entering Alarm state! Manager alert active.")
        self.start_alarm()

    def exit_alarm(self) -> None:
        """Exit action for State 4 (Alarm mode)."""
        Log.i("FeedbackController: Exiting Alarm state.")
        self.stop_alarm()
        self._stats.reset()

    # =========================================================================
    # Alarm Control Methods
    # =========================================================================

    def start_alarm(self) -> None:
        """Activate the audible and visual emergency manager alert."""
        self._alarm_active = True
        self._alarm_tone_toggle = False
        self._last_alarm_toggle = time.time()

        if self._timer:
            self._timer.cancel()

        if self._lcd:
            self._show_display("CALLING MANAGER", "Score Below 30%!")

        # Turn entire light strip red
        if self._lights:
            if hasattr(self._lights, "set_red"):
                self._lights.set_red()
            elif hasattr(self._lights, "setColor"):
                self._lights.setColor(RED)
            elif hasattr(self._lights, "fill"):
                self._lights.fill(RED)

    def stop_alarm(self) -> None:
        """Deactivate the emergency alert."""
        self._alarm_active = False

        if self._buzzer and hasattr(self._buzzer, "stop"):
            self._buzzer.stop()

        if self._lights:
            if hasattr(self._lights, "clear"):
                self._lights.clear()
            elif hasattr(self._lights, "off"):
                self._lights.off()

    def update(self) -> None:
        """Periodic update cycle (handles alarm sound toggling)."""
        if self._alarm_active and self._buzzer:
            now = time.time()
            if now - self._last_alarm_toggle >= 0.25:
                self._last_alarm_toggle = now
                self._alarm_tone_toggle = not self._alarm_tone_toggle
                freq = 1100 if self._alarm_tone_toggle else 700
                if hasattr(self._buzzer, "play"):
                    self._buzzer.play(freq)

    # =========================================================================
    # StateModel Protocol Callbacks
    # =========================================================================

    def stateEntered(self, state: int, event: str) -> None:
        """
        Lifecycle callback invoked when entering a state.

        Parameters:
        ----------
        state : int
            State number being entered.
        event : str
            Event that triggered the transition.
        """
        Log.i(f"StateModel: Entered State {state} on event '{event}'")
        if state == self.STATE_WELCOME:
            self.enter_welcome()
        elif state == self.STATE_SELECTION:
            self.enter_selection()
        elif state == self.STATE_HAPPY:
            self.enter_happy()
        elif state == self.STATE_UNHAPPY:
            self.enter_unhappy()
        elif state == self.STATE_ALARM:
            self.enter_alarm()

    def stateLeft(self, state: int, event: str) -> None:
        """
        Lifecycle callback invoked when leaving a state.

        Parameters:
        ----------
        state : int
            State number being exited.
        event : str
            Event that triggered the transition.
        """
        Log.i(f"StateModel: Left State {state} on event '{event}'")
        if state in (self.STATE_HAPPY, self.STATE_UNHAPPY):
            if self._buzzer and hasattr(self._buzzer, "stop"):
                self._buzzer.stop()
        elif state == self.STATE_ALARM:
            self.exit_alarm()

    def stateDo(self, state: int) -> None:
        """
        Continuous activity callback invoked during the model execution loop.

        Parameters:
        ----------
        state : int
            Currently active state.
        """
        if state == self.STATE_ALARM:
            self.update()

    def stateEvent(self, state: int, event: str) -> bool:
        """In-state event handler fallback."""
        return False

    def buttonPressed(self, button) -> None:
        """
        Direct button press callback for manual event processing.

        Parameters:
        ----------
        button : Button
            Button instance that triggered the press.
        """
        btn_name = getattr(button, "_name", str(button))
        Log.i(f"FeedbackController: Button pressed: {btn_name}")
        if self._model:
            self._model.processEvent(f"{btn_name}_press")

    # =========================================================================
    # Helper Display & Light Methods
    # =========================================================================

    def _show_display(self, line1: str, line2: str) -> None:
        """Helper to safely format 2-line messages on the LCD."""
        if not self._lcd:
            return
        if hasattr(self._lcd, "show_message"):
            self._lcd.show_message(line1, line2)
        elif hasattr(self._lcd, "clear") and hasattr(self._lcd, "showText"):
            self._lcd.clear()
            self._lcd.showText(line1, row=0, col=0)
            self._lcd.showText(line2, row=1, col=0)

    def _update_light_strip(self) -> None:
        """Helper to reflect the current satisfaction ratio on the LED strip."""
        if not self._lights:
            return
        level = self._stats.get_light_level()
        if hasattr(self._lights, "show_level"):
            self._lights.show_level(level)
        elif hasattr(self._lights, "fill"):
            color = GREEN if self._stats.calculate_percentage() >= 0.5 else RED
            self._lights.fill(color)

    def run(self) -> None:
        """Run the kiosk main execution loop."""
        Log.i("FeedbackController: Starting Kiosk State Machine...")
        if self._model:
            self._model.run()

    def stop(self) -> None:
        """Stop the kiosk state machine."""
        Log.i("FeedbackController: Stopping Kiosk...")
        if self._model:
            self._model.stop()


if __name__ == "__main__":
    Log.i("Starting FeedbackController self-test...")

    # Mock hardware components for self-contained desktop verification
    class MockLCD:
        def __init__(self): self.lines = ["", ""]
        def clear(self): self.lines = ["", ""]
        def showText(self, t, row=0, col=0): self.lines[row] = t; Log.i(f"[Mock LCD Row {row}]: {t}")
        def show_message(self, l1, l2): self.clear(); self.showText(l1, 0); self.showText(l2, 1)

    class MockLights:
        def __init__(self): self.color = None; self.level = 0
        def clear(self): self.color = None; Log.i("[Mock Lights]: Cleared")
        def off(self): self.clear()
        def on(self): Log.i("[Mock Lights]: ON")
        def set_red(self): self.color = "RED"; Log.i("[Mock Lights]: Set RED")
        def show_level(self, lvl): self.level = lvl; Log.i(f"[Mock Lights]: Level {lvl}")

    class MockBuzzer:
        def __init__(self): self.tone = 0
        def play(self, tone): self.tone = tone; Log.i(f"[Mock Buzzer]: Playing {tone}Hz")
        def stop(self): self.tone = 0; Log.i("[Mock Buzzer]: Stopped")

    class MockButton:
        def __init__(self, name):
            self._name = name
            self._handler = None
        def setHandler(self, h): self._handler = h

    class MockSensor:
        def __init__(self, name):
            self._name = name
            self._tripped = False
        def tripped(self): return self._tripped
        def set_tripped(self, v): self._tripped = v

    class MockTimer:
        def __init__(self, name):
            self._name = name
            self.running = False
            self._handler = None
        def setHandler(self, h): self._handler = h
        def start(self, s): self.running = True; Log.i(f"[Mock Timer]: Started for {s}s")
        def cancel(self): self.running = False; Log.i("[Mock Timer]: Cancelled")
        def check(self): pass

    lcd = MockLCD()
    lights = MockLights()
    buzzer = MockBuzzer()
    green = MockButton("green")
    red = MockButton("red")
    mgr = MockButton("manager")
    timer = MockTimer("timer")
    uss = MockSensor("uss")

    controller = FeedbackController(
        lcd=lcd, lights=lights, buzzer=buzzer, uss=uss,
        green_btn=green, red_btn=red, manager_btn=mgr,
        timer=timer
    )

    # 1. Test Welcome entry
    controller.stateEntered(FeedbackController.STATE_WELCOME, "no_event")
    assert lcd.lines[0] == "Welcome to Ikea", "Welcome line 1 check"

    # 2. Test Selection entry (customer arrives)
    controller.stateEntered(FeedbackController.STATE_SELECTION, "uss_trip")
    assert lcd.lines[0] == "How was visit?", "Selection line 1 check"
    assert timer.running is True, "Timer should be running in Selection"

    # 3. Test Happy feedback
    controller.stateEntered(FeedbackController.STATE_HAPPY, "green_press")
    assert controller._stats.get_total_count() == 1, "Total should be 1"
    assert buzzer.tone == 880, "Happy tone check"

    # 4. Return to Welcome
    controller.stateLeft(FeedbackController.STATE_HAPPY, "timer_timeout")
    controller.stateEntered(FeedbackController.STATE_WELCOME, "timer_timeout")

    # 5. Customer 2 arrives -> Selection -> Unhappy (below 30% check: 1 happy, 3 unhappy = 25%)
    controller.stateEntered(FeedbackController.STATE_SELECTION, "uss_trip")
    controller.stateEntered(FeedbackController.STATE_UNHAPPY, "red_press")
    controller.stateEntered(FeedbackController.STATE_UNHAPPY, "red_press")
    controller.stateEntered(FeedbackController.STATE_UNHAPPY, "red_press")
    pct = controller._stats.calculate_percentage()
    assert pct == 0.25, f"Expected 0.25, got {pct}"

    # 6. Test Alarm entry
    controller.stateEntered(FeedbackController.STATE_ALARM, "feedback_below_threshold")
    assert controller._alarm_active is True, "Alarm should be active"
    assert lights.color == "RED", "Lights should be red in alarm"

    # 7. Test Manager reset
    controller.stateLeft(FeedbackController.STATE_ALARM, "manager_press")
    assert controller._alarm_active is False, "Alarm should be cleared"
    assert controller._stats.get_total_count() == 0, "Stats should be reset to 0 by manager"

    Log.i("Testing complete - all checks passed!")
