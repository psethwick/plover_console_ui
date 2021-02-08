from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.application import get_app

from plover import log
from plover.formatting import RetroFormatter


def dictionary_filter(key, value):
    # Allow undo...
    if value == "=undo":
        return False
    # ...and translations with special entries. Do this by looking for
    # braces but take into account escaped braces and slashes.
    escaped = value.replace("\\\\", "").replace("\\{", "")
    special = "{#" in escaped or "{PLOVER:" in escaped
    return not special


class AddTranslation:
    def __init__(self, engine, on_output, on_exit):
        self.engine = engine
        self.on_exit = on_exit
        self.on_output = on_output

        # we start in the strokes field
        self.engine.add_dictionary_filter(dictionary_filter)

        self.strokes_field = TextArea(
            prompt="Strokes: ",
            height=1,
            multiline=False,
            wrap_lines=False,
            accept_handler=self.accept,
        )

        self.strokes_field.buffer.on_text_changed += self.strokes_changed
        self.translation_field = TextArea(
            prompt="Output: ",
            height=1,
            multiline=False,
            wrap_lines=False,
            accept_handler=self.accept,
        )

        self.translation_field.buffer.on_text_changed += self.translation_changed

        last_translations = engine.translator_state.translations
        retro_formatter = RetroFormatter(last_translations)
        last_words = retro_formatter.last_words(1)

        if last_words:
            self.translation_field.text = last_words[0]

        kb = KeyBindings()

        @kb.add("escape", eager=True)
        def _(event):
            self.engine.remove_dictionary_filter(dictionary_filter)
            on_exit()

        @kb.add("tab")
        def _(event):
            self.cycle_focus()

        self.container = HSplit(
            [self.strokes_field, self.translation_field],
            key_bindings=kb,
        )

    def cycle_focus(self):
        layout = get_app().layout
        if layout.has_focus(self.strokes_field):
            self.engine.remove_dictionary_filter(dictionary_filter)
        else:
            self.engine.add_dictionary_filter(dictionary_filter)
        layout.focus_next()

    def accept(self, _):
        self.engine.add_translation(
            tuple(self.strokes_field.text.strip().split()), self.translation_field.text
        )

    def strokes_changed(self, buff: Buffer):
        pass
        res = self.engine

    def translation_changed(self, buff: Buffer):
        pass
        log.info("translation changed: " + buff.text)