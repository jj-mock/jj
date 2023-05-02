import os
import shutil
from distutils.util import strtobool
from pprint import pformat as pf
from typing import List, Optional, Union

from ._history_item import HistoryItem

__all__ = ("default_history_repr", "HistoryType", "HistoryRepr",)

HistoryType = Union[List[HistoryItem], None]

REMOTE_MOCK_PPRINT = os.environ.get("JJ_REMOTE_MOCK_PPRINT", "True")
REMOTE_MOCK_PPRINT_LIMIT = os.environ.get("JJ_REMOTE_MOCK_PPRINT_LIMIT", 1000000)
REMOTE_MOCK_PPRINT_WIDTH = os.environ.get("JJ_REMOTE_MOCK_PPRINT_WIDTH")


class HistoryRepr:
    def __init__(self,
                 pretty_print: Optional[bool] = None,
                 history_output_limit: Optional[int] = None,
                 history_output_width: Optional[int] = None) -> None:

        if pretty_print is None:
            pretty_print = bool(strtobool(REMOTE_MOCK_PPRINT))
        if history_output_limit is None:
            history_output_limit = int(REMOTE_MOCK_PPRINT_LIMIT) \
                if REMOTE_MOCK_PPRINT_LIMIT else None
        if history_output_width is None:
            history_output_width = int(REMOTE_MOCK_PPRINT_WIDTH) \
                if REMOTE_MOCK_PPRINT_WIDTH else None

        self._pretty_print = pretty_print if pretty_print else True
        self._history_output_limit = history_output_limit \
            if history_output_limit else 1000000
        self._history_output_width = history_output_width if history_output_width \
            else shutil.get_terminal_size((80, 20))[0]

    def parse_history(self, history: Optional[List[HistoryItem]]) -> List[str]:
        parsed_history = [{"req": x["request"].to_dict(),
                           "res": x["response"].to_dict()} for x in history] if history else []

        def cut_str(string: str, length: int, separator: str = "..") -> str:
            assert length > len(separator)
            if len(string) <= length:
                return string
            length -= len(separator)
            return string[:length // 2] + separator + string[-length // 2:]

        if self._pretty_print:
            return [cut_str(string=pf(x, width=self._history_output_width),
                            length=self._history_output_limit) for x in parsed_history]
        else:
            return []


default_history_repr = HistoryRepr()
