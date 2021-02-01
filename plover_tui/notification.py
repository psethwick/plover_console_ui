from plover import log
from plover.log import logging

class TuiNotificationHandler(logging.Handler):
    """ Handler using tui output_field to show messages. """

    def __init__(self, on_output):
        super().__init__()
        self._on_output = on_output
        # do we care about the level?
        #self.setLevel(log.WARNING)
        self.setFormatter(log.NoExceptionTracebackFormatter('%(levelname)s: %(message)s'))

    def emit(self, record):
        message = self.format(record)
        if message.endswith('\n'):
            message = message[:-1]
        self._on_output(message)
