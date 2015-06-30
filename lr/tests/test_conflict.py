import typing

from lr.conflict import ConflictMap


def test_conflict() -> None:
    con = ConflictMap([1, 2, 3]) # type: ConflictMap[int, str]
    con.add(1, 'a')
    con.add(1, 'b')
    con.add(2, 'c')
    good, bad = con.finish()
    assert good == {2: 'c'}
    assert bad == {1: ['a', 'b']}

def test_default() -> None:
    con = ConflictMap([1, 2, 3]) # type: ConflictMap[int, str]
    con.add(1, 'a')
    con.add(2, 'c')
    con.add_default('d')
    good, bad = con.finish()
    assert good == {1: 'a', 2: 'c', 3: 'd'}
    assert bad == {}

def test_conflict_default() -> None:
    con = ConflictMap([1, 2, 3]) # type: ConflictMap[int, str]
    con.add(1, 'a')
    con.add(2, 'c')
    con.add_default('d')
    con.add_default('e')
    good, bad = con.finish()
    assert good == {1: 'a', 2: 'c'}
    assert bad == {3: ['d', 'e']}
