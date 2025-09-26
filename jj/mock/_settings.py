import os
from typing import Union

__all__ = (
    "get_remote_mock_url",
    "get_remote_mock_disposable",
    "get_remote_mock_pprint",
    "get_remote_mock_pprint_length",
    "get_remote_mock_pprint_width",
)


def get_remote_mock_url() -> str:
    """
    Get the remote mock URL from environment variable.

    This method dynamically fetches the value from the environment,
    avoiding race conditions with load_dotenv().

    :return: The remote mock URL, defaults to "http://localhost:8080".
    """
    return os.environ.get("JJ_REMOTE_MOCK_URL", "http://localhost:8080")


def get_remote_mock_disposable() -> bool:
    """
    Get the remote mock disposable setting from environment variable.

    This method dynamically fetches the value from the environment,
    avoiding race conditions with load_dotenv().

    :return: `True` if disposable mode is enabled, defaults to `True`.
    """
    value = os.environ.get("JJ_REMOTE_MOCK_DISPOSABLE", "True")
    return value.lower() in ("true", "1", "yes", "on")


def get_remote_mock_pprint() -> bool:
    """
    Get the remote mock pretty print setting from environment variable.

    This method dynamically fetches the value from the environment,
    avoiding race conditions with load_dotenv().

    :return: `True` if pretty printing is enabled, defaults to `False`.
    """
    value = os.environ.get("JJ_REMOTE_MOCK_PPRINT", "False")
    return value.lower() in ("true", "1", "yes", "on")


def get_remote_mock_pprint_length() -> Union[int, None]:
    """
    Get the remote mock pretty print length from environment variable.

    This method dynamically fetches the value from the environment,
    avoiding race conditions with load_dotenv().

    :return: The pprint length limit, or `None` if not set or invalid.
    """
    value = os.environ.get("JJ_REMOTE_MOCK_PPRINT_LENGTH", "")
    if value:
        try:
            return int(value)
        except ValueError:
            return None
    return None


def get_remote_mock_pprint_width() -> Union[int, None]:
    """
    Get the remote mock pretty print width from environment variable.

    This method dynamically fetches the value from the environment,
    avoiding race conditions with load_dotenv().

    :return: The pprint width limit, or `None` if not set or invalid.
    """
    value = os.environ.get("JJ_REMOTE_MOCK_PPRINT_WIDTH", "")
    if value:
        try:
            return int(value)
        except ValueError:
            return None
    return None
