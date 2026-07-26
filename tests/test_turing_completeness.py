"""
Evidence of Turing-complete computational power.

Turing completeness isn't something you verify with a pass/fail test the
way "5 + 3 == 8" is -- it's a structural property of the language, backed
by a real theorem, not a runtime check. The formal argument (the
"While-language" result, Meyer & Ritchie 1967) says: a language with
assignment, sequencing, conditionals, and an *unbounded* loop -- one whose
exit condition depends on runtime data, not a fixed compile-time count --
is provably Turing complete. `keep the vibes going <condition>` is exactly
that kind of loop (unlike `vibing through i in range(10)`, which can only
ever run a fixed number of times known in advance).

What this file provides isn't a proof by itself -- no finite test run can
prove a property about *unlimited* time/memory -- but genuine, checkable
evidence consistent with that theorem, using two real, independently
verifiable landmarks from computability theory:

1. The Ackermann function -- famous specifically because it's *provably
   not* primitive recursive. Any language that can correctly compute it
   demonstrates it has more computational power than a "for-loops-only"
   language ever could, no matter how deeply you nest those loops.
2. The Collatz "stopping time" function -- its own loop bound can't be
   known in advance for arbitrary input (nobody has even proven it always
   terminates), so computing it at all requires a genuinely unbounded
   `while`, not a disguised `for`.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vibes.interpreter import run_source


def run(src):
    out = []
    run_source(src, output=out)
    return out


ACKERMANN_SRC = """
new vibes ackermann(m, n)
vibes on
  it's giving m vibe match 0
  vibes on
    sending vibes n + 1
  vibes off
  it's giving n vibe match 0
  vibes on
    sending vibes ackermann(m - 1, 1)
  vibes off
  sending vibes ackermann(m - 1, ackermann(m, n - 1))
vibes off
"""


def test_ackermann_matches_known_mathematical_values():
    # A(2, n) = 2n + 3 and A(3, n) = 2^(n+3) - 3 are closed forms used to
    # sanity-check any Ackermann implementation -- these aren't arbitrary
    # numbers, they're the textbook reference values.
    assert run(ACKERMANN_SRC + "manifesting ackermann(2, 3)") == ["9"]
    assert run(ACKERMANN_SRC + "manifesting ackermann(2, 4)") == ["11"]
    assert run(ACKERMANN_SRC + "manifesting ackermann(3, 3)") == ["61"]


COLLATZ_SRC = """
new vibes collatz_steps(n)
vibes on
  steps vibes with 0
  keep the vibes going n vibe doesn't match 1
  vibes on
    it's giving n vibe match 2 * int(n / 2)
    vibes on
      n vibes with int(n / 2)
    vibes off
    or not
    vibes on
      n vibes with 3 * n + 1
    vibes off
    steps vibes with steps + 1
  vibes off
  sending vibes steps
vibes off
"""


def test_collatz_stopping_time_matches_known_values():
    # 27 is a commonly-cited example specifically because it's a
    # surprisingly long trajectory (111 steps) for such a small starting
    # number -- a standard reference value in any Collatz implementation.
    assert run(COLLATZ_SRC + "manifesting collatz_steps(27)") == ["111"]
    assert run(COLLATZ_SRC + "manifesting collatz_steps(97)") == ["118"]


def test_while_loop_exit_condition_is_genuinely_data_dependent():
    # The concrete distinction this whole file rests on: a `keep the vibes
    # going` loop's exit is decided by a runtime value, not a fixed count
    # known in advance -- unlike `vibing through i in range(10)`, which
    # could never express "loop until this arithmetic condition holds"
    # without knowing the answer before you start.
    src = """
    new vibes first_power_of_two_over(limit)
    vibes on
      x vibes with 1
      keep the vibes going x no more vibes than limit
      vibes on
        x vibes with x * 2
      vibes off
      sending vibes x
    vibes off

    manifesting first_power_of_two_over(1000)
    manifesting first_power_of_two_over(1000000)
    """
    assert run(src) == ["1024", "1048576"]
