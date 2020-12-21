from plover.translation import unescape_translation

from asciimatics.event import KeyboardEvent
from asciimatics.widgets import Frame, Layout, Text, ListBox
from asciimatics.screen import Screen

from .viewcommon import set_color_scheme
from .focus import focus_pop


class AddTranslationModel():
    def __init__(self):
        pass

    def get_results(self):
        return []


class AddTranslation(Frame):
    def __init__(self, screen, model, engine):
        super(AddTranslation, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            title="Add Translation"
        )
        self._model = model
        self._engine = engine

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Text("Strokes:", "strokes",
                               on_change=self._on_change))
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
                focus_pop()
                self.delete_count = 0
            # enter, I sure hope this is cross platform
            if event.key_code == 10:
                focus_pop()
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
