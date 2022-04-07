import pathlib
from typing import List, Union

from .tokens import TokenController, Token
from .bufferio import BufferContainer


class LexerError(BaseException):
    def __init__(self, file: str, line: int, c: str):
        super().__init__('Lexer error in file {} line {} near {}\n\tUnexpected symbol.'.format(file, line, c))


class InvalidLexemeError(BaseException):
    def __init__(self, file: str, line: int, c: str):
        super().__init__('Lexer error in file {} line {} near {}\n\tDoes not match any valid token.'.format(file, line,
                                                                                                            c))


class Lexeme:
    def __init__(self, code: int, token: str, line: int = 0, file: pathlib.Path = None):
        self.code = code
        self.token = token
        self.line = line
        self.file = file

    def __repr__(self):
        return 'File {} Line {:>8} Token {:>3} Text {}'.format(str(self.file)[-20:], self.line, self.code, self.token)


class Lexer:
    def __init__(self, buffer: BufferContainer):
        self.buffer = buffer
        self.reset_buffer: List[List[Lexeme]] = [[]]
        self.lexeme_buffer: List[Lexeme] = []

    def __repr__(self):
        return '{}'.format(self.buffer)

    def strip_spaces(self):
        self.buffer.set_reset_point()
        c = self.buffer.read_char()
        while len(c) > 0 and c.isspace():
            self.buffer.set_reset_point()
            c = self.buffer.read_char()
        self.buffer.reset()

    def find_matching_token(self, check_all: bool = False, return_comments: bool = False) -> Union[Token, None]:
        vt = TokenController.get_instance()

        keep_going = True
        while keep_going:
            keep_going = False
            for tok in (vt.enabled_tokens if not check_all else vt.tokens):
                if tok.matches(self.buffer):
                    self.buffer.reset()
                    if tok.code >= 0 or return_comments:
                        return tok
                    else:
                        # We found a comment lexeme
                        tok.parse_file(self.buffer)
                        self.strip_spaces()
                        if self.buffer.is_empty():
                            return None
                        keep_going = True
                    break
                else:
                    self.buffer.reset()

        return None

    def has_next(self) -> bool:
        self.strip_spaces()

        if self.buffer.is_empty():
            return False

        if self.find_matching_token(True) is not None:
            return True
        elif self.find_matching_token(True, True) is not None:
            return False
        else:
            raise InvalidLexemeError(self.buffer.error_name, self.buffer.line, self.buffer.read_char())

    def get_next(self) -> Union[Lexeme, None]:
        self.strip_spaces()

        if self.buffer.is_empty():
            return None

        if len(self.lexeme_buffer) > 0:
            lex = self.lexeme_buffer.pop(-1)
            self.reset_buffer[-1].append(lex)
            return lex

        tok = self.find_matching_token()
        found = tok is not None
        if found:
            tline = self.buffer.line
            lexeme = tok.parse_file(self.buffer)
            lex = Lexeme(tok.code, lexeme, tline, self.buffer.error_name)

            if lex.code >= 0:
                self.reset_buffer[-1].append(lex)
                return lex

        if not found and not self.buffer.has_error:
            self.buffer.has_error = True
            self.buffer.error = LexerError(self.buffer.error_name, self.buffer.line, self.buffer.read_char())

        if self.buffer.has_error:
            raise self.buffer.error

        self.buffer.set_reset_point()

    def reset(self):
        if len(self.reset_buffer) > 0:
            self.lexeme_buffer += self.reset_buffer[-1]
            self.reset_buffer[-1].clear()

    def set_reset_point(self):
        if len(self.reset_buffer) > 0:
            self.reset_buffer[-1].clear()

    def add_reset_buffer(self):
        self.reset_buffer.append([])

    def pop_reset_buffer(self):
        if len(self.reset_buffer) > 0:
            pt = self.reset_buffer.pop(-1)
            if len(self.reset_buffer) > 0:
                self.reset_buffer[-1] += pt
