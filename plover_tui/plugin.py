from plover.translation import unescape_translation
from plover.oslayer.keyboardcontrol import KeyboardEmulation
from plover.oslayer.wmctrl import SetForegroundWindow, GetForegroundWindow
from plover import log
# this will never come back to bite me
from plover.log import __logger

from plover.registry import registry
from plover.steno_dictionary import StenoDictionaryCollection

from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea, Frame

from .tuiengine import TuiEngine
from .suggestions import on_translated, format_suggestions
from .notification import TuiNotificationHandler
from functools import partial

from threading import Event

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
    
focus = Focus()

help_text = """
Type any expression (e.g. "4 + 4") followed by enter to execute.
Press Control-C to exit.
"""


output_field = TextArea(text=help_text, focusable=False)
paper_tape = TextArea(focusable=False)
suggestions = TextArea(focusable=False)
input_field = TextArea(
    height=1,
    # TODO this should take a callable
    prompt=">>> ",
    multiline=False,
    wrap_lines=False
)

container = HSplit(
    [
        VSplit([
            Frame(output_field, title="Plover"),
            Frame(paper_tape, title="Paper Tape"),
            Frame(suggestions, title="Suggestions"),
        ]),
        input_field,
    ]
)

#
# Attach accept handler to the input field. We do this by assigning the
# handler to the `TextArea` that we created earlier. it is also possible to
# pass it to the constructor of `TextArea`.
# NOTE: It's better to assign an `accept_handler`, rather then adding a
#       custom ENTER key binding. This will automatically reset the input
#       field and add the strings to the history.

# The key bindings.
kb = KeyBindings()

@kb.add("c-c")
@kb.add("c-q")
def _(event):
    " Pressing Ctrl-Q or Ctrl-C will exit the user interface. "
    event.app.exit()

@kb.add("escape", eager=True)
def _(event):
    focus.prev()

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

# minimum
# TODO lookup
# TODO dictionary update
# TODO enable/disable
# TODO choose machine
# TODO commandline args?


def output_to_buffer(buffer, text):
    o = f"{buffer.text[:1000]}\n{text}"
    buffer.document = Document(
        text=o, cursor_position=len(o)
    )
    # todo perhaps pass this in
    application.invalidate()


def accept(engine, buff):
    # Evaluate "calculator" expression.
    try:
        output = f"Unknown command '{buff.text}'"
        words = buff.text.split()
        if len(words) > 0:
            if words[0].lower() == "quit":
                application.exit()
            if words[0] == "lookup":
                lookup = unescape_translation(" ".join(words[1:]))
                output = format_suggestions(engine.get_suggestions(lookup))

    except BaseException as e:
        output = "\n\n{}".format(e)
    output_to_buffer(output_field.buffer, output)


def on_stroked(on_output, stroke):
    on_output(stroke.rtfcre)

def on_focus():
    focus.set_prev()
    focus.tui()

def on_add_translation():
    focus.set_prev()
    focus.tui()


def show_error(title, message):
    # this only gets called if gui.main fails
    # so we can't rely on prompt application stuff
    # printing is fine
    print(f"{title}: {message}")


def main(config):
    # this screws things up
    # hax tho
    log.remove_handler(__logger._print_handler)

    # lets set up something better
    log.add_handler(TuiNotificationHandler(partial(output_to_buffer, output_field.buffer)))

    engine = TuiEngine(config, KeyboardEmulation())
    engine.daemon = True
    input_field.accept_handler = partial(accept, engine)
    if not engine.load_config():
        return 3
    quitting = Event()
    engine.hook_connect('quit', quitting.set)
    engine.hook_connect('stroked',
                        partial(on_stroked,
                                partial(output_to_buffer,
                                        paper_tape.buffer)))
    engine.hook_connect('focus', on_focus)
    engine.hook_connect('translated',
                        partial(on_translated,
                                engine,
                                partial(output_to_buffer,
                                        suggestions.buffer)))

    engine.hook_connect('add_translation', on_add_translation)

    engine.start()

    application.run()

    engine.quit()

    quitting.wait()
    return engine.join()
