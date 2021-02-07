from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.layout.containers \
    import HSplit, VSplit, DynamicContainer, Window, FloatContainer, Float
from prompt_toolkit.widgets import TextArea, Frame, Label, Dialog
from prompt_toolkit.document import Document
from prompt_toolkit.application import get_app
from prompt_toolkit.styles import Style

from .focus import Focus


def output_to_buffer(buffer, text):
    o = f"{buffer.text[:1000]}\n{text}"
    buffer.document = Document(
        text=o, cursor_position=len(o)
    )
    get_app().invalidate()


def dictionary_filter(key, value):
    # Allow undo...
    if value == '=undo':
        return False
    # ...and translations with special entries. Do this by looking for
    # braces but take into account escaped braces and slashes.
    escaped = value.replace('\\\\', '').replace('\\{', '')
    special = '{#'  in escaped or '{PLOVER:' in escaped
    return not special


plover_text = """ _____  _
|  __ \| |
| |__) | | _____   _____ _ __
|  ___/| |/ _ \ \ / / _ \ '__|
| |    | | (_) \ V /  __/ |
|_|    |_|\___/ \_/ \___|_|
"""


class TuiLayout:
    def __init__(self, focus) -> None:
        self.focus = focus
        self.input = TextArea(
                height=1,
                multiline=False,
                wrap_lines=False,
            )

        self.status_bar = Label("Loading status bar...",
                                style="class:status")

        self.console = Frame(TextArea(plover_text, focusable=False),
                             title="Console")
        self.tape = Frame(TextArea(focusable=False),
                          title="Paper Tape")
        self.suggestions = Frame(TextArea(focusable=False),
                                 title="Suggestions")
        self.outputs = [
            self.console
        ]
        self.float = Window()
        self.container = FloatContainer(
            HSplit(
                [
                    DynamicContainer(lambda: VSplit(self.outputs)),
                    self.input,
                    self.status_bar
                ]
            ),
            floats=[
                Float(DynamicContainer(lambda: self.float))
            ]
        )

    def __call__(self):
        return self.container

    def output_to_tape(self, text):
        output_to_buffer(self.tape.body.buffer, text)

    def output_to_console(self, text):
        output_to_buffer(self.console.body.buffer, text)

    def output_to_suggestions(self, text):
        output_to_buffer(self.suggestions.body.buffer, text)

    def toggle_tape(self):
        return "Tape: " + self._toggle(self.tape)

    def toggle_console(self):
        return "Console: " + self._toggle(self.console)

    def toggle_suggestions(self):
        return "Suggestions: " + self._toggle(self.suggestions)

    def _toggle(self, item):
        if item in self.outputs:
            self.outputs.remove(item)
            return "off"
        else:
            self.outputs.append(item)
            return "on"

    def focus_tui(self):
        self.focus.set_prev()
        self.focus.tui()

    # TODO solve the probs
    def on_add_translation(self, engine):
        self.focus_tui()
        engine.add_dictionary_filter(dictionary_filter)
        strokes = TextArea(prompt="Strokes:")
        translation = TextArea(prompt="Output: ")

        output = TextArea(focusable=False)
        dialog = Dialog(
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
            ),
            width=40,
        )
        self.float = dialog
        get_app().layout.focus(dialog)


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
    layout=Layout(DynamicContainer(layout),
                  focused_element=layout.input),
    key_bindings=kb,
    style=style,
    mouse_support=False,
    full_screen=True,
    enable_page_navigation_bindings=False
)
