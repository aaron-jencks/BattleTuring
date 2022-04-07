from typing import List

from .bufferio import BufferContainer


class Token:
    def __init__(self, code: int, pattern: str):
        self.code = code
        self.pattern = pattern
        self.enabled = True

    def matches(self, s: BufferContainer) -> bool:
        pass

    def parse_file(self, s: BufferContainer) -> str:
        pass


class SimpleStringToken(Token):
    def __init__(self, code: int, pattern: str):
        super().__init__(code, pattern)

    def matches(self, s: BufferContainer) -> bool:
        for c in self.pattern:
            if c != s.read_char():
                s.reset()
                return False
        s.reset()
        return True

    def parse_file(self, s: BufferContainer) -> str:
        result = ''
        for c in self.pattern:
            if c != s.read_char():
                s.reset()
                return ''
            result += c
        return result


class LiteralToken(Token):
    def __init__(self):
        super().__init__(300, r"'.+'")

    def matches(self, s: BufferContainer) -> bool:
        if s.read_char() == "'":
            s.read_char()
            if s.read_char() != "'":
                s.reset()
                return False
            s.reset()
            return True
        s.reset()
        return False

    def parse_file(self, s: BufferContainer) -> str:
        result = ''
        if s.read_char() == "'":
            result += "'" + s.read_char() + "'"
            if s.read_char() != "'":
                s.reset()
                return ''
            return result
        s.reset()
        return ''


class CommentToken(Token):
    def __init__(self):
        super().__init__(-1, r"#.+\n")

    def matches(self, s: BufferContainer) -> bool:
        if s.read_char() == "#":
            s.reset()
            return True
        s.reset()
        return False

    def parse_file(self, s: BufferContainer) -> str:
        result = ''
        if s.read_char() == "#":
            result += "#"
            c = s.read_char()
            while c not in "\n\f":
                result += c
                if s.is_empty():
                    return result
                c = s.read_char()
            result += c
            return result
        s.reset()
        return ''


class IdentifierToken(Token):
    def __init__(self):
        super().__init__(302, r"[^0-9][_a-zA-Z]+[_a-zA-Z0-9]*")
        self.initial_character_string = "_abcdefghijklmnopqrstuvwxyABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.accepting_character_string = self.initial_character_string + '0123456789'

    def matches(self, s: BufferContainer) -> bool:
        if s.read_char() in self.initial_character_string:
            s.reset()
            return True
        s.reset()
        return False

    def parse_file(self, s: BufferContainer) -> str:
        result = ''
        c = s.read_char()
        if c in self.initial_character_string:
            result += c
            c = s.read_char()
            while c in self.accepting_character_string:
                result += c
                if s.is_empty():
                    return result
                c = s.read_char()
            s.push_str(c, False)
            return result
        s.reset()
        return ''


class IntegerLiteralToken(Token):
    def __init__(self):
        super().__init__(301, r"\d+")
        self.digits = '0123456789'

    def matches(self, s: BufferContainer) -> bool:
        if s.read_char() in self.digits:
            s.reset()
            return True
        s.reset()
        return False

    def parse_file(self, s: BufferContainer) -> str:
        result = ''
        c = s.read_char()
        if c in self.digits:
            result += c
            c = s.read_char()
            while c in self.digits:
                result += c
                if s.is_empty():
                    return result
                c = s.read_char()
            s.push_str(c, False)
            return result
        s.reset()
        return ''


class SingleCharToken(SimpleStringToken):
    def __init__(self, c: str):
        super().__init__(ord(c), c)


class TokenController:
    instance = None

    def __init__(self):
        self.tokens: List[Token] = []
        self.generate_tokens()

    @property
    def enabled_tokens(self) -> List[Token]:
        return [t for t in self.tokens if t.enabled]

    @staticmethod
    def get_instance():
        if TokenController.instance is None:
            TokenController.instance = TokenController()
        return TokenController.instance

    def generate_tokens(self):
        for o in single_char_operators:
            self.tokens.append(SingleCharToken(o))
        for ki, k in enumerate(keywork_tokens):
            self.tokens.append(SimpleStringToken(303 + ki, k))
        self.tokens.append(LiteralToken())
        self.tokens.append(CommentToken())
        self.tokens.append(IdentifierToken())
        self.tokens.append(IntegerLiteralToken())


single_char_operators = [
    ';', '^', '>', '<', ':', '=', '!', '{', '}', '(', ')'
]


keywork_tokens = [
    'if', 'else',
    'while',
    'read', 'write',
    'goto',
    'left', 'right',
    '!=', '<<', '>>', '<=', '>=',
    'true', 'false', 'halt'
]
