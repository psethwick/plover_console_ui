from functools import partial

from plover_tui.suggestions import on_translated
from plover_tui.presentation import TuiLayout
from threading import Thread, current_thread

from plover.engine import StenoEngine


class TuiEngine(StenoEngine, Thread):

    def __init__(self, config, keyboard_emulation, layout: TuiLayout):
        StenoEngine.__init__(self, config, keyboard_emulation)
        Thread.__init__(self)
        self.name += '-engine'
        self.layout = layout
        # TODO format tape
        self.hook_connect('stroked', lambda stroke: layout.output_to_tape(stroke.rtfcre))
        self.hook_connect('focus', layout.on_focus)
        self.hook_connect('translated', self.on_translated)
        self.hook_connect('add_translation', partial(layout.on_add_translation, self))

    def _in_engine_thread(self):
        return current_thread() == self

    def start(self):
        Thread.start(self)
        StenoEngine.start(self)

    def join(self):
        Thread.join(self)
        return self.code
    
    def on_translated(self, old, new):
        on_translated(self, self.layout.output_to_suggestions, old, new)

