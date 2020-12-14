from asciimatics.widgets import \
    Frame, Layout, Text, ListBox, Button, DropdownList, \
    Divider, VerticalDivider

from plover.registry import registry

from .viewcommon import set_color_scheme


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
        self._machine = DropdownList(
            self._machines,
            name="machine",
            on_change=self._on_machine_changed)

        status_layout.add_widget(Text("Machine:", readonly=True))
        status_layout.add_widget(Button("reset", self._reconnect_machine), 2)
        status_layout.add_widget(self._machine, 1)
        status_layout.add_widget(Text("System:", readonly=True))

        self._system = DropdownList(self._systems,
                                    name="system",
                                    on_change=self._on_system_changed)
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
        return 1
