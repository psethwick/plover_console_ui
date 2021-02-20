from plover import log
from plover.log import logging


class ConsoleNotificationHandler(logging.Handler):
    """ Handler using console to show messages. """

    def __init__(self, output):
        super().__init__()
        self.output = output
        self.setLevel(log.WARNING)
        self.setFormatter(
            log.NoExceptionTracebackFormatter("%(levelname)s: %(message)s")
        )

    def emit(self, record):
        message = self.format(record)
        if message.endswith("\n"):
            message = message[:-1]
        self.output(message)
