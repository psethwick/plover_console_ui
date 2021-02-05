from plover_tui.presentation import output_to_buffer
from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer

from plover.translation import unescape_translation

from .suggestions import format_suggestions

class Commander:
    def __init__(self, engine, layout) -> None:
        self._engine = engine
        self._config = engine._config
        self._layout = layout

    def __call__(self, buff: Buffer):
        try:
            # TODO prompt state
            output = f"Unknown command '{buff.text}'"
            words = buff.text.split()
            if len(words) > 0:
                if words[0].lower() == "quit":
                    output = "Exiting..."
                    get_app().exit(0)
                if words[0] == "lookup": 
                    lookup = unescape_translation(" ".join(words[1:]))
                    output = f"Lookup\n------\n"
                    suggestions = format_suggestions(self._engine.get_suggestions(lookup))
                    if suggestions:
                        output += suggestions
                    else:
                        output += f"'{lookup}' not found"
                if words[0] == "tape":
                    output = self._layout.toggle_tape()
                if words[0] == "suggestions":
                    output = self._layout.toggle_suggestions()
                if words[0] == "console":
                    output = self._layout.toggle_console()
                if words[0] == "save":
                    output = "Saving config..."
                    with open(self._config.target_file, 'wb') as f:
                        self._config.save(f)
                if words[0] == "output":
                    if self._engine.output:
                        self._engine.output = False
                    else:
                        self._engine.output = True
                    output = "Output: " + str(self._engine.output)
                if words[0] == "machine":
                    new_machine = " ".join(words[1:])
                    output = f"Setting machine to {new_machine}"
                    self._engine.config = {"machine_type": new_machine}

        except BaseException as e:
            output = "\n\n{}".format(e)
        output_to_buffer(buff, output)
    
    def prompt(self):
        return "well >>> "
