__all__ = ("ExpirationPolicy",)


class ExpirationPolicy:
    def is_expired(self) -> bool:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"
