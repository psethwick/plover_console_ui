from functools import partial
from threading import Event

from plover.oslayer.keyboardcontrol import KeyboardEmulation
from plover import log
from plover.config import Config
# this will never come back to bite me
from plover.log import __logger

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import DynamicContainer
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.styles import Style

from .tuiengine import TuiEngine
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

layout = TuiLayout(focus)

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

    engine = TuiEngine(config, KeyboardEmulation(), layout)

    if not engine.load_config():
        return 3

    cmder = Commander(engine, layout)

    layout.input_field.control.input_processors.append(
                BeforeInput(cmder.prompt, style="class:text-area.prompt"),
    )

    layout.input_field.accept_handler = cmder
    layout.status_bar.text = partial(status_bar_text, engine)

    quitting = Event()
    engine.hook_connect('quit', quitting.set)
    engine.start()

    code = application.run()

    engine.quit()
    quitting.wait()
    engine.join()
    return code
