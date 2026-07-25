import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.interpreter import run_source, VibesRuntimeError, VibesRaised


def run(src):
    out = []
    run_source(src, output=out)
    return out


def test_raise_with_custom_message_is_caught():
    src = """
    catch the vibe
    vibes on
      big yikes wrong vibes("that's not a number")
    vibes off
    bad vibes wrong vibes as e
    vibes on
      manifesting e
    vibes off
    """
    assert run(src) == ["that's not a number"]


def test_raise_without_message_uses_default():
    src = """
    catch the vibe
    vibes on
      big yikes wrong vibes
    vibes off
    bad vibes wrong vibes as e
    vibes on
      manifesting e
    vibes off
    """
    assert run(src) == ["wrong vibes: that value is not it, bestie."]


def test_all_fourteen_default_messages():
    expected = {
        "wrong vibes": "wrong vibes: that value is not it, bestie.",
        "mixed vibes": "mixed vibes: you can't mix those two and expect good things.",
        "crashed out": "crashed out: the program just... couldn't anymore.",
        "ghosted": "ghosted: that key was here and then it wasn't. classic.",
        "out of pocket": "out of pocket: you went way too far and you know it.",
        "negative vibes": "negative vibes: something went wrong and it's giving chaos.",
        "cap": "cap: that was NOT true and everyone knew it.",
        "left on read": "left on read: that thing doesn't have what you're looking for and it's not even sorry.",
        "who?": "who?: that file doesn't exist and never has.",
        "spiraling": "spiraling: bestie went too deep, too fast, no chill.",
        "still cooking": "still cooking: this isn't built yet, manifest patience.",
        "pressed": "pressed: someone yanked the plug mid-vibe, rude.",
        "no service": "no service: reached out and got absolutely nothing back.",
        "timed out": "timed out: waited, and waited, and then said forget it.",
    }
    for phrase, message in expected.items():
        src = f"""
        catch the vibe
        vibes on
          big yikes {phrase}
        vibes off
        bad vibes {phrase} as e
        vibes on
          manifesting e
        vibes off
        """
        assert run(src) == [message], phrase


def test_wrong_handler_does_not_catch():
    src = """
    catch the vibe
    vibes on
      big yikes wrong vibes
    vibes off
    bad vibes ghosted as e
    vibes on
      manifesting "shouldn't get here"
    vibes off
    """
    with pytest.raises(VibesRaised):
        run(src)


def test_catchall_negative_vibes_catches_anything():
    src = """
    catch the vibe
    vibes on
      big yikes ghosted("missing key")
    vibes off
    bad vibes negative vibes as e
    vibes on
      manifesting "caught: " + e
    vibes off
    """
    assert run(src) == ["caught: missing key"]


def test_first_matching_handler_wins_in_order():
    src = """
    catch the vibe
    vibes on
      big yikes wrong vibes("oops")
    vibes off
    bad vibes wrong vibes as e
    vibes on
      manifesting "specific: " + e
    vibes off
    bad vibes negative vibes as e
    vibes on
      manifesting "catchall: " + e
    vibes off
    """
    assert run(src) == ["specific: oops"]


def test_else_runs_only_when_no_error():
    src = """
    catch the vibe
    vibes on
      manifesting "trying"
    vibes off
    bad vibes wrong vibes as e
    vibes on
      manifesting "caught"
    vibes off
    or not
    vibes on
      manifesting "no errors happened"
    vibes off
    """
    assert run(src) == ["trying", "no errors happened"]


def test_else_does_not_run_when_error_occurs():
    src = """
    catch the vibe
    vibes on
      big yikes wrong vibes
    vibes off
    bad vibes wrong vibes as e
    vibes on
      manifesting "caught"
    vibes off
    or not
    vibes on
      manifesting "should not print"
    vibes off
    """
    assert run(src) == ["caught"]


def test_finally_always_runs_on_success():
    src = """
    catch the vibe
    vibes on
      manifesting "trying"
    vibes off
    good vibes only
    vibes on
      manifesting "always"
    vibes off
    """
    assert run(src) == ["trying", "always"]


def test_finally_always_runs_on_caught_error():
    src = """
    catch the vibe
    vibes on
      big yikes wrong vibes
    vibes off
    bad vibes wrong vibes as e
    vibes on
      manifesting "caught"
    vibes off
    good vibes only
    vibes on
      manifesting "always"
    vibes off
    """
    assert run(src) == ["caught", "always"]


def test_finally_runs_even_on_uncaught_error():
    src = """
    catch the vibe
    vibes on
      big yikes ghosted
    vibes off
    bad vibes wrong vibes as e
    vibes on
      manifesting "should not print"
    vibes off
    good vibes only
    vibes on
      manifesting "always runs"
    vibes off
    """
    out = []
    with pytest.raises(VibesRaised):
        run_source(src, output=out)
    assert out == ["always runs"]


def test_custom_error_class_inheriting_from_builtin():
    src = """
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
    """
    assert run(src) == ["names can't start with a number"]


def test_custom_error_class_caught_by_parent_type():
    # subclass instances should still be catchable by the built-in parent
    # type's except clause -- same as Python's exception matching
    src = """
    new aesthetic InvalidNameError(wrong vibes)
    vibes on
    vibes off

    catch the vibe
    vibes on
      big yikes InvalidNameError("bad name")
    vibes off
    bad vibes wrong vibes as e
    vibes on
      manifesting "caught via parent: " + e
    vibes off
    """
    assert run(src) == ["caught via parent: bad name"]


def test_custom_error_class_without_own_message_uses_parent_default():
    src = """
    new aesthetic InvalidNameError(wrong vibes)
    vibes on
    vibes off

    catch the vibe
    vibes on
      big yikes InvalidNameError
    vibes off
    bad vibes InvalidNameError as e
    vibes on
      manifesting e
    vibes off
    """
    assert run(src) == ["wrong vibes: that value is not it, bestie."]


def test_error_inside_function_propagates_and_is_catchable_by_caller():
    src = """
    new vibes risky()
    vibes on
      big yikes crashed out("function blew up")
    vibes off

    catch the vibe
    vibes on
      risky()
    vibes off
    bad vibes crashed out as e
    vibes on
      manifesting e
    vibes off
    """
    assert run(src) == ["function blew up"]


def test_uncaught_error_propagates_out_of_run_source():
    with pytest.raises(VibesRaised) as exc_info:
        run("big yikes crashed out(\"boom\")")
    assert "boom" in str(exc_info.value)


def test_interpreter_level_errors_are_not_caught_by_bad_vibes():
    # VibeError-flavored interpreter faults (like divide by zero) are
    # deliberately NOT catchable by the vibes-level try/except -- see
    # VibesRuntimeError's docstring.
    src = """
    catch the vibe
    vibes on
      manifesting 5 / 0
    vibes off
    bad vibes negative vibes as e
    vibes on
      manifesting "caught"
    vibes off
    """
    with pytest.raises(VibesRuntimeError):
        run(src)
