import re
from typing import List, Tuple, Union

from constants import REGEX_DIGITS
from dbg_utils import print_grid


def day_8_build_grid(instructions: List[str]) -> List[List[bool]]:
    H, W = 6, 50
    grid = [[False]*W for _ in range(H)]

    def rect(x_limit, y_limit: int) -> None:
        for y in range(y_limit):
            for x in range(x_limit):
                grid[y][x] = True

    def column(x, b: int) -> None:
        while (b := b - 1) > -1:
            next_ = grid[-1][x]
            for y in range(H):
                grid[y][x], next_ = next_, grid[y][x]

    def row(y, b: int) -> None:
        while (b := b - 1) > -1:
            next_ = grid[y][-1]
            for x in range(W):
                grid[y][x], next_ = next_, grid[y][x]

    ops = {
        'rect': rect,
        'column': column,
        'row': row,
    }

    for instruction in instructions:
        action, *args = instruction.split()
        action = args[0] if action == 'rotate' else action
        ops[action](*map(int, re.findall(REGEX_DIGITS, ''.join(args))))
    return grid
