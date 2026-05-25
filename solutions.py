import math
from collections import defaultdict, Counter
from functools import reduce, cache
from hashlib import md5
from itertools import permutations
from json import loads
import heapq
import inspect
import re
import sys
from typing import List, Dict, Set, Tuple

from constants import DIRECTIONS, CARDINAL_DIRECTIONS, REGEX_WORDS, REGEX_DIGITS, NUMS_TO_ALPHAS, ALPHAS_TO_NUMS
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


def day_4(part_1=True) -> int:
    def get_valid_rooms(rooms: List[str]) -> List[Tuple[List[str], int]]:
        valid_rooms = []
        for room in rooms:
            words = re.findall(REGEX_WORDS, room)
            name = Counter(''.join(words[:-1]))
            sector_id = abs(int(re.findall(REGEX_DIGITS, room)[0]))
            checksum = words[-1]
            expctd = ''.join(c for c, _ in sorted(name.items(), key=lambda x: (-x[1], x[0]))[:5])
            if checksum == expctd:
                valid_rooms.append((words[:-1], sector_id))
        return valid_rooms

    valids = get_valid_rooms(read_input(day=4))
    if part_1:
        return sum(sect_id for _, sect_id in valids)

    def room_name(rooms: List[str], sector_id: int) -> str:
        return ' '.join(''.join(NUMS_TO_ALPHAS[(ALPHAS_TO_NUMS[c] + sector_id) % 26]
                                for c in room) for room in rooms)

    north_pole_storage = 'northpole object storage'
    for rooms_, sect_id in valids:
        if room_name(rooms_, sect_id) == north_pole_storage:
            return sect_id
    return -1


def day_5(part_1=True) -> str:
    door_id, num_zeroes, len_password, count = read_input(day=5, delim=None), 5, 8, -1
    zeroes = '0' * num_zeroes
    password, password2 = [], {}
    while len(password) < len_password and len(password2) < len_password:
        count += 1
        key = md5(f'{door_id}{count}'.encode()).hexdigest()
        while not key.startswith(zeroes) and (count := count + 1):
            key = md5(f'{door_id}{count}'.encode()).hexdigest()
        if part_1:
            password.append(key[num_zeroes])
            continue
        indx = int(key[num_zeroes]) if key[num_zeroes].isnumeric() else -1
        if 0 <= indx < len_password and indx not in password2:
            password2[indx] = key[num_zeroes+1]
    return ''.join(password) if part_1 else ''.join(password2[i] for i in range(len_password))


def day_6(part_1=True) -> str:
    data = read_input(day=6)
    maxes = {i: (-1, '') for i in range(len(data[0]))}
    counts = defaultdict(lambda: defaultdict(int))

    for entry in data:
        for i, c in enumerate(entry):
            counts[i][c] += 1
            if counts[i][c] > maxes[i][0]:
                maxes[i] = (counts[i][c], c)

    if part_1:
        return ''.join(maxes[i][1] for i in range(len(maxes)))
    return ''.join(min(counts[key].items(), key=lambda x: x[1])[0] for key in counts)


def day_7(part_1=True) -> int:
    addresses = read_input(day=7)
    def supports_tls(address: str) -> bool:
        def has_bridge(str_: List[str]) -> bool:
            for i in range(len(str_)-3):
                if not str_[i] == str_[i+1] and str_[i:i+2] == str_[i+2:i+4][::-1]:
                    return True
            return False

        indx, is_hypernet, bridged = 0, False, False
        while indx < len(address):
            sequence = []
            while indx < len(address) and address[indx] not in '[]':
                sequence.append(address[indx])
                indx += 1
            bridge = has_bridge(sequence)
            if is_hypernet:
                if bridge:
                    return False
            else:
                bridged |= bridge
            is_hypernet = not is_hypernet
            indx += 1
        return bridged

    if part_1:
        return sum(supports_tls(addr) for addr in addresses)

    def supports_ssl(address: str) -> bool:
        sequences, hypernets = [], []
        indx, is_hypernet = 0, False
        while indx < len(address):
            sequence = []
            while indx < len(address) and address[indx] not in '[]':
                sequence.append(address[indx])
                indx += 1
            if is_hypernet:
                hypernets.append(''.join(sequence))
            else:
                sequences.append(''.join(sequence))
            is_hypernet = not is_hypernet
            indx += 1

        for sequence in sequences:
            for i in range(len(sequence)-2):
                a, b, c = sequence[i], sequence[i+1], sequence[i+2]
                if not a == b and a == c:
                    if any(f'{b}{a}{b}' in hypernet for hypernet in hypernets):
                        return True
        return False

    return sum(supports_ssl(addr) for addr in addresses)


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