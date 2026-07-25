# Vibes 🌀

### vibecode with vibes

> An esolang where syntax is entirely vibes-based.
> Structurally closer to C (explicit block delimiters instead of indentation),
> semantically closer to Python (try/except naming, no semicolons, no forced
> type declarations).

```vibes
new aesthetic Person
vibes on
  new vibes __init__(self, name)
  vibes on
    self.name vibes with name
  vibes off

  new vibes greet(self)
  vibes on
    manifesting "hey, " + self.name
  vibes off
vibes off

main_character_vibes
vibes on
  p vibes with Person("bestie")
  p.greet()
  that's a wrap
vibes off
```

```
$ vibes run examples/hello_person.vibes
hey, bestie
```

---

## Status

This is a complete, working v1. Every construct in [`vibes_spec.md`](./vibes_spec.md)
is implemented and tested — lexer, parser, and tree-walking interpreter, all
built from scratch in Python with no dependency on Python's own grammar
(renaming keywords doesn't get you Python's parser for free; see
[Known limitations](#known-limitations--v2-ideas) for what's intentionally
out of scope for now).

**174 tests, 0 failures.**

---

## Installation

Requires Python 3.8+.

**Option 1 — install it as a real command (recommended):**

```bash
git clone <this-repo>
cd vibes_lang
pip install -e .
```

This gives you a genuine `vibes` command on your PATH, matching the spec's
own "Run with" line exactly:

```bash
vibes run myfile.vibes
```

**Option 2 — zero install:**

```bash
cd vibes_lang
python3 -m vibes run myfile.vibes
```

---

## Quick start

```bash
cat > hello.vibes << 'EOF'
manifesting "hello from vibes"
x vibes with 6 * 7
manifesting x
EOF

vibes run hello.vibes
```

```
hello from vibes
42
```

More runnable examples live in [`examples/`](./examples), covering
FizzBuzz, recursion, classes with inheritance, `channeling` a real Python
module, and full try/except/finally error handling. `examples/errors/`
contains small programs that each deliberately trigger a different kind of
error, so you can see exactly what each failure mode looks like.

---

## Language overview

Full keyword-by-keyword reference: [`vibes_spec.md`](./vibes_spec.md).
Quick taste:

| Vibes | Python equivalent |
|---|---|
| `vibes on` / `vibes off` | `{` / `}` (block delimiters, not indentation) |
| `it's giving` / `or it's giving` / `or not` | `if` / `elif` / `else` |
| `keep the vibes going` | `while` |
| `vibing through x in range(10)` | `for x in range(10)` |
| `no more vibes` / `next vibe` | `break` / `continue` |
| `vibes with` | `=` |
| `vibe match` / `vibe doesn't match` | `==` / `!=` |
| `new vibes name(args)` | `def name(args):` |
| `sending vibes <expr>` | `return <expr>` |
| `new aesthetic Name(Parent)` | `class Name(Parent):` |
| `manifesting` / `absorbing` | `print()` / `input()` |
| `channeling math` | `import math` |
| `catch the vibe` / `bad vibes X as e` / `good vibes only` | `try` / `except X as e` / `finally` |
| `big yikes wrong vibes("msg")` | `raise ValueError("msg")` |
| `main_character_vibes` | your program's entry point |
| `that's a wrap` | `exit(0)` |
| `~ comment ~` | `# comment` |

14 built-in error types are supported (`wrong vibes`, `mixed vibes`,
`crashed out`, `ghosted`, `out of pocket`, `negative vibes` as the
catch-all, `cap`, `left on read`, `who?`, `spiraling`, `still cooking`,
`pressed`, `no service`, `timed out`), each with its own default message,
overridable with a custom one: `big yikes wrong vibes("custom message")`.
User classes can even inherit from a built-in error type to make their own
custom exceptions.

---

## Running the tests

```bash
pip install pytest
python3 -m pytest tests/ -v
```

All 174 tests should pass. The suite is split one file per feature area
(lexer, parser/interpreter pairs for each language construct, CLI
subprocess tests, and a final integration test that runs the spec's own
full example program end-to-end) so a failure tells you roughly where to
look before you even read the traceback.

---

## Project structure

```
vibes_lang/
  vibes/
    keywords.py      # the multi-word keyword table (lexer's source of truth)
    lexer.py          # source text -> tokens (greedy multi-word matching,
                       #   handles ~ comments ~ and string literals correctly)
    ast_nodes.py       # AST node definitions (plain dataclasses)
    parser.py          # tokens -> AST (recursive descent)
    environment.py      # variable scoping / closures
    interpreter.py       # tree-walking evaluator
    cli.py                # `vibes run file.vibes`
    __main__.py             # lets `python3 -m vibes` work with no install
  tests/                     # one file per feature area, ~174 tests total
  examples/                    # runnable .vibes programs
    errors/                     # programs that each demonstrate one error message
  pyproject.toml                 # packaging (gives you the `vibes` command)
  vibes_spec.md                   # the original language spec
```

**How it works, in one paragraph:** source text is tokenized in two phases —
a raw character scan (handles string literals and `~ comments ~` correctly,
including a `~` appearing *inside* a string) followed by greedy longest-match
folding of raw words into keyword tokens, since most Vibes keywords are
multiple words and some are prefixes of others (`no more vibes` vs.
`no more vibes than`). The parser is a standard recursive-descent parser
producing an AST, and the interpreter walks that AST directly — no bytecode,
no compilation step. Control flow (`break`/`continue`/`return`/`that's a wrap`)
is implemented via internal Python exceptions caught at the right level,
a standard technique for tree-walking interpreters. Scoping uses a simple
parent-linked `Environment` chain, giving closures and recursion for free
once function calls swap in a child scope.

---

## Known limitations / v2 ideas

Called out here deliberately, so nothing below reads as an accidental bug:

- **No collection types.** No list/tuple/dict/set literals, no indexing
  (`x[0]`), no slicing. The spec doesn't mention them, so v1 doesn't have
  them — this is the biggest gap if you want to write real programs with it.
- **`bad vibes X as e` binds a plain string**, not a rich error object.
  `e` is always just the error's message text (matches every example in the
  spec, which only ever does `"prefix: " + e`), so a custom error subclass
  can't carry extra queryable fields (like an error code) accessible via `e`.
- **The v2 "runtime vibe system"** described in the spec (a global 0–100
  energy level affecting execution) is intentionally not implemented —
  the spec itself says to get the language working first and defer this.
- Class bodies currently only allow method definitions (no class-level
  fields outside `__init__`).
- `sending vibes` always requires an expression — no bare `return` — to
  sidestep a real grammar ambiguity (Vibes has no statement separators, so
  a bare return immediately followed by another statement would be
  ambiguous about where the return value ends).
- `channeling` only supports a single bare module name (`channeling math`),
  no dotted paths or `as` aliasing.

---

## License

MIT — see [`LICENSE`](./LICENSE).
