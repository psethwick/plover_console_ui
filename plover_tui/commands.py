from abc import ABCMeta, abstractmethod

from prompt_toolkit.application import get_app

from plover.translation import unescape_translation

from .suggestions import format_suggestions
from .presentation import style_colored

# TODO each command describes itself
# TODO special 'help' command that exists at every level (describes available)


class Command(metaclass=ABCMeta):
    def __init__(self, name, sub_commands=[]) -> None:
        self.name = name
        self.sub_commands = sub_commands

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def handle(self, output, words=None):
        output("Not supported: " + " ".join(words))


class ColorCommand(Command):
    def __init__(self) -> None:
        super().__init__("color")

    def handle(self, output, words=None):
        if words:
            get_app().style = style_colored(words[0])


class ConfigCommand(Command):
    def __init__(self, config, sub_commands) -> None:
        self.config = config
        super().__init__("configure", sub_commands)

    #def handle(self, output, words):
    #    pass
        # for o in self.config._config:
        #     output(o)
        # self.config._config.add_section("Console UI")
        # self.config._config.set("Console UI", "fg", "green")
        # section = " ".join(words)
        # if section in self.config._config:
        #     output(self.config._config.options(section))


class ExitCommand(Command):
    def __init__(self):
        super().__init__("exit")

    def handle(self, output, words=None):
        get_app().exit(0)


class LookupCommand(Command):
    """
    TODO this could live under a 'dictionary' command
    """

    def __init__(self, engine):
        self.engine = engine
        super().__init__("lookup")

    def container(self):
        return True

    def handle(self, output, words):
        text = " ".join(words)
        lookup = unescape_translation(text)
        suggestions = format_suggestions(self.engine.get_suggestions(lookup))
        if suggestions:
            output = suggestions
        else:
            output = f"'{lookup}' not found"
        output(output)


class ToggleTapeCommand(Command):
    def __init__(self, toggler, engine):
        self.toggler = toggler
        self.engine = engine
        super().__init__("tape")

    def handle(self, output, words=None):
        show = self.toggler()
        self.engine.config = {"show_stroke_display": show}
        output(f"Show tape: {show}")


class ToggleSuggestionsCommand(Command):
    def __init__(self, toggler, engine):
        self.toggler = toggler
        self.engine = engine
        super().__init__("suggestions")

    def handle(self, output, words=None):
        show = self.toggler()
        self.engine.config = {"show_suggestions_display": show}
        output(f"Show suggestions: {show}")


class ResetMachineCommand(Command):
    def __init__(self, resetter):
        self.resetter = resetter
        super().__init__("reset")

    def handle(self, output, words=None):
        output("Resetting machine...")
        self.resetter()


class ToggleOutputCommand(Command):
    def __init__(self, engine):
        self.engine = engine
        super().__init__("output")

    def handle(self, output, words=None):
        if self.engine.output:
            self.engine.output = False
        else:
            self.engine.output = True
        output("Output: " + str(self.engine.output))


# TODO probably also belongs under 'config'
# TODO needs to be able to set the various machine parameter thingies
class SetMachineCommand(Command):
    def __init__(self, engine):
        self.engine = engine
        super().__init__("machine")

    def handle(self, output, words=None):
        new_machine = " ".join(words)
        output(f"Setting machine to {new_machine}")
        self.engine.config = {"machine_type": new_machine}


class TopCommand(Command):
    def __init__(self, sub_commands) -> None:
        super().__init__(None, sub_commands=sub_commands)


def build_commands(engine, layout):
    return TopCommand(
        [
            # dictionary?
            LookupCommand(engine),
            ExitCommand(),
            ResetMachineCommand(engine.reset_machine),
            ToggleOutputCommand(engine),
            # this could do more stuff
            ConfigCommand(engine._config, [ColorCommand()]),
            SetMachineCommand(engine),
            # UI? (maybe color in here)
            ToggleTapeCommand(layout.toggle_tape, engine),
            ToggleSuggestionsCommand(layout.toggle_suggestions, engine),
        ]
    )
