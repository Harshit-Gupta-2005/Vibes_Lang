# Vibes Language Reference

- **File extension:** `.vibes`
- **Run with:** `vibes run myfile.vibes` (see the main [README](./README.md) for install options)
- **Comments:** `~ like this ~` — `~` inside a string literal is just a character, not a comment delimiter

---

## Program Structure

| Vibes | Maps to | Notes |
|---|---|---|
| `main_character_vibes` | your program's entry point | Optional. At most one per program. Executes inline, in normal top-to-bottom order — not a special "jump here" target — so defs/classes/`channeling` above it are already available by the time it runs. |
| `vibes on` / `vibes off` | `{` / `}` | Opens/closes any block. An unclosed block raises `VibeError: mismatched vibes on/off`. |
| `that's a wrap` | `exit(0)` | Stops the whole program immediately, from anywhere, even deep inside nested loops or functions. Still triggers any enclosing `good vibes only` block on the way out (like Python's `SystemExit` triggering `finally`), but is never caught by `bad vibes negative vibes` the way a real raised error would be. |
| `channeling <module>` | `import <module>` | Only a single bare module name (`channeling math`), no dotted paths, no `as` aliasing. Once imported, real Python module contents work via dot access: `math.sqrt(16)`, `math.pi`. |

---

## Functions

| Vibes | Maps to | Notes |
|---|---|---|
| `new vibes name(args)` | `def name(args):` | No colon. Block follows with `vibes on`/`vibes off`. |
| `sending vibes <expr>` | `return <expr>` | **An expression is always required** — no bare `return`. Vibes has no statement separators, so a bare `sending vibes` immediately followed by another statement would be genuinely ambiguous about where the return value ends. A function with no `sending vibes` at all returns `no vibes`, same as Python returning `None` implicitly. |

Functions support closures and recursion normally — a function sees variables from where it was *defined*, not from wherever it's called.

---

## Classes

| Vibes | Maps to | Notes |
|---|---|---|
| `new aesthetic Name` | `class Name:` | Class definition. |
| `new aesthetic Name(Parent)` | `class Name(Parent):` | Single inheritance. `Parent` can be another user class **or one of the 14 built-in error types** (see Error Handling) — e.g. `new aesthetic MyError(wrong vibes)` makes a custom exception that inherits `wrong vibes`'s default message and is catchable both by its own name and by `bad vibes wrong vibes`. |
| `new vibes` (inside a class) | `def` (as a method) | Same keyword as top-level functions. `self` is always an explicit first parameter, exactly like Python — not auto-injected. |
| `self` | `self` | Unchanged — mechanics, not personality. |

Class bodies currently only allow method definitions — no class-level fields declared outside `__init__`.

---

## Control Flow

| Vibes | Maps to | Notes |
|---|---|---|
| `it's giving` | `if` | `it's giving x more vibes than 0` |
| `or it's giving` | `elif` | Chains after a closing `vibes off`. |
| `or not` | `else` | Also doubles as `try`'s "no error occurred" clause — see Error Handling. |
| `keep the vibes going` | `while` | |
| `vibing through` | `for` | `vibing through i in range(10)` |
| `no more vibes` | `break` | Exits only the nearest enclosing loop. Used outside any loop, raises a clean `VibeError`. |
| `next vibe` | `continue` | Same scoping rule as `no more vibes`. |

Truthiness and operator precedence mirror Python exactly — no new rules invented for either.

---

## Operators

| Vibes | Maps to |
|---|---|
| `vibes with` | `=` |
| `vibe match` | `==` |
| `vibe doesn't match` | `!=` |
| `more vibes than` | `>` |
| `less vibes than` | `<` |
| `no less vibes than` | `>=` |
| `no more vibes than` | `<=` |
| `+ - * /` | unchanged |

---

## Types & Values

| Vibes | Maps to | Notes |
|---|---|---|
| `numeric vibes` | `int` | Optional type-prefix keyword before a variable name in an assignment, e.g. `numeric vibes x vibes with 5`. Parsed but **never enforced** — Vibes has no forced type declarations, so this is purely cosmetic and can be omitted entirely. |
| `word vibes` | `string` | Same optional-prefix rule. |
| `vibe or no vibe` | `bool` | Same optional-prefix rule. |
| `immaculate vibes` | `True` | |
| `dead vibes` | `False` | |
| `no vibes` | `None` | |

When `manifesting` prints a boolean or `no vibes`, it prints the vibes-flavored words themselves (`immaculate vibes`, `dead vibes`, `no vibes`) rather than Python's `True`/`False`/`None` text.

---

## I/O

| Vibes | Maps to | Notes |
|---|---|---|
| `manifesting <expr>` | `print(expr)` | |
| `absorbing [<prompt_expr>]` | `input([prompt])` | The prompt is optional — `absorbing` alone with nothing after it is a bare `input()` with no prompt text. |

---

## Error Handling

| Vibes | Maps to | Notes |
|---|---|---|
| `catch the vibe` | `try` | |
| `bad vibes [type] [as e]` | `except [Type] as e` | The `as e` binding is optional. **`e` is always the error's message text as a plain string**, not a rich error object — every example that motivated this only ever does `"prefix: " + e`, so a custom error subclass can't carry extra queryable fields accessible via `e`. |
| `or not` | `else` | Runs only if the `try` body completed with no error. |
| `good vibes only` | `finally` | Always runs — including when `that's a wrap` fires inside the `try`. |
| `big yikes [type] [("message")]` | `raise Type("message")` | The message is optional; a message-less raise uses the type's own default message. |

### Error Message Rule

- Custom message provided → use it: `big yikes wrong vibes("that's not a number")`
- No message provided → fall back to the type's default (or its nearest ancestor's default, if it's a custom subclass that doesn't set its own)

### Error Types & Default Messages

| Vibes name | Maps to | Default message |
|---|---|---|
| `wrong vibes` | `ValueError` | `wrong vibes: that value is not it, bestie.` |
| `mixed vibes` | `TypeError` | `mixed vibes: you can't mix those two and expect good things.` |
| `crashed out` | `RuntimeError` | `crashed out: the program just... couldn't anymore.` |
| `ghosted` | `KeyError` | `ghosted: that key was here and then it wasn't. classic.` |
| `out of pocket` | `IndexError` | `out of pocket: you went way too far and you know it.` |
| `negative vibes` | `Exception` (catch-all) | `negative vibes: something went wrong and it's giving chaos.` |
| `cap` | `AssertionError` | `cap: that was NOT true and everyone knew it.` |
| `left on read` | `AttributeError` | `left on read: that thing doesn't have what you're looking for and it's not even sorry.` |
| `who?` | `FileNotFoundError` | `who?: that file doesn't exist and never has.` |
| `spiraling` | `RecursionError` | `spiraling: bestie went too deep, too fast, no chill.` |
| `still cooking` | `NotImplementedError` | `still cooking: this isn't built yet, manifest patience.` |
| `pressed` | `KeyboardInterrupt` | `pressed: someone yanked the plug mid-vibe, rude.` |
| `no service` | `ConnectionError` | `no service: reached out and got absolutely nothing back.` |
| `timed out` | `TimeoutError` | `timed out: waited, and waited, and then said forget it.` |

`negative vibes` sits at the root of all 14 — a `bad vibes negative vibes` clause catches anything, same as Python's `Exception`.

### Custom error classes

A user class can inherit from any built-in error type:

```vibes
new aesthetic InvalidNameError(wrong vibes)
vibes on
vibes off

catch the vibe
vibes on
  big yikes InvalidNameError("names can't start with a number")
vibes off
bad vibes InvalidNameError as e
vibes on
  manifesting e
vibes off
```

A raised `InvalidNameError` is catchable **both** by its own name and by `bad vibes wrong vibes` (its parent), same as real exception subclassing. If raised without its own message, it falls back to `wrong vibes`'s default message.

### What's *not* catchable

A fixed, short list of fatal interpreter-level faults are never catchable by `bad vibes`, no matter which type you name — they represent the interpreter itself breaking, not a normal program error:

```
VibeError: you tried to divide by zero and honestly? the audacity.
VibeError: undefined variable 'x' — it literally does not exist, bestie.
VibeError: stack overflow — you went too deep. touch grass.
VibeError: mismatched vibes on/off — you opened a block and just... left.
VibeError: you called no vibes and then used it. what did you expect.
```

Calling something that isn't callable at all (not `None`, just not a function/class), calling with the wrong number of arguments, and a few similar interpreter faults also raise uncatchable `VibeError:`-prefixed messages, following the same "this is a program-breaking mistake, not a normal error" logic.

---

## Standard Library Rule

Keywords that control flow or shape how the language *feels* get renamed. Utility functions that just do a job — `range()`, `len()`, `int()`, `str()`, `type()` — stay as-is, and so does anything reached through `channeling` (a module's own functions/constants are never renamed).

---

## Known limitations (v1)

- **No collection types** — no list/tuple/dict/set literals, no indexing (`x[0]`), no slicing. Biggest gap if you want to write substantial programs.
- **`bad vibes X as e` binds a plain string**, not a rich error object — `e` is always just the error's message text, so a custom error subclass can't carry extra queryable fields (like an error code) accessible via `e`.
- Class bodies currently only allow method definitions — no class-level fields declared outside `__init__`.
- `sending vibes` always requires an expression — no bare `return` — since there's no statement separator to disambiguate where a bare return would end and the next statement would begin.
- `channeling` only supports a single bare module name (`channeling math`), no dotted paths or `as` aliasing.

---

## Full Example

```vibes
~ a class, a function, error handling, a loop ~

channeling math

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

new vibes count_up(limit)
vibes on
  x vibes with 0
  vibing through i in range(limit)
  vibes on
    it's giving i vibe match 5
    vibes on
      no more vibes
    vibes off
    x vibes with x + i
  vibes off
  sending vibes x
vibes off

main_character_vibes
vibes on
  word vibes name vibes with absorbing "what's your name?"

  catch the vibe
  vibes on
    p vibes with Person(name)
    p.greet()
    result vibes with count_up(10)
    manifesting result
  vibes off
  bad vibes wrong vibes as e
  vibes on
    manifesting "bad vibes detected: " + e
  vibes off
  bad vibes negative vibes as e
  vibes on
    manifesting "something went off: " + e
  vibes off
  good vibes only
  vibes on
    manifesting "that's a wrap"
  vibes off

  that's a wrap
vibes off
```
