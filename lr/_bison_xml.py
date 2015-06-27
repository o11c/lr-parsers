import typing

from typing import (
        Callable,
        Dict,
        List,
        Optional,
        TypeVar,
)

from . import _mypy_bugs

import lxml.etree as etree


T = TypeVar('T')

xml_identity = typing.cast(Callable[[etree._Element], etree._Element], _mypy_bugs.identity)


# TODO Use `enum` for assoc and usefulness.


def attr(xml: etree._Element, name: str, cls: Callable[[str], T]) -> T:
    return cls(xml.attrib[name])

def opt_attr(xml: etree._Element, name: str, cls: Callable[[str], T]) -> Optional[T]:
    attr = xml.attrib.get(name)
    if attr is None:
        return None
    return cls(attr) # pragma: no cover

def child(xml: etree._Element, name: str, cls: Callable[[etree._Element], T]) -> T:
    rv = children(xml, name, cls)
    assert len(rv) == 1
    return rv[0]

def opt_child(xml: etree._Element, name: str, cls: Callable[[etree._Element], T]) -> Optional[T]:
    rv = children(xml, name, cls)
    if not rv:
        return None
    assert len(rv) == 1
    return rv[0]

def children(xml: etree._Element, name: str, cls: Callable[[etree._Element], T]) -> List[T]:
    return [cls(c) for c in xml.iterchildren(name)]
# There is no need for opt_children; it DTRT when there is nothing.

def inner_children(xml: etree._Element, name1: str, name2: str, cls: Callable[[etree._Element], T]) -> List[T]:
    xml_tmp = child(xml, name1, xml_identity)
    return children(xml_tmp, name2, cls)

def opt_inner_children(xml: etree._Element, name1: str, name2: str, cls: Callable[[etree._Element], T]) -> List[T]:
    xml_tmp = opt_child(xml, name1, xml_identity)
    if xml_tmp is None:
        return typing.cast(List[T], [])
    return children(xml_tmp, name2, cls)

def root(xml: etree._ElementTree, cls: Callable[[etree._Element], T]) -> T:
    return cls(xml.getroot())


def String(xml: etree._Element) -> str:
    return xml.text

class BisonXmlReport:
    __slots__ = ('version', 'bug_report', 'url', 'filename', 'grammar', 'automaton')

    def __init__(self, xml: etree._Element) -> None:
        self.version = attr(xml, 'version', str)
        self.bug_report = attr(xml, 'bug-report', str)
        self.url = attr(xml, 'url', str)
        self.filename = child(xml, 'filename', String)
        self.grammar = child(xml, 'grammar', Grammar)
        self.automaton = inner_children(xml, 'automaton', 'state', State)

class Grammar:
    __slots__ = ('rules', 'terminals', 'nonterminals')

    def __init__(self, xml: etree._Element) -> None:
        self.rules = inner_children(xml, 'rules', 'rule', Rule)
        self.terminals = inner_children(xml, 'terminals', 'terminal', Terminal)
        self.nonterminals = inner_children(xml, 'nonterminals', 'nonterminal', Nonterminal)

class Rule:
    __slots__ = ('number', 'usefulness', 'lhs', 'rhs')

    def __init__(self, xml: etree._Element) -> None:
        self.number = attr(xml, 'number', int)
        self.usefulness = attr(xml, 'usefulness', str)
        self.lhs = child(xml, 'lhs', String)
        self.rhs = inner_children(xml, 'rhs', 'symbol', String)

class Terminal:
    __slots__ = ('symbol_number', 'token_number', 'name', 'usefulness', 'prec', 'assoc')

    def __init__(self, xml: etree._Element) -> None:
        self.symbol_number = attr(xml, 'symbol-number', int)
        self.token_number = attr(xml, 'token-number', int)
        self.name = attr(xml, 'name', str)
        self.usefulness = attr(xml, 'usefulness', str)
        self.prec = opt_attr(xml, 'prec', int)
        self.assoc = opt_attr(xml, 'assoc', str)

class Nonterminal:
    __slots__ = ('symbol_number', 'name', 'usefulness')

    def __init__(self, xml: etree._Element) -> None:
        self.symbol_number = attr(xml, 'symbol-number', int)
        self.name = attr(xml, 'name', str)
        self.usefulness = attr(xml, 'usefulness', str)

class State:
    __slots__ = ('number', 'itemset', 'actions', 'solved_conflicts')

    def __init__(self, xml: etree._Element) -> None:
        self.number = attr(xml, 'number', int)
        self.itemset = inner_children(xml, 'itemset', 'item', Item)
        self.actions = child(xml, 'actions', Actions)
        self.solved_conflicts = inner_children(xml, 'solved-conflicts', 'resolution', GetResolution)

class Item:
    __slots__ = ('rule', 'point', 'lookaheads')

    def __init__(self, xml: etree._Element) -> None:
        self.rule = attr(xml, 'rule-number', int)
        self.point = attr(xml, 'point', int)
        self.lookaheads = opt_inner_children(xml, 'lookaheads', 'symbol', String)

class Actions:
    __slots__ = ('transitions', 'errors', 'reductions')

    def __init__(self, xml: etree._Element) -> None:
        self.transitions = inner_children(xml, 'transitions', 'transition', GetTransition)
        self.errors = inner_children(xml, 'errors', 'error', Error)
        self.reductions = inner_children(xml, 'reductions', 'reduction', Reduction)

class TransitionBase:
    __slots__ = ('symbol', 'state')

    def __init__(self, xml: etree._Element) -> None:
        self.symbol = attr(xml, 'symbol', str)
        self.state = attr(xml, 'state', int)

class GotoTransition(TransitionBase):
    __slots__ = ()

    type = 'goto'

class ShiftTransition(TransitionBase):
    __slots__ = ()

    type = 'shift'

_transition_types = {'goto': GotoTransition, 'shift': ShiftTransition} # type: Dict[str, Callable[[etree._Element], TransitionBase]]

def GetTransition(xml: etree._Element) -> TransitionBase:
    type = attr(xml, 'type', str)
    return _transition_types[type](xml)

class Error:
    __slots__ = ('symbol', 'content')

    def __init__(self, xml: etree._Element) -> None:
        self.symbol = attr(xml, 'symbol', str) # pragma: no cover
        self.content = String(xml)             # pragma: no cover

class Reduction:
    __slots__ = ('symbol', 'rule', 'enabled')

    def __init__(self, xml: etree._Element) -> None:
        self.symbol = attr(xml, 'symbol', str)
        self.rule = attr(xml, 'rule', IntOrAccept)
        self.enabled = attr(xml, 'enabled', Bool)

def IntOrAccept(text: str) -> int:
    if text == 'accept':
        return 0
    return int(text)

def Bool(text: str) -> int:
    return {'true': True, 'false': False}[text]

class ResolutionBase:
    __slots__ = ('rule', 'symbol', 'content')

    def __init__(self, xml: etree._Element) -> None:
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

_resolution_types = {'shift': ShiftResolution, 'reduce': ReduceResolution, 'error': ErrorResolution} # type: Dict[str, Callable[[etree._Element], ResolutionBase]]

def GetResolution(xml: etree._Element) -> ResolutionBase:
    type = attr(xml, 'type', str)       # pragma: no cover
    return _resolution_types[type](xml) # pragma: no cover
