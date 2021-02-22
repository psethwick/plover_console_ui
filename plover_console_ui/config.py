from plover.config import raw_option

CONSOLE_SECTION = "Console UI"


def dummy_validate(config, key, value):
    # TODO maybe we can check this in advace from prompt toolkit
    return value


console_ui_options = [
    # TODO show dictionary pane? (boolean_option)
    raw_option("console_ui_fg", None, CONSOLE_SECTION, "fg", dummy_validate)
]
