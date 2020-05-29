from io import BufferedReader, BytesIO, StringIO, TextIOWrapper

import pytest
from aiohttp.web import ContentCoding
from pytest import raises

from jj._version import server_version
from jj.responses import Response

from .._test_utils.steps import given, then, when


def default_packed(headers, status=200, reason="OK", body=b"",
                   cookies=None, chunked=False, compression=None):
    return {
        "status": status,
        "reason": reason,
        "body": body,
        "cookies": cookies or [],
        "headers": headers,
        "chunked": chunked,
        "compression": compression,
    }


def test_pack_text_body():
    with given:
        text = "200 OK"
        binary_text = b"200 OK"
        response = Response(text=text)

    with when:
        actual = response.__packed__()

    with then:
        assert actual == default_packed(body=binary_text, headers=[
            ["Content-Type", "text/plain; charset=utf-8"],
            ["Server", server_version],
        ])


def test_pack_json_body():
    with given:
        json = {}
        binary_json = b"{}"
        response = Response(json=json)

    with when:
        actual = response.__packed__()

    with then:
        assert actual == default_packed(body=binary_json, headers=[
            ["Content-Type", "application/json"],
            ["Server", server_version],
            ["Content-Length", str(len(binary_json))],
        ])


@pytest.mark.parametrize(("body", "expected", "headers"), [
    (None, b"", [
        ["Server", server_version],
        ["Content-Length", "0"],
        ["Content-Type", "text/plain; charset=utf-8"],
    ]),
    (b"text", b"text", [
        ["Server", server_version],
    ]),
    (bytearray(b"text"), b"text", [
        ["Server", server_version],
    ]),
    (memoryview(b"text"), b"text", [
        ["Server", server_version],
        ["Content-Length", "4"],
        ["Content-Type", "application/octet-stream"],
    ]),
    ("text", b"text", [
        ["Server", server_version],
        ["Content-Length", "4"],
        ["Content-Type", "text/plain; charset=utf-8"],
    ]),
    (StringIO("text"), b"text", [
        ["Content-Disposition", "inline"],
        ["Server", server_version],
        ["Content-Length", "4"],
        ["Content-Type", "text/plain; charset=utf-8"],
    ]),
    (BytesIO(b"text"), b"text", [
        ["Content-Disposition", "inline"],
        ["Server", server_version],
        ["Content-Length", "4"],
        ["Content-Type", "application/octet-stream"],
    ]),
    (TextIOWrapper(BytesIO(b"text")), b"text", [
        ["Content-Disposition", "inline"],
        ["Server", server_version],
        ["Content-Type", "text/plain; charset=utf-8"],
    ]),
    (BufferedReader(BytesIO(b"text")), b"text", [
        ["Content-Disposition", "inline"],
        ["Server", server_version],
        ["Content-Type", "application/octet-stream"],
    ]),
])
def test_pack_body(body, expected, headers):
    with given:
        response = Response(body=body)

    with when:
        actual = response.__packed__()

    with then:
        assert actual == default_packed(body=expected, headers=headers)


def test_pack_unsupported_body():
    with given:
        class AsyncIterable:
            def __aiter__(self):
                return self

            async def __anext__(self):
                raise StopAsyncIteration

        response = Response(body=AsyncIterable())

    with when, raises(Exception) as exception:
        response.__packed__()

    with then:
        assert exception.type is ValueError


def test_pack_chunked():
    with given:
        body = b"200 OK"
        response = Response(body=body)
        response.enable_chunked_encoding()

    with when:
        actual = response.__packed__()

    with then:
        assert actual == default_packed(body=body, chunked=True, headers=[
            ["Server", server_version],
        ])


def test_pack_compressed():
    with given:
        body = b"200 OK"
        response = Response(body=body)
        response.enable_compression(ContentCoding.gzip)

    with when:
        actual = response.__packed__()

    with then:
        assert actual == default_packed(body=body, compression=ContentCoding.gzip.value, headers=[
            ["Server", server_version],
        ])


def test_pack_cookies():
    with given:
        body = b"200 OK"
        response = Response(body=body)
        cookie = {
            "name": "name1",
            "value": "value1",
            "expires": "Thu, 01 Jan 1970 00:00:01 GMT",
            "domain": ".localhost",
            "max_age": "0",
            "path": "/path",
            "secure": "secure",
            "httponly": "httponly",
            "version": "1",
        }
        response.set_cookie(**cookie)
        response.set_cookie("name2", "value2")

    with when:
        actual = response.__packed__()

    with then:
        assert actual == default_packed(body=body, headers=[["Server", server_version]], cookies=[
            cookie,
            {
                "name": "name2",
                "value": "value2",
                "expires": None,
                "domain": None,
                "max_age": None,
                "path": "/",
                "secure": None,
                "httponly": None,
                "version": None,
            }
        ])


def test_pack_text_body_with_headers():
    with given:
        text = "200 OK"
        binary_text = b"200 OK"
        response = Response(text=text, headers=[
            ("X-Custom-Header1", "Value1"),
            ("X-Custom-Header2", "Value2"),
        ])

    with when:
        actual = response.__packed__()

    with then:
        assert actual == default_packed(body=binary_text, headers=[
            ["X-Custom-Header1", "Value1"],
            ["X-Custom-Header2", "Value2"],
            ["Content-Type", "text/plain; charset=utf-8"],
            ["Server", server_version],
        ])
