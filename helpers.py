import re
from collections import deque
from typing import List, Tuple, Union

from classes import MemoryNode
from constants import REGEX_DIGITS, CARDINAL_DIRECTIONS
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


def day_22_bfs(nodes: List[MemoryNode]) -> int | None:
    max_x = max([n.x for n in nodes])
    start = next((n.y, n.x) for n in nodes if n.use == 0)
    wall_limit = min(n.size for n in nodes if n.use == 0)
    locations = {(n.y, n.x) for n in nodes if n.used < wall_limit}
    q, visited = deque([(start, 0)]), set()
    while q:
        (y, x), dist = q.popleft()
        if y == 0 and x == max_x - 1:
            return dist
        for yi, xi in CARDINAL_DIRECTIONS:
            yn, xn = y+yi, x+xi
            if (yn, xn) in visited or (yn, xn) not in locations:
                continue
            visited.add((yn, xn))
            q.append(((yn, xn), dist + 1))
    return None
