from threading import Event
from functools import partial

from plover.oslayer.keyboardcontrol import KeyboardEmulation


from plover.gui_none.engine import Engine

from asciimatics.scene import Scene
from asciimatics.screen import Screen

from .lookup import LookupView, LookupModel
from .main import MainView

from .papertape import PaperTapeModel, on_stroked
from .suggestions import SuggestionsModel, on_translated
from .focus import mark, focus_tui, TUI_MARKER


def show_error(title, message):
    print(title + message)


def on_lookup(screen, engine):
    focus_tui()
    scenes = [
        Scene([LookupView(screen, lookup_model, engine)], -1, name="Lookup"),
        Scene([MainView(screen, main_model, engine)], -1, name="Main"),
    ]
    screen.set_scenes(scenes)


def on_add_translation(screen, engine):
    raise

# machine status
# reconnect
# choose machine
# choose system
# output/etc


# I think I want a single column
# TODO foxus!
# TODO dictionary update
# TODO I guess the config stuff

class MainModel():
    def __init__(self, paper_tape, suggestions):
        self.paper_tape = paper_tape
        self.suggestions = suggestions


paper_tape_model = PaperTapeModel()
lookup_model = LookupModel()
suggestions_model = SuggestionsModel()
main_model = MainModel(paper_tape_model, suggestions_model)
last_scene = None


def app(screen, scene, engine):
    scenes = [
        Scene([MainView(screen, main_model, engine)], -1, name="Main"),
        Scene([LookupView(screen, lookup_model, engine)], -1, name="Lookup"),
    ]

    engine.hook_connect('stroked',
                        partial(on_stroked, paper_tape_model))
    engine.hook_connect('lookup',
                        partial(on_lookup, screen, engine))
    engine.hook_connect('translated',
                        partial(on_translated, engine, suggestions_model))
    engine.hook_connect('add_translation',
                        partial(on_add_translation, screen, engine))
    engine.start()
    screen.play(scenes, start_scene=scene)


def main(config):
    mark(TUI_MARKER)
    engine = Engine(config, KeyboardEmulation())
    if not engine.load_config():
        return 3
    quitting = Event()
    engine.hook_connect('quit', quitting.set)
    try:
        Screen.wrapper(app, arguments=[last_scene, engine])
        quitting.wait()
    except KeyboardInterrupt:
        engine.quit()
    return engine.join()
