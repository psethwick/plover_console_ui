from threading import Event
from functools import partial

from time import sleep

from plover.oslayer.keyboardcontrol import KeyboardEmulation
from plover.oslayer.wmctrl import SetForegroundWindow, GetForegroundWindow

from plover.gui_none.engine import Engine

from prompt_toolkit import Application

def show_error(title, message):
    print(title + message)


# minimum
# TODO suggestions
# TODO enable/disable
# TODO choose machine
# TODO dictionary update
# TODO lookup
# TODO commandline args?

# TODO should maybe find a way to find the window
tui_window = GetForegroundWindow()
previous_window = None

def on_lookup():
    previous_window = GetForegroundWindow()
    SetForegroundWindow(tui_window)
    sleep(2)
    SetForegroundWindow(previous_window)

app = Application(full_screen=True)

def main(config):
    engine = Engine(config, KeyboardEmulation())
    if not engine.load_config():
        return 3
    quitting = Event()
    engine.hook_connect('quit', quitting.set)
    engine.start()
    app.run()
    quitting.wait()
    engine.quit()
    return engine.join()
