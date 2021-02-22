from prompt_toolkit.application import get_app

from plover.translation import unescape_translation
from plover.registry import registry

from .suggestions import format_suggestions
from .application import create_style
from .config import setvalue


class Command:
    def __init__(self, name, output, sub_commands=[]) -> None:
        self.name = name
        self.output = output
        self._sub_commands = sub_commands

    def sub_commands(self):
        return self._sub_commands

    def handle(self, words=[]):
        if words:
            self.output("Unsupported command: " + " ".join(words))
        else:
            self.describe()
        return False

    def describe(self):
        section = self.name if self.name else "console"
        self.output(section.capitalize())
        self.output("".join(["-" for _ in section]))

        if self.sub_commands():
            for sc in self.sub_commands():
                desc = sc.__doc__ if sc.__doc__ else "..."
                self.output(f"{sc.name}: {desc}")


class ColorCommand(Command):
    """sets foreground color of console (web colors or hexes should work)"""

    def __init__(self, output, config) -> None:
        self.config = config
        super().__init__("color", output)

    def handle(self, words=[]):
        if words:
            color = words[0]
            # TODO would be cool to allow any style here
            # not too hard to implement
            get_app().style = create_style(color)
            # above line will throw if prompt_toolkit hates it
            # it's ok to set it in config now
            setvalue(self.config, "fg", color)
            return True
        return False


class ExitCommand(Command):
    """exits plover"""

    def __init__(self, output):
        super().__init__("exit", output)

    def handle(self, words=[]):
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

    def handle(self, words=[]):
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

    def handle(self, words=[]):
        show = self.toggler()
        self.engine.config = {"show_suggestions_display": show}
        self.output(f"Show suggestions: {show}")
        return True


class ResetMachineCommand(Command):
    """reconnects current machine"""

    def __init__(self, output, resetter):
        self.resetter = resetter
        super().__init__("reset", output)

    def handle(self, words=[]):
        self.output("Resetting machine...")
        self.resetter()
        return True


class ToggleOutputCommand(Command):
    """toggles plover output on/off"""

    def __init__(self, output, engine):
        self.engine = engine
        super().__init__("output", output)

    def handle(self, words=[]):
        if self.engine.output:
            self.engine.output = False
        else:
            self.engine.output = True

        state = "Enabled" if self.engine.output else "Disabled"
        self.output(f"Output: {state}")
        return True


class MachineCommand(Command):
    def __init__(self, output, engine) -> None:
        sub_commands = [MachineOptionsCommand(output, engine)] + [
            MachineSetterCommand(p.name, output, engine)
            for p in registry.list_plugins("machine")
        ]
        super().__init__("machine", output, sub_commands)


class SystemCommand(Command):
    def __init__(self, output, engine) -> None:
        sub_commands = [
            SystemSetterCommand(p.name, output, engine)
            for p in registry.list_plugins("system")
        ]
        super().__init__("system", output, sub_commands)


class SystemSetterCommand(Command):
    def __init__(self, system_name, output, engine) -> None:
        self.engine = engine
        self.__doc__ = f"sets system to {system_name}"
        super().__init__(system_name, output)

    def handle(self, words=[]):
        self.output(f"Setting system to {self.name}")
        self.engine.config = {"system_name": self.name}
        return True


class MachineOptionsCommand(Command):
    def __init__(self, output, engine) -> None:
        self.engine = engine
        super().__init__("options", output)

    def sub_commands(self):
        machine_name = self.engine.config["machine_type"]
        machine_class = registry.get_plugin("machine", machine_name).obj
        return [
            MachineOptionSetterCommand(
                self.output, machine_name, name, default, self.engine
            )
            for name, default in machine_class.get_option_info().items()
        ]


class MachineOptionSetterCommand(Command):
    def __init__(self, output, machine_name, name, default, engine) -> None:
        super().__init__(name, output)
        self.engine = engine
        self.default = default[0]
        self.t = type(self.default) if self.default else default[1]
        current = self.engine.config["machine_specific_options"][name]
        self.__doc__ = f"default: {self.default} current: {str(current)}"

    def handle(self, words=[]):
        options = self.engine.config["machine_specific_options"].copy()

        if self.t is str:
            change_to = " ".join(words)
        elif self.t is int:
            change_to = int("".join(words))
        elif self.t is float:
            change_to = float("".join(words))
        else:
            self.output(f"Unsupported type {self.t}, doing nothing...")
            return True

        self.output(f"setting {self.name} to {str(change_to)}")
        options[self.name] = change_to

        self.engine.config = {"machine_specific_options": options}

        # this at least should throw errors if something is wrong
        self.engine.reset_machine()
        return True


class MachineSetterCommand(Command):
    def __init__(self, machine_name, output, engine) -> None:
        self.engine = engine
        self.__doc__ = f"set to {machine_name}"
        super().__init__(machine_name, output)

    def handle(self, words=[]):
        self.output(f"Setting machine to {self.name}")
        self.engine.config = {"machine_type": self.name}
        return True


class ConfigureCommand(Command):
    def __init__(self, output, engine) -> None:
        self.engine = engine
        super().__init__("configure", output)

    def sub_commands(self):
        ignore_here = [
            # handled elsewhere
            "dictionaries",  # TODO separate command
            "machine_type",
            "machine_specific_options",
            "system_name",
            "show_stroke_display",
            "show_suggestions_display",
            # we have no control over these
            "translation_frame_opacity",
            "start_minimized",
            # live in the future, fix it if there are complaints
            "classic_dictionaries_display_order",
            # ignore this forever
            "system_keymap",
            # handled seperately
            "enabled_extensions",
        ]
        options = [
            ConfigureOptionCommand(self.output, self.engine, option)
            for option in self.engine.config.items()
            if option[0] not in ignore_here
        ]

        options.append(ConfigureEnabledExtensionsCommand(self.output, self.engine))
        return options


class ConfigureEnabledExtensionsCommand(Command):
    def __init__(self, output, engine):
        sub_commands = [
            EnableDisableExtensionCommand(p.name, output, engine)
            for p in registry.list_plugins("extension")
        ]
        super().__init__("extensions", output, sub_commands)


class EnableDisableExtensionCommand(Command):
    def __init__(self, extension_name, output, engine):
        super().__init__(extension_name, output)
        self.engine = engine

        if self.name in self.engine.config["enabled_extensions"]:
            self.__doc__ = "enabled"
        else:
            self.__doc__ = "disabled"

    def handle(self, words=[]):
        enabled: set = self.engine.config["enabled_extensions"].copy()

        if self.name in enabled:
            self.output(f"Disabling extension {self.name}")
            enabled.remove(self.name)
        else:
            self.output(f"Enabling extension {self.name}")
            enabled.add(self.name)
        self.engine.config = {"enabled_extensions": enabled}
        return True


class ConfigureOptionCommand(Command):
    def __init__(self, output, engine, option):
        key, value = option
        self.engine = engine
        self.t = type(value)

        self.__doc__ = str(value)

        super().__init__(key, output)

    def handle(self, words=[]):
        if self.t is bool:
            change_to = not self.engine.config[self.name]
            self.output(f"Setting {self.name} to {change_to}")
            self.engine.config = {self.name: change_to}
        elif self.t is str:
            change_to = " ".join(words)
            self.output(f"Setting {self.name} to {change_to}")
            self.engine.config = {self.name: change_to}
        elif self.t is int:
            change_to = int("".join(words))
            self.output(f"Setting {self.name} to {change_to}")
            self.engine.config = {self.name: change_to}
        else:
            self.output(f"Type {self.t} not supported currently")
        return True


def build_commands(engine, layout):
    output = layout.output_to_console
    return Command(
        name=None,
        output=output,
        sub_commands=[
            MachineCommand(output, engine),
            SystemCommand(output, engine),
            ConfigureCommand(
                output,
                engine,
            ),
            # dictionary?
            LookupCommand(output, engine),
            ResetMachineCommand(output, engine.reset_machine),
            ToggleOutputCommand(output, engine),
            Command(
                "ui",
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
