
from plover.oslayer.wmctrl import SetForegroundWindow, GetForegroundWindow


class Focus():
    def __init__(self) -> None:
        self._tui = GetForegroundWindow()
        self._prev = None
    
    def reset_tui(self) -> None:
        self._tui = GetForegroundWindow()

    def set_prev(self):
        self._prev = GetForegroundWindow()

    def prev(self):
        SetForegroundWindow(self._prev)
    
    def tui(self):
        SetForegroundWindow(self._tui)
    