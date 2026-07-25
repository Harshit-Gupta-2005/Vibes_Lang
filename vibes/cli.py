"""
Command-line interface for Vibes.

Usage:
    vibes run myfile.vibes
    python3 -m vibes run myfile.vibes   (works without installing anything)

Catches every layer's own exception type and prints a clean message instead
of a raw Python traceback, since none of VibesLexError / VibesParseError /
VibesRuntimeError / VibesRaised are things a Vibes programmer should ever
need to see a Python stack trace for.
"""

import sys

from .lexer import tokenize, VibesLexError
from .parser import parse, VibesParseError
from .interpreter import Interpreter, VibesRuntimeError, VibesRaised
from .environment import VibesNameError


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) < 2 or argv[0] != "run":
        print("usage: vibes run <file.vibes>", file=sys.stderr)
        return 1

    path = argv[1]
    try:
        with open(path, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(
            f"VibeError: who?: that file doesn't exist and never has. ('{path}')",
            file=sys.stderr,
        )
        return 1
    except OSError as e:
        print(f"VibeError: couldn't read '{path}': {e}", file=sys.stderr)
        return 1

    try:
        tokens = tokenize(source)
        program = parse(tokens)
        Interpreter().run(program)
    except VibesLexError as e:
        print(str(e), file=sys.stderr)
        return 1
    except VibesParseError as e:
        print(str(e), file=sys.stderr)
        return 1
    except VibesRaised as e:
        print(f"Uncaught vibes error: {e}", file=sys.stderr)
        return 1
    except VibesRuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1
    except VibesNameError as e:
        print(str(e), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
