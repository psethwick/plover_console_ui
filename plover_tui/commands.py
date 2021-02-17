from abc import ABCMeta, abstractmethod

from prompt_toolkit.application import get_app

from plover.translation import unescape_translation

from .suggestions import format_suggestions
from .presentation import style_colored

# TODO each command describes itself
# TODO special 'help' command that exists at every level (describes available)


class Command(metaclass=ABCMeta):
    def stateful(self):
        return False

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    @abstractmethod
    def handle(self, output, words=None):
        return "Unknown"


class ColorCommand(Command):
    def __init__(self) -> None:
        self.handles = "color"

    def stateful(self):
        return True

    def handle(self, output, words=None):
        if words:
            get_app().style = style_colored(words[0])


class ConfigCommand(Command):
    def __init__(self, config) -> None:
        self.handles = "config"
        self.config = config

    def stateful(self):
        return True

    def handle(self, output, words):
        for o in self.config._config:
            output(o)
        self.config._config.add_section("Console UI")
        self.config._config.set("Console UI", "fg", "green")
        section = " ".join(words)
        if section in self.config._config:
            output(self.config._config.options(section))


class ExitCommand(Command):
    def __init__(self):
        self.handles = "exit"

    def handle(self, output, words=None):
        get_app().exit(0)


class LookupCommand(Command):
    """
    TODO this could live under a 'dictionary' command
    """

    def __init__(self, engine):
        self.handles = "lookup"
        self.engine = engine

    def stateful(self):
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
        self.handles = "tape"
        self.toggler = toggler
        self.engine = engine

    def handle(self, output, words=None):
        show = self.toggler()
        self.engine.config = {"show_stroke_display": show}
        output(f"Show tape: {show}")


class ToggleSuggestionsCommand(Command):
    def __init__(self, toggler, engine):
        self.handles = "suggestions"
        self.toggler = toggler
        self.engine = engine

    def handle(self, output, words=None):
        show = self.toggler()
        self.engine.config = {"show_suggestions_display": show}
        output(f"Show suggestions: {show}")


class ResetMachineCommand(Command):
    def __init__(self, resetter):
        self.handles = "reset"
        self.resetter = resetter

    def handle(self, output, words=None):
        output("Resetting machine...")
        self.resetter()


class ToggleOutputCommand(Command):
    def __init__(self, engine):
        self.handles = "output"
        self.engine = engine

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
        self.handles = "machine"
        self.engine = engine

    def handle(self, output, words=None):
        new_machine = " ".join(words)
        output(f"Setting machine to {new_machine}")
        self.engine.config = {"machine_type": new_machine}


def build_commands(engine, layout):
    return [
        LookupCommand(engine),
        ExitCommand(),
        ToggleTapeCommand(layout.toggle_tape, engine),
        ToggleSuggestionsCommand(layout.toggle_suggestions, engine),
        ResetMachineCommand(engine.reset_machine),
        ToggleOutputCommand(engine),
        ConfigCommand(engine._config),
        SetMachineCommand(engine),
        ColorCommand(),
    ]
