from prompt_toolkit.buffer import Buffer
from .commands import UnsupportedCommand


def peek(list):
    if list:
        return list[0]
    return None


class Commander:
    def __init__(self, top_command, output) -> None:
        self.top_command = top_command
        self.output = output
        self.on_exit_state = None
        self.state = []

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

    def prompt(self):
        return " ".join(self.state) + "> "
