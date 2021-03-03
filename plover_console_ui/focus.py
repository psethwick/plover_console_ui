from plover.oslayer.wmctrl import SetForegroundWindow, GetForegroundWindow


class Focus:
    def __init__(self) -> None:
        self.console = GetForegroundWindow()
        self.prev = None

    def reset_console(self) -> None:
        self.console = GetForegroundWindow()

    def toggle(self) -> None:
        current = GetForegroundWindow()
        if current == self.console:
            self.focus_prev()
        else:
            self.prev = current
            self.focus_console()

    def set_prev(self):
        self.prev = GetForegroundWindow()

    def focus_prev(self):
        if self.prev:
            SetForegroundWindow(self.prev)

    def focus_console(self):
        self.set_prev()
        if self.console:
            SetForegroundWindow(self.console)


focus = Focus()

focus_console = focus.focus_console
focus_prev = focus.focus_prev
focus_toggle = focus.toggle
