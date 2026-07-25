import sys, os, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

VIBES_LANG_ROOT = os.path.join(os.path.dirname(__file__), "..")


def run_cli(source, extra_args=None):
    """Writes `source` to a temp .vibes file and runs it via
    `python3 -m vibes run <file>`, returning (returncode, stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".vibes", delete=False) as f:
        f.write(source)
        path = f.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "vibes", "run", path] + (extra_args or []),
            cwd=VIBES_LANG_ROOT,
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout, result.stderr
    finally:
        os.unlink(path)


def test_cli_runs_a_simple_program():
    code, out, err = run_cli('manifesting "hello from a real subprocess"')
    assert code == 0
    assert out == "hello from a real subprocess\n"
    assert err == ""


def test_cli_runs_arithmetic_and_variables():
    code, out, err = run_cli("""
    x vibes with 6 * 7
    manifesting x
    """)
    assert code == 0
    assert out == "42\n"


def test_cli_missing_file_gives_clean_error():
    result = subprocess.run(
        [sys.executable, "-m", "vibes", "run", "/definitely/not/a/real/path.vibes"],
        cwd=VIBES_LANG_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "doesn't exist" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_parse_error_gives_clean_error_not_a_traceback():
    code, out, err = run_cli("""
    it's giving immaculate vibes
    vibes on
      manifesting "oops"
    """)
    assert code == 1
    assert "mismatched vibes on/off" in err
    assert "Traceback" not in err


def test_cli_uncaught_raised_error_gives_clean_error_not_a_traceback():
    code, out, err = run_cli('big yikes crashed out("everything is on fire")')
    assert code == 1
    assert "everything is on fire" in err
    assert "Traceback" not in err


def test_cli_undefined_variable_gives_clean_error_not_a_traceback():
    # regression test: VibesNameError (raised by Environment.get) used to
    # escape the CLI's exception handling entirely and print a raw Python
    # traceback instead of a clean VibeError line.
    code, out, err = run_cli("manifesting this_variable_was_never_defined")
    assert code == 1
    assert "undefined variable" in err
    assert "Traceback" not in err


def test_cli_no_arguments_shows_usage():
    result = subprocess.run(
        [sys.executable, "-m", "vibes"],
        cwd=VIBES_LANG_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "usage" in result.stderr.lower()


def test_cli_full_person_class_example():
    code, out, err = run_cli("""
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

    main_character_vibes
    vibes on
      p vibes with Person("bestie")
      p.greet()
      that's a wrap
    vibes off
    """)
    assert code == 0
    assert out == "hey, bestie\n"
