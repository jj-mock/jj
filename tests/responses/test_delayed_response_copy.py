import pytest
from aiohttp.web import ContentCoding

from jj.responses import DelayedResponse

from .._test_utils.steps import given, then, when


def eq(r1: DelayedResponse, r2: DelayedResponse) -> None:
    assert r1.status == r2.status
    assert r1.reason == r2.reason
    assert r1.body == r2.body
    assert r1.headers == r2.headers
    assert r1.cookies == r2.cookies
    assert r1.chunked == r2.chunked
    assert r1.compression == r2.compression
    assert r1.content_coding == r2.content_coding
    assert r1.delay == r2.delay


@pytest.mark.parametrize(("attr", "val"), [
    ("status", 204),
    ("reason", "not found"),
    ("body", b"text"),
    ("headers", [
        ("key", "1"),
        ("key", "2"),
        ("another_key", "3"),
    ]),
    ("delay", 1.0),
])
def test_response_attrs(attr, val):
    with given:
        response = DelayedResponse(**{attr: val})

    with when:
        copy = response.copy()

    with then:
        assert eq(copy, response) is None


def test_response_cookies():
    with given:
        response = DelayedResponse()
        response.set_cookie("name", "1")
        response.set_cookie("another_name", "2")

    with when:
        copy = response.copy()

    with then:
        assert eq(copy, response) is None


def test_response_chunked():
    with given:
        response = DelayedResponse(body=b"text")
        response.enable_chunked_encoding()

    with when:
        copy = response.copy()

    with then:
        assert eq(copy, response) is None


def test_response_compression():
    with given:
        response = DelayedResponse(body=b"text")
        response.enable_compression(ContentCoding.gzip)

    with when:
        copy = response.copy()

    with then:
        assert eq(copy, response) is None
