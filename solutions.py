import math
from collections import defaultdict
from functools import reduce, cache
from hashlib import md5
from itertools import permutations
from json import loads
import heapq
import inspect
import re
import sys
from typing import List, Dict, Set, Tuple

from constants import DIRECTIONS, CARDINAL_DIRECTIONS
from utils import read_input, get_inbounds



def day_1(part_1=True) -> int:
    data = read_input(day=1, delim=', ', parse=lambda x: (x[0], int(x[1:])))
    incs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    indx = 0
    y, x = 0, 0
    visited = {(0, 0)}
    for direction, magnitude in data:
        indx += 1 if direction == 'R' else -1
        if indx < 0:
            indx += len(incs)
        indx %= len(incs)
        for _ in range(magnitude):
            x += incs[indx][1]
            y += incs[indx][0]
            if (y, x) in visited and not part_1:
                return abs(y) + abs(x)
            visited.add((y, x))
    return abs(y) + abs(x)


def day_2(part_1=True) -> str:
    directions = dict(zip('DRUL', ((1, 0), (0, 1), (-1, 0), (0, -1))))
    grid = [['1','2', '3'], ['4', '5', '6'], ['7', '8', '9']]
    y, x = 1, 1
    if not part_1:
        grid = [
            [None, None, '1', None, None],
            [None, '2', '3', '4', None],
            ['5', '6', '7', '8', '9'],
            [None, 'A', 'B', 'C', None],
            [None, None, 'D', None, None],
        ]
        y, x = 2, 0
    inbounds = get_inbounds(grid)
    data = read_input(day=2)
    code = []
    for instruction in data:
        for direction in instruction:
            yi, xi = directions[direction]
            if not inbounds(y+yi, x+xi) or grid[y+yi][x+xi] is None:
                continue
            y += yi
            x += xi
        code.append(grid[y][x])
    return ''.join(code)


def day_3(part_1=True) -> int:
    def parse_1(x :str) -> List[str] | Tuple[int, int, int]:
        return (s:=x.split()) and (int(s[0]), int(s[1]), int(s[2]))

    def parse_2(data_: str) -> List[List[int]]:
        data_ = [(int((s:=d.split())[0]), int(s[1]), int(s[2])) for d in data_.split('\n')]
        triangles = []
        for i in range(0, len(data_)-2, 3):
            triangles.append((data_[i][0], data_[i+1][0], data_[i+2][0]))
            triangles.append((data_[i][1], data_[i + 1][1], data_[i + 2][1]))
            triangles.append((data_[i][2], data_[i + 1][2], data_[i + 2][2]))
        return triangles

    data = read_input(
        day=3,
        delim='\n' if part_1 else None,
        parse=parse_1 if part_1 else parse_2,
    )

    def is_valid(a, b, c: int) -> bool:
        return a + b > c and b + c > a and c + a > b
    return sum(is_valid(d1, d2, d3) for d1, d2, d3 in data)



if __name__ == '__main__':
    args = (f'day_{i}' for i in (sys.argv[1:] if
                                 sys.argv[1:] else range(1, 26)) if
            type(i) == int or i.isnumeric())
    members = inspect.getmembers(inspect.getmodule(inspect.currentframe()))
    funcs = {name: member for name, member in members
             if inspect.isfunction(member)}
    for day in args:
        if day not in funcs:
            print(f'{day}() = NotImplemented')
            continue
        print(f'{day}() = {funcs[day]()}')
        print(f'{day}(part=2) = {funcs[day](part_1=False)}')