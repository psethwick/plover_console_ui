from prompt_toolkit.buffer import Buffer

from .commands import LookupCommand, ExitCommand, ToggleTapeCommand, \
    ToggleSuggestionsCommand, ResetMachineCommand, SaveConfigCommand, \
    ToggleOutputCommand, SetMachineCommand


class Commander:
    def __init__(self, engine, layout) -> None:
        self.commands = [
            LookupCommand(engine),
            ExitCommand(),
            ToggleTapeCommand(layout.toggle_tape),
            ToggleSuggestionsCommand(layout.toggle_suggestions),
            ResetMachineCommand(engine.reset_machine),
            SaveConfigCommand(engine),
            ToggleOutputCommand(engine),
            SetMachineCommand(engine)
        ]
        self.output = layout.output_to_console
        self.state = None

    def __call__(self, buff: Buffer):
        try:
            words = buff.text.split()

            self.handle_command(words)

        except BaseException as e:
            self.output("\n\n{}".format(e))

    def handle_command(self, words):
        if not words:
            if self.state:
                self.output(f"Exit {self.state}")
            self.state = None
            return

        if self.state:
            command = self.state
            args = words
        else:
            command = words[0]
            args = words[1:]
        for h in self.commands:
            if h.handles.startswith(command):
                if not args:
                    if h.stateful():
                        self.state = h.handles
                        self.output(f"Enter {self.state}")
                        return
                h.handle(self.output, args)
                return

        self.output(f"Unknown command: {' '.join(words)}")

    def prompt(self):
        prompt = ""
        if self.state:
            prompt += self.state
        return prompt + "> "
