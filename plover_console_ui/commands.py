from os.path import isfile

from prompt_toolkit.application import get_app

from plover.translation import unescape_translation
from plover.registry import registry
from plover.misc import normalize_path
from plover.config import DictionaryConfig

from .suggestions import format_suggestions
from .application import create_style
from .config import log_levels
from .notification import notification_handler


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
            return True
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


class SetBackgroundColor(Command):
    """<web-name or hex>"""

    def __init__(self, output, engine):
        self.engine = engine
        super().__init__("background", output)

    def handle(self, words=[]):
        background = None
        if words:
            background = words[0]

        with self.engine:
            fg = self.engine.config["console_ui_fg"]
            get_app().style = create_style(fg, background)
            self.engine.config = {"console_ui_bg": background}
        return True


class SetForegroundColor(Command):
    """<web-name or hex>"""

    def __init__(self, output, engine):
        self.engine = engine
        super().__init__("foreground", output)

    def handle(self, words=[]):
        foreground = None
        if words:
            foreground = words[0]
        with self.engine:
            bg = self.engine.config["console_ui_bg"]
            get_app().style = create_style(foreground, bg)
            self.engine.config = {"console_ui_fg": foreground}

        return True


class Exit(Command):
    """exits plover"""

    def __init__(self, output):
        super().__init__("exit", output)

    def handle(self, words=[]):
        get_app().exit(0)
        return True


class Lookup(Command):
    """<word(s)> looks up in current dictionaries"""

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


class ToggleTape(Command):
    """toggles tape"""

    def __init__(self, output, toggler, engine):
        self.toggler = toggler
        self.engine = engine
        super().__init__("tape", output)

    def handle(self, words=[]):
        show = self.toggler()
        with self.engine:
            self.engine.config = {"show_stroke_display": show}
        self.output(f"Show tape: {show}")
        return True


class ToggleSuggestions(Command):
    """toggles suggestions"""

    def __init__(self, output, toggler, engine):
        self.toggler = toggler
        self.engine = engine
        super().__init__("suggestions", output)

    def handle(self, words=[]):
        show = self.toggler()
        with self.engine:
            self.engine.config = {"show_suggestions_display": show}
        self.output(f"Show suggestions: {show}")
        return True


class ResetMachine(Command):
    """reconnects machine"""

    def __init__(self, output, resetter):
        self.resetter = resetter
        super().__init__("reset", output)

    def handle(self, words=[]):
        self.output("Resetting machine...")
        self.resetter()
        return True


class ToggleOutput(Command):
    """enables/disables output"""

    def __init__(self, output, engine):
        self.engine = engine
        super().__init__("output", output)

    def handle(self, words=[]):
        with self.engine:
            if self.engine.output:
                self.engine.output = False
            else:
                self.engine.output = True
            state = "Enabled" if self.engine.output else "Disabled"
        self.output(f"Output: {state}")
        return True


class Machine(Command):
    def __init__(self, output, engine) -> None:
        sub_commands = [MachineOptions(output, engine)] + [
            SetMachine(p.name, output, engine) for p in registry.list_plugins("machine")
        ]
        super().__init__("machine", output, sub_commands)


class System(Command):
    def __init__(self, output, engine) -> None:
        sub_commands = [
            SetSystem(p.name, output, engine) for p in registry.list_plugins("system")
        ]
        super().__init__("system", output, sub_commands)


class SetSystem(Command):
    def __init__(self, system_name, output, engine) -> None:
        self.engine = engine
        self.__doc__ = f"sets to {system_name}"
        super().__init__(system_name, output)

    def handle(self, words=[]):
        self.output(f"Setting system to {self.name}")
        with self.engine:
            self.engine.config = {"system_name": self.name}
        return True


class MachineOptions(Command):
    def __init__(self, output, engine) -> None:
        self.engine = engine
        super().__init__("options", output)

    def sub_commands(self):
        machine_name = self.engine.config["machine_type"]
        machine_class = registry.get_plugin("machine", machine_name).obj
        return [
            SetMachineOption(self.output, name, default, self.engine)
            for name, default in machine_class.get_option_info().items()
        ]


class SetMachineOption(Command):
    def __init__(self, output, name, default, engine) -> None:
        super().__init__(name, output)
        self.engine = engine
        self.default = default[0]
        self.t = type(self.default) if self.default else default[1]
        current = self.engine.config["machine_specific_options"][name]
        self.__doc__ = f"current: {str(current)}"

    def handle(self, words=[]):
        with self.engine:
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
        # annoyingly plover seems to allow changing these to garbage
        self.engine.reset_machine()
        return True


class SetMachine(Command):
    def __init__(self, machine_name, output, engine) -> None:
        self.engine = engine
        self.__doc__ = f"set to {machine_name}"
        super().__init__(machine_name, output)

    def handle(self, words=[]):
        self.output(f"Setting machine to {self.name}")
        with self.engine:
            self.engine.config = {"machine_type": self.name}
        return True


class Configure(Command):
    def __init__(self, output, engine) -> None:
        self.engine = engine
        super().__init__("configure", output)

    def sub_commands(self):
        ignore_here = [
            # handled elsewhere
            "dictionaries",
            "machine_type",
            "machine_specific_options",
            "system_name",
            "show_stroke_display",
            "show_suggestions_display",
            "console_ui_loglevel",
            "console_ui_fg",
            "console_ui_bg",
            # we have no control over these
            "translation_frame_opacity",
            "start_minimized",
            # live in the future, fix it if there are complaints
            "classic_dictionaries_display_order",
            # ignore this forever (maybe)
            "system_keymap",
            # handled seperately
            "enabled_extensions",
        ]
        options = [
            ConfigureOption(self.output, self.engine, option)
            for option in self.engine.config.items()
            if option[0] not in ignore_here
        ]

        options.extend(
            [
                ConfigureEnabledExtensions(self.output, self.engine),
            ]
        )
        return options


class ConfigureLogLevel(Command):
    """threshold for showing log messages in the console"""

    def __init__(self, output, engine) -> None:
        super().__init__("loglevel", output)
        self.engine = engine
        self._sub_commands = [
            SetLogLevel(level, self.output, self.engine) for level in log_levels
        ]


class SetLogLevel(Command):
    def __init__(self, name, output, engine) -> None:
        super().__init__(name, output)
        self.engine = engine
        self.__doc__ = f"set log level to {self.name}"

    def handle(self, words=None):
        self.output(f"setting level to {self.name}")
        notification_handler.setLevel(self.name)
        self.engine.config = {"console_ui_loglevel": self.name}
        return True


class ConfigureEnabledExtensions(Command):
    def __init__(self, output, engine):
        sub_commands = [
            EnableDisableExtension(p.name, output, engine)
            for p in registry.list_plugins("extension")
        ]
        super().__init__("extensions", output, sub_commands)


class EnableDisableExtension(Command):
    def __init__(self, extension_name, output, engine):
        super().__init__(extension_name, output)
        self.engine = engine

        if self.name in self.engine.config["enabled_extensions"]:
            self.__doc__ = "enabled"
        else:
            self.__doc__ = "disabled"

    def handle(self, words=[]):
        with self.engine:
            enabled: set = self.engine.config["enabled_extensions"].copy()

            if self.name in enabled:
                self.output(f"Disabling extension {self.name}")
                enabled.remove(self.name)
            else:
                self.output(f"Enabling extension {self.name}")
                enabled.add(self.name)
            self.engine.config = {"enabled_extensions": enabled}
        return True


class ConfigureOption(Command):
    def __init__(self, output, engine, option):
        key, value = option
        self.engine = engine
        self.t = type(value)

        self.__doc__ = str(value)

        super().__init__(key, output)

    def handle(self, words=[]):
        with self.engine:
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


class DictionaryHelper:
    def __init__(self, engine, output):
        self.engine = engine
        self.output = output
        engine.hook_connect("dictionaries_loaded", self.dictionaries_loaded)

    def format_dictionary(self, index, dict):
        enabled = "Enabled" if dict.enabled else "Disabled"
        return f"{index +1}. {dict.path} {enabled}"

    def output_dictionaries(self):
        self.output("--------")
        dicts = self.engine.config["dictionaries"]
        for i, d in enumerate(dicts):
            self.output(self.format_dictionary(i, d))

    def dictionaries_loaded(self, dicts):
        self.engine.hook_connect("config_changed", self.config_changed)

    def config_changed(self, update):
        if "dictionaries" in update:
            self.output_dictionaries()


class Dictionaries(Command):
    def __init__(self, output, engine) -> None:
        self.engine = engine
        super().__init__("dictionaries", output)
        self.helper = DictionaryHelper(engine, output)

    def describe(self):
        super().describe()
        self.helper.output_dictionaries()

    def sub_commands(self):
        return [
            AddDictionary(self.output, self.engine),
            RemoveDictionary(self.output, self.engine),
            ToggleDictionary(self.output, self.engine),
            SetPriorityDictionary(self.output, self.engine),
        ]


class AddDictionary(Command):
    """<path-to-dictionary>"""

    def __init__(self, output, engine) -> None:
        self.engine = engine
        super().__init__("add", output)

    def handle(self, words=[]):
        path = normalize_path(" ".join(words))
        if not isfile(path):
            self.output(f"{path} is not a file")
            return True
        with self.engine:
            dicts = self.engine.config["dictionaries"].copy()

            dicts.insert(0, DictionaryConfig(path))

            self.engine.config = {"dictionaries": dicts}
            return True


class ToggleDictionary(Command):
    """<dictionary-number>"""

    def __init__(self, output, engine) -> None:
        self.engine = engine
        super().__init__("toggle", output)

    def handle(self, words=[]):
        with self.engine:
            index = int("".join(words)) - 1
            dicts = self.engine.config["dictionaries"].copy()

            dicts[index] = dicts[index].replace(enabled=not dicts[index].enabled)

            self.engine.config = {"dictionaries": dicts}
            return True


class RemoveDictionary(Command):
    """<dictionary-number>"""

    def __init__(self, output, engine) -> None:
        self.engine = engine
        super().__init__("remove", output)

    def handle(self, words=[]):
        index = int("".join(words)) - 1
        with self.engine:
            dicts = self.engine.config["dictionaries"].copy()
            dicts.remove(dicts[index])
            self.engine.config = {"dictionaries": dicts}
            return True


class SetPriorityDictionary(Command):
    """<dictionary-number> <new-dictionary-number>"""

    def __init__(self, output, engine) -> None:
        self.engine = engine
        super().__init__("priority", output)

    def handle(self, words):
        dictionary = int(words[0]) - 1
        new_index = int(words[1]) - 1
        with self.engine:
            dicts = self.engine.config["dictionaries"].copy()
            d = dicts.pop(dictionary)
            dicts.insert(new_index, d)
            self.engine.config = {"dictionaries": dicts}

        return True


def build_commands(engine, layout):
    output = layout.output_to_console
    return Command(
        name=None,
        output=output,
        sub_commands=[
            Lookup(output, engine),
            ResetMachine(output, engine.reset_machine),
            Machine(output, engine),
            System(output, engine),
            Configure(output, engine),
            Dictionaries(output, engine),
            ToggleOutput(output, engine),
            ToggleTape(output, layout.toggle_tape, engine),
            ToggleSuggestions(output, layout.toggle_suggestions, engine),
            Command(
                "colors",
                output,
                [
                    SetForegroundColor(output, engine),
                    SetBackgroundColor(output, engine),
                ],
            ),
            ConfigureLogLevel(output, engine),
            Exit(output),
        ],
    )
