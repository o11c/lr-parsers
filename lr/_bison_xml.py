import lxml.etree as etree


def xml_identity(obj): return obj


class AutoRepr:
    __slots__ = ()

    def __repr__(self):
        slots = []                                                          # pragma: no cover
        for cls in self.__class__.mro()[:-1]:                               # pragma: no cover
            slots.extend(cls.__slots__)                                     # pragma: no cover
        name = self.__class__.__name__                                      # pragma: no cover
        members = ', '.join('%s=%r' % (x, getattr(self, x)) for x in slots) # pragma: no cover
        return '<%s(%s)>' % (name, members)                                 # pragma: no cover


# TODO Finish coverage by feeding known-bad grammars.
# TODO Use `enum` for assoc and usefulness.


def attr(xml, name, cls):
    return cls(xml.attrib[name])

def opt_attr(xml, name, cls):
    attr = xml.attrib.get(name)
    if attr is None:
        return None
    return cls(attr) # pragma: no cover

def child(xml, name, cls):
    rv = children(xml, name, cls)
    assert len(rv) == 1
    return rv[0]

def opt_child(xml, name, cls):
    rv = children(xml, name, cls)
    if not rv:
        return None
    assert len(rv) == 1
    return rv[0]

def children(xml, name, cls):
    return [cls(c) for c in xml.iterchildren(name)]
# There is no need for opt_children; it DTRT when there is nothing.

def inner_children(xml, name1, name2, cls):
    xml_tmp = child(xml, name1, xml_identity)
    return children(xml_tmp, name2, cls)

def opt_inner_children(xml, name1, name2, cls):
    xml_tmp = opt_child(xml, name1, xml_identity)
    if xml_tmp is None:
        return []
    return children(xml_tmp, name2, cls)

def root(xml, cls):
    return cls(xml.getroot())


def String(xml):
    return xml.text

class BisonXmlReport(AutoRepr):
    __slots__ = ('version', 'bug_report', 'url', 'filename', 'grammar', 'automaton')

    def __init__(self, xml):
        self.version = attr(xml, 'version', str)
        self.bug_report = attr(xml, 'bug-report', str)
        self.url = attr(xml, 'url', str)
        self.filename = child(xml, 'filename', String)
        self.grammar = child(xml, 'grammar', Grammar)
        self.automaton = inner_children(xml, 'automaton', 'state', State)

class Grammar(AutoRepr):
    __slots__ = ('rules', 'terminals', 'nonterminals')

    def __init__(self, xml):
        self.rules = inner_children(xml, 'rules', 'rule', Rule)
        self.terminals = inner_children(xml, 'terminals', 'terminal', Terminal)
        self.nonterminals = inner_children(xml, 'nonterminals', 'nonterminal', Nonterminal)

class Rule(AutoRepr):
    __slots__ = ('number', 'usefulness', 'lhs', 'rhs')

    def __init__(self, xml):
        self.number = attr(xml, 'number', int)
        self.usefulness = attr(xml, 'usefulness', str)
        self.lhs = child(xml, 'lhs', String)
        self.rhs = inner_children(xml, 'rhs', 'symbol', String)

class Terminal(AutoRepr):
    __slots__ = ('symbol_number', 'token_number', 'name', 'usefulness', 'prec', 'assoc')

    def __init__(self, xml):
        self.symbol_number = attr(xml, 'symbol-number', int)
        self.token_number = attr(xml, 'token-number', int)
        self.name = attr(xml, 'name', str)
        self.usefulness = attr(xml, 'usefulness', str)
        self.prec = opt_attr(xml, 'prec', int)
        self.assoc = opt_attr(xml, 'assoc', str)

class Nonterminal(AutoRepr):
    __slots__ = ('symbol_number', 'name', 'usefulness')

    def __init__(self, xml):
        self.symbol_number = attr(xml, 'symbol-number', int)
        self.name = attr(xml, 'name', str)
        self.usefulness = attr(xml, 'usefulness', str)

class State(AutoRepr):
    __slots__ = ('number', 'itemset', 'actions', 'solved_conflicts')

    def __init__(self, xml):
        self.number = attr(xml, 'number', int)
        self.itemset = inner_children(xml, 'itemset', 'item', Item)
        self.actions = child(xml, 'actions', Actions)
        self.solved_conflicts = inner_children(xml, 'solved-conflicts', 'resolution', GetResolution)

class Item(AutoRepr):
    __slots__ = ('rule', 'point', 'lookaheads')

    def __init__(self, xml):
        self.rule = attr(xml, 'rule-number', int)
        self.point = attr(xml, 'point', int)
        self.lookaheads = opt_inner_children(xml, 'lookaheads', 'symbol', String)

class Actions(AutoRepr):
    __slots__ = ('transitions', 'errors', 'reductions')

    def __init__(self, xml):
        self.transitions = inner_children(xml, 'transitions', 'transition', GetTransition)
        self.errors = inner_children(xml, 'errors', 'error', Error)
        self.reductions = inner_children(xml, 'reductions', 'reduction', Reduction)

class TransitionBase(AutoRepr):
    __slots__ = ('symbol', 'state')

    def __init__(self, xml):
        self.symbol = attr(xml, 'symbol', str)
        self.state = attr(xml, 'state', int)

class GotoTransition(TransitionBase):
    __slots__ = ()

    type = 'goto'

class ShiftTransition(TransitionBase):
    __slots__ = ()

    type = 'shift'

_transition_types = {'goto': GotoTransition, 'shift': ShiftTransition}

def GetTransition(xml):
    type = attr(xml, 'type', str)
    return _transition_types[type](xml)

class Error(AutoRepr):
    __slots__ = ('symbol', 'content')

    def __init__(self, xml):
        self.symbol = attr(xml, 'symbol', str) # pragma: no cover
        self.content = String(xml)             # pragma: no cover

class Reduction(AutoRepr):
    __slots__ = ('symbol', 'rule', 'enabled')

    def __init__(self, xml):
        self.symbol = attr(xml, 'symbol', str)
        self.rule = attr(xml, 'rule', IntOrAccept)
        self.enabled = attr(xml, 'enabled', Bool)

def IntOrAccept(text):
    if text == 'accept':
        return 0
    return int(text)

def Bool(text):
    return {'true': True, 'false': False}[text]

class ResolutionBase(AutoRepr):
    __slots__ = ('rule', 'symbol', 'content')

    def __init__(self, xml):
        self.rule = attr(xml, 'rule', int)     # pragma: no cover
        self.symbol = attr(xml, 'symbol', str) # pragma: no cover
        self.content = String(xml)             # pragma: no cover

class ShiftResolution(ResolutionBase):
    __slots__ = ()

    type = 'shift'

class ReduceResolution(ResolutionBase):
    __slots__ = ()

    type = 'reduce'

class ErrorResolution(ResolutionBase):
    __slots__ = ()

    type = 'error'

_resolution_types = {'shift': ShiftResolution, 'reduce': ReduceResolution, 'error': ErrorResolution}

def GetResolution(xml):
    type = attr(xml, 'type', str)       # pragma: no cover
    return _resolution_types[type](xml) # pragma: no cover
