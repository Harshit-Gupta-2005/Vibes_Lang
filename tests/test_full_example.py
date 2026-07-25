"""
The final integration test: the spec's own full example program
(tests/fixtures/full_example.vibes), completely unmodified, exercising
every feature built across all 9 previous steps in one program --
channeling, a class with __init__/methods, a function with a loop and
break, main_character_vibes, absorbing, try/except/finally, and
that's a wrap.
"""

import sys, os, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vibes.interpreter import run_source

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "full_example.vibes")
VIBES_LANG_ROOT = os.path.join(os.path.dirname(__file__), "..")


def test_full_example_via_run_source():
    with open(FIXTURE_PATH) as f:
        source = f.read()

    out = []
    run_source(source, output=out, input_fn=lambda prompt: "Bob")

    assert out == ["hey, Bob", "10", "that's a wrap"]


def test_full_example_via_real_cli_subprocess():
    result = subprocess.run(
        [sys.executable, "-m", "vibes", "run", FIXTURE_PATH],
        cwd=VIBES_LANG_ROOT,
        input="Bob\n",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    # stdout includes the un-newlined input prompt text right before the
    # first manifesting output, since real input() doesn't add a newline
    # after the prompt
    assert "hey, Bob" in result.stdout
    assert "10" in result.stdout
    assert "that's a wrap" in result.stdout
    # and in the right order
    assert result.stdout.index("hey, Bob") < result.stdout.index("10") < result.stdout.index("that's a wrap")
