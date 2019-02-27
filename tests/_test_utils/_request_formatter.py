from io import SEEK_END

from aiohttp.web_request import FileField


class RequestFormatter:
    def __init__(self, request):
        self._request = request

    def format_params(self, params):
        return {key: params.getall(key) for key in params}

    def format_headers(self, headers):
        return {key: headers.getall(key) for key in headers}

    def format_data(self, data):
        return {key: data.getall(key) for key in data}

    def format_file(self, file_field):
        file_field.file.seek(0, SEEK_END)
        size = file_field.file.tell()
        file_field.file.close()
        return {
            "name": file_field.filename,
            "size": str(size),
            "type": file_field.content_type,
        }

    def format_form(self, form):
        payload = {}
        for key in form:
            payload[key] = []
            for val in form.getall(key):
                payload[key] += [self.format_file(val) if isinstance(val, FileField) else val]
        return payload

    def format_raw(self, raw):
        try:
            return raw.decode()
        except UnicodeDecodeError:
            return "<binary>"

    async def format(self):
        data = await self._request.post()
        raw = await self._request.read()
        return {
            "method": self._request.method,
            "path": self._request.path,
            "params": self.format_params(self._request.query),
            "headers": self.format_headers(self._request.headers),
            "data": self.format_data(data) if len(data) > 0 and len(raw) > 0 else None,
            "form": self.format_form(data) if len(data) > 0 and len(raw) == 0 else None,
            "raw": self.format_raw(raw),
        }
