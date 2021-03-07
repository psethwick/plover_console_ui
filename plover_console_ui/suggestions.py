# some of this code is derivative of code in plover core
# for full source of that, visit: https://github.com/openstenoproject/plover

import re

from plover.formatting import RetroFormatter

from .output import output_to_buffer

from prompt_toolkit.widgets import TextArea, Frame


WORD_RX = re.compile(r"(?:\w+|[^\w\s]+)\s*")


def tails(ls):
    for i in range(len(ls)):
        yield ls[i:]


def format_suggestions(suggestions):
    results = []
    for r in suggestions:
        results.append(r.text + ":")
        for s in r.steno_list:
            results.append("    " + "/".join(s))
    return "\n".join(results)


class Suggestions(Frame):
    def __init__(self):
        self.engine = None
        super().__init__(
            TextArea(focusable=False, width=23), title="Suggestions", style="class:normal"
        )

    def output(self, text):
        output_to_buffer(self.body.buffer, text)

    def on(self):
        self.engine.hook_connect("translated", self.on_translated)

    def off(self):
        self.engine.hook_disconnect("translated", self.on_translated)

    # TODO perhaps this algo could use some work
    def on_translated(self, old, new):
        # Check for new output.
        for a in reversed(new):
            if a.text and not a.text.isspace():
                break
        else:
            return

        last_translations = self.engine.translator_state.translations
        retro_formatter = RetroFormatter(last_translations)
        split_words = retro_formatter.last_words(10, rx=WORD_RX)

        suggestion_list = []
        for phrase in tails(split_words):
            phrase = "".join(phrase)
            suggestion_list.extend(self.engine.get_suggestions(phrase))

        if suggestion_list:
            self.output(format_suggestions(suggestion_list))
