import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.lexer import tokenize
from vibes.parser import parse, VibesParseError
from vibes import ast_nodes as ast
from vibes.keywords import TokenType as T


def parse_src(src):
    return parse(tokenize(src))


def test_if_only():
    prog = parse_src("""
    it's giving immaculate vibes
    vibes on
      manifesting 1
    vibes off
    """)
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.If)
    assert len(stmt.branches) == 1
    cond, body = stmt.branches[0]
    assert cond.value is True
    assert len(body) == 1


def test_if_elif_else_chain():
    prog = parse_src("""
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
    """)
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.If)
    assert len(stmt.branches) == 3
    assert stmt.branches[0][0].op == T.GT
    assert stmt.branches[1][0].op == T.EQ
    assert stmt.branches[2][0] is None  # else branch


def test_if_without_else():
    prog = parse_src("""
    it's giving immaculate vibes
    vibes on
      manifesting 1
    vibes off
    """)
    assert len(prog.statements[0].branches) == 1


def test_while_loop():
    prog = parse_src("""
    keep the vibes going x less vibes than 10
    vibes on
      manifesting x
    vibes off
    """)
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.While)
    assert stmt.cond.op == T.LT
    assert len(stmt.body) == 1


def test_for_loop_with_range_call():
    prog = parse_src("""
    vibing through i in range(10)
    vibes on
      manifesting i
    vibes off
    """)
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.For)
    assert stmt.var_name == "i"
    assert isinstance(stmt.iterable, ast.Call)
    assert stmt.iterable.callee == "range"
    assert stmt.iterable.args[0].value == 10


def test_call_with_multiple_args():
    prog = parse_src("manifesting range(1, 10)")
    call = prog.statements[0].expr
    assert isinstance(call, ast.Call)
    assert len(call.args) == 2


def test_break_and_continue():
    prog = parse_src("""
    keep the vibes going immaculate vibes
    vibes on
      no more vibes
    vibes off
    """)
    body = prog.statements[0].body
    assert isinstance(body[0], ast.Break)

    prog2 = parse_src("""
    keep the vibes going immaculate vibes
    vibes on
      next vibe
    vibes off
    """)
    body2 = prog2.statements[0].body
    assert isinstance(body2[0], ast.Continue)


def test_nested_if_inside_while():
    prog = parse_src("""
    keep the vibes going immaculate vibes
    vibes on
      it's giving x vibe match 5
      vibes on
        no more vibes
      vibes off
    vibes off
    """)
    while_stmt = prog.statements[0]
    inner_if = while_stmt.body[0]
    assert isinstance(inner_if, ast.If)
    assert isinstance(inner_if.branches[0][1][0], ast.Break)


def test_mismatched_block_raises_parse_error():
    with pytest.raises(VibesParseError) as exc_info:
        parse_src("""
        it's giving immaculate vibes
        vibes on
          manifesting 1
        """)  # missing vibes off
    assert "mismatched vibes on/off" in str(exc_info.value)


def test_for_loop_missing_in_raises_parse_error():
    with pytest.raises(VibesParseError):
        parse_src("""
        vibing through i range(10)
        vibes on
          manifesting i
        vibes off
        """)


def test_count_up_loop_fixture_parses_end_to_end():
    # this is the loop/if body from the spec's count_up function, lifted
    # out to bare top-level statements since functions aren't implemented
    # until step 5 -- should now parse (and, in the interpreter test file,
    # run) completely.
    src = open(
        os.path.join(os.path.dirname(__file__), "fixtures", "count_up_loop.vibes")
    ).read()
    prog = parse_src(src)
    assert len(prog.statements) == 3  # assign, for-loop, print
