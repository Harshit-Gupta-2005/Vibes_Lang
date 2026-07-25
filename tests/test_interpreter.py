import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.interpreter import run_source, VibesRuntimeError


def run(src):
    out = []
    run_source(src, output=out)
    return out


def test_print_number():
    assert run("manifesting 42") == ["42"]


def test_print_string():
    assert run('manifesting "hello"') == ["hello"]


def test_arithmetic():
    assert run("manifesting 1 + 2 * 3") == ["7"]
    assert run("manifesting (1 + 2) * 3") == ["9"]
    assert run("manifesting 10 / 4") == ["2.5"]


def test_comparisons():
    assert run("manifesting 5 more vibes than 3") == ["immaculate vibes"]
    assert run("manifesting 5 less vibes than 3") == ["dead vibes"]
    assert run("manifesting 5 vibe match 5") == ["immaculate vibes"]
    assert run("manifesting 5 vibe doesn't match 5") == ["dead vibes"]
    assert run("manifesting 5 no less vibes than 5") == ["immaculate vibes"]
    assert run("manifesting 5 no more vibes than 4") == ["dead vibes"]


def test_boolean_and_none_stringify_as_vibes_flavored_text():
    assert run("manifesting immaculate vibes") == ["immaculate vibes"]
    assert run("manifesting dead vibes") == ["dead vibes"]
    assert run("manifesting no vibes") == ["no vibes"]


def test_unary_minus():
    assert run("manifesting -5 + 10") == ["5"]


def test_divide_by_zero_raises_vibes_runtime_error():
    with pytest.raises(VibesRuntimeError) as exc_info:
        run("manifesting 5 / 0")
    assert "divide by zero" in str(exc_info.value)


def test_assignment_and_reference():
    assert run("x vibes with 5\nmanifesting x") == ["5"]


def test_reassignment():
    assert run("x vibes with 1\nx vibes with 2\nmanifesting x") == ["2"]


def test_assignment_using_previous_value():
    assert run("x vibes with 5\nx vibes with x + 1\nmanifesting x") == ["6"]


def test_assignment_with_type_prefix_is_inert():
    assert run('word vibes name vibes with "bob"\nmanifesting name') == ["bob"]


def test_undefined_variable_raises_name_error():
    from vibes.environment import VibesNameError
    with pytest.raises(VibesNameError) as exc_info:
        run("manifesting ghost")
    assert "undefined variable 'ghost'" in str(exc_info.value)


def test_multiple_statements_execute_in_order():
    assert run('manifesting 1\nmanifesting 2\nmanifesting 3') == ["1", "2", "3"]


def test_full_example_only_prints_statements_before_unsupported_syntax():
    # not a real test of the full program (functions/classes aren't
    # implemented yet) -- just confirms the pipeline doesn't crash weirdly
    # on a plain print-only snippet extracted from the spec's style.
    assert run('manifesting "hey, " + "bestie"') == ["hey, bestie"]
