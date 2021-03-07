from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.layout.containers import DynamicContainer
from prompt_toolkit.styles import Style

from .layout import layout


kb = KeyBindings()


@kb.add("c-c")
@kb.add("c-q")
def _(event):
    " Pressing Ctrl-Q or Ctrl-C will exit the user interface. "
    event.app.exit(0)


@kb.add("pagedown")
def _(event):
    " Pressing PageDown will scroll the console window. "
    layout.scroll_down()


@kb.add("pageup")
def _(event):
    " Pressing PageUp will scroll the console window. "
    layout.scroll_up()


def create_style(fg=None, bg=None) -> Style:
    styles = ""
    # plover.cfg doesn't know that "None" is None
    if fg and fg != "None":
        styles += f"fg:{fg} "
    if bg and bg != "None":
        styles += f"bg:{bg}"
    return Style.from_dict({"status": f"{styles} reverse", "normal": f"{styles}"})


application = Application(
    layout=Layout(DynamicContainer(layout), focused_element=layout.input),
    key_bindings=kb,
    mouse_support=False,
    full_screen=True,
    enable_page_navigation_bindings=False,
)
