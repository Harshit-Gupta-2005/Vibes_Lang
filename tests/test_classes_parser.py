import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.lexer import tokenize
from vibes.parser import parse, VibesParseError
from vibes import ast_nodes as ast


def parse_src(src):
    return parse(tokenize(src))


def test_empty_class():
    prog = parse_src("""
    new aesthetic Animal
    vibes on
    vibes off
    """)
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.ClassDef)
    assert stmt.name == "Animal"
    assert stmt.superclass_name is None
    assert stmt.body == []


def test_class_with_inheritance():
    prog = parse_src("""
    new aesthetic Dog(Animal)
    vibes on
    vibes off
    """)
    stmt = prog.statements[0]
    assert stmt.superclass_name == "Animal"


def test_class_with_methods():
    prog = parse_src("""
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
    """)
    stmt = prog.statements[0]
    assert len(stmt.body) == 2
    assert all(isinstance(m, ast.FuncDef) for m in stmt.body)
    assert stmt.body[0].name == "__init__"
    assert stmt.body[1].name == "greet"


def test_attribute_assignment_inside_method():
    prog = parse_src("""
    new aesthetic Person
    vibes on
      new vibes __init__(self, name)
      vibes on
        self.name vibes with name
      vibes off
    vibes off
    """)
    init_body = prog.statements[0].body[0].body
    setattr_stmt = init_body[0]
    assert isinstance(setattr_stmt, ast.SetAttr)
    assert isinstance(setattr_stmt.obj, ast.Name)
    assert setattr_stmt.obj.name == "self"
    assert setattr_stmt.attr == "name"


def test_attribute_read_in_expression():
    prog = parse_src("manifesting self.name")
    expr = prog.statements[0].expr
    assert isinstance(expr, ast.Get)
    assert expr.attr == "name"


def test_method_call():
    prog = parse_src("p.greet()")
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.ExprStmt)
    assert isinstance(stmt.expr, ast.MethodCall)
    assert stmt.expr.method == "greet"
    assert stmt.expr.args == []


def test_method_call_with_args():
    prog = parse_src("manifesting p.distance_to(other)")
    call = prog.statements[0].expr
    assert isinstance(call, ast.MethodCall)
    assert call.method == "distance_to"
    assert len(call.args) == 1


def test_instantiation_is_a_plain_call():
    prog = parse_src("p vibes with Person(name)")
    stmt = prog.statements[0]
    assert isinstance(stmt, ast.Assign)
    assert isinstance(stmt.expr, ast.Call)
    assert stmt.expr.callee == "Person"


def test_class_body_with_non_method_statement_raises_parse_error():
    with pytest.raises(VibesParseError):
        parse_src("""
        new aesthetic Person
        vibes on
          x vibes with 5
        vibes off
        """)


def test_full_spec_person_class_and_usage_parses():
    src = """
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

    p vibes with Person(name)
    p.greet()
    """
    prog = parse_src(src)
    assert len(prog.statements) == 3
    assert isinstance(prog.statements[0], ast.ClassDef)
    assert isinstance(prog.statements[1], ast.Assign)
    assert isinstance(prog.statements[2], ast.ExprStmt)

