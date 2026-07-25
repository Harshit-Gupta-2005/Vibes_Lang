"""
AST node definitions.

Kept as plain dataclasses -- no behavior lives here, just structure.
Grows incrementally as we add language features; this file currently only
covers what step 2 needs (expressions + `manifesting`).
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ---------- top level ----------

@dataclass
class Program:
    statements: List["Stmt"]


# ---------- statements ----------

@dataclass
class Print:
    """manifesting <expr>"""
    expr: "Expr"
    line: int


@dataclass
class Assign:
    """[optional type keyword] <name> vibes with <expr>

    The optional type prefix (numeric vibes / word vibes / vibe or no vibe)
    is parsed but not enforced -- Vibes has no forced type declarations, so
    `type_hint` is stored only for potential future tooling/error messages
    and is otherwise inert at runtime."""
    name: str
    expr: "Expr"
    type_hint: Optional[object]  # TokenType or None
    line: int


@dataclass
class If:
    """it's giving <cond> vibes on ... vibes off
       [or it's giving <cond> vibes on ... vibes off]*
       [or not vibes on ... vibes off]

    branches is an ordered list of (condition, body) pairs. A branch whose
    condition is None is the trailing `or not` (else) and, if present, must
    be last -- the parser enforces that, not this node."""
    branches: List[tuple]  # List[Tuple[Optional[Expr], List[Stmt]]]
    line: int


@dataclass
class While:
    """keep the vibes going <cond> vibes on ... vibes off"""
    cond: "Expr"
    body: List["Stmt"]
    line: int


@dataclass
class For:
    """vibing through <var> in <iterable> vibes on ... vibes off"""
    var_name: str
    iterable: "Expr"
    body: List["Stmt"]
    line: int


@dataclass
class Break:
    """no more vibes"""
    line: int


@dataclass
class Continue:
    """next vibe"""
    line: int


@dataclass
class ExprStmt:
    """An expression used as a whole statement, e.g. a bare function call."""
    expr: "Expr"
    line: int


@dataclass
class FuncDef:
    """new vibes name(params) vibes on ... vibes off"""
    name: str
    params: List[str]
    body: List["Stmt"]
    line: int


@dataclass
class Return:
    """sending vibes <expr>

    NOTE: an expression is currently required (matches every example in the
    spec -- `sending vibes 42`, `sending vibes x`). Vibes has no statement
    separator, so a bare `sending vibes` immediately followed by another
    statement would be ambiguous about where the return value ends and the
    next statement begins; requiring an expr sidesteps that. Revisit if a
    genuine bare-return use case shows up."""
    expr: "Expr"
    line: int


@dataclass
class ClassDef:
    """new aesthetic Name [(Superclass)] vibes on ... vibes off

    `body` holds only FuncDef nodes -- the parser enforces that only method
    definitions are allowed directly inside a class body for now (matches
    every example in the spec; class-level fields outside __init__ aren't
    shown anywhere, so there's nothing to model yet)."""
    name: str
    superclass_name: Optional[str]
    body: List["Stmt"]
    line: int


@dataclass
class SetAttr:
    """<obj>.<attr> vibes with <expr>, e.g. `self.name vibes with name`."""
    obj: "Expr"
    attr: str
    expr: "Expr"
    line: int


@dataclass
class ExceptHandler:
    """bad vibes <error_type> [as <name>] vibes on ... vibes off

    `error_type` is a plain string key -- either one of the 14 built-in
    error-type token names (e.g. "ERR_VALUE" for `wrong vibes`) or a
    user-defined class name, resolved against the environment the same way
    a class's superclass reference is. See parser._parse_error_type_ref."""
    error_type: str
    var_name: Optional[str]
    body: List["Stmt"]
    line: int


@dataclass
class Try:
    """catch the vibe vibes on ... vibes off
       [bad vibes <type> [as e] vibes on ... vibes off]*
       [or not vibes on ... vibes off]      -- runs only if no error occurred
       [good vibes only vibes on ... vibes off]  -- always runs"""
    body: List["Stmt"]
    handlers: List[ExceptHandler]
    else_body: Optional[List["Stmt"]]
    finally_body: Optional[List["Stmt"]]
    line: int


@dataclass
class Raise:
    """big yikes <error_type> [(<message_expr>)]

    If message_expr is None, the error's own default message is used at
    runtime (see keywords.DEFAULT_ERROR_MESSAGES / VibesClass.default_message)."""
    error_type: str
    message_expr: Optional["Expr"]
    line: int


@dataclass
class Import:
    """channeling <module_name>

    Only a single bare module name is supported (matches the spec's only
    example, `channeling math`) -- no dotted paths, no `as` aliasing."""
    module_name: str
    line: int


@dataclass
class MainBlock:
    """main_character_vibes vibes on ... vibes off

    Executes inline, exactly where it appears in top-to-bottom program
    flow -- it isn't a callable entry point the interpreter jumps to, just
    a labeled block (the parser enforces there's at most one per program,
    and only at the top level, matching every spec example's structure of
    defs/classes/channeling above it, script logic inside it)."""
    body: List["Stmt"]
    line: int


@dataclass
class Exit:
    """that's a wrap -- a clean, deliberate exit(0)."""
    line: int



# ---------- expressions ----------

@dataclass
class Literal:
    """A number, string, True/False, or None literal."""
    value: object
    line: int


@dataclass
class BinOp:
    """left <op> right, where op is a TokenType (PLUS, MINUS, STAR, SLASH,
    EQ, NEQ, GT, LT, GTE, LTE)."""
    left: "Expr"
    op: object  # TokenType
    right: "Expr"
    line: int


@dataclass
class UnaryOp:
    """-<expr>, currently only unary minus."""
    op: object  # TokenType
    operand: "Expr"
    line: int


@dataclass
class Name:
    """A reference to a variable by name, e.g. the `x` in `manifesting x`."""
    name: str
    line: int


@dataclass
class Call:
    """callee(arg1, arg2, ...). `callee` is a plain name -- resolved at
    runtime against user-defined functions, classes (instantiation), and
    builtins (range/len/int/str/type), in that priority order."""
    callee: str
    args: List["Expr"]
    line: int


@dataclass
class Get:
    """<obj>.<attr> used as a value, e.g. the `self.name` inside an
    expression like `manifesting self.name`."""
    obj: "Expr"
    attr: str
    line: int


@dataclass
class MethodCall:
    """<obj>.<method>(arg1, arg2, ...), e.g. `p.greet()`.

    Kept distinct from Call rather than making Call.callee a general
    expression, since every plain Call in this language resolves by a
    simple name lookup (function/class/builtin) while a method call always
    needs the receiver object to look the method up on its class."""
    obj: "Expr"
    method: str
    args: List["Expr"]
    line: int


@dataclass
class Input:
    """absorbing [<prompt_expr>], e.g. `absorbing "what's your name?"`.

    The prompt is optional -- `absorbing` with nothing after it is a bare
    input() call with no prompt text."""
    prompt: Optional["Expr"]
    line: int


# Type alias for readability elsewhere; not enforced at runtime.
Expr = object
Stmt = object
