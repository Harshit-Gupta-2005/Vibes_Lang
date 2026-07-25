"""
Interpreter for Vibes.

Covers the full language: expressions (including builtin calls,
user-defined function calls, attribute access, and method calls),
`manifesting`, variable assignment (plain and attribute), control flow
(if/elif/else, while, for, break, continue), functions (`new vibes` /
`sending vibes`) with proper lexical scoping and closures, classes
(`new aesthetic`) with single inheritance and instance state, error
handling (`catch the vibe` / `bad vibes` / `good vibes only` /
`big yikes`) with the 14 built-in error types, custom-vs-default messages,
and user classes that can inherit from a built-in error type, `channeling`
(import) with real Python modules accessible via attribute/method access,
`absorbing` (input), `main_character_vibes`, and `that's a wrap`.
"""

import importlib

from .keywords import TokenType as T, DEFAULT_ERROR_MESSAGES
from . import ast_nodes as ast
from .environment import Environment, VibesNameError


class VibesRuntimeError(Exception):
    """Interpreter-level errors -- the ones from the spec's VibeError list
    (divide by zero, undefined variable, etc), not user-raised vibes errors.
    These are NOT catchable by a Vibes program's own try/except -- they
    represent fatal interpreter faults, same spirit as an uncatchable
    SyntaxError, not something idiomatic code is expected to recover from."""
    pass


class VibesRaised(Exception):
    """Wraps a VibesInstance of an error class so a user-raised error (via
    `big yikes`) can flow through Python's real exception machinery -- this
    is what makes try/except/else/finally actually work, by reusing
    Python's own try/except/else/finally under the hood (see Interpreter's
    handling of ast.Try)."""
    def __init__(self, instance):
        self.instance = instance
        super().__init__(instance.fields.get("message", ""))

    def __str__(self):
        return str(self.instance.fields.get("message", ""))


class BreakSignal(Exception):
    """Internal control-flow signal for `no more vibes` -- caught by the
    nearest enclosing while/for loop, never seen by user code."""
    pass


class ContinueSignal(Exception):
    """Internal control-flow signal for `next vibe` -- caught by the
    nearest enclosing while/for loop, never seen by user code."""
    pass


class ReturnSignal(Exception):
    """Internal control-flow signal for `sending vibes <expr>` -- caught by
    the function call that's currently executing, never seen by user code."""
    def __init__(self, value):
        super().__init__()
        self.value = value


class ExitSignal(BaseException):
    """Internal signal for `that's a wrap` -- a clean, deliberate program
    exit. Deliberately extends BaseException rather than Exception, same
    as Python's own SystemExit: this means it still triggers `good vibes
    only` (finally) blocks while unwinding, but is never accidentally
    swallowed by a broad `bad vibes negative vibes` handler, which only
    catches VibesRaised (an Exception subclass)."""
    pass


class VibesFunction:
    """A user-defined function: the AST of its body plus the environment it
    closed over at definition time (so it can see variables from its
    enclosing scope even when called from somewhere else -- same model as
    Python closures)."""
    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure

    def __repr__(self):
        return f"<function {self.name}>"


class VibesClass:
    """A user-defined class: a name, an optional superclass, and the
    methods defined directly on it. Method lookup walks the superclass
    chain, same as Python's single inheritance.

    `default_message` is only set (non-None) on the 14 built-in error
    classes; a user class that inherits from one (e.g.
    `new aesthetic MyError(wrong vibes)`) picks up its ancestor's default
    message via find_default_message, same chain-walk as find_method."""
    def __init__(self, name, superclass, methods, default_message=None):
        self.name = name
        self.superclass = superclass  # VibesClass or None
        self.methods = methods  # dict[str, VibesFunction]
        self.default_message = default_message

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.find_method(name)
        return None

    def find_default_message(self):
        if self.default_message is not None:
            return self.default_message
        if self.superclass is not None:
            return self.superclass.find_default_message()
        return "negative vibes: something went wrong and it's giving chaos."

    def is_or_inherits_from(self, other):
        """True if this class *is* `other` or has it somewhere up its
        superclass chain -- used to match a raised error against an
        except clause's target type."""
        cls = self
        while cls is not None:
            if cls is other:
                return True
            cls = cls.superclass
        return False

    def __repr__(self):
        return f"<class {self.name}>"


class VibesInstance:
    """An instance of a VibesClass. Fields are just a plain dict set via
    `self.attr vibes with ...` inside methods -- there's no fixed schema,
    matching Python's own instances."""
    def __init__(self, cls):
        self.cls = cls
        self.fields = {}

    def __repr__(self):
        return f"<{self.cls.name} instance>"


# Per the spec's "Standard Library Rule": utility functions that just do a
# job (range, len, int, str, type) stay as-is rather than getting renamed.
_BUILTINS = {
    "range": range,
    "len": len,
    "int": int,
    "str": str,
    "type": type,
}


_BIN_OPS = {
    T.PLUS: lambda a, b: a + b,
    T.MINUS: lambda a, b: a - b,
    T.STAR: lambda a, b: a * b,
    T.EQ: lambda a, b: a == b,
    T.NEQ: lambda a, b: a != b,
    T.GT: lambda a, b: a > b,
    T.LT: lambda a, b: a < b,
    T.GTE: lambda a, b: a >= b,
    T.LTE: lambda a, b: a <= b,
}


class Interpreter:
    def __init__(self, output=None, input_fn=None):
        """`output`, if given, is a list that print output gets appended to
        (as strings) instead of going to real stdout -- makes this testable
        without capturing process stdout.

        `input_fn`, if given, replaces Python's real `input()` for
        `absorbing` -- takes a prompt string, returns a string. Defaults to
        real `input()` so a program actually blocks on real stdin unless a
        test supplies a fake."""
        self.output = output
        self.input_fn = input_fn if input_fn is not None else input
        self.globals = Environment()
        self.env = self.globals  # current scope; swapped during function calls
        self._register_builtin_errors()

    def _register_builtin_errors(self):
        """Registers the 14 built-in error types as VibesClass objects in
        the global scope, keyed by their TokenType's enum name (e.g.
        "ERR_VALUE" for `wrong vibes`) -- see parser._parse_error_type_ref
        for why that key format was chosen. `negative vibes` (ERR_EXCEPTION)
        is the catch-all and sits at the root; every other built-in type's
        superclass is set to it, so an except clause catching ERR_EXCEPTION
        catches everything, mirroring Python's Exception base class."""
        root_message = DEFAULT_ERROR_MESSAGES[T.ERR_EXCEPTION]
        root = VibesClass(name="ERR_EXCEPTION", superclass=None,
                           methods={}, default_message=root_message)
        self.globals.define("ERR_EXCEPTION", root)

        for token_type, message in DEFAULT_ERROR_MESSAGES.items():
            if token_type is T.ERR_EXCEPTION:
                continue
            cls = VibesClass(name=token_type.name, superclass=root,
                              methods={}, default_message=message)
            self.globals.define(token_type.name, cls)

    def _emit(self, text):
        if self.output is not None:
            self.output.append(text)
        else:
            print(text)

    def run(self, program: ast.Program):
        try:
            self._exec_body(program.statements)
        except BreakSignal:
            raise VibesRuntimeError("VibeError: 'no more vibes' used outside of a loop")
        except ContinueSignal:
            raise VibesRuntimeError("VibeError: 'next vibe' used outside of a loop")
        except ReturnSignal:
            raise VibesRuntimeError("VibeError: 'sending vibes' used outside of a function")
        except ExitSignal:
            pass  # that's a wrap -- a clean, deliberate stop, not an error
        except RecursionError:
            raise VibesRuntimeError(
                "VibeError: stack overflow — you went too deep. touch grass."
            )

    def _exec_body(self, statements):
        for stmt in statements:
            self._exec_statement(stmt)

    # ---------- statements ----------

    def _exec_statement(self, stmt):
        if isinstance(stmt, ast.Print):
            value = self._eval(stmt.expr)
            self._emit(self._stringify(value))
            return

        if isinstance(stmt, ast.Assign):
            value = self._eval(stmt.expr)
            self.env.assign(stmt.name, value)
            return

        if isinstance(stmt, ast.If):
            for cond, body in stmt.branches:
                if cond is None or self._truthy(self._eval(cond)):
                    self._exec_body(body)
                    return
            return

        if isinstance(stmt, ast.While):
            while self._truthy(self._eval(stmt.cond)):
                try:
                    self._exec_body(stmt.body)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
            return

        if isinstance(stmt, ast.For):
            iterable = self._eval(stmt.iterable)
            for item in iterable:
                self.env.assign(stmt.var_name, item)
                try:
                    self._exec_body(stmt.body)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
            return

        if isinstance(stmt, ast.Break):
            raise BreakSignal()

        if isinstance(stmt, ast.Continue):
            raise ContinueSignal()

        if isinstance(stmt, ast.FuncDef):
            func = VibesFunction(stmt.name, stmt.params, stmt.body, closure=self.env)
            self.env.define(stmt.name, func)
            return

        if isinstance(stmt, ast.ClassDef):
            superclass = None
            if stmt.superclass_name is not None:
                superclass = self.env.get(stmt.superclass_name)
                if not isinstance(superclass, VibesClass):
                    raise VibesRuntimeError(
                        f"VibeError: mixed vibes: '{stmt.superclass_name}' isn't a "
                        f"class, so {stmt.name} can't inherit from it (line {stmt.line})"
                    )

            # Execute the class body (a sequence of `new vibes` method defs)
            # in its own scope so each method's closure is the class scope,
            # then lift whatever got defined there into the class's method
            # table. The class scope's parent is wherever the class itself
            # was defined, so methods can still see outer/global names.
            class_env = Environment(parent=self.env)
            previous_env = self.env
            self.env = class_env
            try:
                self._exec_body(stmt.body)
            finally:
                self.env = previous_env

            methods = dict(class_env.values)
            cls = VibesClass(name=stmt.name, superclass=superclass, methods=methods)
            self.env.define(stmt.name, cls)
            return

        if isinstance(stmt, ast.SetAttr):
            obj = self._eval(stmt.obj)
            if not isinstance(obj, VibesInstance):
                raise VibesRuntimeError(
                    f"VibeError: mixed vibes: can't set '.{stmt.attr}' on {obj!r} "
                    f"— that's not even a vibes instance. (line {stmt.line})"
                )
            obj.fields[stmt.attr] = self._eval(stmt.expr)
            return

        if isinstance(stmt, ast.Try):
            self._exec_try(stmt)
            return

        if isinstance(stmt, ast.Raise):
            raise self._make_raised(stmt.error_type, stmt.message_expr, stmt.line)

        if isinstance(stmt, ast.Import):
            try:
                module = importlib.import_module(stmt.module_name)
            except ImportError:
                raise VibesRuntimeError(
                    f"VibeError: channeling '{stmt.module_name}' failed -- that "
                    f"module doesn't exist and never has. (line {stmt.line})"
                )
            self.env.define(stmt.module_name, module)
            return

        if isinstance(stmt, ast.MainBlock):
            self._exec_body(stmt.body)
            return

        if isinstance(stmt, ast.Exit):
            raise ExitSignal()

        if isinstance(stmt, ast.Return):
            value = self._eval(stmt.expr)
            raise ReturnSignal(value)

        if isinstance(stmt, ast.ExprStmt):
            self._eval(stmt.expr)
            return

        raise VibesRuntimeError(
            f"VibeError: interpreter has no handler for statement type "
            f"{type(stmt).__name__}"
        )

    # ---------- expressions ----------

    def _eval(self, node):
        if isinstance(node, ast.Literal):
            return node.value

        if isinstance(node, ast.Name):
            return self.env.get(node.name)

        if isinstance(node, ast.Call):
            return self._eval_call(node)

        if isinstance(node, ast.Get):
            obj = self._eval(node.obj)
            if isinstance(obj, VibesInstance):
                if node.attr in obj.fields:
                    return obj.fields[node.attr]
                method = obj.cls.find_method(node.attr)
                if method is not None:
                    return method
                raise VibesRuntimeError(
                    f"VibeError: left on read: {obj.cls.name} doesn't have a "
                    f"'.{node.attr}' and it's not even sorry about it. (line {node.line})"
                )
            # Fallback for anything that isn't a VibesInstance -- e.g. a
            # module brought in via `channeling`, so `math.pi` etc work.
            try:
                return getattr(obj, node.attr)
            except AttributeError:
                raise VibesRuntimeError(
                    f"VibeError: left on read: {obj!r} doesn't have a "
                    f"'.{node.attr}' and it's not even sorry about it. (line {node.line})"
                )

        if isinstance(node, ast.MethodCall):
            obj = self._eval(node.obj)
            args = [self._eval(a) for a in node.args]
            if isinstance(obj, VibesInstance):
                method = obj.cls.find_method(node.method)
                if method is None:
                    raise VibesRuntimeError(
                        f"VibeError: left on read: {obj.cls.name} doesn't have a "
                        f"method called '{node.method}' and it's not even sorry "
                        f"about it. (line {node.line})"
                    )
                return self._call_function(method, [obj] + args, node.line)
            # Fallback for anything that isn't a VibesInstance -- e.g. a
            # module brought in via `channeling`, so `math.sqrt(16)` etc work.
            try:
                attr = getattr(obj, node.method)
            except AttributeError:
                raise VibesRuntimeError(
                    f"VibeError: left on read: {obj!r} doesn't have a method "
                    f"called '{node.method}' and it's not even sorry about it. "
                    f"(line {node.line})"
                )
            return attr(*args)

        if isinstance(node, ast.Input):
            prompt = self._eval(node.prompt) if node.prompt is not None else ""
            return self.input_fn(prompt)

        if isinstance(node, ast.UnaryOp):
            operand = self._eval(node.operand)
            if node.op == T.MINUS:
                return -operand
            raise VibesRuntimeError(f"VibeError: unknown unary operator on line {node.line}")

        if isinstance(node, ast.BinOp):
            left = self._eval(node.left)
            right = self._eval(node.right)

            if node.op == T.SLASH:
                if right == 0:
                    raise VibesRuntimeError(
                        "VibeError: you tried to divide by zero and honestly? the audacity."
                    )
                return left / right

            op_fn = _BIN_OPS.get(node.op)
            if op_fn is None:
                raise VibesRuntimeError(
                    f"VibeError: unknown binary operator on line {node.line}"
                )
            return op_fn(left, right)

        raise VibesRuntimeError(
            f"VibeError: interpreter has no handler for expression type "
            f"{type(node).__name__}"
        )

    def _eval_call(self, node):
        # A plain Call's name might resolve to a user function, a class
        # (instantiation), or -- only if the name isn't bound at all -- fall
        # through to a builtin. Mirrors Python: a local def/class/variable
        # always shadows a builtin of the same name, even if that local
        # value isn't itself callable (previously this used `None` both as
        # the "not found" signal and as a legitimately-resolved `no vibes`
        # value, which conflated "undefined name" with "called no vibes"
        # and let a shadowed non-callable incorrectly fall through to a
        # same-named builtin -- fixed by tracking `found` explicitly).
        found = True
        try:
            candidate = self.env.get(node.callee)
        except VibesNameError:
            candidate = None
            found = False

        args = [self._eval(a) for a in node.args]

        if found:
            if isinstance(candidate, VibesClass):
                return self._instantiate(candidate, args, node.line)
            if isinstance(candidate, VibesFunction):
                return self._call_function(candidate, args, node.line)
            if candidate is None:
                raise VibesRuntimeError(
                    "VibeError: you called no vibes and then used it. what did "
                    f"you expect. (line {node.line})"
                )
            raise VibesRuntimeError(
                f"VibeError: '{node.callee}' isn't a function, a class, or "
                f"anything else you can call — it's giving nothing. (line {node.line})"
            )

        if node.callee in _BUILTINS:
            return _BUILTINS[node.callee](*args)

        raise VibesRuntimeError(
            f"VibeError: undefined variable '{node.callee}' — it literally "
            f"does not exist, bestie. (line {node.line})"
        )

    def _make_raised(self, error_type_name, message_expr, line):
        try:
            cls = self.env.get(error_type_name)
        except VibesNameError:
            raise VibesRuntimeError(
                f"VibeError: '{error_type_name}' isn't a real error type, so "
                f"there's nothing to raise. (line {line})"
            )
        if not isinstance(cls, VibesClass):
            raise VibesRuntimeError(
                f"VibeError: mixed vibes: '{error_type_name}' isn't an error "
                f"type — can't manifest a whole vibe out of nothing. (line {line})"
            )
        message = self._eval(message_expr) if message_expr is not None else cls.find_default_message()
        instance = VibesInstance(cls)
        instance.fields["message"] = message
        return VibesRaised(instance)

    def _exec_try(self, stmt):
        # This is a near-direct mapping onto Python's own try/except/else/
        # finally -- which already has exactly the semantics we want
        # (else only runs if the try body didn't raise; finally always
        # runs, even if a handler itself raises or re-raises).
        try:
            self._exec_body(stmt.body)
        except VibesRaised as raised:
            for handler in stmt.handlers:
                try:
                    target_cls = self.env.get(handler.error_type)
                except VibesNameError:
                    raise VibesRuntimeError(
                        f"VibeError: '{handler.error_type}' isn't a real error "
                        f"type, so there's nothing to catch here. (line {handler.line})"
                    )
                if raised.instance.cls.is_or_inherits_from(target_cls):
                    if handler.var_name is not None:
                        self.env.assign(handler.var_name, raised.instance.fields.get("message", ""))
                    self._exec_body(handler.body)
                    break
            else:
                raise  # no handler matched -- propagate
        else:
            if stmt.else_body is not None:
                self._exec_body(stmt.else_body)
        finally:
            if stmt.finally_body is not None:
                self._exec_body(stmt.finally_body)

    def _instantiate(self, cls, args, line):
        instance = VibesInstance(cls)
        init_method = cls.find_method("__init__")
        if init_method is not None:
            self._call_function(init_method, [instance] + args, line)
        elif args:
            raise VibesRuntimeError(
                f"VibeError: mixed vibes: {cls.name}() doesn't even have an "
                f"__init__, so it's not taking any arguments right now. you "
                f"brought {len(args)}. (line {line})"
            )
        return instance

    def _call_function(self, func, args, call_line):
        if len(args) != len(func.params):
            raise VibesRuntimeError(
                f"VibeError: mixed vibes: {func.name}() wanted {len(func.params)} "
                f"argument(s), you brought {len(args)}. read the room. (line {call_line})"
            )

        call_env = Environment(parent=func.closure)
        for pname, aval in zip(func.params, args):
            call_env.define(pname, aval)

        previous_env = self.env
        self.env = call_env
        try:
            self._exec_body(func.body)
            return None  # no explicit `sending vibes` -> function returns no vibes
        except ReturnSignal as rs:
            return rs.value
        finally:
            self.env = previous_env

    # ---------- helpers ----------

    @staticmethod
    def _stringify(value):
        if value is True:
            return "immaculate vibes"
        if value is False:
            return "dead vibes"
        if value is None:
            return "no vibes"
        return str(value)

    @staticmethod
    def _truthy(value):
        """Python truthiness rules, per spec discussion."""
        return bool(value)


def run_source(source: str, output=None, input_fn=None):
    """Convenience: lex + parse + run a full source string in one call."""
    from .lexer import tokenize
    from .parser import parse

    tokens = tokenize(source)
    program = parse(tokens)
    Interpreter(output=output, input_fn=input_fn).run(program)
