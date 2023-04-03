from typing import Callable, List, Union

from ._history_item import HistoryItem

__all__ = ("default_history_repr", "HistoryType", "HistoryReprType",)

HistoryType = Union[List[HistoryItem], None]
HistoryReprType = Callable[[HistoryType], str]


class HistoryRepr:
    def __init__(self,
                 pretty_print: bool = None,
                 history_output_limit: int = None,
                 history_output_width: int = None) -> None:

        if pretty_print is None:
            pretty_print = bool(strtobool(REMOTE_MOCK_PPRINT))
        if history_output_limit is None:
            history_output_limit = int(REMOTE_MOCK_PPRINT_LIMIT)
        if history_output_width is None:
            history_output_width = REMOTE_MOCK_PPRINT_WIDTH

        self._pretty_print = pretty_print
        self._history_output_limit = history_output_limit
        self._history_output_width = history_output_width


default_history_repr = HistoryRepr()
