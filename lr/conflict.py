class ConflictMap:
    __slots__ = ('_keys', '_data', '_default')

    def __init__(self, keys):
        self._keys = keys
        self._data = {}
        self._default = []

    def add(self, k, v):
        assert k in self._keys
        self._data.setdefault(k, []).append(v)

    def add_default(self, v):
        self._default.append(v)

    def finish(self):
        rv_good = {}
        rv_bad = {}

        for k in self._keys:
            v = self._data.get(k) or self._default
            if len(v) == 0:
                continue
            if len(v) == 1:
                rv_good[k] = v[0]
            else:
                rv_bad[k] = v
        return rv_good, rv_bad
