from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.layout.containers \
    import HSplit, VSplit, DynamicContainer
from prompt_toolkit.widgets import TextArea, Frame, Label
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


class AddTranslation:
    def __init__(self, engine, on_output, on_exit):
        self.engine = engine
        self.on_exit = on_exit
        self.on_output = on_output

        # we start in the strokes field
        self.engine.add_dictionary_filter(dictionary_filter)

        self.strokes_field = TextArea(
                    prompt="Strokes: ",
                    height=1,
                    multiline=False,
                    wrap_lines=False,
                )
        self.translation_field = TextArea(
                    prompt="Output: ",
                    height=1,
                    multiline=False,
                    wrap_lines=False,
                ),
        kb = KeyBindings()

        @kb.add("escape", eager=True)
        def _(event):
            # TODO cleanup fields
            on_exit()

        @kb.add("tab")
        def _(event):
            if get_app().layout.has_focus(self.strokes_field):
                self.engine.remove_dictionary_filter(dictionary_filter)
            else:
                self.engine.add_dictionary_filter(dictionary_filter)
            get_app().layout.focus_next()
            self.on_exit()

        self.container = HSplit(
            [
                self.strokes_field,
                self.translation_field
            ],
            # TODO do I want to modal?
            key_bindings=self.kb,
        )
        get_app().layout.focus(self.strokes_field)


class TuiLayout:
    def __init__(self, focus) -> None:
        self.focus = focus
        self.cmder_input = TextArea(
                height=1,
                multiline=False,
                wrap_lines=False,
            )
        add_translation_kb = KeyBindings()

        @add_translation_kb.add("escape", eager=True)
        def _(event):
            self.input = self.cmder_input
            get_app().layout.focus(self.cmder_input)
            self.focus.prev()

        @add_translation_kb.add("s-tab")
        @add_translation_kb.add("tab")
        def _(event):
            if get_app().layout.has_focus(self.add_translation_input.children[0]):
                self.engine.remove_dictionary_filter(dictionary_filter)
            else:
                self.engine.add_dictionary_filter(dictionary_filter)
            get_app().layout.focus_next()

        # TODO this needs all the handlers
        # TODO and probably to live in its own class
        self.add_translation_input = HSplit(
            [
                TextArea(
                    prompt="Strokes: ",
                    height=1,
                    multiline=False,
                    wrap_lines=False,
                ),
                TextArea(
                    prompt="Output: ",
                    height=1,
                    multiline=False,
                    wrap_lines=False,
                ),
            ],
            # TODO do I want to modal?
            key_bindings=add_translation_kb,
        )

        self.input = self.cmder_input

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
        self.container = HSplit(
                [
                    DynamicContainer(lambda: VSplit(self.outputs)),
                    DynamicContainer(lambda: self.input),
                    self.status_bar
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
        at = AddTranslation(engine, ooutput, exxti)
        self.input = at.container


focus = Focus()
kb = KeyBindings()


@kb.add("c-c")
@kb.add("c-q")
def _(event):
    " Pressing Ctrl-Q or Ctrl-C will exit the user interface. "
    event.app.exit(0)


# TODO not too sure about this
#@kb.add("escape", eager=True)
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
