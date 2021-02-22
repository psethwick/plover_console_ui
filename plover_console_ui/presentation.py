from functools import partial

from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.layout.containers import HSplit, VSplit, DynamicContainer
from prompt_toolkit.widgets import TextArea, Frame, Label
from prompt_toolkit.application import get_app
from prompt_toolkit.styles import Style

from .focus import Focus
from .add_translation import AddTranslation
from .tape import Tape
from .output import output_to_buffer, output_to_buffer_position
from .suggestions import Suggestions


# TODO maybe a slanted version of this?
plover_text = """ _____  _
|  __ \| |
| |__) | | _____   _____ _ __
|  ___/| |/ _ \ \ / / _ \ '__|
| |    | | (_) \ V /  __/ |
|_|    |_|\___/ \_/ \___|_|

"""


class ConsoleLayout:
    def __init__(self, focus) -> None:
        self.focus = focus
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
            self.outputs.remove(item)
            return False
        else:
            self.outputs.append(item)
            return True

    def focus_console(self):
        self.focus.set_prev()
        self.focus.console()

    def focus_toggle(self):
        self.focus.toggle()

    def exit_modal(self):
        self.input = self.cmder_input
        get_app().layout.focus(self.cmder_input)
        self.focus.prev()

    def on_add_translation(self, engine):
        self.focus_console()
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


focus = Focus()
kb = KeyBindings()


@kb.add("c-c")
@kb.add("c-q")
def _(event):
    " Pressing Ctrl-Q or Ctrl-C will exit the user interface. "
    event.app.exit(0)


def style_colored(color=None) -> Style:
    if color:
        return Style.from_dict(
            {
                "status": f"fg:{color} reverse",
                "normal": f"fg:{color}",
            }
        )
    return Style.from_dict(
        {
            "status": "reverse",
        }
    )


style = style_colored()

layout = ConsoleLayout(focus)

application = Application(
    layout=Layout(DynamicContainer(layout), focused_element=layout.input),
    key_bindings=kb,
    style=style,
    mouse_support=False,
    full_screen=True,
    enable_page_navigation_bindings=False,
)
