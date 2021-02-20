from functools import partial
from threading import Thread, current_thread

from plover.engine import StenoEngine

from prompt_toolkit.layout.processors import BeforeInput

from .commander import Commander
from .commands import build_commands
from .suggestions import on_translated
from .presentation import ConsoleLayout


def status_bar_text(engine) -> str:
    return (
        " | Plover"
        f" | Machine: {engine.config['machine_type']}"
        f" | Output: {'Enabled' if engine.output else 'Disabled'}"
        f" | System: { engine.config['system_name']}"
        " |"
    )

# TODO hook dictionaries_loaded


class ConsoleEngine(StenoEngine, Thread):
    def __init__(self, config, keyboard_emulation, layout: ConsoleLayout):
        StenoEngine.__init__(self, config, keyboard_emulation)
        Thread.__init__(self)
        self.name += "-engine"
        self.layout = layout
        self.hook_connect("stroked", layout.output_to_tape)
        self.hook_connect("focus", layout.focus_toggle)
        self.hook_connect("translated", self.on_translated)
        self.hook_connect("add_translation", partial(layout.on_add_translation, self))
        self.cmder = Commander(build_commands(self, layout), layout.output_to_console)

        def on_lookup():
            layout.focus_console()
            self.cmder.set_state(["lookup"], layout.exit_modal)

        self.hook_connect("lookup", on_lookup)

        def on_configure():
            layout.focus_console()
            self.cmder.set_state(["configure"], layout.exit_modal)

        self.hook_connect("configure", on_configure)
        self.hook_connect("config_changed", layout.on_config_changed)

        def on_quit():
            self.cmder.set_state([])
            self.cmder.handle_command(["exit"])

        self.hook_connect("quit", on_quit)

        layout.cmder_input.control.input_processors.append(
            BeforeInput(self.cmder.prompt, style="class:text-area.prompt"),
        )

        layout.cmder_input.accept_handler = self.cmder
        layout.status_bar.text = partial(status_bar_text, self)
        # nice starter
        self.cmder.handle_command(["help"])

    def _in_engine_thread(self):
        return current_thread() == self

    def start(self):
        Thread.start(self)
        StenoEngine.start(self)

    def join(self):
        Thread.join(self)
        return self.code

    def on_translated(self, old, new):
        on_translated(self, self.layout.output_to_suggestions, old, new)
