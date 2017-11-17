from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from .rule import Rule
from .handler import Handler


class Mock:

    def __init__(self):
        self._rules = []
        self.last_rule = None

    def __call__(self, environ, start_response):
        request = Request(environ)
        for rule, handler in reversed(self._rules):
            if rule.match(request):
                return handler(request)(environ, start_response)
        return Response(status=204)(environ, start_response)

    def when(self, method=None, route=None, params=None, headers=None, data=None):
        self.last_rule = Rule(method, route, params, headers, data)
        return self

    def then(self, status=None, body=None, json=None, headers=None, latency=None,
             target=None, abort=None, handler=None):
        if handler is None:
            handler = Handler(status, body, json, headers, latency, target, abort)
        self._rules += [(self.last_rule, handler)]
        return self

    def run(self, host='127.0.0.1', port=8080, debug=False):
        run_simple(host, int(port), self, use_reloader=debug, use_debugger=debug, threaded=True)
