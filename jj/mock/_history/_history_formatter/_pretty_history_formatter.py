from os import linesep
from pprint import pformat
from shutil import get_terminal_size
from typing import List, Optional

from .._history_item import HistoryItem
from ._history_formatter import HistoryFormatter

__all__ = ("PrettyHistoryFormatter",)


class PrettyHistoryFormatter(HistoryFormatter):
    def __init__(self, width: Optional[int] = None, length: Optional[int] = None) -> None:
        self._width = width if width else self._get_terminal_width()
        self._length = length

    def _get_terminal_width(self) -> int:
        columns, _ = get_terminal_size()
        return columns

    def _cut_str(self, string: str, length: int, separator: str = "...") -> str:
        assert length > len(separator)
        if len(string) <= length:
            return string
        length -= len(separator)
        return string[:length // 2] + separator + string[-length // 2:]

    def format_history(self, history: List[HistoryItem]) -> str:
        result = []
        for index, history_item in enumerate(history):
            formatted = pformat(
                {
                    "index": index,
                    "request": history_item["request"].to_dict(),
                    "response": history_item["response"].to_dict(),
                    # "tags": history_item["tags"],
                },
                width=self._width
            )
            if self._length:
                formatted = self._cut_str(formatted, self._length)
            result.append(formatted)
        if len(result) == 0:
            return "[]"
        return f"[{linesep}" + f",{linesep}".join(result) + f"{linesep}]"
