import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.interpreter import run_source


def run(src):
    out = []
    run_source(src, output=out)
    return out


def test_main_block_executes_inline():
    src = """
    manifesting "before main"

    main_character_vibes
    vibes on
      manifesting "inside main"
    vibes off
    """
    assert run(src) == ["before main", "inside main"]


def test_defs_before_main_are_usable_inside_main():
    src = """
    new vibes greet()
    vibes on
      manifesting "hi from a function defined before main"
    vibes off

    main_character_vibes
    vibes on
      greet()
    vibes off
    """
    assert run(src) == ["hi from a function defined before main"]


def test_exit_stops_execution_immediately():
    src = """
    manifesting "one"
    that's a wrap
    manifesting "two"
    """
    assert run(src) == ["one"]


def test_exit_inside_main_stops_the_program():
    src = """
    main_character_vibes
    vibes on
      manifesting "one"
      that's a wrap
      manifesting "should not print"
    vibes off
    """
    assert run(src) == ["one"]


def test_exit_inside_loop_stops_the_whole_program_not_just_the_loop():
    src = """
    vibing through i in range(10)
    vibes on
      manifesting i
      it's giving i vibe match 2
      vibes on
        that's a wrap
      vibes off
    vibes off
    manifesting "should not print"
    """
    assert run(src) == ["0", "1", "2"]


def test_exit_still_triggers_finally_block():
    src = """
    catch the vibe
    vibes on
      that's a wrap
    vibes off
    good vibes only
    vibes on
      manifesting "finally still ran"
    vibes off
    manifesting "should not print, program already exited"
    """
    assert run(src) == ["finally still ran"]


def test_exit_is_not_caught_by_bad_vibes_catchall():
    # `that's a wrap` must not be swallowed by `bad vibes negative vibes`
    # the way a real raised error would be
    src = """
    catch the vibe
    vibes on
      that's a wrap
    vibes off
    bad vibes negative vibes as e
    vibes on
      manifesting "should not print -- exit isn't a caught error"
    vibes off
    """
    assert run(src) == []


def test_full_program_shape_defs_then_main():
    src = """
    new aesthetic Greeter
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

    new vibes double(x)
    vibes on
      sending vibes x * 2
    vibes off

    main_character_vibes
    vibes on
      g vibes with Greeter("bestie")
      g.greet()
      manifesting double(21)
      that's a wrap
    vibes off
    """
    assert run(src) == ["hey, bestie", "42"]
