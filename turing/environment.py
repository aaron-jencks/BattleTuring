from typing import List


class TheTape:
    def __init__(self):
        self.memory = []
        self.pointers: List[int] = []
        self.alive: List[bool] = []
        self.default_character = '0'
        self.initial_string = ''
        self.reset()

    def to_dict(self) -> dict:
        return {
            'memory': self.memory,
            'pointers': self.pointers,
            'alive': self.alive
        }

    def __len__(self):
        return len(self.memory)

    def __repr__(self):
        result = ''
        ploc = sorted(self.pointers)
        prev = 0
        for p in ploc:
            diff = p - prev
            result += ' '*diff + 'v'
        result += '\n' + ''.join(self.memory)
        return result

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.pointers[item]
        else:
            return self.pointers[item.ident]

    def clear_memory(self, change_pointers: bool = False):
        if change_pointers:
            self.pointers = [0] * len(self.pointers)
        self.memory = []

    def initialize_tape(self, s: str, reset_pointers: bool = False):
        self.clear_memory(reset_pointers)
        self.initial_string = s
        for c in s:
            self.memory.append(c)

    def reset(self, reset_pointers: bool = False):
        self.initialize_tape(self.initial_string, reset_pointers)
        self.memory.append(self.generate_new())

    def register_machine(self, starting_pos: int) -> int:
        nid = len(self.pointers)
        self.pointers.append(0)
        self.alive.append(True)
        if starting_pos != 0:
            self.move(nid, abs(starting_pos), starting_pos > 0)
        return nid

    def unregister_machine(self, ident: int):
        if 0 <= ident < len(self.pointers):
            self.alive[ident] = False

    def generate_new(self) -> str:
        return self.default_character

    def read(self, ident: int) -> str:
        if 0 <= ident < len(self.pointers):
            return self.memory[self.pointers[ident]]
        return ''

    def move(self, ident: int, n: int, right: bool = True):
        if 0 <= ident < len(self.pointers):
            if right:
                self.pointers[ident] += n
            else:
                self.pointers[ident] -= n

            if self.pointers[ident] >= len(self.memory):
                diff = (self.pointers[ident] - len(self.memory)) + 1
                for _ in range(diff):
                    self.memory.append(self.generate_new())
            elif self.pointers[ident] < 0:
                diff = abs(self.pointers[ident])
                new_mem = []
                for _ in range(diff):
                    new_mem.append(self.generate_new())
                self.memory = new_mem + self.memory
                self.pointers[ident] = 0

    def write(self, ident: int, c: str):
        if 0 <= ident < len(self.pointers):
            self.memory[self.pointers[ident]] = c
