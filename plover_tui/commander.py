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

        while possible_command and not end_of_line:
            self.output("handler: " + str(handler.name))
            if not handler.sub_commands:
                self.output("END")
                end_of_line = True
                break
            for c in handler.sub_commands:
                if c.name.startswith(possible_command):
                    handler = c
                    self.output("setting handler: " + c.name)
                    _ = cmdline.pop(0)
                    possible_command = peek(cmdline)
                    break

        handler.handle(cmdline)

        # if self.state:
        #     cmdline = self.state[:]
        #     args = words
        #     # find class which handles, call it
        #     # then return
        #     while cmdline:
        #         c = cmdline.pop(0)
        #         self.output(c)
        #         for s in handler.sub_commands:
        #             if s.name.startswith(c):
        #                 self.output("found " + s.name)
        #                 handler = s
        #                 break

        #     handler.handle(self.output, args)
        #     return

        # else:
        #     # grab commands off the word list
        #     found_level = False
        #     while not found_level:
        #         if handler.sub_commands:
        #             cmdline = words.pop(0)
        #             for s in handler.sub_commands:
        #                 if s.name.startswith(cmdline):
        #                     handler = s
        #                     break
        #         else:
        #             found_level = True

        #     handler.handle(self.output, words)
        #     return

        self.output(f"Unknown command: {' '.join(words)}")

    def prompt(self):
        return " ".join(self.state) + "> "
