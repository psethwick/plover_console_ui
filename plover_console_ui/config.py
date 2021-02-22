from plover.config import raw_option

CONSOLE_SECTION = "Console UI"


def dummy_validate(config, key, value):
    # we always set these on the application first
    # it throws if it's bad so here... just let it go
    return value


console_ui_options = [
    # TODO show dictionary pane? (boolean_option)
    raw_option("console_ui_fg", None, CONSOLE_SECTION, "fg", dummy_validate),
    raw_option("console_ui_bg", None, CONSOLE_SECTION, "bg", dummy_validate),
]
