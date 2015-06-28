import sys
from types import ModuleType


class AutoRepr:
    __slots__ = ()

    def __repr__(self):
        slots = []                                                          # pragma: no cover
        for cls in self.__class__.mro()[:-1]:                               # pragma: no cover
            slots.extend(cls.__slots__)                                     # pragma: no cover
        name = self.__class__.__name__                                      # pragma: no cover
        members = ', '.join('%s=%r' % (x, getattr(self, x)) for x in slots) # pragma: no cover
        return '<%s(%s)>' % (name, members)                                 # pragma: no cover


as_tuple = tuple

def identity(obj): return obj

def module_decorator(cls):
    outer_mod = cls.__module__
    name = '%s.%s' % (outer_mod, cls.__qualname__)
    assert name not in sys.modules
    rv = sys.modules[name] = ModuleType(name, cls.__doc__)
    rv.__file__ = sys.modules[outer_mod].__file__
    for k, v in cls.__dict__.items():
        if k.startswith('_'):
            continue
        setattr(rv, k, v)
    return rv
