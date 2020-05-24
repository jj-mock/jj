from aiohttp.web import ContentCoding

from jj._version import server_version
from jj.responses import Response

from .._test_utils.steps import given, then, when


def test_unpack_binary():
    with given:
        packed = {
            "status": 201,
            "reason": None,
            "headers": [["Server", server_version]],
            "cookies": [],
            "body": b"201 Created",
            "chunked": False,
            "compression": None,
        }

    with when:
        response = Response.__unpacked__(**packed)

    with then:
        assert response.__packed__() == {**packed, "reason": "Created"}


def test_unpack_text():
    with given:
        body = b"202 Accepted"
        packed = {
            "status": 202,
            "reason": "Accepted",
            "headers": [
                ["Server", server_version],
                ["Content-Length", str(len(body))],
                ["Content-Type", "text/plain; charset=utf-8"],
            ],
            "cookies": [],
            "body": body,
            "chunked": False,
            "compression": None,
        }

    with when:
        response = Response.__unpacked__(**packed)

    with then:
        assert response.__packed__() == packed


def test_unpack_no_body():
    with given:
        packed = {
            "status": 200,
            "reason": "OK",
            "headers": [
                ["Server", server_version],
                ["Content-Length", "0"],
                ["Content-Type", "text/plain; charset=utf-8"],
            ],
            "cookies": [],
            "body": b"",
            "chunked": False,
            "compression": None,
        }

    with when:
        response = Response.__unpacked__(**packed)

    with then:
        assert response.__packed__() == {**packed}


def test_unpack_cookies():
    with given:
        packed = {
            "status": 200,
            "reason": "OK",
            "headers": [["Server", server_version]],
            "cookies": [
                {
                    "name": "name1",
                    "value": "value1",
                    "expires": "Thu, 01 Jan 1970 00:00:01 GMT",
                    "domain": ".localhost",
                    "max_age": "0",
                    "path": "/path",
                    "secure": "secure",
                    "httponly": "httponly",
                    "version": "1",
                },
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
                },
            ],
            "body": b"200 OK",
            "chunked": False,
            "compression": None,
        }

    with when:
        response = Response.__unpacked__(**packed)

    with then:
        assert response.__packed__() == packed


def test_unpack_chunked():
    with given:
        packed = {
            "status": 200,
            "reason": "OK",
            "headers": [
                ["Server", server_version],
                ["X-Correlation-ID", "1234"],
            ],
            "cookies": [],
            "body": b"200 OK",
            "chunked": True,
            "compression": None,
        }

    with when:
        response = Response.__unpacked__(**packed)

    with then:
        assert response.__packed__() == packed


def test_unpack_compressed():
    with given:
        packed = {
            "status": 200,
            "reason": "OK",
            "headers": [["Server", server_version]],
            "cookies": [],
            "body": b"200 OK",
            "chunked": False,
            "compression": ContentCoding.gzip,
        }

    with when:
        response = Response.__unpacked__(**packed)

    with then:
        assert response.__packed__() == {**packed, "compression": ContentCoding.gzip.value}


def test_unpack_text_body_with_headers():
    with given:
        body = b"200 OK"
        packed = {
            "status": 200,
            "reason": "Accepted",
            "headers": [
                ["X-Custom-Header1", "Value1"],
                ["X-Custom-Header2", "Value2"],
                ["Server", server_version],
                ["Content-Length", str(len(body))],
                ["Content-Type", "text/plain; charset=utf-8"],
            ],
            "cookies": [],
            "body": body,
            "chunked": False,
            "compression": None,
        }

    with when:
        response = Response.__unpacked__(**packed)

    with then:
        assert response.__packed__() == packed
