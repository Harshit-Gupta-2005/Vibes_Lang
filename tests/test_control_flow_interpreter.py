import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.interpreter import run_source, VibesRuntimeError


def run(src):
    out = []
    run_source(src, output=out)
    return out


def test_if_true_branch():
    assert run("""
    it's giving immaculate vibes
    vibes on
      manifesting "yes"
    vibes off
    """) == ["yes"]


def test_if_false_no_else_prints_nothing():
    assert run("""
    it's giving dead vibes
    vibes on
      manifesting "yes"
    vibes off
    """) == []


def test_if_elif_else_picks_right_branch():
    src = """
    x vibes with 0
    it's giving x more vibes than 0
    vibes on
      manifesting "positive"
    vibes off
    or it's giving x vibe match 0
    vibes on
      manifesting "zero"
    vibes off
    or not
    vibes on
      manifesting "negative"
    vibes off
    """
    assert run(src) == ["zero"]

    src_negative = src.replace("x vibes with 0", "x vibes with -5")
    assert run(src_negative) == ["negative"]

    src_positive = src.replace("x vibes with 0", "x vibes with 5")
    assert run(src_positive) == ["positive"]


def test_while_loop_counts():
    src = """
    x vibes with 0
    keep the vibes going x less vibes than 5
    vibes on
      manifesting x
      x vibes with x + 1
    vibes off
    """
    assert run(src) == ["0", "1", "2", "3", "4"]


def test_for_loop_over_range():
    src = """
    vibing through i in range(3)
    vibes on
      manifesting i
    vibes off
    """
    assert run(src) == ["0", "1", "2"]


def test_break_exits_loop_early():
    src = """
    vibing through i in range(10)
    vibes on
      it's giving i vibe match 3
      vibes on
        no more vibes
      vibes off
      manifesting i
    vibes off
    """
    assert run(src) == ["0", "1", "2"]


def test_continue_skips_iteration():
    src = """
    vibing through i in range(5)
    vibes on
      it's giving i vibe match 2
      vibes on
        next vibe
      vibes off
      manifesting i
    vibes off
    """
    assert run(src) == ["0", "1", "3", "4"]


def test_nested_loops_with_break_only_exits_inner():
    src = """
    vibing through i in range(2)
    vibes on
      vibing through j in range(3)
      vibes on
        it's giving j vibe match 1
        vibes on
          no more vibes
        vibes off
        manifesting j
      vibes off
    vibes off
    """
    assert run(src) == ["0", "0"]


def test_break_outside_loop_raises_runtime_error():
    with pytest.raises(VibesRuntimeError) as exc_info:
        run("no more vibes")
    assert "outside of a loop" in str(exc_info.value)


def test_continue_outside_loop_raises_runtime_error():
    with pytest.raises(VibesRuntimeError) as exc_info:
        run("next vibe")
    assert "outside of a loop" in str(exc_info.value)


def test_builtin_len_and_str():
    assert run('manifesting len("hello")') == ["5"]
    assert run("manifesting str(42)") == ["42"]


def test_count_up_loop_fixture_runs_and_produces_expected_sum():
    src = open(
        os.path.join(os.path.dirname(__file__), "fixtures", "count_up_loop.vibes")
    ).read()
    # matches the spec's own count_up(10) semantics: sums 0..4 then breaks at i==5
    assert run(src) == ["10"]
