# jj

[![License](https://img.shields.io/github/license/nikitanovosibirsk/jj.svg)](https://github.com/nikitanovosibirsk/jj)
[![Drone](https://cloud.drone.io/api/badges/nikitanovosibirsk/jj/status.svg)](https://cloud.drone.io/nikitanovosibirsk/jj)
[![Codecov](https://img.shields.io/codecov/c/github/nikitanovosibirsk/jj/master.svg)](https://codecov.io/gh/nikitanovosibirsk/jj)
[![PyPI](https://img.shields.io/pypi/v/jj/2.0.0-dev.3.svg)](https://pypi.python.org/pypi/jj/2.0.0-dev.3)
[![Python Version](https://img.shields.io/pypi/pyversions/jj/2.0.0-dev.3.svg)](https://pypi.python.org/pypi/jj/2.0.0-dev.3)

## Installation

```bash
pip3 install jj==2.0.0-dev.3
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

* [Matchers](#matchers)
    * [Method](#method)
    * [Path](#path)
    * [Segments](#segments)
    * [Params](#params)
    * [Headers](#headers)
    * [Combining Matchers](#combining-matchers)
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
    * [TunnelResponse](#tunnelresponse-β)
* [Apps](#apps)
    * [Single App](#single-app)
    * [Multiple Apps](#multiple-apps)
    * [App Inheritance](#app-inheritance)
* [Middlewares](#middlewares)
    * [Handler Middleware](#handler-middleware)
    * [App Middleware](#app-middleware)

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

#### TunnelResponse `β`

```python
@jj.match("*")
async def handler(request):
    return jj.TunnelResponse(target="https://httpbin.org/")
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

private = @ReusableMiddleware("<SECRET_KEY>")

@private
class App(jj.App):
    @jj.match("*")
    async def handler(self, request: jj.Request) -> jj.Response:
        return jj.Response(status=OK, body="Ok")

jj.serve(App())
```
