import logging


__all__ = ("Logger",)


class Logger(logging.Logger):
    def clearHandlers(self) -> "Logger":
        for handler in self.handlers:
            self.removeHandler(handler)
        return self
