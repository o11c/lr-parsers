This package implements LR parsers and tests them against grammars.

The automaton and runtime is frontend-agnostic.

Planned frontends:

- LR(0) (nearly useless)
- SLR(1)
- LALR(1) (best choice)
- LR(1) (i.e. canonical LR, uses optimizations but may still be expensive)
- automatic selection of the above
- bison xml (requires external tool, can do precedence parsing)
