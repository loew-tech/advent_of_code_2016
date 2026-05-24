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