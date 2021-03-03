from functools import partial
from threading import Thread, current_thread

from plover.engine import StenoEngine

from prompt_toolkit.layout.processors import BeforeInput

from .commander import Commander
from .commands import build_commands
from .layout import ConsoleLayout
from .focus import focus_toggle, focus_console


def status_bar_text(engine) -> str:
    return (
        " | Plover"
        f" | Machine: {engine.config['machine_type']}"
        f" | Output: {'Enabled' if engine.output else 'Disabled'}"
        f" | System: { engine.config['system_name']}"
        " |"
    )


class ConsoleEngine(StenoEngine, Thread):
    def __init__(self, config, keyboard_emulation, layout: ConsoleLayout):
        StenoEngine.__init__(self, config, keyboard_emulation)
        Thread.__init__(self)
        self.name += "-engine"
        self.layout = layout
        self.hook_connect("focus", focus_toggle)
        self.hook_connect(
            "translated",
            partial(self.layout.suggestions.on_translated, self),
        )
        self.hook_connect("add_translation", partial(layout.on_add_translation, self))
        self.cmder = Commander(build_commands(self, layout), layout.output_to_console)

        def on_lookup():
            focus_console()
            self.layout.cmder_input.text = ""
            self.cmder.set_state(["lookup"], layout.exit_modal)

        self.hook_connect("lookup", on_lookup)

        def on_configure():
            focus_console()
            self.layout.cmder_input.text = ""
            self.cmder.set_state(["configure"], layout.exit_modal)

        self.hook_connect("configure", on_configure)

        # tape hooks
        self.hook_connect("config_changed", layout.tape.on_config_changed)
        self.hook_connect("stroked", layout.tape.on_stroked)

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