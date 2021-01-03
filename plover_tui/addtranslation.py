from plover.translation import unescape_translation
from plover.oslayer.wmctrl import SetForegroundWindow

from asciimatics.event import KeyboardEvent
from asciimatics.widgets import Frame, Layout, Text, ListBox
from asciimatics.screen import Screen

from .viewcommon import set_color_scheme


class AddTranslationModel():
    def __init__(self):
        self.strokes = "PPHORB"
        self.translation = "mosh"
        self.strokeconflict = None

    def get_results(self):
        results = []
        if self.conflicts:
            return


        f'{self.strokes} is d'


class AddTranslation(Frame):
    def __init__(self, screen, model, engine, previous_window):
        super(AddTranslation, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            title="Add Translation"
        )
        self._previous_window = previous_window
        self._model = model
        self._engine = engine

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

        self.data["strokes"] = self._model.strokes
        layout.add_widget(Text("Strokes:", "strokes",
                               on_change=self._on_change))
        self.data["translation"] = self._model.translation
        layout.add_widget(Text("Translation:", "translation",
                               on_change=self._on_change))

        self._existing_translations = ListBox(
            100,
            model.get_results(),
        )
        layout.add_widget(self._existing_translations)

        self.palette = set_color_scheme(self.palette)
        self.fix()

    def update(self, frame_no):
        self._existing_translations.options = self._model.get_results()
        super(AddTranslation, self).update(frame_no)

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.KEY_ESCAPE:
                # nope out
                SetForegroundWindow(self._previous_window)
                self.delete_count = 0
            # enter, I sure hope this is cross platform
            if event.key_code == 10:
                # add the translation if things are valid
                # then nope out
                SetForegroundWindow(self._previous_window)
                self.delete_count = 0
        super(AddTranslation, self).process_event(event)

    def _on_change(self):
        self.save()
        if "lookup" in self.data:
            lookup = unescape_translation(self.data["lookup"].strip())
            self._model.set_lookup = lookup
            self._model.set_results(self._engine.get_suggestions(lookup))

    @property
    def frame_update_count(self):
        return 1
