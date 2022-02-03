# jj


[![Codecov](https://img.shields.io/codecov/c/github/nikitanovosibirsk/jj/master.svg?style=flat-square)](https://codecov.io/gh/nikitanovosibirsk/jj)
[![PyPI](https://img.shields.io/pypi/v/jj.svg?style=flat-square)](https://pypi.python.org/pypi/jj)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/jj?style=flat-square)](https://pypi.python.org/pypi/jj)
[![Python Version](https://img.shields.io/pypi/pyversions/jj.svg?style=flat-square)](https://pypi.python.org/pypi/jj)

## Installation

```bash
pip3 install jj
```

## Usage

```python
import jj

@jj.match("*")
async def handler(request: jj.Request) -> jj.Response:
    return jj.Response(body="200 OK")

jj.serve()
```

## Documentation

* [Documentation](#documentation)
  * [Matchers](#matchers)
    * [Method](#method)
      * [match_method(`method`)](#match_methodmethod)
      * [match_methods(`methods`)](#match_methodsmethods)
    * [Path](#path)
      * [match_path(`path`)](#match_pathpath)
    * [Segments](#segments)
    * [Params](#params)
      * [match_param(`name`, `val`)](#match_paramname-val)
      * [match_params(`params`)](#match_paramsparams)
    * [Headers](#headers)
      * [match_header(`name`, `val`)](#match_headername-val)
      * [match_headers(`headers`)](#match_headersheaders)
    * [Combining Matchers](#combining-matchers)
      * [match_any(`matchers`)](#match_anymatchers)
      * [match_all(`matchers`)](#match_allmatchers)
      * [match(`method`, `path`, `params`, `headers`)](#matchmethod-path-params-headers)
  * [Responses](#responses)
    * [Response](#response)
      * [JSON Response](#json-response)
      * [HTML Response](#html-response)
      * [Binary Response](#binary-response)
      * [Not Found Response](#not-found-response)
      * [Predefined Body](#predefined-body)
    * [StaticResponse](#staticresponse)
      * [Inline Content](#inline-content)
      * [Downloadable File](#downloadable-file)
    * [RelayResponse `β`](#relayresponse-β)
  * [Apps](#apps)
    * [Single App](#single-app)
    * [Multiple Apps](#multiple-apps)
    * [App Inheritance](#app-inheritance)
  * [Middlewares](#middlewares)
    * [Handler Middleware](#handler-middleware)
    * [App Middleware](#app-middleware)
  * [Remote Mock](#remote-mock)
    * [Server Side](#server-side)
      * [Start Remote Mock](#start-remote-mock)
    * [Client Side](#client-side)
      * [Low Level API](#low-level-api)
        * [Register Remote Handler](#register-remote-handler)
        * [Deregister Remote Handler](#deregister-remote-handler)
        * [Retrieve Remote Handler History](#retrieve-remote-handler-history)
    * [Custom Logger](#custom-logger)

---

### Matchers

#### Method

##### match_method(`method`)

```python
from jj.http.methods import ANY, GET, POST

@jj.match_method(GET)
async def handler(request):
    return jj.Response(body="Method: " + request.method)
```

##### match_methods(`methods`)

```python
from jj.http.methods import PUT, PATCH

@jj.match_methods(PUT, PATCH)
async def handler(request):
    return jj.Response(body="Method: " + request.method)
```

#### Path

##### match_path(`path`)

```python
@jj.match_path("/users")
async def handler(request):
    return jj.Response(body="Path: " + request.path)
```

#### Segments

```python
@jj.match_path("/users/{users_id}")
async def handler(request):
    return jj.Response(body=f"Segments: {request.segments}")
```

More information available here https://docs.aiohttp.org/en/stable/web_quickstart.html#variable-resources

#### Params

##### match_param(`name`, `val`)

```python
@jj.match_param("locale", "en_US")
async def handler(request):
    locales = request.params.getall('locale')
    return jj.Response(body="Locales: " + ",".join(locales))
```

##### match_params(`params`)

```python
@jj.match_params({"locale": "en_US", "timezone": "UTC"})
async def handler(request):
    # Literal String Interpolation (PEP 498)
    return jj.Response(body=f"Params: {request.params}")
```

#### Headers

#####  match_header(`name`, `val`)

```python
@jj.match_header("X-Forwarded-Proto", "https")
async def handler(request):
    proto = request.headers.getone("X-Forwarded-Proto")
    return jj.Response(body="Proto: " + proto)
```

##### match_headers(`headers`)

```python
@jj.match_headers({
    "x-user-id": "1432",
    "x-client-id": "iphone",
})
async def handler(request):
    return jj.Response(body=f"Headers: {request.headers}")
```

#### Combining Matchers

##### match_any(`matchers`)

```python
from jj.http import PATCH, PUT

@jj.match_any([
    jj.match_method(PUT),
    jj.match_method(PATCH),
])
async def handler(request):
    return jj.Response(body="200 OK")
```

##### match_all(`matchers`)

```python
@jj.match_all([
    jj.match_method("*"),
    jj.match_path("/"),
    jj.match_params({"locale": "en_US"}),
    jj.match_headers({"x-request-id": "0fefbf48"}),
])
async def handler(request):
    return jj.Response(body="200 OK")
```

##### match(`method`, `path`, `params`, `headers`)

```python
@jj.match("*", "/", {"locale": "en_US"}, {"x-request-id": "0fefbf48"})
async def handler(request):
    return jj.Response(body="200 OK")
```

---

### Responses

#### Response

##### JSON Response

```python
@jj.match("*")
async def handler(request):
    return jj.Response(json={"message": "200 OK"})
```

##### HTML Response

```python
@jj.match("*")
async def handler(request):
    return jj.Response(body="<p>text<p>", headers={"Content-Type": "text/html"})
```

##### Binary Response

```python
@jj.match("*")
async def handler(request):
    return jj.Response(body=b"<binary>")
```

##### Not Found Response

```python
@jj.match("*")
async def handler(request):
    return jj.Response(status=404, reason="Not Found")
```

##### Predefined Body

```python
from jj.http import GET

@jj.match(GET, "/users")
async def handler(request):
    return jj.Response(body=open("responses/users.json", "rb"))
```

```python
from jj.http import POST, CREATED

@jj.match(POST, "/users")
async def handler(request):
    return jj.Response(body=open("responses/created.json", "rb"), status=CREATED)
```

#### StaticResponse

##### Inline Content

```python
from jj.http import GET

@jj.match(GET, "/image")
async def handler(request):
    return jj.StaticResponse("public/image.jpg")
```

##### Downloadable File

```python
from jj.http import GET

@jj.match(GET, "/report")
async def handler(request):
    return jj.StaticResponse("public/report.csv", attachment=True)
```

```python
from jj.http import GET

@jj.match(GET, "/")
async def handler(request):
    return jj.StaticResponse("public/report.csv", attachment="report.csv")
```

For more information visit https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition

#### RelayResponse `β`

```python
@jj.match("*")
async def handler(request):
    return jj.RelayResponse(target="https://httpbin.org/")
```

---

### Apps

#### Single App

```python
import jj
from jj.http.methods import GET, ANY
from jj.http.codes import OK, NOT_FOUND

class App(jj.App):
    @jj.match(GET, "/")
    async def root_handler(self, request: jj.Request) -> jj.Response:
        return jj.Response(status=OK, json={"message": "200 OK"})

    @jj.match(ANY)
    async def default_handler(self, request: jj.Request) -> jj.Response:
        return jj.Response(status=NOT_FOUND, json={"message": "Not Found"})

jj.serve(App(), port=5000)
```

#### Multiple Apps

```python
import jj

class App(jj.App):
    @jj.match("*")
    async def handler(self, request: jj.Request) -> jj.Response:
        return jj.Response(body="App")

class AnotherApp(jj.App):
    @jj.match("*")
    async def handler(self, request: jj.Request) -> jj.Response:
        return jj.Response(body="AnotherApp")

jj.start(App(), port=5001)
jj.start(AnotherApp(), port=5002)

jj.wait_for([KeyboardInterrupt])
```

#### App Inheritance

```python
import jj

class UsersApp(jj.App):
    @jj.match("*", path="/users")
    async def handler(self, request: jj.Request) -> jj.Response:
        return jj.Response(body="Users")

class GroupsApp(jj.App):
    @jj.match("*", path="/groups")
    async def handler(self, request: jj.Request) -> jj.Response:
        return jj.Response(body="Groups")

class App(UsersApp, GroupsApp):
    pass

jj.serve(App())
```

### Middlewares

#### Handler Middleware

```python
import jj
from jj.http.codes import OK, FORBIDDEN

class Middleware(jj.Middleware):
    async def do(self, request, handler, app):
        if request.headers.get("x-secret-key") != "<SECRET_KEY>":
            return jj.Response(status=FORBIDDEN, body="Forbidden")
        return await handler(request)

class App(jj.App):
    @Middleware()
    @jj.match("*")
    async def handler(self, request: jj.Request) -> jj.Response:
        return jj.Response(status=OK, body="Ok")

jj.serve(App())
```

#### App Middleware

```python
import jj
from jj.http.codes import OK, FORBIDDEN

class ReusableMiddleware(jj.Middleware):
    def __init__(self, secret_key):
        super().__init__()
        self._secret_key = secret_key

    async def do(self, request, handler, app):
        if request.headers.get("x-secret-key") != self._secret_key:
            return jj.Response(status=FORBIDDEN, body="Forbidden")
        return await handler(request)

private = ReusableMiddleware("<SECRET_KEY>")

@private
class App(jj.App):
    @jj.match("*")
    async def handler(self, request: jj.Request) -> jj.Response:
        return jj.Response(status=OK, body="Ok")

jj.serve(App())
```

---

### Remote Mock

#### Server Side

##### Start Remote Mock

```python
import jj
from jj.mock import Mock

jj.serve(Mock(), port=8080)
```

or via docker
```shell
docker run -p 8080:80 nikitanovosibirsk/jj:0.1
```

#### Client Side

```python
import asyncio

import jj
from jj.mock import mocked


async def main():
    matcher = jj.match("GET", "/users")
    response = jj.Response(status=200, json=[])

    async with mocked(matcher, response) as mock:
        # Request GET /users
        # Returns status=200 body=[]
    assert len(mock.history) == 1

asyncio.run(main())
```

##### Low Level API

###### Register Remote Handler

```python
import asyncio

import jj
from jj.mock import RemoteMock


async def main():
    remote_mock = RemoteMock("http://localhost:8080")

    matcher = jj.match("GET", "/users")
    response = jj.Response(status=200, json=[])
    remote_handler = remote_mock.create_handler(matcher, response)
    await remote_handler.register()

    # Request GET /users
    # Returns status=200 body=[]

asyncio.run(main())
```

###### Deregister Remote Handler

```python
import asyncio

import jj
from jj.mock import RemoteMock


async def main():
    remote_mock = RemoteMock("http://localhost:8080")

    matcher = jj.match("GET", "/users")
    response = jj.Response(status=200, json=[])
    remote_handler = remote_mock.create_handler(matcher, response)
    await remote_handler.register()

    # Request GET /users
    # Returns status=200 body=[]

    await remote_handler.deregister()

asyncio.run(main())
```

###### Retrieve Remote Handler History

```python
import asyncio

import jj
from jj.mock import RemoteMock


async def main():
  remote_mock = RemoteMock("http://localhost:8080")

  matcher = jj.match("GET", "/users")
  response = jj.Response(status=200, json=[])
  remote_handler = remote_mock.create_handler(matcher, response)
  await remote_handler.register()

  # Request GET /users
  # Returns status=200 body=[]

  history = await remote_handler.fetch_history()
  print(history)

  await remote_handler.deregister()

asyncio.run(main())
```

History:

```python
[
    {
        'request': HistoryRequest(
            method='GET',
            path='/users',
            params=<MultiDictProxy()>,
            headers=<CIMultiDictProxy('Host': 'localhost:8080',
                                      'Accept': '*/*',
                                      'Accept-Encoding': 'gzip, deflate',
                                      'User-Agent': 'Python/3.8 aiohttp/3.7.3')>,
            body=b'',
        ),
        'response': HistoryResponse(
            status=200,
            reason='OK',
            headers=<CIMultiDictProxy('Content-Type': 'application/json',
                                      'Server': 'jj via aiohttp/3.7.3',
                                      'Content-Length': '2',
                                      'Date': 'Sun, 09 May 2021 08:08:19 GMT')>,
            body=b'[]',
        ),
        'tags': ['f75c2ab7-f68d-4b4a-85e0-1f38bb0abe9a']
    }
]
```

#### Custom Logger

```python
import logging

import jj
from jj.logs import SimpleFormatter
from jj.mock import Mock, SystemLogFilter


class Formatter(SimpleFormatter):
    def format_request(self, request: jj.Request, record: logging.LogRecord) -> str:
        return f"-> {request.method} {request.url.path_qs} {request.headers}"

    def format_response(self, response: jj.Response, request: jj.Request, record: logging.LogRecord) -> str:
        return f"<- {response.status} {response.reason} {response.body}"


handler = logging.StreamHandler()
handler.setFormatter(Formatter())

logger = logging.getLogger("custom_logger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addFilter(SystemLogFilter())

jj.serve(Mock(), logger=logger)
```
