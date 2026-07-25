import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from vibes.interpreter import run_source, VibesRuntimeError


def run(src):
    out = []
    run_source(src, output=out)
    return out


def test_basic_instantiation_and_method_call():
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

    p vibes with Person("bestie")
    p.greet()
    """
    assert run(src) == ["hey, bestie"]


def test_full_spec_example_person_and_greet():
    # exact structure from the spec's own example
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

    name vibes with "bob"
    p vibes with Person(name)
    p.greet()
    """
    assert run(src) == ["hey, bob"]


def test_attribute_read_directly():
    src = """
    new aesthetic Person
    vibes on
      new vibes __init__(self, name)
      vibes on
        self.name vibes with name
      vibes off
    vibes off

    p vibes with Person("sam")
    manifesting p.name
    """
    assert run(src) == ["sam"]


def test_attribute_can_be_reassigned():
    src = """
    new aesthetic Counter
    vibes on
      new vibes __init__(self)
      vibes on
        self.count vibes with 0
      vibes off

      new vibes bump(self)
      vibes on
        self.count vibes with self.count + 1
      vibes off
    vibes off

    c vibes with Counter()
    c.bump()
    c.bump()
    c.bump()
    manifesting c.count
    """
    assert run(src) == ["3"]


def test_instance_without_init_still_works():
    src = """
    new aesthetic Thing
    vibes on
      new vibes describe(self)
      vibes on
        manifesting "just a thing"
      vibes off
    vibes off

    t vibes with Thing()
    t.describe()
    """
    assert run(src) == ["just a thing"]


def test_two_instances_have_independent_state():
    src = """
    new aesthetic Person
    vibes on
      new vibes __init__(self, name)
      vibes on
        self.name vibes with name
      vibes off
    vibes off

    a vibes with Person("alice")
    b vibes with Person("bianca")
    manifesting a.name
    manifesting b.name
    """
    assert run(src) == ["alice", "bianca"]


def test_single_inheritance_method_lookup():
    src = """
    new aesthetic Animal
    vibes on
      new vibes speak(self)
      vibes on
        manifesting "some generic sound"
      vibes off
    vibes off

    new aesthetic Dog(Animal)
    vibes on
      new vibes fetch(self)
      vibes on
        manifesting "fetching!"
      vibes off
    vibes off

    d vibes with Dog()
    d.speak()
    d.fetch()
    """
    assert run(src) == ["some generic sound", "fetching!"]


def test_subclass_can_override_method():
    src = """
    new aesthetic Animal
    vibes on
      new vibes speak(self)
      vibes on
        manifesting "..."
      vibes off
    vibes off

    new aesthetic Dog(Animal)
    vibes on
      new vibes speak(self)
      vibes on
        manifesting "woof"
      vibes off
    vibes off

    d vibes with Dog()
    d.speak()
    """
    assert run(src) == ["woof"]


def test_subclass_init_can_call_parent_style_setup():
    # not testing super() (not in spec) -- just confirming inherited
    # __init__ works when the subclass doesn't define its own
    src = """
    new aesthetic Animal
    vibes on
      new vibes __init__(self, name)
      vibes on
        self.name vibes with name
      vibes off
    vibes off

    new aesthetic Dog(Animal)
    vibes on
      new vibes bark(self)
      vibes on
        manifesting self.name + " says woof"
      vibes off
    vibes off

    d vibes with Dog("rex")
    d.bark()
    """
    assert run(src) == ["rex says woof"]


def test_undefined_attribute_raises_runtime_error():
    src = """
    new aesthetic Empty
    vibes on
      new vibes noop(self)
      vibes on
      vibes off
    vibes off

    e vibes with Empty()
    manifesting e.ghost
    """
    with pytest.raises(VibesRuntimeError) as exc_info:
        run(src)
    assert "left on read" in str(exc_info.value)


def test_undefined_method_raises_runtime_error():
    src = """
    new aesthetic Empty
    vibes on
      new vibes noop(self)
      vibes on
      vibes off
    vibes off

    e vibes with Empty()
    e.ghost_method()
    """
    with pytest.raises(VibesRuntimeError) as exc_info:
        run(src)
    assert "left on read" in str(exc_info.value)


def test_instantiating_with_wrong_superclass_name_raises_error():
    with pytest.raises(VibesRuntimeError):
        run("""
        x vibes with 5

        new aesthetic Dog(x)
        vibes on
        vibes off
        """)
