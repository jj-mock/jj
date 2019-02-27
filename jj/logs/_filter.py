import logging
from logging import LogRecord


__all__ = ("Filter",)


class Filter(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        return True
