import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.environment import Environment, VibesNameError


def test_define_and_get():
    env = Environment()
    env.define("x", 5)
    assert env.get("x") == 5


def test_undefined_variable_raises_name_error():
    env = Environment()
    with pytest.raises(VibesNameError) as exc_info:
        env.get("ghost")
    assert "undefined variable 'ghost'" in str(exc_info.value)


def test_assign_creates_binding_if_not_present():
    env = Environment()
    env.assign("x", 10)
    assert env.get("x") == 10


def test_assign_overwrites_existing_binding():
    env = Environment()
    env.define("x", 1)
    env.assign("x", 2)
    assert env.get("x") == 2


def test_child_scope_can_read_parent_scope():
    parent = Environment()
    parent.define("x", 100)
    child = Environment(parent=parent)
    assert child.get("x") == 100


def test_child_scope_assign_updates_parent_binding():
    parent = Environment()
    parent.define("x", 1)
    child = Environment(parent=parent)
    child.assign("x", 99)
    assert parent.get("x") == 99
    assert "x" not in child.values  # wasn't shadowed, the parent's binding was updated


def test_child_scope_define_shadows_parent():
    parent = Environment()
    parent.define("x", 1)
    child = Environment(parent=parent)
    child.define("x", 2)
    assert child.get("x") == 2
    assert parent.get("x") == 1
