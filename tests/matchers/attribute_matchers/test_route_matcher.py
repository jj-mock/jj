from unittest.mock import sentinel

from jj.matchers import AttributeMatcher
from jj.matchers.attribute_matchers import RouteMatcher

from ..._test_utils.steps import given, then, when


def test_is_instance_of_attribute_matcher():
    with given:
        matcher = RouteMatcher("/")

    with when:
        actual = isinstance(matcher, AttributeMatcher)

    with then:
        assert actual is True


def test_repr():
    with given:
        matcher = RouteMatcher("/")

    with when:
        actual = repr(matcher)

    with then:
        assert actual == "RouteMatcher('/')"


def test_pack():
    with given:
        path = "/"
        matcher = RouteMatcher(path)

    with when:
        actual = matcher.__packed__()

    with then:
        assert actual == {"path": path}


def test_unpack():
    with given:
        kwargs = {
            "path": "/",
            "future_field": sentinel,
        }

    with when:
        actual = RouteMatcher.__unpacked__(**kwargs)

    with then:
        assert isinstance(actual, RouteMatcher)
