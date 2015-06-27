import typing

import subprocess

import lxml.etree as etree

from .error import LoweringError
from .grammar import Grammar
from .automaton import Automaton
from . import _bison_xml


BISON = 'bison'


def run_bison(grammar: Grammar, lr_type: str = 'lalr') -> etree._ElementTree:
    args = [BISON, '/dev/stdin', '-o', '/dev/null', '--xml=/dev/stdout']
    if True:
        # Without this, bison will attempt to read the input file twice
        # if there is any warning/error, which obviously fails with a pipe.
        # Bug report here: https://lists.gnu.org/archive/html/bug-bison/2015-06/msg00001.html
        args.append('--feature=none')
    args.append('-Werror=all')
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    def p(*s: str) -> None:
        proc.stdin.writelines([x.encode('utf-8') for x in s] + [b'\n'])
    for sym in grammar._symbols._data[1:grammar._symbols._num_terminals]:
        assert sym._is_term
        p('%token ', sym._bison())
    p('%start ', grammar._data[0]._rhs[0]._data()._bison())
    p('%define lr.type ', lr_type)
    p('%%')
    for rule in grammar._data[1:]:
        p(rule._bison())
    p('%%')
    proc.stdin.close()
    parser = etree.XMLParser(schema=etree.XMLSchema(file='bison.xsd'))
    rv = etree.parse(proc.stdout, parser=parser)
    if proc.wait():
        raise LoweringError('bison failed') # pragma: no cover
    return rv

def parse_bison(xml: etree._ElementTree) -> _bison_xml.BisonXmlReport:
    return _bison_xml.root(xml, _bison_xml.BisonXmlReport)

def compute_automaton(grammar: Grammar) -> Automaton:
    xml = run_bison(grammar)
    bison_xml_report = parse_bison(xml)
    raise NotImplementedError
