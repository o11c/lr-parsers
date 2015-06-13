import typing

from typing import (
        List,
)

from .grammar import SymbolId, RuleId


class Value:
    __slots__ = ('_sym',)

class Terminal(Value):
    __slots__ = ('_text',)

    def __init__(self, sym: SymbolId, text: str) -> None:
        self._sym = sym
        self._text = text

    def __repr__(self) -> str:
        sym = self._sym._data()._name
        text = self._text
        if sym == text:
            return repr(text)
        return '%s(%r)' % (sym, text)

class Nonterminal(Value):
    __slots__ = ('_rule', '_children')

    def __init__(self, rule: RuleId, children: List[Value]) -> None:
        self._sym = rule._data()._lhs
        self._rule = rule
        self._children = children

    def __repr__(self) -> str:
        if len(self._children) == 1:
            return '.%r' % (self._children[0],)
        sym = self._sym._data()._name
        alt = self._rule._data()._alt_number
        children = ', '.join([repr(child) for child in self._children])
        return '%s%d(%s)' % (sym, alt, children)
