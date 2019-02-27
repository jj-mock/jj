# jj

[![License](https://img.shields.io/github/license/nikitanovosibirsk/jj.svg)](https://github.com/nikitanovosibirsk/jj)
[![Drone](https://cloud.drone.io/api/badges/nikitanovosibirsk/jj/status.svg)](https://cloud.drone.io/nikitanovosibirsk/jj)
[![Codecov](https://img.shields.io/codecov/c/github/nikitanovosibirsk/jj/master.svg)](https://codecov.io/gh/nikitanovosibirsk/jj)
[![PyPI](https://img.shields.io/pypi/v/jj/2.0.0.dev1.svg)](https://pypi.python.org/pypi/jj/2.0.0.dev1)
[![Python Version](https://img.shields.io/pypi/pyversions/jj/2.0.0.dev1.svg)](https://pypi.python.org/pypi/jj/2.0.0.dev1)

## Installation

```bash
pip3 install jj==2.0.0-dev.1
```

## Usage

```python3
import jj

@jj.match("*")
async def handler(request: jj.Request) -> jj.Response:
    return jj.Response(body="200 OK")

jj.serve(port=8080)
```

### App

```python3
import jj

class App(jj.App):
    @jj.match("*")
    async def handler(request: jj.Request) -> jj.Response:
        return jj.Response(body="200 OK")

jj.serve(App(), port=8080)
```
