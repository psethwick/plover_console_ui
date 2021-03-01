from plover import log
from plover.log import logging


class ConsoleNotificationHandler(logging.Handler):
    """ Handler using console to show messages. """

    def __init__(self):
        super().__init__()
        self.output = None
        self.setFormatter(
            log.NoExceptionTracebackFormatter("%(levelname)s: %(message)s")
        )

    def set_output(self, output):
        self.output = output

    def emit(self, record):
        if not self.output:
            return
        message = self.format(record)
        if message.endswith("\n"):
            message = message[:-1]
        self.output(message)


notification_handler = ConsoleNotificationHandler()