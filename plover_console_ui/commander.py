from prompt_toolkit.buffer import Buffer

from .commands import Command, UnsupportedCommand


def peek(list):
    if list:
        return list[0]
    return None


class Help(Command):
    def __init__(self, commander) -> None:
        self.commander = commander
        super().__init__("help", commander.output)

    def handle(self, words=None):
        handler = self.commander.current_handler()
        handler.describe()
        return True


def build_meta_commands(commander):
    return [Help(commander)]


class Commander:
    def __init__(self, top_command, output) -> None:
        self.top_command = top_command
        self.output = output
        self.on_exit_state = None
        self.state = []
        self.meta_commands = build_meta_commands(self)

    def __call__(self, buff: Buffer):
        try:
            words = buff.text.split()

            self.handle_command(words)

        except UnsupportedCommand:
            self.output("Unsupported command: " + buff.text)
        except BaseException as e:
            self.output(f"Error: {e}")

    def set_state(self, state, on_exit=None):
        self.state = state
        self.on_exit_state = on_exit

    def current_handler(self):
        handler = self.top_command
        if not self.state:
            return handler
        state = self.state[:]
        handler_name = state.pop(0)
        done = False
        while not done:
            handler = next(
                h
                for h in handler.sub_commands()
                if h.name.lower() == handler_name.lower()
            )
            if not handler.sub_commands() or not state:
                done = True
            else:
                handler_name = state.pop(0)
        return handler

    def handle_command(self, words):
        if not words:
            if self.state:
                if self.on_exit_state:
                    self.on_exit_state()
                    self.on_exit_state = None
                self.state.pop()
            return

        if self.handled_meta_command(words):
            return

        local_state = self.state[:]
        handler = self.current_handler()

        possible_command = peek(words)
        done = False
        while possible_command and not done:
            found_command = False
            for c in handler.sub_commands():
                if c.name.lower().startswith(possible_command.lower()):
                    found_command = True
                    local_state.append(c.name)
                    handler = c
                    _ = words.pop(0)
                    possible_command = peek(words)
                    break
            if not found_command:
                done = True

        if not handler.handle(words):
            self.state = local_state

    def handled_meta_command(self, words):
        possible_meta = peek(words)
        for meta in self.meta_commands:
            if meta.name.lower().startswith(possible_meta.lower()):
                meta.handle(words)
                return True
        return False

    def prompt(self):
        return " ".join(self.state) + "> "
