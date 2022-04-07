from typing import Union, Dict
import pathlib
import json


class BufferContainer:
    def __init__(self, buffer_size: int = 1024):
        self.line = 1
        self.has_error = False
        self.error: Union[None, BaseException] = None
        self.prev_reset_point = ''
        self.reset_point = ''
        self.reset_additions = []
        self.buffer = ''
        self.buffer_size = buffer_size
        self.line_start = True
        self.initial_position = True

    def __repr__(self):
        return 'file: {} line: {} contents: {}'.format(self.error_name[-5:], self.line, self.buffer[-5:])

    @property
    def error_name(self) -> str:
        return ''

    def is_empty(self) -> bool:
        return len(self.buffer) == 0

    def __len__(self) -> int:
        return len(self.buffer)

    def set_reset_point(self):
        if len(self.reset_point):
            if self.initial_position:
                self.initial_position = False

            self.prev_reset_point = self.reset_point[-1]
        self.reset_point = ''
        self.reset_additions = []

    def peek(self, n: int = 0) -> str:
        if (0 <= n < len(self.buffer)) or (n < 0 and abs(n) <= len(self.buffer)):
            return self.buffer[n]
        return ''

    def read_char(self) -> str:
        if len(self.buffer) == 0:
            # We hit the end of the file
            return ''

        c = self.buffer[-1]

        self.line_start = False
        if c == '\n' or c == '\f':
            self.line += 1

        if c == '\n' or c == '\r':
            self.line_start = True

        self.buffer = self.buffer[:-1]
        if len(self.reset_additions) == 0:
            self.reset_point += c
        else:
            i, s = self.reset_additions[-1]
            self.reset_additions[-1] = (i, s[:-1])
        return c

    def push_str(self, s: str, track_addition: bool = True, reset: bool = False):
        if track_addition:
            self.reset_additions.append((len(self.buffer), ''.join(reversed(s))))
        self.buffer += ''.join(reversed(s))
        if reset:
            self.reset()

    def reset(self):
        self.buffer += ''.join(reversed(self.reset_point))

        # Chop out the additions
        for i, s in self.reset_additions:
            self.buffer = self.buffer[:i] + self.buffer[i + len(s):]

        self.line_start = self.initial_position if len(self.prev_reset_point) == 0 else \
            (self.prev_reset_point == '\n' or self.prev_reset_point == '\r')

        for c in self.reset_point:
            if c == '\n' or c == '\f':
                self.line -= 1

        self.reset_point = ''


class FileContainer(BufferContainer):
    def __init__(self, filename: pathlib.Path, buffer_size: int = 1048576, fill_trigger: int = 10):
        super().__init__(buffer_size)
        self.fp = open(filename, 'rb')
        self.file = filename
        self.fill_trigger = fill_trigger

    def __del__(self):
        self.fp.close()

    def fill_buffer(self):
        chunk = ''.join(reversed(self.fp.read(self.buffer_size).decode('utf8')))
        self.buffer = chunk + self.buffer

    @property
    def error_name(self) -> str:
        return str(self.file)

    def is_empty(self) -> bool:
        if len(self.buffer) < self.fill_trigger:
            self.fill_buffer()

        return super().is_empty()

    def __len__(self) -> int:
        if len(self.buffer) < self.fill_trigger:
            self.fill_buffer()

        return super().__len__()

    def peek(self, n: int = 0) -> str:
        if len(self.buffer) < self.fill_trigger:
            self.fill_buffer()

        return super().peek(n)

    def read_char(self) -> str:
        if len(self.buffer) < self.fill_trigger:
            self.fill_buffer()

        return super().read_char()


class StringContainer(BufferContainer):
    def __init__(self, data: str):
        super().__init__(len(data))
        self.buffer = ''.join(list(reversed(data)))

    @property
    def error_name(self) -> str:
        return 'String'


class Serializable:
    def save(self, path: pathlib.Path):
        json_obj = self.to_dict()
        with open(path, 'w+') as fp:
            json.dump(json_obj, fp)

    def to_dict(self) -> Dict:
        pass
