import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.interpreter import run_source, VibesRuntimeError


def run(src, input_fn=None):
    out = []
    run_source(src, output=out, input_fn=input_fn)
    return out


def test_channeling_math_and_calling_a_function():
    assert run("""
    channeling math
    manifesting math.sqrt(16)
    """) == ["4.0"]


def test_channeling_math_and_reading_a_constant():
    out = run("""
    channeling math
    manifesting math.pi
    """)
    assert out[0].startswith("3.14")


def test_channeling_unknown_module_raises_runtime_error():
    with pytest.raises(VibesRuntimeError) as exc_info:
        run("channeling this_module_does_not_exist_at_all")
    assert "doesn't exist" in str(exc_info.value)


def test_absorbing_with_prompt_uses_input_fn():
    seen_prompts = []

    def fake_input(prompt):
        seen_prompts.append(prompt)
        return "bestie"

    out = run('''
    name vibes with absorbing "what's your name?"
    manifesting "hey, " + name
    ''', input_fn=fake_input)

    assert out == ["hey, bestie"]
    assert seen_prompts == ["what's your name?"]


def test_absorbing_with_no_prompt():
    out = run("""
    x vibes with absorbing
    manifesting x
    """, input_fn=lambda prompt: "42")
    assert out == ["42"]


def test_channeling_then_using_module_inside_a_function():
    assert run("""
    channeling math

    new vibes hypotenuse(a, b)
    vibes on
      sending vibes math.sqrt(a * a + b * b)
    vibes off

    manifesting hypotenuse(3, 4)
    """) == ["5.0"]
