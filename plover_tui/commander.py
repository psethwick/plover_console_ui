from prompt_toolkit.buffer import Buffer

from .commands import LookupCommand, QuitCommand, ToggleTapeCommand, \
    ToggleSuggestionsCommand, ResetMachineCommand, SaveConfigCommand, \
    ToggleOutputCommand, SetMachineCommand


class Handler():
    def __init__(self, engine, layout):
        self.children = [
            LookupCommand(engine),
            QuitCommand(),
            ToggleTapeCommand(layout.toggle_tape),
            ToggleSuggestionsCommand(layout.toggle_suggestions),
            ResetMachineCommand(engine.reset_machine),
            SaveConfigCommand(engine),
            ToggleOutputCommand(engine),
            SetMachineCommand(engine)
        ]

    def __call__(self, state, on_output, words):
        if not words:
            if state:
                on_output(f"Exit {state}")
            return None

        if state:
            command = state
            args = words
        else:
            command = words[0]
            args = words[1:]
        for h in self.children:
            if h.handles.startswith(command):
                if not args:
                    if h.stateful():
                        return h.handles
                h.handle(on_output, args)
                if state:
                    return state
                else:
                    return None

        on_output(f"Unknown command: {' '.join(words)}")


class Commander:
    def __init__(self, engine, layout) -> None:
        self.engine = engine
        self.handler = Handler(engine, layout)
        self.output = layout.output_to_console
        self.state = None

    def __call__(self, buff: Buffer):
        try:
            words = buff.text.split()

            self.state = self.handler(
                self.state,
                self.output,
                words
            )
        except BaseException as e:
            self.output("\n\n{}".format(e))

    def prompt(self):
        prompt = ""
        if self.state:
            prompt += self.state
        return prompt + "> "
