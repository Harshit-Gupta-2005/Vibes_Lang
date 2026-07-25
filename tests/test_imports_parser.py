import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.lexer import tokenize
from vibes.parser import parse, VibesParseError
from vibes import ast_nodes as ast


def parse_src(src):
    return parse(tokenize(src))


def test_channeling_math():
    prog = parse_src("channeling math")
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.Import)
    assert stmt.module_name == "math"


def test_absorbing_with_prompt():
    prog = parse_src('name vibes with absorbing "what\'s your name?"')
    stmt = prog.statements[0]
    assert isinstance(stmt.expr, ast.Input)
    assert stmt.expr.prompt.value == "what's your name?"


def test_absorbing_with_no_prompt():
    prog = parse_src("manifesting absorbing")
    expr = prog.statements[0].expr
    assert isinstance(expr, ast.Input)
    assert expr.prompt is None


def test_module_attribute_access_after_channeling():
    prog = parse_src("""
    channeling math
    manifesting math.pi
    """)
    assert isinstance(prog.statements[0], ast.Import)
    get_expr = prog.statements[1].expr
    assert isinstance(get_expr, ast.Get)
    assert get_expr.attr == "pi"


def test_module_method_call_after_channeling():
    prog = parse_src("""
    channeling math
    manifesting math.sqrt(16)
    """)
    call_expr = prog.statements[1].expr
    assert isinstance(call_expr, ast.MethodCall)
    assert call_expr.method == "sqrt"
    assert len(call_expr.args) == 1

