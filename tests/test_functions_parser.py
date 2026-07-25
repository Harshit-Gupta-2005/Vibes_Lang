import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.lexer import tokenize
from vibes.parser import parse, VibesParseError
from vibes import ast_nodes as ast
from vibes.keywords import TokenType as T


def parse_src(src):
    return parse(tokenize(src))


def test_func_def_no_params():
    prog = parse_src("""
    new vibes greet()
    vibes on
      manifesting "hi"
    vibes off
    """)
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.FuncDef)
    assert stmt.name == "greet"
    assert stmt.params == []
    assert len(stmt.body) == 1


def test_func_def_with_params():
    prog = parse_src("""
    new vibes add(a, b)
    vibes on
      sending vibes a + b
    vibes off
    """)
    stmt = prog.statements[0]
    assert stmt.params == ["a", "b"]
    assert isinstance(stmt.body[0], ast.Return)


def test_return_with_expression():
    prog = parse_src("""
    new vibes get_num()
    vibes on
      sending vibes 42
    vibes off
    """)
    ret = prog.statements[0].body[0]
    assert isinstance(ret, ast.Return)
    assert ret.expr.value == 42


def test_function_call_as_expression():
    prog = parse_src("manifesting add(1, 2)")
    call = prog.statements[0].expr
    assert isinstance(call, ast.Call)
    assert call.callee == "add"
    assert len(call.args) == 2


def test_function_call_as_bare_statement():
    prog = parse_src("greet()")
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.ExprStmt)
    assert isinstance(stmt.expr, ast.Call)
    assert stmt.expr.callee == "greet"


def test_function_call_no_args():
    prog = parse_src("manifesting greet()")
    call = prog.statements[0].expr
    assert call.args == []


def test_recursive_looking_function_parses():
    prog = parse_src("""
    new vibes countdown(n)
    vibes on
      it's giving n vibe match 0
      vibes on
        sending vibes 0
      vibes off
      sending vibes countdown(n - 1)
    vibes off
    """)
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.FuncDef)
    assert isinstance(stmt.body[1], ast.Return)

