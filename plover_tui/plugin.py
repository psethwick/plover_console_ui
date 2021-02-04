from functools import partial
from threading import Event

from plover.oslayer.keyboardcontrol import KeyboardEmulation
from plover import log
# this will never come back to bite me
from plover.log import __logger

from plover.config import Config

from prompt_toolkit.application import Application, get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, DynamicContainer
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea, Dialog

from .tuiengine import TuiEngine
from .suggestions import on_translated
from .notification import TuiNotificationHandler
from .focus import Focus
from .presentation import TuiLayout, output_to_buffer
from .commander import Commander


focus = Focus()
kb = KeyBindings()

@kb.add("c-c")
@kb.add("c-q")
def _(event):
    " Pressing Ctrl-Q or Ctrl-C will exit the user interface. "
    event.app.exit(0)

@kb.add("escape", eager=True)
def _(event):
    focus.prev()

style = Style.from_dict(
    {
        "status": "reverse",
        "shadow": "bg:#440044",
    }
)

layout = TuiLayout()

application = Application(
    layout=Layout(DynamicContainer(layout), focused_element=layout.input_field),
    key_bindings=kb,
    style=style,
    mouse_support=False,
    full_screen=True,
    enable_page_navigation_bindings=False
)

# minimum
# TODO dictionary update
# TODO tui options?

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
    log.add_handler(TuiNotificationHandler(layout.output_to_console))

    engine = TuiEngine(config, KeyboardEmulation())

    if not engine.load_config():
        return 3
    quitting = Event()
    
    layout.input_field.accept_handler = Commander(engine, layout)

    layout.load_status(partial(status_bar_text, engine))

    engine.hook_connect('quit', quitting.set)

    engine.hook_connect('stroked', layout.output_to_tape)
    engine.hook_connect('focus', on_focus)
    engine.hook_connect('translated',
                        partial(on_translated,
                                engine,
                                layout.output_to_suggestions))

    engine.hook_connect('add_translation', partial(on_add_translation, engine))

    engine.start()

    code = application.run()

    engine.quit()
    quitting.wait()
    engine.join()
    return code
