from prompt_toolkit.buffer import Buffer

from .commands import Command


def peek(list):
    if list:
        return list[0]
    return None


class HelpCommand(Command):
    def __init__(self, commander) -> None:
        self.commander = commander
        super().__init__("help", commander.output)

    def handle(self, words=None):
        handler = self.commander.current_handler()
        self.output(f"Current: {handler.name}")
        if handler.sub_commands:
            self.output("Sub commands:")
            for sc in handler.sub_commands:
                self.output(sc.name)


def build_meta_commands(commander):
    return [HelpCommand(commander)]


class Commander:
    def __init__(self, top_command, output) -> None:
        self.top_command = top_command
        self.output = output
        self.state = []
        self.meta_commands = build_meta_commands(self)

    def __call__(self, buff: Buffer):
        try:
            words = buff.text.split()

            self.handle_command(words)

        except BaseException as e:
            self.output(f"Error: {e}")

    def current_handler(self):
        handler = self.top_command
        if not self.state:
            return handler
        state = self.state[:]
        handler_name = state.pop(0)
        done = False
        while not done:
            handler = next(h for h in handler.sub_commands if h.name == handler_name)
            if not handler.sub_commands:
                done = True
            else:
                handler_name = state.pop(0)

    def handle_command(self, words):
        if not words:
            if self.state:
                exiting = self.state.pop()
                self.output(f"Exit {exiting}")
            return

        if self.handled_meta_command(words):
            return

        cmdline = self.state[:] + words

        possible_command = peek(cmdline)

        end_of_line = False
        local_state = []
        handler = self.top_command

        while possible_command and not end_of_line:
            found_command = False
            for c in handler.sub_commands:
                if c.name.startswith(possible_command):
                    found_command = True
                    local_state.append(c.name)
                    handler = c
                    c.on_enter()
                    _ = cmdline.pop(0)
                    possible_command = peek(cmdline)
                    break
            if not found_command:
                end_of_line = True

        if not handler.handle(cmdline):
            self.state = local_state

    def handled_meta_command(self, words):
        possible_meta = peek(words)
        for meta in self.meta_commands:
            if meta.name.startswith(possible_meta):
                meta.handle(words)
                return True
        return False

    def prompt(self):
        return " ".join(self.state) + "> "
