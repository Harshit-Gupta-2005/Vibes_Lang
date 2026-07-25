# Vibes Language Spec

> An esolang (esoteric programming language) where syntax is entirely vibes-based. Structurally closer to C (explicit block delimiters instead of indentation), semantically closer to Python (try/except naming, no semicolons, no forced type declarations).

- **File extension:** `.vibes`
- **Run with:** `vibes run myfile.vibes`
- **Comments:** `~ like this ~`

---

## Program Structure

| Vibes | Maps to | Notes |
|---|---|---|
| `main_character_vibes` | `main()` | Entry point. Every program has exactly one. |
| `vibes on` | `{` | Opens any block |
| `vibes off` | `}` | Closes any block |
| `that's a wrap` | `exit(0)` | Optional. Ends the program cleanly. |
| `channeling` | `import` | `channeling math` |

---

## Functions

| Vibes | Maps to | Notes |
|---|---|---|
| `new vibes name(args)` | `def name(args)` | No colon. Block follows with vibes on/off. |
| `sending vibes` | `return` | `sending vibes 42` |

---

## Classes

| Vibes | Maps to | Notes |
|---|---|---|
| `new aesthetic Name` | `class Name` | Class definition |
| `new aesthetic Dog(Animal)` | `class Dog(Animal)` | Inheritance stays the same |
| `new vibes` | `def` | Methods use same keyword as functions |
| `self` | `self` | Unchanged — mechanics not personality |

---

## Control Flow

| Vibes | Maps to | Notes |
|---|---|---|
| `it's giving` | `if` | `it's giving x more vibes than 0` |
| `or not` | `else` | Follows a closing vibes off |
| `keep the vibes going` | `while` | `keep the vibes going x no more vibes than 10` |
| `vibing through` | `for` | `vibing through i in range(10)` |
| `no more vibes` | `break` | Exits the current loop |
| `next vibe` | `continue` | Skips to next iteration |

---

## Operators

| Vibes | Maps to | Notes |
|---|---|---|
| `vibes with` | `=` | Assignment. `x vibes with 5` |
| `vibe match` | `==` | Equality check |
| `vibe doesn't match` | `!=` | Inequality check |
| `more vibes than` | `>` | |
| `less vibes than` | `<` | |
| `no less vibes than` | `>=` | |
| `no more vibes than` | `<=` | |
| `+ - * /` | `+ - * /` | Math operators unchanged |

---

## Types & Values

| Vibes | Maps to | Notes |
|---|---|---|
| `numeric vibes` | `int` | Integer type |
| `word vibes` | `string` | String type |
| `vibe or no vibe` | `bool` | Boolean type |
| `immaculate vibes` | `True` | |
| `dead vibes` | `False` | |
| `no vibes` | `None / null` | |

---

## I/O

| Vibes | Maps to | Notes |
|---|---|---|
| `manifesting` | `print()` | `manifesting "hello"` |
| `absorbing` | `input()` | `absorbing "what's your name?"` |
| `channeling` | `import` | `channeling math` |

---

## Error Handling

| Vibes | Maps to | Notes |
|---|---|---|
| `catch the vibe` | `try` | Opens the risky block |
| `bad vibes [type] as e` | `except [Type] as e` | Catches a specific error type |
| `bad vibes negative vibes as e` | `except Exception as e` | Catches anything remaining |
| `or not` | `else` | Runs only if no error occurred |
| `good vibes only` | `finally` | Always runs no matter what |
| `big yikes` | `raise` | `big yikes wrong vibes("not a number")` |

### Error Message Rule
- **Custom message provided** → use it: `wrong vibes: that's not a number`
- **No message provided** → fall back to default below

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

### VibeError (interpreter-level errors)

```
VibeError: you tried to divide by zero and honestly? the audacity.
VibeError: undefined variable 'x' — it literally does not exist, bestie.
VibeError: stack overflow — you went too deep. touch grass.
VibeError: mismatched vibes on/off — you opened a block and just... left.
VibeError: you called no vibes and then used it. what did you expect.
```

---

## Standard Library Rule

Keywords that control flow or shape how the language *feels* get renamed. Utility functions that just do a job — `range()`, `len()`, `int()`, `str()`, `type()` — stay as is.

---

## Runtime Vibe System (v2 — not in initial build)

> Get the language working first. Bolt this on after. Do not build this in v1.

A global vibe level (0–100), starting at 50, would eventually track program "energy" and affect execution (e.g. errors forgiven at high vibes, program "sighs" at low vibes). Fully deferred — no design decisions locked in yet.

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
