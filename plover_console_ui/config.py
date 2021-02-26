from plover.config import raw_option, choice_option

CONSOLE_SECTION = "Console UI"


def validate_colors(config, key, value):
    # we always set these on the application first
    # it throws if it's bad so here... just let it go
    return value


log_levels = [
    "WARNING",
    "CRITICAL",
    "ERROR",
    "INFO",
    "DEBUG",
]

console_ui_options = [
    choice_option(
        "console_ui_loglevel",
        log_levels,
        CONSOLE_SECTION,
        "loglevel",
    ),
    raw_option("console_ui_fg", None, CONSOLE_SECTION, "fg", validate_colors),
    raw_option("console_ui_bg", None, CONSOLE_SECTION, "bg", validate_colors),
]
