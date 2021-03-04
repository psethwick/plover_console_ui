# some of this code is derivative of code in plover core
# for full source of that, visit: https://github.com/openstenoproject/plover


def dictionary_filter(key, value):
    # Allow undo...
    if value == "=undo":
        return False
    # ...and translations with special entries. Do this by looking for
    # braces but take into account escaped braces and slashes.
    escaped = value.replace("\\\\", "").replace("\\{", "")
    special = "{#" in escaped or "{PLOVER:" in escaped
    return not special


def add_filter(engine):
    with engine:
        if dictionary_filter not in engine._dictionaries.filters:
            engine.add_dictionary_filter(dictionary_filter)


def remove_filter(engine):
    with engine:
        if dictionary_filter in engine._dictionaries.filters:
            engine.remove_dictionary_filter(dictionary_filter)
