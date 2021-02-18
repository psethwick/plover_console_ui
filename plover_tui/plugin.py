from functools import partial
from threading import Event

from plover.oslayer.keyboardcontrol import KeyboardEmulation
from plover import log
from plover.config import Config

# this will never come back to bite me
from plover.log import __logger

from .tuiengine import TuiEngine
from .notification import TuiNotificationHandler
from .presentation import layout, application


# TODO tui options?
# TODO layout switch hor/ver


def show_error(title, message):
    # this only gets called if gui.main fails
    # so we can't rely on prompt application stuff
    # printing is fine
    print(f"{title}: {message}")


def config_saver(config: Config, output, update):
    output(f"Saving config: {update}")
    with open(config.target_file, "wb") as f:
        config.save(f)


def main(config: Config):
    # this screws things up
    # hax tho
    log.remove_handler(__logger._print_handler)

    # mor hax ... I don't wanna see QT notifications
    log.remove_handler(__logger._platform_handler)
    __logger._platform_handler = None

    # lets set up something better
    log.add_handler(TuiNotificationHandler(layout.output_to_console))

    engine = TuiEngine(config, KeyboardEmulation(), layout)

    if not engine.load_config():
        return 3

    engine.hook_connect(
        "config_changed", partial(config_saver, config, layout.output_to_console)
    )

    if engine.config["show_stroke_display"]:
        layout.toggle_tape()

    if engine.config["show_suggestions_display"]:
        layout.toggle_suggestions()

    quitting = Event()
    engine.hook_connect("quit", quitting.set)
    engine.start()

    code = application.run()

    engine.quit()
    quitting.wait()
    engine.join()
    return code
