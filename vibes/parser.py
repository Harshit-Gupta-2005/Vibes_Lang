"""
Parser for Vibes.

Currently covers the full language surface: expressions (literals,
arithmetic, comparisons, unary minus, parens, builtin/user calls, attribute
access, method calls, `absorbing` input), `manifesting`, variable
assignment (plain and attribute), control flow (if/elif/else, while, for,
break, continue), functions, classes (`new aesthetic`, single inheritance,
methods with explicit `self`), error handling (`catch the vibe` /
`bad vibes` / `good vibes only` / `big yikes`, plus the 14 built-in error
types), `channeling` (import), `main_character_vibes` (enforced to appear
at most once, only at the top level), and `that's a wrap`.
"""

from .keywords import TokenType as T
from . import ast_nodes as ast


class VibesParseError(Exception):
    pass


# tokens that can start a comparison; kept as a tuple for easy `in` checks
_COMPARISON_OPS = (T.EQ, T.NEQ, T.GT, T.LT, T.GTE, T.LTE)
_ADDITIVE_OPS = (T.PLUS, T.MINUS)
_MULTIPLICATIVE_OPS = (T.STAR, T.SLASH)

_LITERAL_TOKENS = {
    T.NUMBER: lambda tok: tok.value,
    T.STRING: lambda tok: tok.value,
    T.TRUE: lambda tok: True,
    T.FALSE: lambda tok: False,
    T.NONE: lambda tok: None,
}

# Tokens that can start an expression -- used for optional-argument
# lookahead, e.g. deciding whether `absorbing` has a prompt expression
# after it or not.
_EXPRESSION_START_TOKENS = (
    T.NUMBER, T.STRING, T.TRUE, T.FALSE, T.NONE, T.LPAREN, T.IDENT, T.MINUS,
)

# Optional type-prefix keywords that can precede a variable name in an
# assignment, e.g. `word vibes name vibes with ...`. Parsed but not
# enforced -- see ast_nodes.Assign.type_hint.
_TYPE_PREFIX_TOKENS = (T.TYPE_INT, T.TYPE_STRING, T.TYPE_BOOL)

# The 14 built-in error-type keyword tokens (wrong vibes, mixed vibes, ...,
# timed out). Used wherever an error type can be referenced: a class's
# superclass (`new aesthetic MyError(wrong vibes)`), an except clause
# (`bad vibes wrong vibes as e`), and a raise (`big yikes wrong vibes`).
_ERROR_TYPE_TOKENS = (
    T.ERR_VALUE, T.ERR_TYPE, T.ERR_RUNTIME, T.ERR_KEY, T.ERR_INDEX,
    T.ERR_EXCEPTION, T.ERR_ASSERTION, T.ERR_ATTRIBUTE, T.ERR_FILENOTFOUND,
    T.ERR_RECURSION, T.ERR_NOTIMPLEMENTED, T.ERR_KEYBOARDINTERRUPT,
    T.ERR_CONNECTION, T.ERR_TIMEOUT,
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---------- token stream helpers ----------

    def _peek(self, offset=0):
        p = self.pos + offset
        if p < len(self.tokens):
            return self.tokens[p]
        return self.tokens[-1]  # EOF

    def _check(self, *types):
        return self._peek().type in types

    def _advance(self):
        tok = self._peek()
        if tok.type != T.EOF:
            self.pos += 1
        return tok

    def _expect(self, ttype, context=""):
        tok = self._peek()
        if tok.type != ttype:
            raise VibesParseError(
                f"VibeError: expected {ttype.name} {context} but got "
                f"{tok.type.name} ({tok.value!r}) on line {tok.line}"
            )
        return self._advance()

    # ---------- entry point ----------

    def parse(self) -> ast.Program:
        statements = []
        main_seen = False
        while not self._check(T.EOF):
            if self._check(T.MAIN):
                if main_seen:
                    raise VibesParseError(
                        "VibeError: a program can only have one "
                        f"main_character_vibes (second one found on line {self._peek().line})"
                    )
                main_seen = True
                statements.append(self._parse_main_block())
            else:
                statements.append(self._parse_statement())
        return ast.Program(statements)

    def _parse_main_block(self):
        tok = self._expect(T.MAIN)
        body = self._parse_block()
        return ast.MainBlock(body=body, line=tok.line)

    # ---------- blocks ----------

    def _parse_block(self):
        """vibes on <statements> vibes off, with mismatch detection matching
        the spec's own VibeError wording."""
        open_tok = self._expect(T.LBRACE, "to open a block")
        statements = []
        while not self._check(T.RBRACE):
            if self._check(T.EOF):
                raise VibesParseError(
                    "VibeError: mismatched vibes on/off — you opened a block "
                    f"and just... left. (block opened on line {open_tok.line})"
                )
            statements.append(self._parse_statement())
        self._expect(T.RBRACE)
        return statements

    # ---------- statements ----------

    def _parse_statement(self):
        if self._check(T.PRINT):
            return self._parse_print_statement()

        if self._check(T.IF):
            return self._parse_if_statement()

        if self._check(T.WHILE):
            return self._parse_while_statement()

        if self._check(T.FOR):
            return self._parse_for_statement()

        if self._check(T.BREAK):
            tok = self._advance()
            return ast.Break(line=tok.line)

        if self._check(T.CONTINUE):
            tok = self._advance()
            return ast.Continue(line=tok.line)

        if self._check(T.DEF):
            return self._parse_func_def()

        if self._check(T.CLASS):
            return self._parse_class_def()

        if self._check(T.TRY):
            return self._parse_try_statement()

        if self._check(T.RAISE):
            return self._parse_raise_statement()

        if self._check(T.RETURN):
            return self._parse_return_statement()

        if self._check(T.IMPORT):
            return self._parse_import_statement()

        if self._check(T.EXIT):
            tok = self._advance()
            return ast.Exit(line=tok.line)

        if self._check(*_TYPE_PREFIX_TOKENS):
            return self._parse_assignment(type_hint=self._advance().type)

        if self._check(T.IDENT):
            return self._parse_ident_statement()

        tok = self._peek()
        raise VibesParseError(
            f"VibeError: unexpected token {tok.type.name} ({tok.value!r}) "
            f"on line {tok.line} -- not yet supported by the parser"
        )

    def _parse_ident_statement(self):
        """Dispatches the three things a statement starting with an
        identifier can be: a plain assignment (`x vibes with ...`), an
        attribute assignment (`self.name vibes with ...`), or a bare
        expression statement (`greet()`, `p.greet()`). All three start by
        parsing an ordinary expression -- ASSIGN isn't a valid expression
        continuation, so parsing naturally stops right before it if it's
        present, leaving `expr` as exactly the assignment target."""
        start_tok = self._peek()
        expr = self._parse_expression()

        if self._check(T.ASSIGN):
            self._advance()
            value_expr = self._parse_expression()
            if isinstance(expr, ast.Name):
                return ast.Assign(name=expr.name, expr=value_expr, type_hint=None, line=start_tok.line)
            if isinstance(expr, ast.Get):
                return ast.SetAttr(obj=expr.obj, attr=expr.attr, expr=value_expr, line=start_tok.line)
            raise VibesParseError(
                f"VibeError: invalid assignment target on line {start_tok.line}"
            )

        return ast.ExprStmt(expr=expr, line=start_tok.line)

    def _parse_func_def(self):
        tok = self._expect(T.DEF)
        name_tok = self._expect(T.IDENT, "as the function name")
        self._expect(T.LPAREN, "to open the parameter list")
        params = []
        if not self._check(T.RPAREN):
            params.append(self._expect(T.IDENT, "as a parameter name").value)
            while self._check(T.COMMA):
                self._advance()
                params.append(self._expect(T.IDENT, "as a parameter name").value)
        self._expect(T.RPAREN, "to close the parameter list")
        body = self._parse_block()
        return ast.FuncDef(name=name_tok.value, params=params, body=body, line=tok.line)

    def _parse_class_def(self):
        tok = self._expect(T.CLASS)
        name_tok = self._expect(T.IDENT, "as the class name")

        superclass_name = None
        if self._check(T.LPAREN):
            self._advance()
            superclass_name, _ = self._parse_error_type_ref(
                context="as the superclass name"
            )
            self._expect(T.RPAREN, "to close the superclass parentheses")

        body = self._parse_block()
        for member in body:
            if not isinstance(member, ast.FuncDef):
                raise VibesParseError(
                    "VibeError: only method definitions are supported inside "
                    f"a class body right now (line {member.line})"
                )

        return ast.ClassDef(
            name=name_tok.value, superclass_name=superclass_name, body=body, line=tok.line
        )

    def _parse_error_type_ref(self, context=""):
        """Parses a reference to an error type, wherever one can appear:
        a class's superclass, an except clause's caught type, or a raise's
        type. Accepts either one of the 14 built-in error-type keyword
        tokens (returned as their TokenType's enum name, e.g. "ERR_VALUE"
        for `wrong vibes`) or a plain identifier (a user-defined class,
        presumably one that inherits from a built-in error type). Both
        forms resolve identically at runtime via Environment.get, since the
        interpreter pre-registers the built-ins under their enum-name keys.
        Returns (name_string, line)."""
        tok = self._peek()
        if tok.type in _ERROR_TYPE_TOKENS:
            self._advance()
            return tok.type.name, tok.line
        if tok.type == T.IDENT:
            self._advance()
            return tok.value, tok.line
        raise VibesParseError(
            f"VibeError: expected an error type {context} but got "
            f"{tok.type.name} ({tok.value!r}) on line {tok.line}"
        )

    def _parse_try_statement(self):
        tok = self._expect(T.TRY)
        body = self._parse_block()

        handlers = []
        while self._check(T.EXCEPT):
            except_tok = self._advance()
            error_type, _ = self._parse_error_type_ref(context="after 'bad vibes'")
            var_name = None
            if self._check(T.AS):
                self._advance()
                var_name = self._expect(T.IDENT, "as the caught error's variable name").value
            handler_body = self._parse_block()
            handlers.append(ast.ExceptHandler(
                error_type=error_type, var_name=var_name, body=handler_body, line=except_tok.line
            ))

        else_body = None
        if self._check(T.ELSE):
            self._advance()
            else_body = self._parse_block()

        finally_body = None
        if self._check(T.FINALLY):
            self._advance()
            finally_body = self._parse_block()

        return ast.Try(
            body=body, handlers=handlers, else_body=else_body,
            finally_body=finally_body, line=tok.line,
        )

    def _parse_raise_statement(self):
        tok = self._expect(T.RAISE)
        error_type, _ = self._parse_error_type_ref(context="after 'big yikes'")
        message_expr = None
        if self._check(T.LPAREN):
            args = self._parse_arg_list()
            if len(args) != 1:
                raise VibesParseError(
                    f"VibeError: big yikes takes exactly one message argument "
                    f"if given at all, got {len(args)} on line {tok.line}"
                )
            message_expr = args[0]
        return ast.Raise(error_type=error_type, message_expr=message_expr, line=tok.line)

    def _parse_return_statement(self):
        tok = self._expect(T.RETURN)
        expr = self._parse_expression()
        return ast.Return(expr=expr, line=tok.line)

    def _parse_import_statement(self):
        tok = self._expect(T.IMPORT)
        name_tok = self._expect(T.IDENT, "as the module name")
        return ast.Import(module_name=name_tok.value, line=tok.line)

    def _parse_print_statement(self):
        tok = self._expect(T.PRINT)
        expr = self._parse_expression()
        return ast.Print(expr=expr, line=tok.line)

    def _parse_assignment(self, type_hint):
        name_tok = self._expect(T.IDENT, "as the variable name in an assignment")
        self._expect(T.ASSIGN)
        expr = self._parse_expression()
        return ast.Assign(name=name_tok.value, expr=expr, type_hint=type_hint, line=name_tok.line)

    def _parse_if_statement(self):
        tok = self._expect(T.IF)
        cond = self._parse_expression()
        body = self._parse_block()
        branches = [(cond, body)]

        while self._check(T.ELIF):
            self._advance()
            elif_cond = self._parse_expression()
            elif_body = self._parse_block()
            branches.append((elif_cond, elif_body))

        if self._check(T.ELSE):
            self._advance()
            else_body = self._parse_block()
            branches.append((None, else_body))

        return ast.If(branches=branches, line=tok.line)

    def _parse_while_statement(self):
        tok = self._expect(T.WHILE)
        cond = self._parse_expression()
        body = self._parse_block()
        return ast.While(cond=cond, body=body, line=tok.line)

    def _parse_for_statement(self):
        tok = self._expect(T.FOR)
        var_tok = self._expect(T.IDENT, "as the loop variable")
        self._expect(T.IN, "after the loop variable")
        iterable = self._parse_expression()
        body = self._parse_block()
        return ast.For(var_name=var_tok.value, iterable=iterable, body=body, line=tok.line)

    # ---------- expressions (precedence climbing) ----------
    # expression   := comparison
    # comparison   := additive ( (EQ|NEQ|GT|LT|GTE|LTE) additive )*
    # additive     := multiplicative ( (PLUS|MINUS) multiplicative )*
    # multiplicative := unary ( (STAR|SLASH) unary )*
    # unary        := MINUS unary | postfix
    # postfix      := primary ( '.' IDENT | '.' IDENT '(' args ')' )*
    # primary      := NUMBER | STRING | TRUE | FALSE | NONE | LPAREN expression RPAREN
    #                 | IDENT | IDENT '(' args ')'

    def _parse_expression(self):
        return self._parse_comparison()

    def _parse_comparison(self):
        left = self._parse_additive()
        while self._check(*_COMPARISON_OPS):
            op_tok = self._advance()
            right = self._parse_additive()
            left = ast.BinOp(left=left, op=op_tok.type, right=right, line=op_tok.line)
        return left

    def _parse_additive(self):
        left = self._parse_multiplicative()
        while self._check(*_ADDITIVE_OPS):
            op_tok = self._advance()
            right = self._parse_multiplicative()
            left = ast.BinOp(left=left, op=op_tok.type, right=right, line=op_tok.line)
        return left

    def _parse_multiplicative(self):
        left = self._parse_unary()
        while self._check(*_MULTIPLICATIVE_OPS):
            op_tok = self._advance()
            right = self._parse_unary()
            left = ast.BinOp(left=left, op=op_tok.type, right=right, line=op_tok.line)
        return left

    def _parse_unary(self):
        if self._check(T.MINUS):
            op_tok = self._advance()
            operand = self._parse_unary()
            return ast.UnaryOp(op=op_tok.type, operand=operand, line=op_tok.line)
        return self._parse_postfix()

    def _parse_postfix(self):
        expr = self._parse_primary()
        while self._check(T.DOT):
            self._advance()
            attr_tok = self._expect(T.IDENT, "as an attribute or method name after '.'")
            if self._check(T.LPAREN):
                args = self._parse_arg_list()
                expr = ast.MethodCall(obj=expr, method=attr_tok.value, args=args, line=attr_tok.line)
            else:
                expr = ast.Get(obj=expr, attr=attr_tok.value, line=attr_tok.line)
        return expr

    def _parse_primary(self):
        tok = self._peek()

        if tok.type in _LITERAL_TOKENS:
            self._advance()
            return ast.Literal(value=_LITERAL_TOKENS[tok.type](tok), line=tok.line)

        if tok.type == T.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(T.RPAREN, "to close '('")
            return expr

        if tok.type == T.IDENT:
            self._advance()
            if self._check(T.LPAREN):
                return self._parse_call(callee_tok=tok)
            return ast.Name(name=tok.value, line=tok.line)

        if tok.type == T.INPUT:
            self._advance()
            prompt = None
            if self._check(*_EXPRESSION_START_TOKENS):
                prompt = self._parse_expression()
            return ast.Input(prompt=prompt, line=tok.line)

        raise VibesParseError(
            f"VibeError: expected an expression but got {tok.type.name} "
            f"({tok.value!r}) on line {tok.line}"
        )

    def _parse_call(self, callee_tok):
        args = self._parse_arg_list()
        return ast.Call(callee=callee_tok.value, args=args, line=callee_tok.line)

    def _parse_arg_list(self):
        self._expect(T.LPAREN)
        args = []
        if not self._check(T.RPAREN):
            args.append(self._parse_expression())
            while self._check(T.COMMA):
                self._advance()
                args.append(self._parse_expression())
        self._expect(T.RPAREN, "to close the argument list")
        return args


def parse(tokens) -> ast.Program:
    return Parser(tokens).parse()
