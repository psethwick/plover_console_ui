from functools import partial

from plover_tui.suggestions import on_translated
from plover_tui.presentation import TuiLayout
from threading import Thread, current_thread

from plover.engine import StenoEngine
from prompt_toolkit.layout.processors import BeforeInput

from .commander import Commander


def status_bar_text(engine) -> str:
    return (
        " | Plover"
        " | Machine: "
        + engine.config["machine_type"]
        + " | Output: "
        + str(engine.output)
        + " | System: "
        + engine.config["system_name"]
        + " |"
    )


class TuiEngine(StenoEngine, Thread):
    def __init__(self, config, keyboard_emulation, layout: TuiLayout):
        StenoEngine.__init__(self, config, keyboard_emulation)
        Thread.__init__(self)
        self.name += "-engine"
        self.layout = layout
        # TODO format tape
        self.hook_connect(
            "stroked", lambda stroke: layout.output_to_tape(stroke.rtfcre)
        )
        self.hook_connect("focus", layout.focus_tui)
        self.hook_connect("translated", self.on_translated)
        self.hook_connect("add_translation", partial(layout.on_add_translation, self))
        cmder = Commander(self, layout)

        layout.cmder_input.control.input_processors.append(
            BeforeInput(cmder.prompt, style="class:text-area.prompt"),
        )

        layout.cmder_input.accept_handler = cmder
        layout.status_bar.text = partial(status_bar_text, self)

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
