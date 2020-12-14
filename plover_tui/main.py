from threading import Event
from functools import partial
from collections import defaultdict
import re

from plover.translation import unescape_translation
from plover.oslayer.keyboardcontrol import KeyboardEmulation
from plover.formatting import RetroFormatter
from plover.suggestions import Suggestion


from plover.gui_none.engine import Engine
from plover.registry import registry

from asciimatics.widgets import \
    Frame, Layout, Text, ListBox, Button, DropdownList, \
    Divider, VerticalDivider
from asciimatics.scene import Scene
from asciimatics.screen import Screen

from asciimatics.exceptions import NextScene

WORD_RX = re.compile(r'(?:\w+|[^\w\s]+)\s*')


def show_error(title, message):
    print(title + message)


class LookupView(Frame):
    def __init__(self, screen, model, engine):
        super(LookupView, self).__init__(
            screen,
            screen.height,
            screen.width,
            title="Lookup"
        )

        self._model = model
        self._engine = engine

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Text("Translation:", "lookup",
                               on_change=self._on_change))

        self._paper_tape = ListBox(
            100,
            model.get_results(),
            name="paper tape"
        )
        layout.add_widget(self._paper_tape)

        # TODO handle escape?
        # then probably don't need buttons
        button_layout = Layout([1, 1, 1, 1])
        self.add_layout(button_layout)

        button_layout.add_widget(Button("OK", self._ok), 0)
        self.palette = set_color_scheme(self.palette)
        self.fix()

    def update(self, frame_no):
        self._paper_tape.options = self._model.get_results()
        super(LookupView, self).update(frame_no)

    def _on_change(self):
        self.save()
        if "lookup" in self.data:
            lookup = unescape_translation(self.data["lookup"].strip())
            self._model.set_lookup = lookup
            self._model.set_results(self._engine.get_suggestions(lookup))

    def _ok(self):
        raise NextScene("Main")

    @property
    def frame_update_count(self):
        # this one should be fast
        return 1


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


class MainView(Frame):
    def __init__(self, screen, model, engine):
        super(MainView, self).__init__(
            screen,
            screen.height,
            screen.width,
            title="Plover")

        self._engine = engine

        status_layout = Layout([10, 10, 10], fill_frame=True)
        self.add_layout(status_layout)
        self._model = model
        layout = Layout([49, 1, 49])
        self.add_layout(layout)

        # dunno if name is enough, but it'll do for now
        self._machines = [
            (m, m) for m
            in [engine._config.as_dict()["machine_type"]] +
               [m.name for m in registry.list_plugins("machine")]
        ]

        self._systems = [
            (s, s) for s
            in [engine._config.as_dict()["system_name"]] +
               [s.name for s in registry.list_plugins("system")]

        ]
        self._machine = DropdownList(self._machines, name="machine", on_change=self._on_machine_changed)

        status_layout.add_widget(Text("Machine:", readonly=True))
        status_layout.add_widget(Button("reset", self._reconnect_machine), 2)
        status_layout.add_widget(self._machine, 1)
        status_layout.add_widget(Text("System:", readonly=True))
        # TODO implement system switching
        self._system = DropdownList(self._systems, name="system", on_change=self._on_system_changed)
        status_layout.add_widget(self._system, 1)
        self._paper_tape = ListBox(
            100,
            model.paper_tape.get(),
            name="paper tape"
        )
        layout.add_widget(Divider())
        layout.add_widget(Divider(), 1)
        layout.add_widget(Divider(), 2)
        layout.add_widget(Text("Paper Tape", readonly=True))
        layout.add_widget(self._paper_tape)
        self._suggestions = ListBox(
            100,
            model.suggestions.get(),
            name="suggestions"
        )
        layout.add_widget(VerticalDivider(), 1)
        layout.add_widget(Text("Suggestions", readonly=True), 2)
        layout.add_widget(self._suggestions, 2)
        self.palette = set_color_scheme(self.palette)
        self.fix()

    def _reconnect_machine(self):
        self._engine.reset_machine()

    def _on_machine_changed(self):
        self.save()
        if "machine" in self.data:
            self._engine.config = {"machine_type": self.data["machine"]}

    def _on_system_changed(self):
        self.save()
        if "system" in self.data:
            self._engine.config = {"system_name": self.data["system"]}

    def update(self, frame_no):
        # TODO do I need more state refresh
        self._paper_tape.options = self._model.paper_tape.get()
        self._suggestions.options = self._model.suggestions.get()
        super(MainView, self).update(frame_no)

    @property
    def frame_update_count(self):
        # frame is 50ms, 250ms updates should be fine
        return 5


class PaperTapeModel():
    def __init__(self):
        self.tape = []

    def add(self, s):
        self.tape.insert(0, s)

    def get(self):
        return [(s, i) for (i, s)
                in enumerate(self.tape)]


def format_suggestions(suggestions):
    l = []
    for r in suggestions:
        l.append(r.text + ":")
        for s in r.steno_list:
            l.append("   " + "/".join(s))
    return [(b, a) for (a, b) in enumerate(l)]


class LookupModel():
    def __init__(self):
        self._lookup = None
        self._results = []

    def set_lookup(self, lookup):
        self._lookup = lookup

    def set_results(self, results):
        self._results = results

    def get_results(self):
        return format_suggestions(self._results)


class SuggestionsModel():
    def __init__(self):
        self.last_suggestions = []
        self.suggestions = []

    def add(self, suggestions):
        self.suggestions[0:0] = suggestions
        if (len(self.suggestions) > 100):
            del self.suggestions[50:]

    def get(self):
        return format_suggestions(self.suggestions)


class ConfigModel():
    def __init__(self, plover_config):
        # TODO this should probably have a set method
        self.plover_config = plover_config


def on_stroked(paper_tape_model, stroke):
    paper_tape_model.add(stroke.rtfcre)


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


def on_lookup(screen, engine):
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

# models
# 1. config
# 2. tape
# 3. suggestions
# 4. might need some for lookup/dictionary stuff?

# I think I want a single column

class MainModel():
    def __init__(self, lookup, paper_tape, suggestions):
        self.lookup = lookup
        self.paper_tape = paper_tape
        self.suggestions = suggestions


paper_tape_model = PaperTapeModel()
lookup_model = LookupModel()
suggestions_model = SuggestionsModel()
main_model = MainModel(lookup_model, paper_tape_model, suggestions_model)
last_scene = None


def app(screen, scene, engine):
    scenes = [
        Scene([MainView(screen, main_model, engine)], -1, name="Main"),
        Scene([LookupView(screen, lookup_model, engine)], -1, name="Lookup"),
    ]

    engine.hook_connect('stroked', partial(on_stroked, paper_tape_model))
    engine.hook_connect('lookup', partial(on_lookup, screen, engine))
    engine.hook_connect('translated', partial(on_translated, engine, suggestions_model))
    engine.hook_connect('add_translation', partial(on_add_translation, screen, engine))
    engine.start()
    screen.play(scenes, start_scene=scene)


def main(config):
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
