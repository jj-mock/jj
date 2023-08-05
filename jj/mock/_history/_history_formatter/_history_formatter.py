from abc import ABC, abstractmethod
from typing import List

from jj.mock._history._history_item import HistoryItem

__all__ = ("HistoryFormatter",)


class HistoryFormatter(ABC):
    @abstractmethod
    def format_history(self, history: List[HistoryItem]) -> str:
        pass
