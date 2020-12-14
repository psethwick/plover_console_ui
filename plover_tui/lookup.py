from plover.translation import unescape_translation

from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import NextScene
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


class LookupView(Frame):
    def __init__(self, screen, model, engine):
        super(LookupView, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            title="Lookup"
        )

        self._model = model
        self._engine = engine

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Text("Lookup:", "lookup",
                               on_change=self._on_change))

        self._paper_tape = ListBox(
            100,
            model.get_results(),
            name="paper tape"
        )
        layout.add_widget(self._paper_tape)

        self.palette = set_color_scheme(self.palette)
        self.fix()

    def update(self, frame_no):
        self._paper_tape.options = self._model.get_results()
        super(LookupView, self).update(frame_no)

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.KEY_ESCAPE:
                raise NextScene("Main")
            super(LookupView, self).process_event(event)
        else:
            super(LookupView, self).process_event(event)

    def _on_change(self):
        self.save()
        if "lookup" in self.data:
            lookup = unescape_translation(self.data["lookup"].strip())
            self._model.set_lookup = lookup
            self._model.set_results(self._engine.get_suggestions(lookup))

    @property
    def frame_update_count(self):
        # this one should be fast
        return 1
