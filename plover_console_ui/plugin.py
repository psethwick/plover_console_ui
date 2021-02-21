from functools import partial
from threading import Event

from plover.oslayer.keyboardcontrol import KeyboardEmulation
from plover import log
from plover.config import Config

# this will never come back to bite me
from plover.log import __logger

from .console_engine import ConsoleEngine
from .notification import ConsoleNotificationHandler
from .presentation import layout, application, style_colored
from .config import getvalue

# TODO finish machine options
# TODO finish rest of config
# TODO dictionary pane
# TODO dictionary enable/disable
# TODO add/remove dictionaries
# TODO readme
# TODO gifs for readme
# TODO attribute bits borrowed from plover source
# TODO publish pipeline + sanity checks
# TODO work out why windows is broke and at least document
# TODO minimise windows-launcher
# post mvp
# TODO completers? Buffer.completer


def show_error(title, message):
    # this only gets called if gui.main fails
    # so we can't rely on prompt application stuff
    # printing is fine
    print(f"{title}: {message}")


def config_saver(config: Config, output, update):
    # TODO once I've finished config, remove this logging
    # or at least trim it a bit
    output(f"Saving config: {update}")
    # only necessary if version of plover is older than the config fixes
    # probably will remove this after 4.0.0 released
    if hasattr(config, "target_file"):
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
    log.add_handler(ConsoleNotificationHandler(layout.output_to_console))

    engine = ConsoleEngine(config, KeyboardEmulation(), layout)

    if not engine.load_config():
        return 3

    engine.hook_connect(
        "config_changed",
        partial(config_saver, config, layout.output_to_console),
    )

    if engine.config["show_stroke_display"]:
        layout.toggle_tape()

    if engine.config["show_suggestions_display"]:
        layout.toggle_suggestions()

    fg = getvalue(engine._config, "fg")

    if fg:
        application.style = style_colored(fg)

    quitting = Event()
    engine.hook_connect("quit", quitting.set)
    engine.start()

    code = application.run()

    engine.quit()
    quitting.wait()
    engine.join()
    return code
