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


def create_style(color=None) -> Style:
    if color:
        return Style.from_dict(
            {
                "status": f"fg:{color} reverse",
                "normal": f"fg:{color}",
            }
        )
    return Style.from_dict(
        {
            "status": "reverse",
        }
    )


style = create_style()

application = Application(
    layout=Layout(DynamicContainer(layout), focused_element=layout.input),
    key_bindings=kb,
    style=style,
    mouse_support=False,
    full_screen=True,
    enable_page_navigation_bindings=False,
)