from collections import defaultdict
from asciimatics.screen import Screen


def set_color_scheme(palette):
    palette = defaultdict(
        lambda: (Screen.COLOUR_YELLOW, Screen.A_NORMAL, Screen.COLOUR_BLACK)
    )
    for key in ["selected_focus_field", "label"]:
        palette[key] = \
            (Screen.COLOUR_YELLOW, Screen.A_BOLD, Screen.COLOUR_BLACK)
    palette["title"] = \
        (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_YELLOW)
    return palette
