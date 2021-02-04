from prompt_toolkit.layout.containers import HSplit, VSplit, DynamicContainer, FloatContainer, Float, to_container, Window
from prompt_toolkit.widgets import TextArea, Frame, Label, Dialog
from prompt_toolkit.document import Document
from prompt_toolkit.application import get_app

def output_to_buffer(buffer, text):
    o = f"{buffer.text[:1000]}\n{text}"
    buffer.document = Document(
        text=o, cursor_position=len(o)
    )
    get_app().invalidate()

class TuiLayout:
    def __init__(self) -> None:
        self.input_field = TextArea(
                height=1,
                # TODO this should take a callable
                prompt=">>> ",
                multiline=False,
                wrap_lines=False,
            )

        self.console = Frame(TextArea(focusable=False), title="Console")
        self.tape = Frame(TextArea(focusable=False), title="Paper Tape")
        self.suggestions = Frame(TextArea(focusable=False), title="Suggestions")
        self.outputs = [
            self.console
        ]
        self.float = Window()
        self.container = FloatContainer(
            HSplit(
                [
                    DynamicContainer(lambda: VSplit(self.outputs)),
                    self.input_field,
                ]
            ),
            floats=[
                Float(DynamicContainer(lambda: self.float))
            ]
        )

    
    def __call__(self):
        return self.container

    # TODO hm this could be better, not sure who should own what
    def load_status(self, status_callable):
        self.container.content.children \
            .append(to_container(Label(status_callable, style="class:status")))

    def output_to_tape(self, stroke):
        # TODO space out the tape properly
        output_to_buffer(self.tape.body.buffer, stroke.rtfcre)

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
