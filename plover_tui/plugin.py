from threading import Event
from functools import partial

from time import sleep

from plover.oslayer.keyboardcontrol import KeyboardEmulation
from plover.oslayer.wmctrl import SetForegroundWindow, GetForegroundWindow

from plover.registry import registry
from plover.steno_dictionary import StenoDictionaryCollection
from prompt_toolkit import application
from prompt_toolkit.filters import app

from prompt_toolkit import PromptSession

from prompt_toolkit.layout.controls import FormattedTextControl

from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit import Application
from prompt_toolkit.shortcuts import input_dialog
from prompt_toolkit.widgets import RadioList

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.containers import Float, HSplit, VSplit, Window
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import (
    Box,
    Button,
    Checkbox,
    Dialog,
    Frame,
    Label,
    MenuContainer,
    MenuItem,
    ProgressBar,
    RadioList,
    TextArea,
)

from .tuiengine import TuiEngine

class Stroky:
    def __init__(self) -> None:
        self.strokes = ""

    def add(self, stroke: str):
        self.strokes += stroke + "\n"

    def get(self):
        return self.strokes

strocks = Stroky()

def on_stroked(app, stroke):
    strocks.add(stroke.rtfcre)
    app.invalidate()

def accept_yes():
    get_app().exit(result=True)


def accept_no():
    get_app().exit(result=False)


def do_exit():
    get_app().exit(result=False)


yes_button = Button(text="Yes", handler=accept_yes)
no_button = Button(text="No", handler=accept_no)
textfield = Frame(Window(content=FormattedTextControl(text=strocks.get)), title="Paper Tape")
checkbox1 = Checkbox(text="Checkbox")
checkbox2 = Checkbox(text="Checkbox")
dictionaryCheckboxes = [checkbox1, checkbox2]

radios = RadioList(
    values=[
        ('lol', 'lol')
    ]
)

animal_completer = WordCompleter(
    [
        "alligator",
        "ant",
        "ape",
        "bat",
        "bear",
        "beaver",
        "bee",
        "bison",
        "butterfly",
        "cat",
        "chicken",
        "crocodile",
        "dinosaur",
        "dog",
        "dolphin",
        "dove",
        "duck",
        "eagle",
        "elephant",
        "fish",
        "goat",
        "gorilla",
        "kangaroo",
        "leopard",
        "lion",
        "mouse",
        "rabbit",
        "rat",
        "snake",
        "spider",
        "turkey",
        "turtle",
    ],
    ignore_case=True,
)

root_container = HSplit(
    [
        VSplit(
            [
                Frame(body=Label(text="Left frame\ncontent")),
                Dialog(title="The custom window", body=Label("hello\ntest")),
                textfield,
            ],
            height=D(),
        ),
        VSplit(
            [
                Frame(body=ProgressBar(), title="Progress bar"),
                Frame(
                    title="Checkbox list",
                    body=HSplit(dictionaryCheckboxes),
                ),
                Frame(title="Radio list", body=radios),
            ],
            padding=1,
        ),
    ]
)

root_container = MenuContainer(
    body=root_container,
    menu_items=[
        MenuItem(
            "File",
            children=[
                MenuItem("New"),
                MenuItem(
                    "Open",
                    children=[
                        MenuItem("From file..."),
                        MenuItem("From URL..."),
                        MenuItem(
                            "Something else..",
                            children=[
                                MenuItem("A"),
                                MenuItem("B"),
                                MenuItem("C"),
                                MenuItem("D"),
                                MenuItem("E"),
                            ],
                        ),
                    ],
                ),
                MenuItem("Save"),
                MenuItem("Save as..."),
                MenuItem("-", disabled=True),
                MenuItem("Exit", handler=do_exit),
            ],
        ),
        MenuItem(
            "Edit",
            children=[
                MenuItem("Undo"),
                MenuItem("Cut"),
                MenuItem("Copy"),
                MenuItem("Paste"),
                MenuItem("Delete"),
                MenuItem("-", disabled=True),
                MenuItem("Find"),
                MenuItem("Find next"),
                MenuItem("Replace"),
                MenuItem("Go To"),
                MenuItem("Select All"),
                MenuItem("Time/Date"),
            ],
        ),
        MenuItem("View", children=[MenuItem("Status Bar")]),
        MenuItem("Info", children=[MenuItem("About")]),
    ],
    floats=[
        Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=16, scroll_offset=1),
        ),
    ],
)

# Global key bindings.
bindings = KeyBindings()
bindings.add("tab")(focus_next)
bindings.add("s-tab")(focus_previous)


style = Style.from_dict(
    {
        "window.border": "#888888",
        "shadow": "bg:#222222",
        "menu-bar": "bg:#aaaaaa #888888",
        "menu-bar.selected-item": "bg:#ffffff #000000",
        "menu": "bg:#888888 #ffffff",
        "menu.border": "#aaaaaa",
        "window.border shadow": "#444444",
        "focused  button": "bg:#880000 #ffffff noinherit",
        # Styling for Dialog widgets.
        "button-bar": "bg:#aaaaff",
    }
)


def back_channel(engine, app: Application):
    if radios.current_value != engine.config['machine_type']:
            engine.config = {"machine_type": radios.current_value}



def show_error(title, message):
    # TODO probably float a window?
    # or maybe just have a 'notifications' pane
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

    result = input_dialog(
        title="Input dialog example", text="Please type your name:"
    ).run()


def on_config_changed(engine, app, config):
    machine = config["machine_type"]
    radios.values = [
        (m, m) for m
        in sorted(
            [m.name for m in registry.list_plugins("machine") 
            if m.name in ['Keyboard', 'Gemini PR']], # could perhaps configure this
            key=lambda m: m == machine)
    ]
    radios.current_value = machine
    app.invalidate()

def on_dictionaries_loaded(app, checkbs, dicts: StenoDictionaryCollection):
    pass
    # print(dicts)
    # checkbs = [ 
    #     Checkbox(d.short_path, d.enabled)
    #     for d in dicts
    # ]
    # app.invalidate()

def main(config):
    engine = TuiEngine(config, KeyboardEmulation())
    if not engine.load_config():
        return 3
    quitting = Event()

    engine.start()

    with patch_stdout():
        session = PromptSession()
        while True:
            try:
                text = session.prompt('> ')
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            else:
                print('You entered:', text)
        print('GoodBye!')
    
    engine.quit()
    quitting.wait()
    return engine.join()

def main_FULL(config):
    engine = TuiEngine(config, KeyboardEmulation())
    if not engine.load_config():
        return 3
    quitting = Event()
    application = Application(
        layout=Layout(root_container),
        key_bindings=bindings,
        style=style,
        mouse_support=True,
        full_screen=True,
        before_render=partial(back_channel, engine)
    )
    engine.hook_connect('quit', quitting.set)
    engine.hook_connect('stroked', partial(on_stroked, application))
    engine.hook_connect('dictionaries_loaded', partial(on_dictionaries_loaded, application, dictionaryCheckboxes))
    engine.hook_connect('config_changed', partial(on_config_changed, engine, application))
    engine.start()

    application.run()
    engine.quit()
    quitting.wait()
    return engine.join()
