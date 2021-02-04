import re

from plover.formatting import RetroFormatter
from plover.suggestions import Suggestion
from plover import log

WORD_RX = re.compile(r'(?:\w+|[^\w\s]+)\s*')


def tails(ls):
    for i in range(len(ls)):
        yield ls[i:]


def on_translated(engine, on_output, old, new):
    # Check for new output.
    for a in reversed(new):
        if a.text and not a.text.isspace():
            break
    else:
        return

    last_translations = engine.translator_state.translations
    log.info(last_translations[-1:][0].strokes)
    retro_formatter = RetroFormatter(last_translations)
    split_words = retro_formatter.last_words(10, rx=WORD_RX)

    suggestion_list = []
    for phrase in tails(split_words):
        phrase = ''.join(phrase)
        suggestion_list.extend(engine.get_suggestions(phrase))

    if suggestion_list:
        on_output(format_suggestions(suggestion_list))


def format_suggestions(suggestions):
    results = []
    for r in suggestions:
        results.append(r.text + ":")
        for s in r.steno_list:
            results.append("    " + "/".join(s))
    return "\n".join(results)
