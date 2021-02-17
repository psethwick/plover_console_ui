from prompt_toolkit.buffer import Buffer

from .commands import (
    ColorCommand,
    LookupCommand,
    ExitCommand,
    ToggleTapeCommand,
    ToggleSuggestionsCommand,
    ResetMachineCommand,
    ToggleOutputCommand,
    SetMachineCommand,
    ConfigCommand,
)


class Commander:
    def __init__(self, command_container, output) -> None:
        self.command_container = command_container
        self.output = output
        self.state = ["configure"]

    def __call__(self, buff: Buffer):
        try:
            words = buff.text.split()

            self.handle_command(words)

        except BaseException as e:
            self.output("\n\n{}".format(e))

    def handle_command(self, words):
        if not words:
            if self.state:
                exiting = self.state.pop()
                self.output(f"Exit {exiting}")
            return
        handler = self.command_container

        if self.state:
            command = self.state
            args = words
            # find class which handles, call it
            # then return
            while command:
                c = command.pop()
                for s in handler.sub_commands:
                    if s.name.startswith(c):
                        handler = s
                        break

            handler.handle(self.output, args)
            return

        else:
            # grab commands off the word list
            found_level = False
            while not found_level:
                if handler.sub_commands:
                    command = words.pop(0)
                    for s in handler.sub_commands:
                        if s.name.startswith(command):
                            self.state.append(s.name)
                            handler = s
                            break
                else:
                    found_level = True

            handler.handle(self.output, words)

        self.output(f"Unknown command: {' '.join(words)}")

    def prompt(self):
        return " ".join(self.state) + "> "
