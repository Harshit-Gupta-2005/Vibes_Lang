"""
Lexer for Vibes.

Two phases:

  1. Raw scan (character by character): produces a flat stream of
     RawToken(kind, value, line) where kind is one of
     WORD / NUMBER / STRING / PUNCT.
     This is where string literals and `~ comment ~` spans are handled,
     since that requires real character-level lookahead (a `~` inside a
     string literal must NOT be treated as a comment delimiter).

  2. Keyword folding: walks the raw WORD tokens and greedily matches the
     longest possible phrase from keywords.KEYWORDS ("no more vibes than"
     must be checked before "no more vibes"). Non-matching words become
     IDENT tokens. NUMBER/STRING/PUNCT raw tokens pass through as their
     corresponding final token types.
"""

from dataclasses import dataclass
from .keywords import KEYWORDS, TokenType


class VibesLexError(Exception):
    """Raised for malformed source (unterminated string, bad character, etc)."""
    pass


@dataclass
class Token:
    type: TokenType
    value: object
    line: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line})"


@dataclass
class _RawToken:
    kind: str  # 'WORD' | 'NUMBER' | 'STRING' | 'PUNCT'
    value: object
    line: int


_PUNCT_MAP = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    ",": TokenType.COMMA,
    ".": TokenType.DOT,
    ":": TokenType.COLON,
}

_WORD_START = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
_WORD_CONT = _WORD_START | set("0123456789'")


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.length = len(source)

    # ---------- phase 1: raw scan ----------

    def _peek(self, offset=0):
        p = self.pos + offset
        return self.source[p] if p < self.length else ""

    def _advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def _raw_scan(self):
        raw_tokens = []
        while self.pos < self.length:
            ch = self._peek()

            if ch in " \t\r\n":
                self._advance()
                continue

            if ch == "~":
                self._scan_comment()
                continue

            if ch == '"':
                raw_tokens.append(self._scan_string())
                continue

            if ch.isdigit():
                raw_tokens.append(self._scan_number())
                continue

            if ch in _WORD_START:
                raw_tokens.append(self._scan_word())
                continue

            if ch in _PUNCT_MAP:
                line = self.line
                self._advance()
                raw_tokens.append(_RawToken("PUNCT", ch, line))
                continue

            raise VibesLexError(
                f"VibeError: unrecognized character {ch!r} on line {self.line}"
            )

        return raw_tokens

    def _scan_comment(self):
        # consumes the opening ~, everything up to (and including) the closing ~
        start_line = self.line
        self._advance()  # opening ~
        while self.pos < self.length and self._peek() != "~":
            self._advance()
        if self.pos >= self.length:
            raise VibesLexError(
                f"VibeError: unterminated comment starting on line {start_line}"
            )
        self._advance()  # closing ~

    def _scan_string(self):
        start_line = self.line
        self._advance()  # opening quote
        chars = []
        while True:
            if self.pos >= self.length:
                raise VibesLexError(
                    f"VibeError: unterminated string starting on line {start_line}"
                )
            ch = self._peek()
            if ch == '"':
                self._advance()
                break
            if ch == "\\":
                self._advance()
                esc = self._advance() if self.pos < self.length else ""
                chars.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(esc, esc))
                continue
            chars.append(self._advance())
        return _RawToken("STRING", "".join(chars), start_line)

    def _scan_number(self):
        start_line = self.line
        chars = []
        while self.pos < self.length and (self._peek().isdigit() or self._peek() == "."):
            chars.append(self._advance())
        text = "".join(chars)
        value = float(text) if "." in text else int(text)
        return _RawToken("NUMBER", value, start_line)

    def _scan_word(self):
        start_line = self.line
        chars = []
        while self.pos < self.length and self._peek() in _WORD_CONT:
            chars.append(self._advance())
        # allow a single trailing '?' glued to the word (used only by "who?")
        if self.pos < self.length and self._peek() == "?":
            chars.append(self._advance())
        return _RawToken("WORD", "".join(chars), start_line)

    # ---------- phase 2: keyword folding ----------

    def tokenize(self):
        raw = self._raw_scan()
        tokens = []
        i = 0
        n_raw = len(raw)

        while i < n_raw:
            rt = raw[i]

            if rt.kind == "WORD":
                match = self._match_keyword(raw, i)
                if match is not None:
                    ttype, length, text = match
                    tokens.append(Token(ttype, text, rt.line))
                    i += length
                else:
                    tokens.append(Token(TokenType.IDENT, rt.value, rt.line))
                    i += 1
                continue

            if rt.kind == "STRING":
                tokens.append(Token(TokenType.STRING, rt.value, rt.line))
                i += 1
                continue

            if rt.kind == "NUMBER":
                tokens.append(Token(TokenType.NUMBER, rt.value, rt.line))
                i += 1
                continue

            if rt.kind == "PUNCT":
                tokens.append(Token(_PUNCT_MAP[rt.value], rt.value, rt.line))
                i += 1
                continue

            raise VibesLexError(f"VibeError: unknown raw token kind {rt.kind!r}")

        tokens.append(Token(TokenType.EOF, None, self.line))
        return tokens

    def _match_keyword(self, raw, i):
        """Try every phrase (already sorted longest-first) against raw[i:i+len(phrase)].
        Returns (TokenType, phrase_length, matched_text) or None."""
        for phrase_words, ttype in KEYWORDS:
            plen = len(phrase_words)
            if i + plen > len(raw):
                continue
            candidate = raw[i:i + plen]
            if all(c.kind == "WORD" for c in candidate) and all(
                c.value.lower() == w for c, w in zip(candidate, phrase_words)
            ):
                text = " ".join(c.value for c in candidate)
                return ttype, plen, text
        return None


def tokenize(source: str):
    return Lexer(source).tokenize()
