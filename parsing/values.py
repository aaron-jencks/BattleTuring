class Value:
    def __init__(self):
        self.value = None

    def __eq__(self, other):
        if isinstance(other, Value):
            return other.value == self.value
        return False

    def __lt__(self, other):
        if isinstance(other, Value):
            return other.value < self.value
        return False

    def __gt__(self, other):
        if isinstance(other, Value):
            return other.value > self.value
        return False

    def __repr__(self):
        return repr(self.value)


class Numeric(Value):
    def __init__(self, n: int):
        super().__init__()
        self.value = n


class Character(Value):
    def __init__(self, c: str):
        super().__init__()
        self.value = c


class Boolean(Value):
    def __init__(self, b: bool):
        super().__init__()
        self.value = b
