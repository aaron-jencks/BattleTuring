from typing import List

from parsing.commands import TuringCommand, MoveCommand, CommandEnum, ReadCommand, WriteCommand, JumpCommand, \
    CondJumpCommand, CallCommand, HaltCommand, ValueCommand, EqualsComparison, ComparisonCommand, \
    StackManipulationCommand
from parsing.parser import AST
from parsing.values import Value, Character, Boolean, Numeric
from turing.machine import TuringMachine


class Commander:
    def __init__(self, tree: AST):
        self.tree = tree
        self.stack: List[Value] = []
        self.command_history = []
        self.command_buffer: List[TuringCommand] = []
        self.command_buffer += reversed(self.tree.compile())
        self.move_buffer = []

    def has_next(self) -> bool:
        return len(self.command_buffer) > 0

    def run_next(self, machine: TuringMachine):
        if len(self.move_buffer) > 0:
            distance, c = self.move_buffer.pop(-1)
            if distance.value > 1:
                distance.value -= 1
                self.move_buffer.append((distance, c))
            machine.move(1, c.type == CommandEnum.RIGHT)
            return

        while len(self.command_buffer) > 0:
            c = self.command_buffer.pop(-1)
            self.command_history.append(c)
            if isinstance(c, MoveCommand):
                distance = self.stack.pop(-1).value
                if distance > 1:
                    self.move_buffer.append((Numeric(distance - 1), c))
                machine.move(1, c.type == CommandEnum.RIGHT)
                return
            elif isinstance(c, ReadCommand):
                self.stack.append(Character(machine.read()))
                return
            elif isinstance(c, WriteCommand):
                machine.write(self.stack.pop(-1).value)
                return
            elif isinstance(c, CondJumpCommand):
                if self.stack.pop(-1).value:
                    for _ in range(abs(c.distance)):
                        if c.distance > 0:
                            if len(self.command_buffer) > 0:
                                self.command_history.append(self.command_buffer.pop(-1))
                        else:
                            if len(self.command_history) > 0:
                                self.command_buffer.append(self.command_history.pop(-1))
                    if c.distance < 0:
                        if len(self.command_history) > 0:
                            self.command_buffer.append(self.command_history.pop(-1))
            elif isinstance(c, JumpCommand):
                for _ in range(abs(c.distance)):
                    if c.distance > 0:
                        if len(self.command_buffer) > 0:
                            self.command_history.append(self.command_buffer.pop(-1))
                    else:
                        if len(self.command_history) > 0:
                            self.command_buffer.append(self.command_history.pop(-1))
                if c.distance < 0:
                    if len(self.command_history) > 0:
                        self.command_buffer.append(self.command_history.pop(-1))
            elif isinstance(c, CallCommand):
                self.command_buffer += reversed(self.tree.env[c.name])
            elif isinstance(c, HaltCommand):
                self.command_buffer.clear()
                self.stack.clear()
                self.command_history.clear()
                return
            elif isinstance(c, ValueCommand):
                self.stack.append(c.value)
            elif isinstance(c, ComparisonCommand):
                args = []
                for _ in range(c.nargs):
                    args.append(self.stack.pop(-1))
                self.stack.append(Boolean(c.evaluate(args)))
            elif isinstance(c, StackManipulationCommand):
                c.execute(self.stack)
        self.command_buffer.clear()
        self.stack.clear()
        self.command_history.clear()
        return
