from functools import partial

from prompt_toolkit.layout.containers import HSplit, VSplit, DynamicContainer
from prompt_toolkit.widgets import TextArea, Frame, Label
from prompt_toolkit.application import get_app

from .focus import focus_prev, focus_console
from .add_translation import AddTranslation
from .tape import Tape
from .output import output_to_buffer, output_to_buffer_position
from .suggestions import Suggestions


plover_text = """
    ____  __                    
   / __ \/ /___ _   _____  _____
  / /_/ / / __ \ | / / _ \/ ___/
 / ____/ / /_/ / |/ /  __/ /    
/_/   /_/\____/|___/\___/_/     
"""


class ConsoleLayout:
    def __init__(self) -> None:
        self.cmder_input = TextArea(
            height=1, multiline=False, wrap_lines=False, style="class:normal"
        )
        self.input = self.cmder_input

        self.status_bar = Label("Loading status bar...", style="class:status")

        self.console = Frame(
            TextArea(plover_text, focusable=False),
            title="Console",
            style="class:normal",
        )

        self.tape = Tape()
        self.suggestions = Suggestions()

        self.outputs = [self.console]

        self.container = HSplit(
            [
                DynamicContainer(lambda: VSplit(self.outputs)),
                DynamicContainer(lambda: self.input),
                self.status_bar,
            ]
        )

    def __call__(self):
        return self.container

    def output_to_console(self, text):
        output_to_buffer(self.console.body.buffer, text)

    def toggle_tape(self):
        return self._toggle(self.tape)

    def toggle_suggestions(self):
        return self._toggle(self.suggestions)

    def _toggle(self, item):
        if item in self.outputs:
            item.off()
            self.outputs.remove(item)
            return False
        else:
            item.on()
            self.outputs.append(item)
            return True

    def exit_modal(self):
        self.input = self.cmder_input
        get_app().layout.focus(self.cmder_input)
        focus_prev()

    def on_add_translation(self, engine):
        focus_console()
        at = AddTranslation(
            engine,
            partial(
                output_to_buffer_position,
                self.console.body.buffer,
                len(self.console.body.buffer.text),
            ),
            self.exit_modal,
        )
        self.input = at.container
        get_app().layout.focus(at.strokes_field)


layout = ConsoleLayout()
