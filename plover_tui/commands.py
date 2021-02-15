from abc import ABCMeta, abstractmethod

from prompt_toolkit.application import get_app

from plover.translation import unescape_translation

from .suggestions import format_suggestions

# TODO each command describes itself
# TODO special 'help' command that exists at every level (describes available)


class Command(metaclass=ABCMeta):
    def stateful(self):
        return False

    @abstractmethod
    def handle(self, output, words=None):
        return "Unknown"


class ConfigCommand(Command):
    def __init__(self, config) -> None:
        self.handles = "config"
        self.config = config

    def stateful(self):
        return True

    def handle(self, output, words):
        if words:
            for k in self.config:
                if k.startswith(words[0]):
                    output(k)
                    output(self.config[k])
        # for w in words:
        #     if w in self.config:
        #         output(self.config[w])


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
    def __init__(self, toggler):
        self.handles = "tape"
        self.toggler = toggler

    def handle(self, output, words=None):
        output(self.toggler())


class ToggleSuggestionsCommand(Command):
    def __init__(self, toggler):
        self.handles = "suggestions"
        self.toggler = toggler

    def handle(self, output, words=None):
        output(self.toggler())


class ResetMachineCommand(Command):
    def __init__(self, resetter):
        self.handles = "reset"
        self.resetter = resetter

    def handle(self, output, words=None):
        output("Resetting machine...")
        self.resetter()


# TODO belongs under 'config'
class SaveConfigCommand(Command):
    def __init__(self, engine):
        self.handles = "save"
        self.engine = engine

    def handle(self, output, words=None):
        output("Saving config...")
        with open(self.engine._config.target_file, "wb") as f:
            self._config.save(f)


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
