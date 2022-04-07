from enum import Enum
from typing import List

from parsing.values import Value


class CommandEnum(Enum):
    RIGHT = 0
    LEFT = 1
    READ = 2
    WRITE = 3
    JUMP = 4
    CALL = 5
    HALT = 6
    COMPARE = 7
    VALUE = 8
    COND_JUMP = 9
    STACK_MANIP = 10


class TuringCommand:
    def __init__(self, ctype: CommandEnum):
        self.type = ctype


class MoveCommand(TuringCommand):
    def __init__(self, direction: CommandEnum):
        super().__init__(direction)


class ReadCommand(TuringCommand):
    def __init__(self):
        super().__init__(CommandEnum.READ)


class WriteCommand(TuringCommand):
    def __init__(self):
        super().__init__(CommandEnum.WRITE)


class JumpCommand(TuringCommand):
    def __init__(self, distance: int):
        super().__init__(CommandEnum.JUMP)
        self.distance = distance


class CondJumpCommand(TuringCommand):
    def __init__(self, distance: int):
        super().__init__(CommandEnum.JUMP)
        self.distance = distance


class CallCommand(TuringCommand):
    def __init__(self, name: str):
        super().__init__(CommandEnum.CALL)
        self.name = name


class HaltCommand(TuringCommand):
    def __init__(self):
        super().__init__(CommandEnum.HALT)


class ValueCommand(TuringCommand):
    def __init__(self, v: Value):
        super().__init__(CommandEnum.VALUE)
        self.value = v


class ComparisonCommand(TuringCommand):
    def __init__(self, nargs: int = 2):
        super().__init__(CommandEnum.COMPARE)
        self.nargs = nargs

    def evaluate(self, args: List[Value]) -> bool:
        pass


class EqualsComparison(ComparisonCommand):
    def __init__(self):
        super().__init__()

    def evaluate(self, args: List[Value]) -> bool:
        return args[0] == args[1]


class NotEqualsComparison(ComparisonCommand):
    def __init__(self):
        super().__init__()

    def evaluate(self, args: List[Value]) -> bool:
        return args[0] != args[1]


class GreaterComparison(ComparisonCommand):
    def __init__(self):
        super().__init__()

    def evaluate(self, args: List[Value]) -> bool:
        return args[0] > args[1]


class LessComparison(ComparisonCommand):
    def __init__(self):
        super().__init__()

    def evaluate(self, args: List[Value]) -> bool:
        return args[0] < args[1]


class GreaterEqualsComparison(ComparisonCommand):
    def __init__(self):
        super().__init__()

    def evaluate(self, args: List[Value]) -> bool:
        return args[0] >= args[1]


class LessEqualsComparison(ComparisonCommand):
    def __init__(self):
        super().__init__()

    def evaluate(self, args: List[Value]) -> bool:
        return args[0] <= args[1]


class NegationComparison(ComparisonCommand):
    def __init__(self):
        super().__init__(1)

    def evaluate(self, args: List[Value]) -> bool:
        return not args[0].value


class StackManipulationCommand(TuringCommand):
    def __init__(self):
        super().__init__(CommandEnum.STACK_MANIP)

    def execute(self, stack: List[Value]):
        pass


class DuplicateStackCommand(StackManipulationCommand):
    def execute(self, stack: List[Value]):
        stack.append(stack[-1])
