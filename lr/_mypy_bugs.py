import sys
from types import ModuleType


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
