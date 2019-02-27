import logging


class TestLogRecord(logging.LogRecord):
    def __init__(self, message):
        super().__init__(
            name=None,
            level=None,
            pathname=None,
            lineno=None,
            msg=message,
            args=None,
            exc_info=None)
