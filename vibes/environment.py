"""
Variable scoping for Vibes.

A single Environment is a flat dict of name -> value, with an optional
parent for nested scopes. Only the global scope is used right now (step 3),
but function calls (step 5) will each get a child Environment whose parent
is the defining scope, so lookups chain outward -- same model as Python's
closures.
"""


class VibesNameError(Exception):
    """Raised for undefined-variable lookups -- matches the spec's own
    VibeError wording, not a generic KeyError."""
    pass


class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.values = {}

    def define(self, name, value):
        """Create or overwrite a binding in *this* scope."""
        self.values[name] = value

    def get(self, name):
        env = self
        while env is not None:
            if name in env.values:
                return env.values[name]
            env = env.parent
        raise VibesNameError(
            f"VibeError: undefined variable '{name}' — it literally does not exist, bestie."
        )

    def assign(self, name, value):
        """Assign to an existing binding, searching outward through parent
        scopes (like Python). If the name isn't bound anywhere yet, this
        creates it in the current (innermost) scope -- Vibes has no
        forced declarations, so first assignment doubles as definition."""
        env = self
        while env is not None:
            if name in env.values:
                env.values[name] = value
                return
            env = env.parent
        self.values[name] = value
