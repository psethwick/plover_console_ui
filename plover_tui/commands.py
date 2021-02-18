from abc import ABCMeta

from prompt_toolkit.application import get_app

from plover.translation import unescape_translation
from plover.registry import registry

from .suggestions import format_suggestions
from .presentation import style_colored
from .config import set


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


class UICommands(Command):
    """commands for user interface"""

    def __init__(self, output, sub_commands) -> None:
        super().__init__("ui", output, sub_commands)


class ColorCommand(Command):
    """sets foreground color of console"""

    def __init__(self, output, config) -> None:
        self.config = config
        super().__init__("color", output)

    def handle(self, words=None):
        if words:
            color = words[0]
            get_app().style = style_colored(color)
            # above line will throw if it's a bad color
            # it's ok to set it in config now
            set(self.config, "fg", color)
            return True
        return False


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


class MachineCommand(Command):
    """set machine commands"""

    def __init__(self, output, engine) -> None:
        sub_commands = [
            MachineSetterCommand(p.name, output, engine)
            for p in registry.list_plugins("machine")
        ]
        super().__init__("machine", output, sub_commands)


class MachineSetterCommand(Command):
    def __init__(self, machine_name, output, engine) -> None:
        self.engine = engine
        self.__doc__ = f"sets machine to {machine_name}"
        super().__init__(machine_name, output)

    def handle(self, words=None):
        self.output(f"Setting machine to {self.name}")
        self.engine.config = {"machine_type": self.name}
        return True


# TODO implement config in a somewhat generic manner
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


class ConfigureCommand(Command):
    """configuration commands"""

    def __init__(self, output, sub_commands, engine) -> None:
        self.engine = engine
        super().__init__("configure", output, sub_commands)

    def handle(self, words=None):
        self.output(self.engine._config._config["Console UI"])
        return False


def build_commands(engine, layout):
    output = layout.output_to_console
    return Command(
        name=None,
        output=output,
        sub_commands=[
            ConfigureCommand(
                output,
                [
                    MachineCommand(output, engine),
                ],
                engine,
            ),
            # dictionary?
            LookupCommand(output, engine),
            ResetMachineCommand(output, engine.reset_machine),
            ToggleOutputCommand(output, engine),
            UICommands(
                output,
                [
                    ToggleTapeCommand(output, layout.toggle_tape, engine),
                    ToggleSuggestionsCommand(output, layout.toggle_suggestions, engine),
                    ColorCommand(output, engine._config),
                ],
            ),
            ExitCommand(output),
        ],
    )
