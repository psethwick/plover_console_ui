from prompt_toolkit.buffer import Buffer


def peek(list):
    if list:
        return list[0]
    return None


class Commander:
    def __init__(self, command_container, output) -> None:
        self.command_container = command_container
        self.output = output
        self.state = ["configure", "color"]

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

        cmdline = self.state[:] + words

        possible_command = peek(cmdline)

        end_of_line = False

        local_state = []
        while possible_command and not end_of_line:
            self.output("handler: " + str(handler.name))
            if not handler.sub_commands:
                self.output("END")
                end_of_line = True
                break
            for c in handler.sub_commands:
                if c.name.startswith(possible_command):
                    local_state.append(c.name)
                    handler = c
                    self.output("setting handler: " + c.name)
                    _ = cmdline.pop(0)
                    possible_command = peek(cmdline)
                    break

        if not cmdline and handler.sub_commands:
            self.state = local_state

        handler.handle(self.output, cmdline)

    def prompt(self):
        return " ".join(self.state) + "> "
