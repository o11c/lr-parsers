from typing import (
        Iterable,
        Sequence,
        TypeVar,
)


T = TypeVar('T')


def as_tuple(x: Iterable[T]) -> Sequence[T]:
    pass

def identity(obj: T) -> T:
    pass

module_decorator = identity
