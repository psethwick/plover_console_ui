from threading import Event
from functools import partial
from collections import defaultdict

from plover.translation import unescape_translation
from plover.oslayer.keyboardcontrol import KeyboardEmulation

from plover.gui_none.engine import Engine
from plover.registry import registry

from asciimatics.widgets import \
    Frame, Layout, Text, ListBox, Widget, Button, PopUpDialog, DropdownList
from asciimatics.scene import Scene
from asciimatics.screen import Screen

from asciimatics.exceptions import NextScene

from asciimatics.renderers import FigletText
from asciimatics.effects import Print


def tui_show_error(screen, title, message):
    # TODO what am I gonna do with this
    print('%s: %s' % (title, message))


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

        self._list = ListBox(
            50,
            model.get_results(),
            name="paper tape"
        )
        layout.add_widget(self._list)

        # TODO handle escape?
        # then probably don't need buttons
        button_layout = Layout([1, 1, 1, 1])
        self.add_layout(button_layout)

        button_layout.add_widget(Button("OK", self._ok), 0)
        self.palette = set_color_scheme(self.palette)
        self.fix()

    def update(self, frame_no):
        if self._model.dirty:
            self._list.options = self._model.get_results()
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

        status_layout = Layout([1, 2])
        self.add_layout(status_layout)
        self._model = model
        layout = Layout([1])
        self.add_layout(layout)

        # dunno if name is enough, but it'll do for now
        self._machines = [
            (m, m) for m
            in [engine._config.as_dict()["machine_type"]] +
               [m.name for m in registry.list_plugins("machine")]
        ]

        self._machine = DropdownList(self._machines, on_change=self._on_machine_changed, name="machine")

        status_layout.add_widget(Text("Machine:", readonly=True))
        status_layout.add_widget(self._machine, 1)
        status_layout.add_widget(Text("System:", readonly=True))
        status_layout.add_widget(Text(engine._config.as_dict()["system_name"], readonly=True), 1)
        status_layout.add_widget
        self._list = ListBox(
            50,
            model.paper_tape.get(),
            name="paper tape"
        )
        layout.add_widget(self._list)
        self.palette = set_color_scheme(self.palette)
        self.fix()

    def _on_machine_changed(self):
        self.save()
        if "machine" in self.data:
            new_machine = self.data["machine"]
            self._engine.config = {"machine_type": new_machine}




    def update(self, frame_no):
        self._list.options = self._model.paper_tape.get()
        super(MainView, self).update(frame_no)

    @property
    def frame_update_count(self):
        # frame is 50ms, 250ms updates should be fine
        return 5


class PaperTapeModel():
    def __init__(self):
        self.tape = []

    def add(self, s):
        if len(self.tape) > 50:
            self.tape.pop(0)
        self.tape.append((s))

    def get(self):
        return [(s, i) for (i, s)
                in enumerate(self.tape)]


def format_suggestion(suggestion):
    return suggestion.text + ":\n" + "\n".join(
        ["/".join(t) for t in suggestion.steno_list])


class LookupModel():
    def __init__(self):
        self.dirty = False
        self._lookup = None
        self._results = []

    def set_lookup(self, lookup):
        self._lookup = lookup

    def set_results(self, results):
        self.dirty = True
        self._results = results

    def get_results(self):
        self.dirty = False
        l = []
        for r in self._results:
            l.append(r.text + ":")
            for s in r.steno_list:
                l.append("   " + "/".join(s))
        return [(b, a) for (a, b) in enumerate(l)]


class ConfigModel():
    def __init__(self, plover_config):
        # TODO this should probably have a set method
        self.plover_config = plover_config


def on_stroked(model, stroke):
    model.add(stroke.rtfcre)

def scene_key(scene):
    return scene.name

def on_lookup(screen, engine):
    scenes = [
        Scene([LookupView(screen, lookup_model, engine)], -1, name="Lookup"),
        Scene([MainView(screen, main_model, engine)], -1, name="Main"),
    ]
    screen.set_scenes(scenes)


def on_add_translation(screen, engine):
    raise



def reset_machine(engine):
    engine._update(reset_machine=True)



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


class MainModel():
    def __init__(self, lookup, paper_tape):
        self.lookup = lookup
        self.paper_tape = paper_tape
        self.view = 'main'


paper_tape_model = PaperTapeModel()
lookup_model = LookupModel()
main_model = MainModel(lookup_model, paper_tape_model)
last_scene = None


def app(screen, scene, engine):
    scenes = [
        Scene([MainView(screen, main_model, engine)], -1, name="Main"),
        Scene([LookupView(screen, lookup_model, engine)], -1, name="Lookup"),
    ]

    engine.hook_connect('stroked', partial(on_stroked, paper_tape_model))
    engine.hook_connect('lookup', partial(on_lookup, screen, engine))
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
