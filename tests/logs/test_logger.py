import logging

import pytest

from jj.logs import Logger

from .._test_utils.steps import given, then, when


@pytest.fixture()
def logger():
    return Logger(__name__)


def test_no_default_handlers(logger: Logger):
    with when:
        assert len(logger.handlers) == 0


def test_add_handler(logger: Logger):
    with given:
        handler = logging.NullHandler()

    with when:
        logger.addHandler(handler)

    with then:
        assert len(logger.handlers) == 1


def test_clear_handlers(logger: Logger):
    with given:
        handler = logging.NullHandler()
        logger.addHandler(handler)

    with when:
        res = logger.clearHandlers()

    with then:
        assert res == logger
        assert len(logger.handlers) == 0
