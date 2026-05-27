import math
from collections import defaultdict, Counter, namedtuple
from functools import reduce, cache
from hashlib import md5
from itertools import permutations
from json import loads
import heapq
import inspect
import re
import sys
from typing import List, Dict, Set, Tuple, Any

from classes import Bot
from constants import DIRECTIONS, CARDINAL_DIRECTIONS, REGEX_WORDS, REGEX_DIGITS, NUMS_TO_ALPHAS, ALPHAS_TO_NUMS
from dbg_utils import print_grid
from helpers import day_8_build_grid
from utils import read_input, get_inbounds



def day_1(part_1=True) -> int:
    data = read_input(day=1, delim=', ', parse=lambda x_: (x_[0], int(x_[1:])))
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
    Address = namedtuple('Address', ['sequences', 'hypernets'])
    def build_addresses(data: List[str]) -> List[Address]:
        addresses_ = []
        for address in data:
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
            addresses_.append(Address(sequences, hypernets))
        return addresses_
    addresses = build_addresses(read_input(day=7))

    def supports_tls(address: Address) -> bool:
        def has_bridge(str_: List[str]) -> bool:
            for i in range(len(str_)-3):
                if not str_[i] == str_[i+1] and str_[i:i+2] == str_[i+2:i+4][::-1]:
                    return True
            return False

        return any(has_bridge(seq) for seq in address.sequences) and \
            not any(has_bridge(hypernet) for hypernet in address.hypernets)

    def supports_ssl(address: Address) -> bool:
        for seq in address.sequences:
            for i in range(len(seq)-2):
                a, b, c = seq[i:i+3]
                if not a == b and a == c:
                    if any(f'{b}{a}{b}' in hypernet for hypernet in address.hypernets):
                        return True
        return False

    check = supports_tls if part_1 else supports_ssl
    return sum(check(address) for address in addresses)


def day_8(part_1=True) -> int | None:
    grid = day_8_build_grid(read_input(day=8))
    if part_1:
        return sum(sum(b for b in row) for row in grid)
    print_grid([['#' if b else ' ' for b in row] for row in grid])
    return None


def day_9(part_1=True) -> int:
    data = read_input(day=9, delim=None)
    def decompress_recursive(start=0, stop=float('inf'), repititions=1, depth = 0) -> Tuple[int, int]:
        size, count, end = 0, 0, start
        while end < len(data) and end < stop:
            if not data[end] == '(':
                size += 1
                end += 1
                count += 1
                continue
            term = data.index(')', end)
            chars, repeats = map(int, data[end+1:term].split('x'))
            if part_1:
                end = term + 1 + chars
                size += chars * repeats
                continue
            size_i, new_end = decompress_recursive(start=term+1, stop=term + 1 + chars, repititions=repeats, depth=depth+1)
            size += size_i
            end = new_end
        return size * repititions, end
    return decompress_recursive()[0]


def day_10(part_1=True) -> int:
    graph: Dict[int | str, Bot]  = {}
    bots_with_values, targets = set(), {17 ,61}
    to_search: Set[int] = set()
    def parse(bot_) -> None:
        instruction, *digs = bot_.split()
        if instruction == 'value':
            val, b = map(int, re.findall(REGEX_DIGITS, ''.join(digs)))
            if b in bots_with_values:
                to_search.add(b)
            bots_with_values.add(b)
            if b in graph:
                graph[b].add_value(val)
                return
            graph[b] = Bot(value=val)
            return
        b, l, h = map(int, re.findall(REGEX_DIGITS, ''.join(digs)))
        l = f'output {l}' if f'output {l}' in bot_ else l
        h = f'output {h}' if f'output {h}' in bot_ else h
        if b in graph:
            graph[b].low_nghbr, graph[b].high_nghbr = l, h
            return
        graph[b] = Bot(low_bot=l, high_bot=h)

    read_input(day=10, parse=parse)
    outputs = {}
    while to_search:
        b_ = to_search.pop()
        bot = graph[b_]
        if part_1 and bot.low == 17 and bot.high == 61:
            return b_
        if isinstance((low:=bot.low_nghbr), str):
            int_ = int(low.split()[-1])
            outputs[int_] = bot.get_low()
        elif low is not None :
            graph[low].add_value(bot.get_low())
            if graph[low].can_proceed:
                to_search.add(low)
        if isinstance((high:=bot.high_nghbr), str):
            int_ = int(high.split()[-1])
            outputs[int_] = bot.get_high()
        elif high is not None:
            graph[high].add_value(bot.get_high())
            if graph[high].can_proceed:
                to_search.add(high)
    return outputs[0] * outputs[1] * outputs[2]


def day_11(part_1=True) -> int:
    data = read_input(day=11)

    return NotImplemented


def day_12(part_1=True) -> int:
    Instruction = namedtuple('Instruction', ['action', 'args'])
    instructions: List[Instruction] = read_input(
        day=12,
        parse=lambda x: Instruction(
            action=(s:=x.split())[0],
            args=[int(w) if w.lstrip('-').isnumeric() else w for w in s[1:]]
        )
    )

    registers = {'a': 0, 'b': 0, 'c': 0 if part_1 else 1, 'd': 0}
    def modify(register: str, new_val: int) -> None:
        registers[register] = new_val

    def value(x):
        return registers[x] if x in registers else x

    actions = {
        'inc': lambda reg: modify(reg, value(reg) + 1),
        'dec': lambda reg: modify(reg, value(reg)-1),
        'cpy': lambda v, reg: modify(reg, value(v))
    }
    indx = 0
    while indx < len(instructions):
        instruction = instructions[indx]
        if instruction.action == 'jnz':
            should_jump = value(instruction.args[0])
            val = value(instruction.args[1])
            indx += val if should_jump else 1
            continue
        actions[instruction.action](*instruction.args)
        indx += 1
    return registers['a']


if __name__ == '__main__':
    args = (f'day_{i}' for i in (sys.argv[1:] if
                                 sys.argv[1:] else range(1, 26)) if
            type(i) == int or str(i).isnumeric())
    members = inspect.getmembers(inspect.getmodule(inspect.currentframe()))
    funcs = {name: member for name, member in members
             if inspect.isfunction(member)}
    for day in args:
        if day not in funcs:
            print(f'{day}() = NotImplemented')
            continue
        print(f'{day}() = {funcs[day]()}')
        print(f'{day}(part=2) = {funcs[day](part_1=False)}')