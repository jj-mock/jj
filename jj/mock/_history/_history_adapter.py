from typing import Callable

from ._body_parser import BodyParser
from ._history_item import HistoryItem

__all__ = ("default_history_adapter", "HistoryAdapterType")

HistoryAdapterType = Callable[[HistoryItem], HistoryItem]

default_history_adapter = BodyParser().parse
