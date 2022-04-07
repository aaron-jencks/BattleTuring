from copy import deepcopy, copy
from typing import List, Dict, Optional, Union
from enum import Enum

from .lexer import Lexer, Lexeme
from .commands import TuringCommand, EqualsComparison, LessComparison, GreaterComparison, NotEqualsComparison, \
    LessEqualsComparison, GreaterEqualsComparison, NegationComparison, ReadCommand, ValueCommand, MoveCommand, \
    CommandEnum, WriteCommand, CallCommand, JumpCommand, CondJumpCommand, HaltCommand, DuplicateStackCommand, \
    OrComparison, AndComparison
from .values import Numeric, Character, Boolean

"""
An expression will consist of:

Any binary operator followed by the left and then right expressions
A unary operator followed by an expression

( an expression and then )

read/^

Binary operators are (=, !=, <=, >=, <, >)
Unary operators are (!)

a literal

A statement block will consist of:
{ followed by any number of statements and then }

A statement will consist of this:
; by itself

>>/<</left/right and a number followed by ;

write and a literal followed by ;

goto an identifier and then a ;

if(expression) followed by a statement block
followed by an optional else and another statement block

while(expression) followed by a statement block

A function declaration will consist of:

identifier followed by an :

recursion is supported
"""


class ParserError(BaseException):
    def __init__(self, l: Lexeme, description: str):
        super().__init__('Parser Error Line {} near {}\n\t{}'.format(l.line, l.token, description))


class Environment:
    def __init__(self):
        self.labels: Dict[str, ASTNode] = {}
        self.label_stack = []

    def nest(self):
        self.label_stack.append(copy(self.labels))

    def unnest(self):
        self.labels = self.label_stack.pop(-1)

    def __contains__(self, item):
        return item in self.labels

    def __getitem__(self, item):
        return self.labels[item]

    def __setitem__(self, key: str, value):
        self.labels[key] = value


class ASTNode:
    def __init__(self, code: int):
        self.code = code

    def traverse(self) -> List[Lexeme]:
        pass

    def compile(self, env: Environment) -> List[TuringCommand]:
        pass


class TypeEnum(Enum):
    NUMBER = 0
    CHARACTER = 1
    BOOLEAN = 2


class ExpressionAST(ASTNode):
    def __init__(self, rtype: TypeEnum, code: int):
        super().__init__(code)
        self.rtype = rtype


class NestedExpressionAST(ExpressionAST):
    def __init__(self, inner: ExpressionAST, lp: Lexeme, rp: Lexeme):
        super().__init__(inner.rtype, inner.code)
        self.inner = inner
        self.lp = lp
        self.rp = rp

    def traverse(self) -> List[Lexeme]:
        return [self.lp] + self.inner.traverse() + [self.rp]

    def compile(self, env: Environment) -> List[TuringCommand]:
        return self.inner.compile(env)


class BinaryOperatorExpression(ExpressionAST):
    def __init__(self, operator: Lexeme, lhs: ExpressionAST, rhs: ExpressionAST):
        super().__init__(TypeEnum.BOOLEAN, operator.code)
        if lhs.rtype != rhs.rtype:
            raise ParserError(operator, 'Argument Types Do Not Match Each Other')
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def traverse(self) -> List[Lexeme]:
        return [self.operator] + self.lhs.traverse() + self.rhs.traverse()

    def compile(self, env: Environment) -> List[TuringCommand]:
        result = []
        if self.operator.code == ord('='):
            result.append(EqualsComparison())
        elif self.operator.code == ord('<'):
            result.append(LessComparison())
        elif self.operator.code == ord('>'):
            result.append(GreaterComparison())
        elif self.operator.code == ord('|'):
            result.append(OrComparison())
        elif self.operator.code == ord('&'):
            result.append(AndComparison())
        elif self.operator.code == 310:
            result.append(NotEqualsComparison())
        elif self.operator.code == 313:
            result.append(LessEqualsComparison())
        elif self.operator.code == 314:
            result.append(GreaterEqualsComparison())
        result = self.lhs.compile(env) + self.rhs.compile(env) + result
        return result


class UnaryOperatorExpression(ExpressionAST):
    def __init__(self, operator: Lexeme, rhs: ExpressionAST):
        super().__init__(TypeEnum.BOOLEAN, operator.code)
        if rhs.rtype != TypeEnum.BOOLEAN:
            raise ParserError(operator, 'Unary Operator Expression must return a boolean')
        self.operator = operator
        self.rhs = rhs

    def traverse(self) -> List[Lexeme]:
        return [self.operator] + self.rhs.traverse()

    def compile(self, env: Environment) -> List[TuringCommand]:
        return self.rhs.compile(env) + [NegationComparison()]


class ReadExpression(ExpressionAST):
    def __init__(self, command: Lexeme):
        super().__init__(TypeEnum.CHARACTER, command.code)
        self.command = command

    def traverse(self) -> List[Lexeme]:
        return [self.command]

    def compile(self, env: Environment) -> List[TuringCommand]:
        return [ReadCommand()]


class PrimitiveExpression(ExpressionAST):
    def __init__(self, lex: Lexeme, t: TypeEnum):
        super().__init__(t, lex.code)
        self.lex = lex

    def traverse(self) -> List[Lexeme]:
        return [self.lex]

    def compile(self, env: Environment) -> List[TuringCommand]:
        if self.code == 301:
            v = Numeric(int(self.lex.token))
        elif self.code == 300:
            v = Character(self.lex.token[1:-1])
        elif self.code in [316, 317]:
            v = Boolean(self.lex.token == 'true')
        else:
            v = None
        return [ValueCommand(v)]


class StatementAST(ASTNode):
    pass


class StatementBlockAST(ASTNode):
    def __init__(self, statements: List[StatementAST], lb: Lexeme, rb: Lexeme):
        super().__init__(lb.code)
        self.statements = statements
        self.lb = lb
        self.rb = rb

    def traverse(self) -> List[Lexeme]:
        result = [self.lb]
        for s in self.statements:
            result += s.traverse()
        return result + [self.rb]

    def compile(self, env: Environment) -> List[TuringCommand]:
        result = []
        for s in self.statements:
            result += s.compile(env)
        return result


class SemicolonStatementAST(StatementAST):
    def __init__(self, semi: Lexeme):
        super().__init__(semi.code)
        self.semi = semi

    def traverse(self) -> List[Lexeme]:
        return [self.semi]

    def compile(self, env: Environment) -> List[TuringCommand]:
        return []


class HaltStatementAST(SemicolonStatementAST):
    def __init__(self, halt: Lexeme, semi: Lexeme):
        super().__init__(semi)
        self.halt = halt

    def traverse(self) -> List[Lexeme]:
        return [self.halt] + super().traverse()

    def compile(self, env: Environment) -> List[TuringCommand]:
        return [HaltCommand()]


class MoveStatementAST(SemicolonStatementAST):
    def __init__(self, semi: Lexeme, number: ExpressionAST, command: Lexeme):
        super().__init__(semi)
        if number.rtype != TypeEnum.NUMBER:
            raise ParserError(command, 'Moving the machine requires a numeric expression')
        self.number = number
        self.command = command

    def traverse(self) -> List[Lexeme]:
        return [self.command] + self.number.traverse() + super().traverse()

    def compile(self, env: Environment) -> List[TuringCommand]:
        return super().compile(env) + self.number.compile(env) + \
               [MoveCommand(CommandEnum.LEFT if self.command.code in [309, 312] else CommandEnum.RIGHT)]


class WriteStatementAST(SemicolonStatementAST):
    def __init__(self, semi: Lexeme, c: ExpressionAST, command: Lexeme):
        super().__init__(semi)
        if c.rtype != TypeEnum.CHARACTER:
            raise ParserError(command, 'Can\'t write anything other than a single character')
        self.char = c
        self.command = command

    def traverse(self) -> List[Lexeme]:
        return [self.command] + self.char.traverse() + super().traverse()

    def compile(self, env: Environment) -> List[TuringCommand]:
        return self.char.compile(env) + [WriteCommand()]


class GotoStatementAST(SemicolonStatementAST):
    def __init__(self, command: Lexeme, ident: Lexeme, semi: Lexeme, env: Environment):
        super().__init__(semi)
        self.goto = command
        self.identifier = ident
        if self.identifier.token not in env:
            raise ParserError(ident, '{} is not defined as a function'.format(ident.token))

    def traverse(self) -> List[Lexeme]:
        return [self.goto, self.identifier] + super().traverse()

    def compile(self, env: Environment) -> List[TuringCommand]:
        return [CallCommand(self.identifier.token)]


class ControlFlowStatementAST(StatementAST):
    def __init__(self, contr: Lexeme, lp: Lexeme, rp: Lexeme, cond: ExpressionAST, sb: StatementBlockAST):
        super().__init__(contr.code)
        if cond.rtype != TypeEnum.BOOLEAN:
            raise ParserError(contr, 'Conditional Statement must return a boolean')
        self.contr = contr
        self.lp = lp
        self.rp = rp
        self.exp = cond
        self.sb = sb

    def traverse(self) -> List[Lexeme]:
        return [self.contr, self.lp] + self.exp.traverse() + [self.rp] + self.sb.traverse()

    def compile(self, env: Environment) -> List[TuringCommand]:
        sbc = self.sb.compile(env)
        expc = self.exp.compile(env)
        if self.code == 305:
            return expc + [NegationComparison(), CondJumpCommand(len(sbc) + 1)] + sbc + \
                   [JumpCommand(-(len(sbc) + 2 + len(expc)))]
        else:
            return expc + [NegationComparison(), CondJumpCommand(len(sbc))] + sbc


class ElseControlFlowStatementAST(ControlFlowStatementAST):
    def __init__(self, contr: Lexeme, lp: Lexeme, rp: Lexeme, cond: ExpressionAST, sb: StatementBlockAST,
                 el: Lexeme, esb: StatementBlockAST):
        super().__init__(contr, lp, rp, cond, sb)
        self.el = el
        self.esb = esb

    def traverse(self) -> List[Lexeme]:
        return [self.contr, self.lp] + self.exp.traverse() + [self.rp] + self.sb.traverse()

    def compile(self, env: Environment) -> List[TuringCommand]:
        sbc = self.sb.compile(env)
        expc = self.exp.compile(env)
        esbc = self.esb.compile(env)
        return expc + [DuplicateStackCommand(), NegationComparison(), CondJumpCommand(len(sbc))] + sbc + \
               [CondJumpCommand(len(esbc))] + esbc


class FunctionDefinitionAST(ASTNode):
    def __init__(self, ident: Lexeme, colon: Lexeme, sb: StatementBlockAST, env: Environment):
        super().__init__(colon.code)
        self.name = ident
        self.colon = colon
        self.sb = sb
        env[self.name.token] = self.sb

    def traverse(self) -> List[Lexeme]:
        return [self.name, self.colon] + self.sb.traverse()

    def compile(self, env: Environment) -> List[TuringCommand]:
        env[self.name.token] = self.sb.compile(env)
        return []


class ProgramAST(ASTNode):
    def __init__(self, statements: List[Union[StatementAST, FunctionDefinitionAST]]):
        super().__init__(0)
        self.statements = statements

    def traverse(self) -> List[Lexeme]:
        result = []
        for s in self.statements:
            result += s.traverse()
        return result

    def compile(self, env: Environment) -> List[TuringCommand]:
        result = []
        for s in self.statements:
            result += s.compile(env)
        return result


class AST:
    def __init__(self, lexer: Lexer):
        self.root = None
        self.env = Environment()
        self.lexer = lexer

    def build_tree(self):
        statements = []
        while True:
            stat = self.parse_statement()
            if stat is not None:
                statements.append(stat)
                continue
            else:
                stat = self.parser_function_definition()
                if stat is not None:
                    statements.append(stat)
                    continue
            break
        self.root = ProgramAST(statements)

    def parse_expression(self) -> Optional[ExpressionAST]:
        self.lexer.add_reset_buffer()
        eme = self.lexer.get_next()
        if eme is not None:
            if eme.code in list(map(ord, '<>=!|&')) + [311, 314, 315]:
                # We found an operator
                expa = self.parse_expression()
                if expa is not None:
                    if eme.code == ord('!'):
                        self.lexer.pop_reset_buffer()
                        return UnaryOperatorExpression(eme, expa)
                    expb = self.parse_expression()
                    if expb is not None:
                        self.lexer.pop_reset_buffer()
                        return BinaryOperatorExpression(eme, expa, expb)
                    raise ParserError(eme, 'Missing second expression for binary operator')
                raise ParserError(eme, 'Missing first expression for binary operator')
            elif eme.code in [ord('^'), 306]:
                self.lexer.pop_reset_buffer()
                return ReadExpression(eme)
            elif eme.code == ord('('):
                exp = self.parse_expression()
                if exp is not None:
                    pr = self.lexer.get_next()
                    if pr.code == ord(')'):
                        self.lexer.pop_reset_buffer()
                        return NestedExpressionAST(exp, eme, pr)
                    raise ParserError(eme, 'Unmatched (')
                raise ParserError(eme, 'Unfilled nested expression')
            elif eme.code in [300, 301]:
                self.lexer.pop_reset_buffer()
                return PrimitiveExpression(eme, TypeEnum.CHARACTER if eme.code == 300 else TypeEnum.NUMBER)
            elif eme.code in [316, 317]:
                self.lexer.pop_reset_buffer()
                return PrimitiveExpression(eme, TypeEnum.BOOLEAN)
        self.lexer.reset()
        self.lexer.pop_reset_buffer()
        return None

    def parse_statement(self) -> Optional[StatementAST]:
        self.lexer.add_reset_buffer()
        eme = self.lexer.get_next()
        if eme is not None:
            if eme.code == ord(';'):
                self.lexer.pop_reset_buffer()
                return SemicolonStatementAST(eme)
            elif eme.code in [309, 310, 312, 313]:
                num = self.parse_expression()
                if num is not None:
                    semi = self.lexer.get_next()
                    if semi is not None and semi.code == ord(';'):
                        self.lexer.pop_reset_buffer()
                        return MoveStatementAST(semi, num, eme)
                    raise ParserError(eme, 'Missing Semicolon')
                raise ParserError(eme, 'Move command missing numeric expression')
            elif eme.code == 307:
                lit = self.parse_expression()
                if lit is not None:
                    semi = self.lexer.get_next()
                    if semi is not None and semi.code == ord(';'):
                        self.lexer.pop_reset_buffer()
                        return WriteStatementAST(semi, lit, eme)
                    raise ParserError(eme, 'Missing Semicolon')
                raise ParserError(eme, 'Write command without a character expression')
            elif eme.code == 308:
                lit = self.lexer.get_next()
                if lit is not None and lit.code == 302:
                    semi = self.lexer.get_next()
                    if semi is not None and semi.code == ord(';'):
                        self.lexer.pop_reset_buffer()
                        return GotoStatementAST(eme, lit, semi, self.env)
                    raise ParserError(eme, 'Missing Semicolon')
                raise ParserError(eme, 'Goto command without a target')
            elif eme.code in [303, 305]:
                # flow control
                pl = self.lexer.get_next()
                if pl is not None and pl.code == ord('('):
                    exp = self.parse_expression()
                    if exp is not None:
                        pr = self.lexer.get_next()
                        if pr is not None and pr.code == ord(')'):
                            sb = self.parse_statement_block()
                            if sb is not None:
                                if eme.code == 303:
                                    self.lexer.add_reset_buffer()
                                    elp = self.lexer.get_next()
                                    if elp is not None and elp.code == 304:
                                        esb = self.parse_statement_block()
                                        if esb is not None:
                                            self.lexer.pop_reset_buffer()
                                            return ElseControlFlowStatementAST(eme, pl, pr, exp, sb, elp, esb)
                                        raise ParserError(elp, 'Missing else statement block')
                                    self.lexer.reset()
                                    self.lexer.pop_reset_buffer()
                                self.lexer.pop_reset_buffer()
                                return ControlFlowStatementAST(eme, pl, pr, exp, sb)
                            raise ParserError(pr, 'Missing Statement block')
                        raise ParserError(pl, 'Unmatched (')
                    raise ParserError(pl, 'Missing conditional statement')
                raise ParserError(eme, 'Missing (')
            elif eme.code == 318:
                semi = self.lexer.get_next()
                if semi is not None and semi.code == ord(';'):
                    self.lexer.pop_reset_buffer()
                    return HaltStatementAST(eme, semi)
                raise ParserError(eme, 'Missing Semicolon')
        self.lexer.reset()
        self.lexer.pop_reset_buffer()
        return None

    def parse_statement_block(self) -> Optional[StatementBlockAST]:
        self.lexer.add_reset_buffer()
        rb = self.lexer.get_next()
        if rb is not None and rb.code == ord('{'):
            self.env.nest()
            statements = []
            stat = self.parse_statement()
            while stat is not None:
                statements.append(stat)
                stat = self.parse_statement()
            lb = self.lexer.get_next()
            if lb is not None:
                self.lexer.pop_reset_buffer()
                return StatementBlockAST(statements, rb, lb)
            raise ParserError(rb, 'Unmatched {')
        self.lexer.reset()
        self.lexer.pop_reset_buffer()
        return None

    def parser_function_definition(self) -> Optional[FunctionDefinitionAST]:
        self.lexer.add_reset_buffer()
        ident = self.lexer.get_next()
        if ident is not None and ident.code == 302:
            colon = self.lexer.get_next()
            if colon is not None and colon.code == ord(':'):
                self.env[ident.token] = None
                sb = self.parse_statement_block()
                if sb is not None:
                    self.lexer.pop_reset_buffer()
                    return FunctionDefinitionAST(ident, colon, sb, self.env)
                raise ParserError(colon, 'Function name missing statement block')
            raise ParserError(ident, 'Function name missing colon')
        self.lexer.reset()
        self.lexer.pop_reset_buffer()
        return None

    def compile(self) -> List[TuringCommand]:
        return self.root.compile(self.env)
