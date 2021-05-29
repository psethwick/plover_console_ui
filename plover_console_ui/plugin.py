from functools import partial
from threading import Event

from plover.oslayer.keyboardcontrol import KeyboardEmulation
from plover import log
from plover.config import Config

# this will never come back to bite me
from plover.log import __logger

from .console_engine import ConsoleEngine
from .notification import notification_handler
from .application import application, create_style
from .layout import layout
from .config import console_ui_options


def show_error(title, message):
    # this only gets called if gui.main fails
    # so we can't rely on prompt application stuff
    # printing is fine
    print(f"{title}: {message}")


def config_saver(config: Config, output, update):
    # only necessary if version of plover is older than the config fixes
    # probably will remove this after 4.0.0 released
    if hasattr(config, "target_file"):
        with open(config.target_file, "wb") as f:
            config.save(f)


def main(config: Config, controller=None):
    # this screws things up
    # hax tho
    log.remove_handler(__logger._print_handler)

    # mor hax ... I don't wanna see QT notifications
    log.remove_handler(__logger._platform_handler)
    __logger._platform_handler = None

    for option in console_ui_options:
        config._OPTIONS[option.name] = option

    engine = ConsoleEngine(config, KeyboardEmulation(), layout, controller)

    if not engine.load_config():
        return 3

    engine.hook_connect(
        "config_changed",
        partial(config_saver, config, layout.output_to_console),
    )

    notification_handler.set_output(layout.output_to_console)
    notification_handler.setLevel(engine.config["console_ui_loglevel"])
    log.add_handler(notification_handler)

    if engine.config["show_suggestions_display"]:
        layout.toggle_suggestions()

    if engine.config["show_stroke_display"]:
        layout.toggle_tape()

    fg = engine.config["console_ui_fg"]
    bg = engine.config["console_ui_bg"]

    application.style = create_style(fg, bg)

    quitting = Event()
    engine.hook_connect("quit", quitting.set)

    engine.start()
    code = application.run()

    engine.quit()
    quitting.wait()
    engine.join()
    return code
