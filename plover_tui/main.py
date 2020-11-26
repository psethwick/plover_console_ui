from threading import Event
from functools import partial

from plover.oslayer.keyboardcontrol import KeyboardEmulation

from plover.gui_none.engine import Engine

from asciimatics.widgets import Frame, Layout, Text, ListBox, Widget
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.renderers import FigletText

from asciimatics.effects import Print


def show_error(title, message):
    # TODO what am I gonna do with this
    print('%s: %s' % (title, message))


class PaperTapeView(Frame):
    def __init__(self, screen, model):
        super(PaperTapeView, self).__init__(screen,
                                            screen.height * 2 // 3,
                                            screen.width * 2 // 3)
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

    def _update(self, frame_no):
        self._list.options = self._model.get()
        super(PaperTapeView, self)._update(frame_no)


class PaperTapeModel():
    def __init__(self):
        self.counter = 1
        self.tape = [('test', 0)]

    def add(self, s):
        if len(self.tape) > 50:
            # good enough for now
            self.tape.pop(0)
        self.counter += 1
        self.tape.append((s, self.counter))

    def get(self):
        return self.tape


def on_stroked(model, steno_keys):
    model.add(str(steno_keys))


def demo(screen, scene):
    s


def app(screen, scene):
    scenes = [
        Scene([PaperTapeView(screen, paper_tape_model)], -1)
    ]
    screen.play(scenes, start_scene=scene)


paper_tape_model = PaperTapeModel()
last_scene = None


def main(config):
    engine = Engine(config, KeyboardEmulation())
    if not engine.load_config():
        return 3
    quitting = Event()
    engine.hook_connect('quit', quitting.set)
    engine.hook_connect('stroked', partial(on_stroked, paper_tape_model))
    try:
        engine.start()
        Screen.wrapper(app, arguments=[last_scene])
        quitting.wait()
    except KeyboardInterrupt:
        engine.quit()
    return engine.join()
