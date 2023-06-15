import json
import os
import shutil
from abc import ABC, abstractmethod
from pprint import pformat as pf
from typing import List, Optional, Union

from jj.mock._history._history_item import HistoryItem

__all__ = ("default_history_formatter", "HistoryFormatter", "PrettyHistoryFormatter",
           "SimpleHistoryFormatter",)


REMOTE_MOCK_PPRINT_LIMIT = os.environ.get("JJ_REMOTE_MOCK_PPRINT_LIMIT", "1000000")
REMOTE_MOCK_PPRINT_WIDTH = os.environ.get("JJ_REMOTE_MOCK_PPRINT_WIDTH")


class HistoryFormatter(ABC):
    @abstractmethod
    def format_history(self, history: Optional[List[HistoryItem]]
                       ) -> Union[List[str], Optional[List[HistoryItem]]]:
        pass


class SimpleHistoryFormatter(HistoryFormatter):
    def __init__(self) -> None:
        self.history_output_width = None

    def format_history(self, history: Optional[List[HistoryItem]]) -> Optional[List[HistoryItem]]:
        return history


class PrettyHistoryFormatter(HistoryFormatter):
    def __init__(self, history_output_limit: Optional[int] = None,
                 history_output_width: Optional[int] = None) -> None:
        if not history_output_limit:
            history_output_limit = int(REMOTE_MOCK_PPRINT_LIMIT) if REMOTE_MOCK_PPRINT_LIMIT \
                else 1000000
        if not history_output_width:
            history_output_width = int(REMOTE_MOCK_PPRINT_WIDTH) if REMOTE_MOCK_PPRINT_WIDTH \
                else shutil.get_terminal_size((80, 20))[0]
        self._history_output_limit = history_output_limit
        self.history_output_width = history_output_width

    def __cut_str__(self, string: str, length: int, separator: str = "..") -> str:
        assert length > len(separator)
        if len(string) <= length:
            return string
        length -= len(separator)
        return string[:length // 2] + separator + string[-length // 2:]

    def format_history(self, history: Optional[List[HistoryItem]]) -> List[str]:
        parsed_history = [{"req": x["request"].to_dict(),
                           "res": x["response"].to_dict()} for x in history] if history else []
        history_as_strings = [self.__cut_str__(string=json.dumps(x, default=str),
                                               length=self._history_output_limit)
                              for x in parsed_history]
        formatted_history = [pf(x, width=self.history_output_width) for x in history_as_strings]
        return formatted_history


default_history_formatter = PrettyHistoryFormatter()
