from abc import ABCMeta, abstractmethod

from prompt_toolkit.application import get_app

from plover.translation import unescape_translation

from .suggestions import format_suggestions
from .presentation import style_colored

# TODO each command describes itself
# TODO special 'help' command that exists at every level (describes available)


class Command(metaclass=ABCMeta):
    def __init__(self, name, output, sub_commands=[]) -> None:
        self.name = name
        self.output = output
        self.sub_commands = sub_commands

    def on_enter(self):
        pass

    def handle(self, words=None):
        if words:
            self.output("Unsupported command: " + " ".join(words))
        return False


class ColorCommand(Command):
    """sets foreground color of console"""

    def __init__(self, output) -> None:
        super().__init__("color", output)

    def handle(self, words=None):
        if words:
            get_app().style = style_colored(words[0])
            return True
        return False


# class ConfigCommand(Command):
#     def __init__(self, config, sub_commands) -> None:
#         self.config = config
#         super().__init__("configure", sub_commands)

# def handle(self, output, words):
#    pass
# for o in self.config._config:
#     output(o)
# self.config._config.add_section("Console UI")
# self.config._config.set("Console UI", "fg", "green")
# section = " ".join(words)
# if section in self.config._config:
#     output(self.config._config.options(section))


class ExitCommand(Command):
    """exits plover"""

    def __init__(self, output):
        super().__init__("exit", output)

    def handle(self, words=None):
        get_app().exit(0)
        return True


class LookupCommand(Command):
    """looks up words in current dictionaries"""

    def __init__(self, output, engine):
        self.engine = engine
        super().__init__("lookup", output)

    def handle(self, words):
        if not words:
            return False
        text = " ".join(words)
        lookup = unescape_translation(text)
        suggestions = format_suggestions(self.engine.get_suggestions(lookup))
        if suggestions:
            self.output(suggestions)
        else:
            self.output(f"'{lookup}' not found")
        return True


class ToggleTapeCommand(Command):
    """turns paper tape pane on/off"""

    def __init__(self, output, toggler, engine):
        self.toggler = toggler
        self.engine = engine
        super().__init__("tape", output)

    def handle(self, words=None):
        show = self.toggler()
        self.engine.config = {"show_stroke_display": show}
        self.output(f"Show tape: {show}")
        return True


class ToggleSuggestionsCommand(Command):
    """turns suggestions pane on/off"""

    def __init__(self, output, toggler, engine):
        self.toggler = toggler
        self.engine = engine
        super().__init__("suggestions", output)

    def handle(self, words=None):
        show = self.toggler()
        self.engine.config = {"show_suggestions_display": show}
        self.output(f"Show suggestions: {show}")
        return True


class ResetMachineCommand(Command):
    """reconnects current machine"""

    def __init__(self, output, resetter):
        self.resetter = resetter
        super().__init__("reset", output)

    def handle(self, words=None):
        self.output("Resetting machine...")
        self.resetter()
        return True


class ToggleOutputCommand(Command):
    """toggles plover output on/off"""

    def __init__(self, output, engine):
        self.engine = engine
        super().__init__("output", output)

    def handle(self, words=None):
        if self.engine.output:
            self.engine.output = False
        else:
            self.engine.output = True

        state = "Enabled" if self.engine.output else "Disabled"
        self.output(f"Output: {state}")
        return True


# TODO probably also belongs under 'config'
# TODO needs to be able to set the various machine parameter thingies
class SetMachineCommand(Command):
    """machine commands"""

    def __init__(self, output, engine):
        self.engine = engine
        super().__init__("machine", output)

    def handle(self, words=None):
        if not words:
            return False
        new_machine = " ".join(words)
        self.output(f"Setting machine to {new_machine}")
        self.engine.config = {"machine_type": new_machine}
        return True


class ContainerCommand(Command):
    def __init__(self, name, output, sub_commands) -> None:
        super().__init__(name, output, sub_commands=sub_commands)


class ConfigureCommand(ContainerCommand):
    """configuration commands"""
    def __init__(self, output, sub_commands) -> None:
        super().__init__("configure", output, sub_commands)


def build_commands(engine, layout):
    output = layout.output_to_console
    return ContainerCommand(
        name=None,
        output=output,
        sub_commands=[
            # dictionary?
            LookupCommand(output, engine),
            ExitCommand(output),
            ResetMachineCommand(output, engine.reset_machine),
            ToggleOutputCommand(output, engine),
            # this could do more stuff
            ConfigureCommand(output, [ColorCommand(output)]),
            SetMachineCommand(output, engine),
            # UI? (maybe color in here)
            ToggleTapeCommand(output, layout.toggle_tape, engine),
            ToggleSuggestionsCommand(output, layout.toggle_suggestions, engine),
        ],
    )
