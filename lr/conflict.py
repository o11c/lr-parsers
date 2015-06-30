import typing

from typing import (
        Dict,
        Generic,
        List,
        Tuple,
        TypeVar,
)


K = TypeVar('K')
V = TypeVar('V')


class ConflictMap(Generic[K, V]):
    __slots__ = ('_keys', '_data', '_default')

    def __init__(self, keys: List[K]) -> None:
        self._keys = keys
        self._data = {}      # type: Dict[K, List[V]]
        self._default = [] # type: List[V]

    def add(self, k: K, v: V) -> None:
        assert k in self._keys
        self._data.setdefault(k, []).append(v)

    def add_default(self, v: V) -> None:
        self._default.append(v)

    def finish(self) -> Tuple[Dict[K, V], Dict[K, List[V]]]:
        rv_good = {} # type: Dict[K, V]
        rv_bad = {} # type: Dict[K, List[V]]

        for k in self._keys:
            v = self._data.get(k) or self._default
            if len(v) == 0:
                continue
            if len(v) == 1:
                rv_good[k] = v[0]
            else:
                rv_bad[k] = v
        return rv_good, rv_bad
