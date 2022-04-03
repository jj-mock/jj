from ..requests import Request

__all__ = ("ExpirationPolicy",)


class ExpirationPolicy:
    async def is_expired(self, request: Request) -> bool:
        await request.post()
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"
