from ..requests import Request

__all__ = ("ExpirationPolicy",)


class ExpirationPolicy:
    def is_expired(self, request: Request) -> bool:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"
