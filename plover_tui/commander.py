from prompt_toolkit.buffer import Buffer


def peek(list):
    if list:
        return list[0]
    return None


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

        cmdline = self.state[:] + words

        possible_command = peek(cmdline)
        end_of_line = False
        local_state = []
        handler = self.command_container

        while possible_command and not end_of_line:
            found_command = False
            for c in handler.sub_commands:
                if c.name.startswith(possible_command):
                    found_command = True
                    local_state.append(c.name)
                    handler = c
                    c.on_enter(self.output)
                    _ = cmdline.pop(0)
                    possible_command = peek(cmdline)
                    break
            if not found_command:
                end_of_line = True

        # self.output("cmdline: " + " ".join(cmdline))
        # self.output("localstate: " + " ".join(local_state))
        # self.output("state: " + " ".join(self.state))
        # self.output("handler: " + str(handler.name))

        if not handler.handle(self.output, cmdline):
            self.state = local_state

    def prompt(self):
        return " ".join(self.state) + "> "
