import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.lexer import tokenize
from vibes.parser import parse, VibesParseError
from vibes import ast_nodes as ast
from vibes.keywords import TokenType as T


def parse_src(src):
    return parse(tokenize(src))


def test_print_number_literal():
    prog = parse_src("manifesting 42")
    assert len(prog.statements) == 1
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.Print)
    assert isinstance(stmt.expr, ast.Literal)
    assert stmt.expr.value == 42


def test_print_string_literal():
    prog = parse_src('manifesting "hello"')
    assert prog.statements[0].expr.value == "hello"


def test_arithmetic_precedence():
    # 1 + 2 * 3 should parse as 1 + (2 * 3), i.e. top node is PLUS
    prog = parse_src("manifesting 1 + 2 * 3")
    expr = prog.statements[0].expr
    assert isinstance(expr, ast.BinOp)
    assert expr.op == T.PLUS
    assert isinstance(expr.left, ast.Literal) and expr.left.value == 1
    assert isinstance(expr.right, ast.BinOp)
    assert expr.right.op == T.STAR


def test_parens_override_precedence():
    prog = parse_src("manifesting (1 + 2) * 3")
    expr = prog.statements[0].expr
    assert expr.op == T.STAR
    assert isinstance(expr.left, ast.BinOp)
    assert expr.left.op == T.PLUS


def test_comparison_lower_precedence_than_arithmetic():
    # 1 + 1 vibe match 2  ==  (1 + 1) == 2
    prog = parse_src("manifesting 1 + 1 vibe match 2")
    expr = prog.statements[0].expr
    assert expr.op == T.EQ
    assert isinstance(expr.left, ast.BinOp) and expr.left.op == T.PLUS


def test_unary_minus():
    prog = parse_src("manifesting -5")
    expr = prog.statements[0].expr
    assert isinstance(expr, ast.UnaryOp)
    assert expr.op == T.MINUS
    assert expr.operand.value == 5


def test_double_unary_minus():
    prog = parse_src("manifesting - -5")
    expr = prog.statements[0].expr
    assert isinstance(expr, ast.UnaryOp)
    assert isinstance(expr.operand, ast.UnaryOp)


def test_boolean_and_none_literals():
    assert parse_src("manifesting immaculate vibes").statements[0].expr.value is True
    assert parse_src("manifesting dead vibes").statements[0].expr.value is False
    assert parse_src("manifesting no vibes").statements[0].expr.value is None


def test_multiple_statements():
    prog = parse_src('manifesting 1\nmanifesting 2\nmanifesting 3')
    assert len(prog.statements) == 3


def test_only_one_main_character_vibes_allowed():
    with pytest.raises(VibesParseError) as exc_info:
        parse_src("""
        main_character_vibes
        vibes on
        vibes off

        main_character_vibes
        vibes on
        vibes off
        """)
    assert "only have one main_character_vibes" in str(exc_info.value)


def test_simple_assignment():
    prog = parse_src("x vibes with 5")
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.Assign)
    assert stmt.name == "x"
    assert stmt.type_hint is None
    assert stmt.expr.value == 5


def test_assignment_with_type_prefix():
    prog = parse_src('word vibes name vibes with "bob"')
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.Assign)
    assert stmt.name == "name"
    assert stmt.type_hint == T.TYPE_STRING
    assert stmt.expr.value == "bob"


def test_assignment_with_numeric_and_bool_type_prefixes():
    prog = parse_src("numeric vibes x vibes with 5")
    assert prog.statements[0].type_hint == T.TYPE_INT

    prog = parse_src("vibe or no vibe flag vibes with immaculate vibes")
    assert prog.statements[0].type_hint == T.TYPE_BOOL


def test_variable_reference_in_expression():
    prog = parse_src("manifesting x")
    expr = prog.statements[0].expr
    assert isinstance(expr, ast.Name)
    assert expr.name == "x"


def test_assignment_referencing_another_variable():
    prog = parse_src("y vibes with x + 1")
    stmt = prog.statements[0]
    assert isinstance(stmt.expr, ast.BinOp)
    assert isinstance(stmt.expr.left, ast.Name)
    assert stmt.expr.left.name == "x"


def test_reassignment_without_type_prefix():
    prog = parse_src("x vibes with 1\nx vibes with 2")
    assert len(prog.statements) == 2
    assert all(isinstance(s, ast.Assign) and s.name == "x" for s in prog.statements)


def test_incomplete_expression_raises_parse_error():
    with pytest.raises(VibesParseError):
        parse_src("manifesting 1 +")


def test_unclosed_paren_raises_parse_error():
    with pytest.raises(VibesParseError):
        parse_src("manifesting (1 + 2")
