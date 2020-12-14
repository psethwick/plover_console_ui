import re

from plover.formatting import RetroFormatter
from plover.suggestions import Suggestion


WORD_RX = re.compile(r'(?:\w+|[^\w\s]+)\s*')


def tails(ls):
    for i in range(len(ls)):
        yield ls[i:]


def on_translated(engine, model, old, new):
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
        phrase = ''.join(phrase)
        suggestion_list.extend(engine.get_suggestions(phrase))

    if not suggestion_list and split_words:
        suggestion_list = [Suggestion(split_words[-1], [])]

    if suggestion_list:
        model.add(suggestion_list)


def format_suggestions(suggestions):
    results = []
    for r in suggestions:
        results.append(r.text + ":")
        for s in r.steno_list:
            results.append("   " + "/".join(s))
    return [(b, a) for (a, b) in enumerate(results)]


class SuggestionsModel():
    def __init__(self):
        self.suggestions = []

    def add(self, suggestions):
        self.suggestions[0:0] = suggestions
        if (len(self.suggestions) > 100):
            del self.suggestions[50:]

    def get(self):
        return format_suggestions(self.suggestions)
