import math
import re
from collections import namedtuple
from itertools import count
from typing import Generator, List, Tuple, Union

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


Instruction = namedtuple('Instruction', ['action', 'args'])


class InstructionExecuter:

    def __init__(self, init_state: str):
        self.state: List[str] = list(init_state)

    def _swap_position(self, x: int, y: int) -> None:
        """Swaps elements at indices x_ and y_."""
        self.state[x], self.state[y] = self.state[y], self.state[x]

    def _swap_letter(self, a, b: str) -> None:
        "Swaps first occuurrences of letters a and b."
        index_a, index_b = self.state.index(a), self.state.index(b)
        self._swap_position(index_a, index_b)

    def _reverse(self, x, y: int) -> None:
        """Reverses the slice of state from index x_ to y_ (inclusive)."""
        self.state = self.state[:x] + self.state[x:y + 1][::-1] + self.state[y + 1:]

    def _rotate_direction(self, move_right: bool, num_moves: int) -> None:
        """Rotates the state right or left by num_moves."""

        if not (shift := num_moves % self.n):
            return

        if move_right:
            self.state = self.state[-shift:] + self.state[:-shift]
        else:
            self.state = self.state[shift:] + self.state[:shift]

    def _rotate_letter(self, letter: str) -> None:
        """
        Rotates the string right based on the index of the given letter.
        Steps: 1 + index + (1 if index >= 4 else 0)
        """
        index = self.state.index(letter)
        num_moves = 1 + index
        if index >= 4:
            num_moves += 1
        self._rotate_direction(move_right=True, num_moves=num_moves)

    def _rotate_letter_inverse(self, letter: str) -> None:
        """
        Undoes a rotation based on a letter position using
        a predefined lookup mapping for an 8-character array.
        """
        undo_map = {0: 1, 1: 1, 2: 6, 3: 2, 4: 7, 5: 3, 6: 8, 7: 4}
        index = self.state.index(letter)
        num_moves = undo_map[index]
        self._rotate_direction(move_right=False, num_moves=num_moves)

    def _move(self, x, y: int) -> None:
        """
        Deletes char c at index x and inserts it at index y.
        """
        char_ = self.state.pop(x)
        self.state.insert(y, char_)

    def execute(self, instructions: List[Instruction], part_1: bool) -> str:
        """
        Executes instructions, performing inverse if part_1 is true
        """

        ops = {
            'swap_position': self._swap_position,
            'swap_letter': self._swap_letter,
            'rotate_left': lambda x: self._rotate_direction(not part_1, x),
            'rotate_right': lambda x: self._rotate_direction(part_1, x),
            'move_position': lambda x, y: self._move(x, y) if part_1 else self._move(y, x),
            'rotate': self._rotate_letter if part_1 else self._rotate_letter_inverse,
            'reverse': self._reverse
        }
        for action, args in instructions:
            ops[action](*args)
        return ''.join(self.state)

    @property
    def n(self):
        return len(self.state)