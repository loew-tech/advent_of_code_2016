import math
import re
from itertools import count
from typing import Generator

from constants import REGEX_DIGITS


class Bot:
    def __init__(self, value: int | None = None, low_bot: int | str | None = None, high_bot: int | str | None = None):
        self._values = [value] if value is not None else []
        self.low_nghbr = low_bot
        self.high_nghbr = high_bot

    def add_value(self, val: int) -> None:
        self._values.append(val)

    def get_high(self) -> int:
        max_index = self._values.index(max(self._values))
        return self._values.pop(max_index)

    def get_low(self) -> int:
        min_index = self._values.index(min(self._values))
        return self._values.pop(min_index)

    @property
    def low(self):
        return None if not self._values else min(self._values)

    @property
    def high(self):
        return None if not self._values else max(self._values)

    @property
    def can_proceed(self):
        return len(self._values) == 2

    def __repr__(self):
        return f'Bot(values={self._values}, low_nghbr={self.low_nghbr}, hihg_nghbr={self.high_nghbr})'


class Disc:

    def __init__(self, id_, num_pos, start_pos: int):
        self.id = id_
        self.num_pos = num_pos
        self.start_pos = start_pos

    @classmethod
    def from_str(cls, s: str) -> Disc:
        id_, num_pos, _, start_pos = map(int,re.findall(REGEX_DIGITS, s))
        return cls(id_, num_pos, start_pos)

    def is_solution(self, time: int) -> bool:
        return not ((time + self.id + self.start_pos) % self.num_pos)

    def __repr__(self):
        return f'Disc(_id={self.id}, num_pos={self.num_pos}, start_pos={self.start_pos})'

class LLNode:

    def __init__(self, id_=None, val=0, prev=None, next_=None):
        self.id, self.val, self.prev, self.next = id_, val, prev, next_

    def delete(self):
        neighbor = self.prev if self.prev is not self else None
        self.prev.next = self.next
        self.next.prev = self.prev
        self.next = None
        self.prev = None
        return neighbor

    def __repr__(self):
        prev = self.prev and self.prev.id
        next_ = self.next and self.next.id
        return f'LLNode(id={self.id}, val={self.val}, {prev=}, {next_=})'
