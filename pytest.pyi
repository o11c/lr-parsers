import typing

from typing import (
        TypeVar,
)


class ContextManager:
    def __enter__(self) -> ContextManager:
        pass
    def __exit__(self, type: object, value: object, traceback: object) -> None:
        pass

def raises(cls: object) -> ContextManager:
    pass

T = TypeVar('T')

class mark:
    @staticmethod
    def xfail(f: T) -> T:
        pass
