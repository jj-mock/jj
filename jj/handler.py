import requests
import time
import socket
from urllib.parse import urlsplit
from werkzeug.wrappers import Response
from requests_toolbelt import MultipartEncoder


class Handler:

    def __init__(self, status, body, json, headers, latency, target, abort):
        self._status = status
        self._body = body
        self._headers = headers
        if json is not None:
            self._body = json
            self._headers = self._headers or {}
            self._headers.update({'Content-Type': 'application/json'})
        self._latency = latency
        self._target = target
        self._abort = abort

    def status(self, default=200):
        return int(self._status) if (self._status is not None) else default

    def body(self, default=None):
        return self._body if (self._body is not None) else default

    def headers(self, default=None):
        headers = default if (default is not None) else {}
        if self._headers is not None:
            headers.update(self._headers)
        return headers

    def latency(self, default=0):
        return float(self._latency) if (self._latency is not None) else default

    def target(self):
        if (self._target is not None) and (self._target[-1] == '/'):
            return self._target[:-1]
        return self._target

    def abort(self):
        return bool(self._abort) if (self._abort is not None) else False

    def _prepare_request(self, request):
        url = self.target() + request.path
        if urlsplit(url).scheme == '':
            url = 'http://' + url

        params = dict(request.args.items())

        headers = dict(request.headers.items())
        if headers.get('Content-Length', None) == '':
            headers.pop('Content-Length', None)

        headers['Host'] = urlsplit(url).netloc

        data = dict(request.form.items())
        if request.headers.get('Content-Type', '').lower().startswith('multipart/form-data'):
            data = MultipartEncoder(data)
            headers['Content-Type'] = data.content_type

        return request.method, url, params, headers, data

    def _prepare_response(self, response):
        headers = dict(response.headers)
        # https://github.com/mitsuhiko/flask/issues/367
        headers.pop('Transfer-Encoding', None)
        return response.content, response.status_code, headers

    def __call__(self, request):
        if self.latency() != 0:
            time.sleep(self.latency())
        if self.abort() is True:
            raise socket.error
        if self.target() is None:
            return Response(self.body(), self.status(), self.headers())
        method, url, params, headers, data = self._prepare_request(request)
        response = requests.request(method, url, params=params, headers=headers, data=data)
        body, status, headers = self._prepare_response(response)
        return Response(self.body(body), self.status(status), self.headers(headers))
