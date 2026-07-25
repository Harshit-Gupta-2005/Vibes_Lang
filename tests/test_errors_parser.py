import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.lexer import tokenize
from vibes.parser import parse, VibesParseError
from vibes import ast_nodes as ast


def parse_src(src):
    return parse(tokenize(src))


def test_bare_try_no_except():
    prog = parse_src("""
    catch the vibe
    vibes on
      manifesting 1
    vibes off
    """)
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.Try)
    assert stmt.handlers == []
    assert stmt.else_body is None
    assert stmt.finally_body is None


def test_try_with_single_except():
    prog = parse_src("""
    catch the vibe
    vibes on
      x vibes with 1
    vibes off
    bad vibes wrong vibes as e
    vibes on
      manifesting e
    vibes off
    """)
    stmt = prog.statements[0]
    assert len(stmt.handlers) == 1
    handler = stmt.handlers[0]
    assert handler.error_type == "ERR_VALUE"
    assert handler.var_name == "e"


def test_try_with_multiple_except_and_finally():
    prog = parse_src("""
    catch the vibe
    vibes on
      x vibes with 1
    vibes off
    bad vibes wrong vibes as e
    vibes on
      manifesting "wrong"
    vibes off
    bad vibes negative vibes as e
    vibes on
      manifesting "catchall"
    vibes off
    good vibes only
    vibes on
      manifesting "always"
    vibes off
    """)
    stmt = prog.statements[0]
    assert len(stmt.handlers) == 2
    assert stmt.handlers[0].error_type == "ERR_VALUE"
    assert stmt.handlers[1].error_type == "ERR_EXCEPTION"
    assert stmt.finally_body is not None
    assert len(stmt.finally_body) == 1


def test_try_with_else_clause():
    prog = parse_src("""
    catch the vibe
    vibes on
      x vibes with 1
    vibes off
    bad vibes wrong vibes as e
    vibes on
      manifesting "err"
    vibes off
    or not
    vibes on
      manifesting "no error happened"
    vibes off
    """)
    stmt = prog.statements[0]
    assert stmt.else_body is not None
    assert stmt.finally_body is None


def test_except_without_as_binding():
    prog = parse_src("""
    catch the vibe
    vibes on
      x vibes with 1
    vibes off
    bad vibes wrong vibes
    vibes on
      manifesting "no binding needed"
    vibes off
    """)
    handler = prog.statements[0].handlers[0]
    assert handler.var_name is None


def test_raise_with_custom_message():
    prog = parse_src('big yikes wrong vibes("not a number")')
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.Raise)
    assert stmt.error_type == "ERR_VALUE"
    assert stmt.message_expr.value == "not a number"


def test_raise_without_message_uses_default():
    prog = parse_src("big yikes wrong vibes")
    stmt = prog.statements[0]
    assert stmt.error_type == "ERR_VALUE"
    assert stmt.message_expr is None


def test_raise_all_fourteen_error_type_keywords_parse():
    phrases = [
        "wrong vibes", "mixed vibes", "crashed out", "ghosted", "out of pocket",
        "negative vibes", "cap", "left on read", "who?", "spiraling",
        "still cooking", "pressed", "no service", "timed out",
    ]
    for phrase in phrases:
        prog = parse_src(f"big yikes {phrase}")
        assert isinstance(prog.statements[0], ast.Raise), phrase


def test_class_inheriting_from_builtin_error_type():
    prog = parse_src("""
    new aesthetic MyError(wrong vibes)
    vibes on
    vibes off
    """)
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.ClassDef)
    assert stmt.superclass_name == "ERR_VALUE"


def test_class_inheriting_from_catchall_error_type():
    prog = parse_src("""
    new aesthetic MyError(negative vibes)
    vibes on
    vibes off
    """)
    assert prog.statements[0].superclass_name == "ERR_EXCEPTION"


def test_raise_with_wrong_number_of_message_args_raises_parse_error():
    with pytest.raises(VibesParseError):
        parse_src('big yikes wrong vibes("a", "b")')


def test_full_spec_error_handling_example_parses():
    src = """
    catch the vibe
    vibes on
      p vibes with Person(name)
      p.greet()
      result vibes with count_up(10)
      manifesting result
    vibes off
    bad vibes wrong vibes as e
    vibes on
      manifesting "bad vibes detected: " + e
    vibes off
    bad vibes negative vibes as e
    vibes on
      manifesting "something went off: " + e
    vibes off
    good vibes only
    vibes on
      manifesting "that's a wrap"
    vibes off
    """
    prog = parse_src(src)
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.Try)
    assert len(stmt.handlers) == 2
    assert stmt.finally_body is not None

