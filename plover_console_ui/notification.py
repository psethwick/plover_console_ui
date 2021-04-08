from plover.log import logging, LOG_FORMAT


class ConsoleNotificationHandler(logging.Handler):
    """ Handler using console to show messages. """

    def __init__(self, format=LOG_FORMAT):
        super().__init__()
        self.output = None
        self.setFormatter(logging.Formatter(format))

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
