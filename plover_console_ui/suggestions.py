import re

from plover.formatting import RetroFormatter

from .output import output_to_buffer

from prompt_toolkit.widgets import TextArea, Frame


WORD_RX = re.compile(r"(?:\w+|[^\w\s]+)\s*")


# TODO attribute
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
        super().__init__(
            TextArea(focusable=False), title="Suggestions", style="class:normal"
        )

    def output(self, text):
        output_to_buffer(self.body.buffer, text)

    # TODO perhaps this algo could use some work
    def on_translated(self, engine, old, new):
        # Check for new output.
        for a in reversed(new):
            if a.text and not a.text.isspace():
                break
        else:
            return

        last_translations = engine.translator_state.translations
        retro_formatter = RetroFormatter(last_translations)
        split_words = retro_formatter.last_words(10, rx=WORD_RX)

        suggestion_list = []
        for phrase in tails(split_words):
            phrase = "".join(phrase)
            suggestion_list.extend(engine.get_suggestions(phrase))

        if suggestion_list:
            self.output(format_suggestions(suggestion_list))
