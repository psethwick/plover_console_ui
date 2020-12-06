from threading import Event
from functools import partial
from collections import defaultdict

from plover.translation import unescape_translation
from plover.oslayer.keyboardcontrol import KeyboardEmulation

from plover.gui_none.engine import Engine

from asciimatics.widgets import \
    Frame, Layout, Text, ListBox, Widget, Button
from asciimatics.scene import Scene
from asciimatics.screen import Screen

from asciimatics.exceptions import NextScene

from asciimatics.renderers import FigletText
from asciimatics.effects import Print


def show_error(title, message):
    # TODO what am I gonna do with this
    print('%s: %s' % (title, message))



class ConfigurationView(Frame):
    def __init__(self, screen, model):
        super(ConfigurationView, self).__init__(
            screen,
            screen.height,
            screen.width)

        self._model = model
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

        self._list = ListBox(
            Widget.FILL_FRAME,
            model.get(),
            name="paper tape"
        )
        layout.add_widget(self._list)
        self.fix()

    def update(self, frame_no):
        if self._model.dirty:
            self._list.options = self._model.get()
        super(MainView, self).update(frame_no)

    @property
    def frame_update_count(self):
        # frame is 50ms, 250ms updates should be fine
        return 5


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
        # Add my own colour palette
        self.palette = defaultdict(
            lambda: (Screen.COLOUR_GREEN, Screen.A_NORMAL, Screen.COLOUR_BLACK))
        for key in ["selected_focus_field", "label"]:
            self.palette[key] = (Screen.COLOUR_GREEN, Screen.A_BOLD, Screen.COLOUR_BLACK)
        self.palette["title"] = (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_GREEN)
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
        # TODO this doesn't work
        raise NextScene("Main")

    @property
    def frame_update_count(self):
        # this one should be fast
        return 1


class MainView(Frame):
    def __init__(self, screen, model):
        super(MainView, self).__init__(
            screen,
            screen.height,
            screen.width,
            title="Plover")

        self._model = model
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

        # TODO add buttons/ widgets for stuff
        self._list = ListBox(
            Widget.FILL_FRAME,
            model.get(),
            name="paper tape"
        )
        layout.add_widget(self._list)
        # Add my own colour palette
        self.palette = defaultdict(
            lambda: (Screen.COLOUR_GREEN, Screen.A_NORMAL, Screen.COLOUR_BLACK))
        for key in ["selected_focus_field", "label"]:
            self.palette[key] = (Screen.COLOUR_GREEN, Screen.A_BOLD, Screen.COLOUR_BLACK)
        self.palette["title"] = (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_GREEN)
        self.fix()

    def update(self, frame_no):
        if self._model.dirty:
            self._list.options = self._model.get()
        super(MainView, self).update(frame_no)

    @property
    def frame_update_count(self):
        # frame is 50ms, 250ms updates should be fine
        return 5


class PaperTapeModel():
    def __init__(self):
        self.tape = []
        self.dirty = False

    def add(self, s):
        self.dirty = True
        if len(self.tape) > 50:
            self.tape.pop(0)
        self.tape.append((s))

    def get(self):
        self.dirty = False
        return [(s, i) for (i, s)
                in enumerate(self.tape)]


def format_suggestion(suggestion):
    return suggestion.text + ":\n" + "\n".join(
        ["/".join(t) for t in suggestion.steno_list])


class LookupModel():
    def __init__(self):
        self.dirty = False
        self._lookup = None
        # List of named tuple
        # (Suggestion, [strokes list])
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
                l.append("/".join(s))
        return [(b, a) for (a, b) in enumerate(l)]


class ConfigModel():
    def __init__(self, plover_config):
        # TODO this should probably have a set method
        self.plover_config = plover_config


def on_stroked(model, stroke):
    model.add(stroke.rtfcre)


def on_lookup(screen, engine):
    scenes = [
        Scene([LookupView(screen, lookup_model, engine)], -1, name="Lookup"),
        Scene([MainView(screen, paper_tape_model)], -1, name="Main"),
    ]
    screen.set_scenes(scenes)


def reset_machine(engine):
    engine._update(reset_machine=True)


def app(screen, scene, engine):
    engine.hook_connect('stroked', partial(on_stroked, paper_tape_model))
    engine.hook_connect('lookup', partial(on_lookup, screen, engine))
    scenes = [
        Scene([MainView(screen, paper_tape_model)], -1, name="Main"),
        #Scene([ConfigurationView(screen, config_model)], -1),
        Scene([LookupView(screen, lookup_model, engine)], -1, name="Lookup"),
    ]
    engine.start()
    screen.play(scenes, start_scene=scene)

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


paper_tape_model = PaperTapeModel()
lookup_model = LookupModel()
last_scene = None


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
