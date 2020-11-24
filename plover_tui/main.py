from threading import Event

from plover.oslayer.keyboardcontrol import KeyboardEmulation

from plover.gui_none.engine import Engine

from random import randint
from asciimatics.screen import ManagedScreen
from asciimatics.renderers import FigletText


def show_error(title, message):
    print('%s: %s' % (title, message))
    # what am I gonna do with this
    pass


class App():
    def __init__(self, screen, engine):
        self.screen = screen
        engine.hook_connect('send_string', self._on_send_string)
        engine.hook_connect('translated', self._on_translated)
        engine.hook_connect('config_changed', self._on_config_changed)
        engine.hook_connect('add_translation', self._on_add_translation)
        engine.hook_connect('configure', self._on_configure)
        engine.hook_connect('lookup', self._on_lookup)
        engine.hook_connect('focus', self._on_focus)
        engine.hook_connect('stroked', self._on_stroked)
        engine.start()

    def _on_send_string(self, s):
        # just for funsies right now
        self.screen.print_at(FigletText(s),
                             randint(0, self.screen.width),
                             randint(0, self.screen.height))
        self.screen.refresh()

    def _on_translated(self, old, new):
        # probably want this for suggestions
        pass

    def _on_config_changed(self, config_update):
        # uhh, idk, save?
        # what is this for
        pass

    def _on_add_translation(self, dictionary=None):
        # open some dialog
        # focus will be interesting
        pass

    def _on_configure(self):
        # open some dialog
        # focus will be interesting
        pass

    def _on_lookup(self):
        pass

    def _on_stroked(self, steno_keys):
        # do we need this for suggestions
        pass

    def _on_focus(self):
        # this gonna be fun
        pass

@ManagedScreen
def main(config, screen):
    engine = Engine(config, KeyboardEmulation())
    if not engine.load_config():
        return 3
    quitting = Event()
    engine.hook_connect('quit', quitting.set)
    try:
        App(screen, engine)
        quitting.wait()
    except KeyboardInterrupt:
        engine.quit()
    return engine.join()
