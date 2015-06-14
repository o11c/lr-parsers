This package implements LR parsers and tests them against grammars.

The automaton and runtime is frontend-agnostic.

# Frontends

- LR(0) (nearly useless)
- SLR(1) (not as flexible as LALR)
- LALR(1) (best choice)
- LR(1) (may be expensive and usually not needed)
- automatic selection of the above
- bison xml (requires external tool, can do precedence parsing)

# Dependencies

- Python 3.3 or later. Porting to 3.2 is possible but not important to me.
- PEP 484 `typing` module (usually included with mypy).

# Test Dependencies

- mypy (o11c's fork may be needed for unmerged PRs).
- pytest (to run tests).
- pytest-cov (to include coverage information with tests).

# Usage

Undocumented, see tests for examples.

# Testing

Tests can be run against a single python version using
`make PYTHON=python3.4`. The default is just `python`, which is wrong
on all sane systems since it refers to `python2` unless you are in a venv.

To easily test in venvs for each python version, run `tox`. If you change
requirements.txt or the remote packages it points to, run `tox -r`.
