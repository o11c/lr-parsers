#!/usr/bin/env python3
import typing

from lr.grammar import (
        Grammar,
)

from lr.fallback import compute_automaton
from lr.runtime import Runtime

from . import grammar_examples


def test_main() -> None:
    grammar = grammar_examples.lr0_grammar
    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    runtime.feed_all(grammar_examples.lr0_input)
    print(runtime.get())
