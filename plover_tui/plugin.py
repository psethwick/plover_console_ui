from concurrent.futures.process import ProcessPoolExecutor
import asyncio
from concurrent import futures
from threading import Event, current_thread
from functools import partial, wraps

from plover.oslayer.keyboardcontrol import KeyboardEmulation
from plover.oslayer.wmctrl import SetForegroundWindow, GetForegroundWindow

from plover import log

from plover.registry import registry
from plover.steno_dictionary import StenoDictionaryCollection
from plover.gui_none.engine import Engine

from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.filters import app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea, Frame
from prompt_toolkit import patch_stdout

from .tuiengine import TuiEngine

help_text = """
Type any expression (e.g. "4 + 4") followed by enter to execute.
Press Control-C to exit.
"""

output_field = TextArea(text=help_text, focusable=False)
paper_tape = TextArea(focusable=False)
suggestions = TextArea(focusable=False)
input_field = TextArea(
    height=1,
    prompt=">>> ",
    multiline=False,
    wrap_lines=False
)

container = HSplit(
    [
        VSplit([
            output_field, 
            HSplit([
                Frame(paper_tape, title="Paper Tape"),
                Frame(suggestions, title="Suggestions"),
            ]),
        ]),
        input_field,
    ]
)

# Attach accept handler to the input field. We do this by assigning the
# handler to the `TextArea` that we created earlier. it is also possible to
# pass it to the constructor of `TextArea`.
# NOTE: It's better to assign an `accept_handler`, rather then adding a
#       custom ENTER key binding. This will automatically reset the input
#       field and add the strings to the history.
def accept(engine, buff):
    # Evaluate "calculator" expression.
    try:
        #output = engine.config["machine_type"]
        output = str(current_thread())

    except BaseException as e:
        output = "\n\n{}".format(e)
    new_text = output_field.text + output

    # Add text to output buffer.
    output_field.buffer.document = Document(
        text=new_text, cursor_position=len(new_text)
    )
    application.invalidate()

# The key bindings.
kb = KeyBindings()

@kb.add("c-c")
@kb.add("c-q")
def _(event):
    " Pressing Ctrl-Q or Ctrl-C will exit the user interface. "
    event.app.exit()

# TODO should maybe find a way to find the window
tui_window = None
previous_window = None

@kb.add("c-x")
def _(event):
    SetForegroundWindow(previous_window)
    
# Style.
style = Style(
    [
        ("output-field", "bg:#000044 #ffffff"),
        ("input-field", "bg:#000000 #ffffff"),
        ("line", "#004400"),
    ]
)

# Run application.

application = Application(
    layout=Layout(container, focused_element=input_field),
    key_bindings=kb,
    style=style,
    mouse_support=False,
    full_screen=True,
    enable_page_navigation_bindings=False
)

def show_error(title, message):
    new_text = f"{output_field.buffer.text[:1000]}\nError: {title} - {message}"
    output_field.buffer.document = Document(
        text=new_text, cursor_position=len(new_text)
    )
    application.invalidate()


def on_stroked(stroke):
    new_text = f"{paper_tape.text[:1000]}\n{stroke.rtfcre}"
    paper_tape.buffer.document = Document(
        text=new_text, cursor_position=len(new_text)
    )
    application.invalidate()
    
def on_focus():
    previous_window = GetForegroundWindow()
    SetForegroundWindow(tui_window)

# minimum
# TODO suggestions
# TODO enable/disable
# TODO choose machine
# TODO dictionary update
# TODO lookup
# TODO commandline args?


def main(config):
    engine = TuiEngine(config, KeyboardEmulation())
    engine.daemon = True
    input_field.accept_handler = partial(accept, engine)
    if not engine.load_config():
        return 3
    quitting = Event()
    engine.hook_connect('quit', quitting.set)
    engine.hook_connect('stroked', on_stroked)
    engine.hook_connect('focus', on_focus)
    #engine.hook_connect('dictionaries_loaded', partial(on_dictionaries_loaded, application, dictionaryCheckboxes))
    #engine.hook_connect('config_changed', partial(on_config_changed, engine, application))

    engine.start()

    application.run()

    quitting.wait()
    return engine.join()
