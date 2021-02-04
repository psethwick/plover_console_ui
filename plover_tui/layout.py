from prompt_toolkit.layout.containers import HSplit, VSplit, DynamicContainer, FloatContainer, Float, to_container, Window
from prompt_toolkit.widgets import TextArea, Frame, Label, Dialog

class TuiLayout:
    def __init__(self, input_field, console, paper_tape, suggestions) -> None:
        self.input_field = input_field
        self.console = Frame(console, title="Console")
        self.tape = Frame(paper_tape, title="Paper Tape")
        self.suggestions = Frame(suggestions, title="Suggestions")
        self.outputs = [
            self.console
        ]
        self.float = Window()
        self.container = FloatContainer(
            HSplit(
                [
                    VSplit(self.outputs),
                    self.input_field,
                ]
            ),
            floats=[
                Float(DynamicContainer(lambda: self.float))
            ]
        )

    
    def __call__(self):
        return self.container

    def load_status(self, status_callable):
        self.container.content.children.append(to_container(Label(status_callable, style="class:status")))

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
