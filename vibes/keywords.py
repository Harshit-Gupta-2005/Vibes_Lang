"""
Single source of truth for every multi-word (and single-word) keyword phrase
in Vibes. The lexer does a greedy, longest-phrase-first match against this
table over a stream of raw word-tokens.

Each entry is: (tuple_of_lowercase_words, TokenType)

IMPORTANT: entries must be tried longest-phrase-first, so we never match
"no more vibes" (BREAK) when the source actually says "no more vibes than"
(LTE). `sorted_keywords()` below handles the ordering -- don't rely on
declaration order in this file.
"""

from enum import Enum, auto


class TokenType(Enum):
    # --- structure ---
    MAIN = auto()            # main_character_vibes
    LBRACE = auto()          # vibes on
    RBRACE = auto()          # vibes off
    EXIT = auto()            # that's a wrap
    IMPORT = auto()          # channeling

    # --- functions / classes ---
    DEF = auto()              # new vibes
    RETURN = auto()           # sending vibes
    CLASS = auto()            # new aesthetic

    # --- control flow ---
    IF = auto()                # it's giving
    ELIF = auto()               # or it's giving
    ELSE = auto()               # or not
    WHILE = auto()              # keep the vibes going
    FOR = auto()                # vibing through
    BREAK = auto()              # no more vibes
    CONTINUE = auto()           # next vibe
    IN = auto()                  # in  (used by "vibing through i in range(...)")

    # --- operators ---
    ASSIGN = auto()          # vibes with
    EQ = auto()              # vibe match
    NEQ = auto()             # vibe doesn't match
    GT = auto()               # more vibes than
    LT = auto()               # less vibes than
    GTE = auto()              # no less vibes than
    LTE = auto()              # no more vibes than

    # --- types / literals ---
    TYPE_INT = auto()          # numeric vibes
    TYPE_STRING = auto()       # word vibes
    TYPE_BOOL = auto()         # vibe or no vibe
    TRUE = auto()               # immaculate vibes
    FALSE = auto()              # dead vibes
    NONE = auto()                # no vibes

    # --- I/O ---
    PRINT = auto()          # manifesting
    INPUT = auto()          # absorbing

    # --- error handling ---
    TRY = auto()             # catch the vibe
    EXCEPT = auto()          # bad vibes
    FINALLY = auto()         # good vibes only
    RAISE = auto()           # big yikes
    AS = auto()               # as

    # --- error type names ---
    ERR_VALUE = auto()               # wrong vibes         -> ValueError
    ERR_TYPE = auto()                # mixed vibes         -> TypeError
    ERR_RUNTIME = auto()             # crashed out         -> RuntimeError
    ERR_KEY = auto()                 # ghosted             -> KeyError
    ERR_INDEX = auto()               # out of pocket       -> IndexError
    ERR_EXCEPTION = auto()           # negative vibes      -> Exception (catch-all)
    ERR_ASSERTION = auto()           # cap                 -> AssertionError
    ERR_ATTRIBUTE = auto()           # left on read        -> AttributeError
    ERR_FILENOTFOUND = auto()        # who?                -> FileNotFoundError
    ERR_RECURSION = auto()           # spiraling           -> RecursionError
    ERR_NOTIMPLEMENTED = auto()      # still cooking       -> NotImplementedError
    ERR_KEYBOARDINTERRUPT = auto()   # pressed             -> KeyboardInterrupt
    ERR_CONNECTION = auto()          # no service          -> ConnectionError
    ERR_TIMEOUT = auto()             # timed out           -> TimeoutError

    # --- literals / identifiers / misc (produced directly by the lexer,
    #     not looked up in the keyword table) ---
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()

    # --- punctuation / raw operators (unchanged from Python) ---
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()

    EOF = auto()


# (phrase words, TokenType) -- declared in any order, sorted_keywords() fixes ordering.
_RAW_KEYWORDS = [
    (("main_character_vibes",), TokenType.MAIN),
    (("vibes", "on"), TokenType.LBRACE),
    (("vibes", "off"), TokenType.RBRACE),
    (("that's", "a", "wrap"), TokenType.EXIT),
    (("channeling",), TokenType.IMPORT),

    (("new", "vibes"), TokenType.DEF),
    (("sending", "vibes"), TokenType.RETURN),
    (("new", "aesthetic"), TokenType.CLASS),

    (("it's", "giving"), TokenType.IF),
    (("or", "it's", "giving"), TokenType.ELIF),
    (("or", "not"), TokenType.ELSE),
    (("keep", "the", "vibes", "going"), TokenType.WHILE),
    (("vibing", "through"), TokenType.FOR),
    (("no", "more", "vibes"), TokenType.BREAK),
    (("next", "vibe"), TokenType.CONTINUE),
    (("in",), TokenType.IN),

    (("vibes", "with"), TokenType.ASSIGN),
    (("vibe", "match"), TokenType.EQ),
    (("vibe", "doesn't", "match"), TokenType.NEQ),
    (("more", "vibes", "than"), TokenType.GT),
    (("less", "vibes", "than"), TokenType.LT),
    (("no", "less", "vibes", "than"), TokenType.GTE),
    (("no", "more", "vibes", "than"), TokenType.LTE),

    (("numeric", "vibes"), TokenType.TYPE_INT),
    (("word", "vibes"), TokenType.TYPE_STRING),
    (("vibe", "or", "no", "vibe"), TokenType.TYPE_BOOL),
    (("immaculate", "vibes"), TokenType.TRUE),
    (("dead", "vibes"), TokenType.FALSE),
    (("no", "vibes"), TokenType.NONE),

    (("manifesting",), TokenType.PRINT),
    (("absorbing",), TokenType.INPUT),

    (("catch", "the", "vibe"), TokenType.TRY),
    (("bad", "vibes"), TokenType.EXCEPT),
    (("good", "vibes", "only"), TokenType.FINALLY),
    (("big", "yikes"), TokenType.RAISE),
    (("as",), TokenType.AS),

    (("wrong", "vibes"), TokenType.ERR_VALUE),
    (("mixed", "vibes"), TokenType.ERR_TYPE),
    (("crashed", "out"), TokenType.ERR_RUNTIME),
    (("ghosted",), TokenType.ERR_KEY),
    (("out", "of", "pocket"), TokenType.ERR_INDEX),
    (("negative", "vibes"), TokenType.ERR_EXCEPTION),
    (("cap",), TokenType.ERR_ASSERTION),
    (("left", "on", "read"), TokenType.ERR_ATTRIBUTE),
    (("who?",), TokenType.ERR_FILENOTFOUND),
    (("spiraling",), TokenType.ERR_RECURSION),
    (("still", "cooking"), TokenType.ERR_NOTIMPLEMENTED),
    (("pressed",), TokenType.ERR_KEYBOARDINTERRUPT),
    (("no", "service"), TokenType.ERR_CONNECTION),
    (("timed", "out"), TokenType.ERR_TIMEOUT),
]


def sorted_keywords():
    """Longest phrase (in words) first, so greedy matching never grabs a
    short phrase when a longer one starting with the same words is present."""
    return sorted(_RAW_KEYWORDS, key=lambda kv: -len(kv[0]))


# Precomputed once at import time.
KEYWORDS = sorted_keywords()

# Default error messages, keyed by TokenType of the error-type token.
DEFAULT_ERROR_MESSAGES = {
    TokenType.ERR_VALUE: "wrong vibes: that value is not it, bestie.",
    TokenType.ERR_TYPE: "mixed vibes: you can't mix those two and expect good things.",
    TokenType.ERR_RUNTIME: "crashed out: the program just... couldn't anymore.",
    TokenType.ERR_KEY: "ghosted: that key was here and then it wasn't. classic.",
    TokenType.ERR_INDEX: "out of pocket: you went way too far and you know it.",
    TokenType.ERR_EXCEPTION: "negative vibes: something went wrong and it's giving chaos.",
    TokenType.ERR_ASSERTION: "cap: that was NOT true and everyone knew it.",
    TokenType.ERR_ATTRIBUTE: "left on read: that thing doesn't have what you're looking for and it's not even sorry.",
    TokenType.ERR_FILENOTFOUND: "who?: that file doesn't exist and never has.",
    TokenType.ERR_RECURSION: "spiraling: bestie went too deep, too fast, no chill.",
    TokenType.ERR_NOTIMPLEMENTED: "still cooking: this isn't built yet, manifest patience.",
    TokenType.ERR_KEYBOARDINTERRUPT: "pressed: someone yanked the plug mid-vibe, rude.",
    TokenType.ERR_CONNECTION: "no service: reached out and got absolutely nothing back.",
    TokenType.ERR_TIMEOUT: "timed out: waited, and waited, and then said forget it.",
}
