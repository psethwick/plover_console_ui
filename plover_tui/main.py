from asciimatics.widgets import \
    Frame, Layout, Text, ListBox, Button, DropdownList, \
    Divider, VerticalDivider, RadioButtons, CheckBox

from plover.registry import registry

from .viewcommon import set_color_scheme


class Main(Frame):
    def __init__(self, screen, model, engine):
        super(Main, self).__init__(
            screen,
            screen.height,
            screen.width,
            title="Plover")

        self._engine = engine

        status_layout = Layout([1, 1])
        self.add_layout(status_layout)
        self._model = model
        layout = Layout([1])
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
            on_change=self._on_config_changed)

        status_layout.add_widget(self._machine)
        self._system = DropdownList(self._systems,
                                    name="system",
                                    on_change=self._on_config_changed)
        status_layout.add_widget(self._system, 1)
        status_layout.add_widget(Divider())
        status_layout.add_widget(Divider(), 1)

        status_layout.add_widget(Button("Reconnect", self._reconnect_machine))
        status_layout.add_widget(RadioButtons(
            [("Suggestions", self._model.suggestions.get),
             ("Paper Tape", self._model.paper_tape.get)], name="list",
            on_change=self._on_config_changed))

        self._output = CheckBox("Output",
                                name="output",
                                on_change=self._on_config_changed)
        status_layout.add_widget(self._output, 1)
        self._list_get = model.suggestions.get
        self._list = ListBox(
            10,
            self._list_get()
        )
        layout.add_widget(Divider())
        layout.add_widget(self._list)
        self.palette = set_color_scheme(self.palette)
        self.fix()

    def _reconnect_machine(self):
        self._engine.reset_machine()

    def _on_config_changed(self):
        self.save()
        if "machine" in self.data:
            self._engine.config = {"machine_type": self.data["machine"]}
        if "system" in self.data:
            self._engine.config = {"system_name": self.data["system"]}
        if "output" in self.data:
            self._engine.output = self.data["output"]
        if "list" in self.data:
            self._list_get = self.data["list"]

    def update(self, frame_no):
        self._list.options = self._list_get()
        self._output.value = self._engine.output
        # self._suggestions.options = self._model.suggestions.get()
        super(Main, self).update(frame_no)

    @property
    def frame_update_count(self):
        # frame is 50ms, 250ms updates should be fine
        return 1
