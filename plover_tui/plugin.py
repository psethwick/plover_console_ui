from plover.translation import unescape_translation
from plover.oslayer.keyboardcontrol import KeyboardEmulation
from plover import log
# this will never come back to bite me
from plover.log import __logger

from plover.registry import registry
from plover.steno_dictionary import StenoDictionaryCollection

from prompt_toolkit.application import Application
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, DynamicContainer, FloatContainer, Window, to_container
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea, Frame, Label

from .tuiengine import TuiEngine
from .suggestions import on_translated, format_suggestions
from .notification import TuiNotificationHandler
from .focus import Focus

from functools import partial

from threading import Event

focus = Focus()

# if I do a multi-level prompty thing
# this should report current command descriptions
help_text = """
Type any expression (e.g. "4 + 4") followed by enter to execute.
Press Control-C to exit.
"""


console = TextArea(text=help_text, focusable=False)
paper_tape = TextArea(focusable=False)
suggestions = TextArea(focusable=False)
input_field = TextArea(
    height=1,
    # TODO this should take a callable
    prompt=">>> ",
    multiline=False,
    wrap_lines=False,
)

class TuiLayout:
    def __init__(self) -> None:
        self.console = Frame(console, title="Console")
        self.tape = Frame(paper_tape, title="Paper Tape")
        self.suggestions = Frame(suggestions, title="Suggestions")
        self.items = [
            self.console
        ]
    
    def __call__(self):
        return VSplit(self.items)        

    def get(self):
        return VSplit(self.items)
    
    def toggle_tape(self):
        if self.tape in self.items:
            self.items.remove(self.tape)
            return "paper tape off"
        else:
            self.items.append(self.tape)
            return "paper tape on"

    def toggle_suggestions(self):
        if self.suggestions in self.items:
            self.items.remove(self.suggestions)
            return "suggestions off"
        else:
            self.items.append(self.suggestions)
            return "suggestions on"



d = TuiLayout()

top_bit = DynamicContainer(d)

container = HSplit(
    [
        top_bit,
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
    try:
        # all this shizzle should move to a class or something
        output = f"Unknown command '{buff.text}'"
        words = buff.text.split()
        if len(words) > 0:
            if words[0].lower() == "quit":
                application.exit()
            if words[0] == "lookup":
                lookup = unescape_translation(" ".join(words[1:]))
                output = f"Lookup - "
                suggestions = format_suggestions(engine.get_suggestions(lookup))
                if suggestions:
                    output += suggestions
                else:
                    output += f"'{lookup}' not found"
            if words[0] == "tape":
                output = d.toggle_tape()
            if words[0] == "suggestions":
                output = d.toggle_suggestions()
            if words[0] == "output":

            if words[0] == "machine":
                new_machine = " ".join(words[1:])
                output = f"Setting machine to {new_machine}"
                engine.config = {"machine_type": new_machine}

    except BaseException as e:
        output = "\n\n{}".format(e)
    output_to_buffer(console.buffer, output)


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

def status_bar_text(engine) -> str:
    return engine.config["machine_type"]

def main(config):
    # this screws things up
    # hax tho
    log.remove_handler(__logger._print_handler)

    # lets set up something better
    log.add_handler(TuiNotificationHandler(partial(output_to_buffer, console.buffer)))

    engine = TuiEngine(config, KeyboardEmulation())
    engine.daemon = True

    input_field.accept_handler = partial(accept, engine)
    container.children.insert(0, to_container(Label(partial(status_bar_text, engine))))

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
