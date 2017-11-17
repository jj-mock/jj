import re


class Rule:

    def __init__(self, method, route, params, headers, data):
        self._method = str(method).upper() if (method is not None) else 'ANY'
        self._route = str(route) if (route is not None) else '/'
        self._params = dict(params) if (params is not None) else {}
        self._headers = dict(headers) if (headers is not None) else {}
        self._data = dict(data) if (data is not None) else {}

    def __match_method(self, method):
        return self._method == 'ANY' or method.upper() == self._method

    def __match_route(self, route):
        pattern = re.sub(r'\{(\w+)\}', '\w+', self._route, flags=re.IGNORECASE)
        return bool(re.compile(pattern).match(route))

    def __match_params(self, params):
        for key, value in self._params.items():
            if key not in params or value != params[key]:
                return False
        return True

    def __match_headers(self, headers):
        for key, value in self._headers.items():
            if key not in headers or value != headers[key]:
                return False
        return True

    def __match_data(self, data):
        for key, value in self._data.items():
            if key not in data or value != data[key]:
                return False
        return True

    def match(self, request):
        return self.__match_method(request.method) and \
               self.__match_route(request.path) and \
               self.__match_params(request.args) and \
               self.__match_headers(request.headers) and \
               self.__match_data(eval(request.data))
