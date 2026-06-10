import math
from bisect import bisect_right, bisect_left
from collections import defaultdict, Counter, namedtuple, deque
from functools import cache
from hashlib import md5
import inspect
import re
import sys
from itertools import permutations, combinations
from typing import List, Dict, Set, Tuple, Any
from unittest.mock import mock_open

from classes import Bot, Disc, LLNode, Instruction, InstructionExecuter, MemoryNode, AssembunnyExecutor, \
    AssembunnyTGLExecutor
from constants import *
from dbg_utils import print_grid
from helpers import day_8_build_grid, day_22_bfs
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
    def parse(address: str) -> Address:
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
        return Address(sequences, hypernets)

    addresses: List[Address] = read_input(day=7, parse=parse)

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
    return sum(check(addr) for addr in addresses)


def day_8(part_1=True) -> int | None:
    grid = day_8_build_grid(read_input(day=8))
    if part_1:
        return sum(sum(b for b in row) for row in grid)
    print_grid([['#' if b else ' ' for b in row] for row in grid])
    return None


def day_9(part_1=True) -> int:
    data = read_input(day=9, delim=None)
    def decompress_recursive(start=0, stop=float('inf'),
                             repetitions=1, depth = 0) -> Tuple[int, int]:
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
            size_i, end = decompress_recursive(start=term+1, stop=term + 1 + chars, repetitions=repeats, depth=depth + 1)
            size += size_i
        return size * repetitions, end
    return decompress_recursive()[0]


def day_10(part_1=True) -> int:
    graph: Dict[int | str, Bot]  = {}
    to_search: Set[int] = set()
    def parse(bot_) -> None:
        instruction, *digs = bot_.split()
        if instruction == 'value':
            val, b_ = map(int, re.findall(REGEX_DIGITS, ''.join(digs)))
            if b_ in graph:
                graph[b_].add_value(val)
                if graph[b_].can_proceed:
                    to_search.add(b_)
                return
            graph[b_] = Bot(value=val)
            return
        b_, l, h = map(int, re.findall(REGEX_DIGITS, ''.join(digs)))
        l = f'output {l}' if f'output {l}' in bot_ else l
        h = f'output {h}' if f'output {h}' in bot_ else h
        if b_ in graph:
            graph[b_].low_nghbr, graph[b_].high_nghbr = l, h
            return
        graph[b_] = Bot(low_bot=l, high_bot=h)

    read_input(day=10, parse=parse)
    outputs = {}
    while to_search:
        b = to_search.pop()
        bot = graph[b]
        if part_1 and bot.low == 17 and bot.high == 61:
            return b
        if isinstance((low:=bot.low_nghbr), str):
            int_ = int(low.split()[-1])
            outputs[int_] = bot.get_low()
        elif low is not None:
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
    def parse(lines: str) -> Dict[str, List[int, int]]:
        pairs = defaultdict(lambda: [None, None])
        for i_, line in enumerate(lines.split('\n')):
            l_ = line.split()
            for j_ in range(len(l_) - 1):
                mol = l_[j_].split('-')[0]
                if 'generator' in l_[j_ + 1]:
                    pairs[mol][0] = i_
                elif 'microchip' in l_[j_ + 1]:
                    pairs[mol][1] = i_
        return pairs

    def canonical(state_):
        elevator, pairs = state_
        return (
            elevator,
            tuple(sorted(pairs))
        )

    def is_floor_safe(floor, pairs) -> bool:
        gens, chips = set(), set()
        for i, (g, m) in enumerate(pairs):
            if g == floor:
                gens.add(i)
            if m == floor:
                chips.add(i)
        if not gens:
            return True
        for chip in chips:
            if chip not in gens:
                return False
        return True

    def state_safe(pairs):
        for floor in range(4):
            if not is_floor_safe(floor, pairs):
                return False
        return True

    def neighbors(state_):
        elevator, pairs = state_
        items = []
        for i, (g, m) in enumerate(pairs):
            if g == elevator:
                items.append(('G', i))
            if m == elevator:
                items.append(('M', i))
        for direction in (-1, 1):
            new_floor = elevator + direction
            if not (0 <= new_floor < 4):
                continue
            for r in (1, 2):
                for load in combinations(items, r):
                    new_pairs = [list(p) for p in pairs]
                    for typ, idx in load:
                        if typ == 'G':
                            new_pairs[idx][0] = new_floor
                        else:
                            new_pairs[idx][1] = new_floor
                    new_pairs = tuple(
                        tuple(p)
                        for p in new_pairs
                    )
                    if state_safe(new_pairs):
                        yield (
                            new_floor,
                            new_pairs
                        )

    def goal(state_):
        _, pairs = state_
        return all(
            g == 3 and m == 3
            for g, m in pairs
        )

    f: Dict[str, List[int, int]] = read_input(day=11, delim=None, parse=parse)
    floors = [tuple(v) for v in f.values()]
    if not part_1:
        floors.extend([(0, 0), (0, 0)])
    init_state = canonical((0, floors))
    q, visited = deque([(init_state, 0)]), set()
    while q:
        state, steps = q.popleft()
        if goal(state):
            return steps

        for nxt in neighbors(state):
            if (key := canonical(nxt)) in visited:
                continue
            visited.add(key)
            q.append((nxt, steps + 1))
    return -1

def day_12(part_1=True) -> int:
    instructions: List[Instruction] = read_input(
        day=12,
        parse=lambda x: Instruction(
            action=(s:=x.split())[0],
            args=[int(w) if w.lstrip('-').isnumeric() else w for w in s[1:]]
        )
    )

    executor = AssembunnyExecutor(c=0 if part_1 else 1)
    executor.execute(instructions)
    return executor.a


def day_13(part_1=True) -> int:
    fav_number: int = read_input(day=13, delim=None, parse=int)
    def inbounds(y_, x_: int) -> bool:
        return 0 <= y_ and 0 <= x_

    @cache
    def is_valid(y_, x_: int) -> bool:
        if not inbounds(y_, x_):
            return False
        num = x_ * x_ + 3 * x_ + 2 * x_ * y_ + y_ + y_ * y_ + fav_number
        return num.bit_count() % 2 == 0

    target_y, target_x = 39, 31
    count, visited, to_search = 0, set(), {(1, 1)}
    while to_search:
        if not part_1 and count > 50:
            return len(visited)
        next_search = set()
        for y, x in to_search:
            visited.add((y, x))
            for yi, xi in CARDINAL_DIRECTIONS:
                if (y+yi, x+xi) not in visited and is_valid(y+yi, x+xi):
                    if y+yi == target_y and x+xi == target_x:
                        return count
                    next_search.add((y+yi, x+xi))
        count += 1
        to_search = next_search
    return -1


def day_14(part_1=True) -> int:
    salt, indx = read_input(day=14, delim=None), 0
    pattern, keys = r"(.)\1{2}", set()
    hash_q = deque([])

    @cache
    def get_hash(indx_):
        h = md5(f'{salt}{indx_}'.encode()).hexdigest()
        for _ in range(2016 * (not part_1)):
            h = md5(h.encode()).hexdigest()
        return h

    for i in range(1001):
        hash_q.append(get_hash(i))

    while len(keys) < 64:
        hash_ = hash_q.popleft()
        if match_ := re.search(pattern, hash_):
            quintuple = match_.group(1) * 5
            if any(quintuple in future_hash for future_hash in hash_q):
                keys.add(indx)
        indx += 1
        hash_q.append(get_hash(1000 + indx))
    return sorted(keys)[63]


def day_15(part_1=True) -> int:
    discs: List[Disc] = read_input(day=15, parse=Disc.from_str)
    if not part_1:
        discs.append(Disc(max(d.id for d in discs) + 1, 11, 0))

    time, lcm = 0, 1
    for disc in discs:
        while not disc.is_solution(time):
            time += lcm
        lcm = math.lcm(lcm, disc.num_pos)
    return time


def day_16(part_1=True) -> str:
    size = 272 if part_1 else 35651584
    data: str | List[bool]= read_input(day=16, delim=None)
    while (n:=len(data)) < size:
        b = ['1' if data[i] == '0' else '0' for i in range(n-1, -1, -1)]
        data = f'{data}0{"".join(b)}'

    def get_checksum() -> List[bool]:
        ret = []
        n_ = min(len(data), size)
        for i_ in range(0, n_-1, 2):
            ret.append(data[i_] == data[i_+1])
        return  ret

    while not len(data:=get_checksum()) % 2:
        pass
    return ''.join(['1' if b else '0' for b in data])


def day_17(part_1=True) -> str | int:
    def inbounds(y_, x_: int) -> bool:
        return 0 <= y_ < 4 and 0 <= x_ < 4

    hash_ = read_input(day=17, delim=None)
    directions = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
    open_ = 'bcdef'
    to_search, stack, max_ = deque([(0, 0, '')]), [(0, 0, '')], 0
    while (part_1 and deque) or (not part_1 and stack):
        search = to_search if part_1 else stack
        pop_f = search.popleft if part_1 else search.pop
        y, x, path = pop_f()
        hashed = md5(f'{hash_}{path}'.encode()).hexdigest()[:4]
        for direction, door in zip('UDLR', hashed):
            if door not in open_:
                continue
            yi, xi = directions[direction]
            yn, xn = y + yi, x + xi
            if yn == 3 and xn == 3:
                if part_1:
                    return f'{path}{direction}'
                max_ = max(max_, len(path) + 1)
                continue
            if inbounds(yn, xn):
                search.append((yn, xn, f'{path}{direction}'))
    return max_


def day_18(part_1=True) -> int:
    row = [c == '^' for c in read_input(day=18, delim=None)]
    N, num_rows, safe = len(row), 40 if part_1 else 400_000, row.count(False)
    for _ in range(1, num_rows):
        old = [False] + row + [False]
        for i in range(1, N+1):
            row[i-1] = old[i-1] ^ old[i+1]
        safe += row.count(False)
    return safe


def day_19(part_1=True) -> int:
    num_elves: int = read_input(day=19, delim=None, parse=int)
    # num_elves = 5
    ll_head = current = LLNode(id_=1, val=1)
    for i in range(1, num_elves + 1):
        if i == num_elves:
            current.next = ll_head
            ll_head.prev = current
            break
        current.next = LLNode(id_=i + 1, val=1, prev=current)
        current = current.next
        if i + 1 == (num_elves // 2) + 1:
            opposite = current

    current = ll_head
    while current.next is not current:
        if part_1:
            node = current.next
            current.val += node.val
            node.delete()
            current = current.next
        else:
            node = opposite
            current.val += node.val
            if num_elves % 2 == 1:
                opposite = opposite.next.next
            else:
                opposite = opposite.next
            num_elves -= 1
            node.delete()
            current = current.next
    return current.id

def day_20(part_1=True) -> int:
    ip_addresses: List[Tuple[int, int]] = read_input(day=20, parse=lambda x: tuple(map(int, x.split('-'))))
    ip_addresses.sort()
    current_ip, valid_count = 0, 0
    for start, stop in ip_addresses:
        if current_ip < start:
            valid_count += 1
            if part_1:
                return current_ip
        current_ip = max(current_ip, stop+1)
    return valid_count


def day_21(part_1=True) -> str:
    def parse(s: str) -> Instruction:
        act, *other = s.split()
        args = list(map(int, re.findall(REGEX_DIGITS, ''.join(other))))
        if act == 'reverse':
            return Instruction(action=act, args=args)
        if act == 'rotate' and other[0] not in {'left', 'right'}:
            args_ = [other[-1]]
            return Instruction(action=act, args=args_)
        if act == 'swap' and other[0] == 'letter':
            args_ = [other[1], other[-1]]
            return Instruction(action='swap_letter', args=args_)
        return Instruction(action=f'{act}_{other[0]}', args=args)

    instructions: List[Instruction] = read_input(day=21, parse=parse)
    active_instructions = instructions if part_1 else reversed(instructions)
    init_state = 'abcdefgh' if part_1 else 'fbgdceah'
    executor = InstructionExecuter(init_state)
    return executor.execute(active_instructions, part_1)


def day_22(part_1=True) -> int:

    def parse(nodes_str: str) -> List[MemoryNode]:
        nodes = []
        for n in nodes_str.split('\n')[2:]:
            id_, vals = n.split()[0], list(map(int, re.findall(REGEX_DIGITS, n)))
            nodes.append(MemoryNode(id_, *vals))
        return nodes

    data: List[MemoryNode] = read_input(day=22, delim=None, parse=parse)
    if not part_1:
        moves = day_22_bfs(data) + 1
        moves += 5 * (max(n.x for n in data) - 1)
        return moves

    used_nodes = [n.used for n in data if n.used]
    available_vals = sorted([n.avail for n in data])
    num_avail = len(available_vals)
    return sum(num_avail - bisect_left(available_vals, n) for n in used_nodes)


def day_23(part_1=True) -> int:
    instructions: List[Instruction] = read_input(
        day=23,
        parse=lambda x: Instruction(
            action=(s:=x.split())[0],
            args=[int(w) if w.lstrip('-').isnumeric() else w for w in s[1:]]
        )
    )

    executor = AssembunnyTGLExecutor(a=7 if part_1 else 12)
    executor.execute(instructions)
    return executor.a


def day_24(part_1=True) -> int:
    grid: List[str] = read_input(day=24)
    locs = {val: (y, x) for y, row in enumerate(grid) for x, val in enumerate(row) if val.isnumeric()}
    num_vals = len(locs)

    def bfs(start_str: str) -> Dict[str, int]:
        to_search, visited, count = {locs[start_str]}, set(), 0
        distances = {k: dct[start_str] for k, dct in lookup.items() if start_str in dct}
        distances[start_str] = 0
        while to_search and (count:=count+1) and len(distances) < num_vals:
            next_search = set()
            for y_, x_ in to_search:
                visited.add((y_, x_))
                for yi, xi in CARDINAL_DIRECTIONS:
                    if (y_+yi, x_+xi) not in visited:
                        val_: str = grid[y_+yi][x_+xi]
                        if is_loc:=val_ in locs:
                            distances[val_] = count
                        if val_ == '.' or is_loc:
                            next_search.add((y_+yi, x_+xi))
            to_search = next_search
        return distances

    lookup = {}
    for location in locs:
        lookup[location] = bfs(location)

    min_ = float('inf')
    for perm in permutations(''.join(k for k in locs.keys() if not k == '0')):
        current, distance = '0', 0
        for location in perm:
            distance += lookup[current][location]
            current = location
        min_ = min(min_, distance + lookup[current]['0'] * (not part_1))
    return min_


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