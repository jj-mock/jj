from aiohttp import web


__all__ = ("Request",)


class Request(web.Request):
    @property
    def params(self):
        return self.query
