import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.interpreter import run_source, VibesRuntimeError


def run(src):
    out = []
    run_source(src, output=out)
    return out


def test_simple_function_call_and_return():
    src = """
    new vibes add(a, b)
    vibes on
      sending vibes a + b
    vibes off

    manifesting add(2, 3)
    """
    assert run(src) == ["5"]


def test_function_with_no_return_gives_no_vibes():
    src = """
    new vibes greet()
    vibes on
      manifesting "hi"
    vibes off

    x vibes with greet()
    manifesting x
    """
    assert run(src) == ["hi", "no vibes"]


def test_function_call_as_bare_statement():
    src = """
    new vibes greet()
    vibes on
      manifesting "hey bestie"
    vibes off

    greet()
    """
    assert run(src) == ["hey bestie"]


def test_recursion():
    src = """
    new vibes factorial(n)
    vibes on
      it's giving n no more vibes than 1
      vibes on
        sending vibes 1
      vibes off
      sending vibes n * factorial(n - 1)
    vibes off

    manifesting factorial(5)
    """
    assert run(src) == ["120"]


def test_closures_capture_defining_scope():
    # function reads a global variable that exists at call time via its
    # closure, not via re-resolution of caller's locals
    src = """
    multiplier vibes with 10

    new vibes scale(x)
    vibes on
      sending vibes x * multiplier
    vibes off

    manifesting scale(5)
    """
    assert run(src) == ["50"]


def test_function_locals_do_not_leak_to_global_scope():
    src = """
    new vibes make_local()
    vibes on
      secret vibes with 99
      sending vibes secret
    vibes off

    result vibes with make_local()
    manifesting result
    """
    out = run(src)
    assert out == ["99"]
    # `secret` should not exist in the global scope after the call
    from vibes.environment import VibesNameError
    with pytest.raises(VibesNameError):
        run("manifesting secret")


def test_function_params_shadow_outer_variable_of_same_name():
    src = """
    x vibes with 100

    new vibes double(x)
    vibes on
      sending vibes x * 2
    vibes off

    manifesting double(5)
    manifesting x
    """
    assert run(src) == ["10", "100"]


def test_wrong_number_of_arguments_raises_runtime_error():
    src = """
    new vibes add(a, b)
    vibes on
      sending vibes a + b
    vibes off

    manifesting add(1)
    """
    with pytest.raises(VibesRuntimeError) as exc_info:
        run(src)
    assert "wanted 2" in str(exc_info.value)


def test_return_outside_function_raises_runtime_error():
    with pytest.raises(VibesRuntimeError) as exc_info:
        run("sending vibes 5")
    assert "outside of a function" in str(exc_info.value)


def test_loop_inside_function_with_break():
    src = """
    new vibes first_over(limit)
    vibes on
      vibing through i in range(100)
      vibes on
        it's giving i more vibes than limit
        vibes on
          sending vibes i
        vibes off
      vibes off
      sending vibes no vibes
    vibes off

    manifesting first_over(5)
    """
    assert run(src) == ["6"]
