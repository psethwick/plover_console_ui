
from plover.oslayer.wmctrl import SetForegroundWindow, GetForegroundWindow


class Focus():
    def __init__(self) -> None:
        self.console = GetForegroundWindow()
        self.prev = None
    
    def reset_console(self) -> None:
        self.console = GetForegroundWindow()

    def set_prev(self):
        self.prev = GetForegroundWindow()

    def prev(self):
        SetForegroundWindow(self.prev)
    
    def console(self):
        SetForegroundWindow(self.console)
