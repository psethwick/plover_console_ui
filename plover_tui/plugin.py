from plover.translation import unescape_translation
from plover.oslayer.keyboardcontrol import KeyboardEmulation
from plover import log
# this will never come back to bite me
from plover.log import __logger

from plover.config import Config
from plover.registry import registry
from plover.steno_dictionary import StenoDictionaryCollection
from prompt_toolkit.buffer import Buffer

from prompt_toolkit.application import Application, get_app
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, DynamicContainer
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea, Dialog

from .tuiengine import TuiEngine
from .suggestions import on_translated, format_suggestions
from .notification import TuiNotificationHandler
from .focus import Focus
from .layout import TuiLayout

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




layout = TuiLayout(input_field, console, paper_tape, suggestions)

container = DynamicContainer(layout)

# The key bindings.
kb = KeyBindings()

@kb.add("c-c")
@kb.add("c-q")
def _(event):
    " Pressing Ctrl-Q or Ctrl-C will exit the user interface. "
    event.app.exit(0)

@kb.add("escape", eager=True)
def _(event):
    focus.prev()

# Style.
style = Style.from_dict(
    {
        "status": "reverse",
        "shadow": "bg:#440044",
    }
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
# TODO dictionary update
# TODO tui options?


def output_to_buffer(buffer, text):
    o = f"{buffer.text[:1000]}\n{text}"
    buffer.document = Document(
        text=o, cursor_position=len(o)
    )
    get_app().invalidate()


def accept(engine: TuiEngine, config: Config, buff: Buffer):
    try:
        # TODO
        # all this shizzle should move to a class or something
        # probably combined with the prompt state I wanna make
        output = f"Unknown command '{buff.text}'"
        words = buff.text.split()
        if len(words) > 0:
            if words[0].lower() == "quit":
                output = "Exiting..."
                application.exit(0)
            if words[0] == "lookup": 
                lookup = unescape_translation(" ".join(words[1:]))
                output = f"Lookup\n------\n"
                suggestions = format_suggestions(engine.get_suggestions(lookup))
                if suggestions:
                    output += suggestions
                else:
                    output += f"'{lookup}' not found"
            if words[0] == "tape":
                output = layout.toggle_tape()
            if words[0] == "suggestions":
                output = layout.toggle_suggestions()
            if words[0] == "console":
                output = layout.toggle_console()
            if words[0] == "save":
                output = "Saving config..."
                with open(config.target_file, 'wb') as f:
                    config.save(f)
            if words[0] == "output":
                if engine.output:
                    engine.output = False
                else:
                    engine.output = True
                output = "Output: " + str(engine.output)
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

def on_add_translation(engine):
    focus.set_prev()
    focus.tui()
    strokes = TextArea(prompt="Strokes:")
    output_to_buffer(strokes.buffer, "testing")
    translation = TextArea(prompt="Output: ")

    output = TextArea(focusable=False)
#   maybe~ buttons
    dialog = Dialog( # maybe style this different
        title="Add Translation",
        body=VSplit(
            [
                HSplit(
                    [
                        strokes,
                        translation,
                    ]
                ),
                output
            ],
            #padding=D(preferred=1, max=1),
        ),
        width=40
        #with_background=True,
    )
    layout.float = dialog
    get_app().layout.focus(dialog)


def show_error(title, message):
    # this only gets called if gui.main fails
    # so we can't rely on prompt application stuff
    # printing is fine
    print(f"{title}: {message}")

def status_bar_text(engine) -> str:
    return \
        " | Plover" + \
        " | Machine: " + engine.config["machine_type"] + \
        " | Output: " + str(engine.output) + \
        " | System: " + engine.config["system_name"] + \
        " |"



def main(config: Config):
    # this screws things up
    # hax tho
    log.remove_handler(__logger._print_handler)

    # mor hax ... I don't wanna see QT notifications
    __logger._platform_handler = None

    # lets set up something better
    log.add_handler(TuiNotificationHandler(partial(output_to_buffer, console.buffer)))

    engine = TuiEngine(config, KeyboardEmulation())
    engine.daemon = True

    input_field.accept_handler = partial(accept, engine, config)

    layout.load_status(partial(status_bar_text, engine))


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

    engine.hook_connect('add_translation', partial(on_add_translation, engine))

    engine.start()

    code = application.run()

    engine.quit()
    quitting.wait()
    engine.join()
    return code
