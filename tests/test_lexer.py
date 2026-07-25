import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vibes.lexer import tokenize
from vibes.keywords import TokenType as T


def types(src):
    return [t.type for t in tokenize(src)][:-1]  # drop EOF for easier comparison


def test_simple_assignment():
    assert types("x vibes with 5") == [T.IDENT, T.ASSIGN, T.NUMBER]


def test_break_vs_lte_prefix_collision():
    # "no more vibes" (BREAK) must not swallow "no more vibes than" (LTE)
    assert types("no more vibes") == [T.BREAK]
    assert types("x no more vibes than 10") == [T.IDENT, T.LTE, T.NUMBER]


def test_gte_vs_none_prefix_collision():
    assert types("no vibes") == [T.NONE]
    assert types("x no less vibes than 10") == [T.IDENT, T.GTE, T.NUMBER]


def test_if_elif_else():
    assert types("it's giving") == [T.IF]
    assert types("or it's giving") == [T.ELIF]
    assert types("or not") == [T.ELSE]


def test_bool_type_vs_none():
    assert types("vibe or no vibe") == [T.TYPE_BOOL]


def test_neq_vs_eq():
    assert types("x vibe match y") == [T.IDENT, T.EQ, T.IDENT]
    assert types("x vibe doesn't match y") == [T.IDENT, T.NEQ, T.IDENT]


def test_error_type_who_with_question_mark():
    assert types('big yikes who?') == [T.RAISE, T.ERR_FILENOTFOUND]
    assert types('big yikes who?("nope")') == [
        T.RAISE, T.ERR_FILENOTFOUND, T.LPAREN, T.STRING, T.RPAREN
    ]


def test_except_vs_catchall_exception_type():
    # "bad vibes negative vibes as e" -> EXCEPT, ERR_EXCEPTION, AS, IDENT
    assert types("bad vibes negative vibes as e") == [
        T.EXCEPT, T.ERR_EXCEPTION, T.AS, T.IDENT
    ]


def test_comment_is_stripped():
    toks = types('~ this is a comment ~ x vibes with 5')
    assert toks == [T.IDENT, T.ASSIGN, T.NUMBER]


def test_tilde_inside_string_is_not_a_comment():
    toks = tokenize('manifesting "vibes ~ check ~ this out"')
    assert [t.type for t in toks][:-1] == [T.PRINT, T.STRING]
    assert toks[1].value == "vibes ~ check ~ this out"


def test_comment_and_string_adjacent():
    # comment immediately followed by a string containing a tilde
    src = '~ note ~ manifesting "still ~ fine"'
    toks = tokenize(src)
    kinds = [t.type for t in toks][:-1]
    assert kinds == [T.PRINT, T.STRING]
    assert toks[1].value == "still ~ fine"


def test_number_and_float():
    assert types("3") == [T.NUMBER]
    toks = tokenize("3.5")
    assert toks[0].value == 3.5


def test_class_and_inheritance_syntax():
    assert types("new aesthetic Dog(Animal)") == [
        T.CLASS, T.IDENT, T.LPAREN, T.IDENT, T.RPAREN
    ]


def test_main_entry_point_and_blocks():
    assert types("main_character_vibes vibes on vibes off") == [
        T.MAIN, T.LBRACE, T.RBRACE
    ]


def test_full_example_tokenizes_without_error():
    src = open(os.path.join(os.path.dirname(__file__), "fixtures", "full_example.vibes")).read()
    toks = tokenize(src)
    assert toks[-1].type == T.EOF
    # spot check a few structurally important tokens appear
    all_types = [t.type for t in toks]
    assert T.MAIN in all_types
    assert T.CLASS in all_types
    assert T.TRY in all_types
    assert T.EXCEPT in all_types
    assert T.FINALLY in all_types
