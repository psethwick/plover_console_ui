from plover.translation import unescape_translation
from plover.oslayer.wmctrl import SetForegroundWindow

from asciimatics.event import KeyboardEvent
from asciimatics.widgets import Frame, Layout, Text, ListBox
from asciimatics.screen import Screen

from .viewcommon import set_color_scheme
from .suggestions import format_suggestions


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


class Lookup(Frame):
    def __init__(self, screen, model, engine, previous_window):
        super(Lookup, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            title="Lookup"
        )

        self._previous_window = previous_window
        self._model = model
        self._engine = engine

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Text("Lookup:", "lookup",
                               on_change=self._on_change))

        self._suggestions = ListBox(
            100,
            model.get_results(),
        )
        layout.add_widget(self._suggestions)

        self.palette = set_color_scheme(self.palette)
        self.fix()

    def update(self, frame_no):
        self._suggestions.options = self._model.get_results()
        super(Lookup, self).update(frame_no)

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.KEY_ESCAPE:
                SetForegroundWindow(self._previous_window)
                self.delete_count = 0
        super(Lookup, self).process_event(event)

    def _on_change(self):
        self.save()
        if "lookup" in self.data:
            lookup = unescape_translation(self.data["lookup"].strip())
            self._model.set_lookup = lookup
            self._model.set_results(self._engine.get_suggestions(lookup))

    @property
    def frame_update_count(self):
        return 1
