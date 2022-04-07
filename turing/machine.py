from .environment import TheTape


class TuringMachine:
    def __init__(self, tape: TheTape, starting_position: int = 0):
        self.ident = tape.register_machine(starting_position)
        self.tape = tape

    def read(self) -> str:
        return self.tape.read(self.ident)

    def move(self, n: int, right: bool = True):
        self.tape.move(self.ident, n, right)

    def write(self, c: str):
        self.tape.write(self.ident, c)
            
