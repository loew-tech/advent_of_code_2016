from operator import add, mul, sub, truediv, floordiv


ADVENT_URI = 'https://adventofcode.com/'

INPUTS_PATH = 'inputs/'

TESTS_PATH = 'tests/'


DIRECTIONS = tuple((i, j) for i in range(-1, 2)
                   for j in range(-1, 2) if not i == j == 0)


CARDINAL_DIRECTIONS = tuple((i, j) for i, j in DIRECTIONS
                            if not abs(i) == abs(j))

OPS_DICT = {'+': add, '*': mul, '-': sub, '/': truediv, '//': floordiv}

REGEX_WORDS = r'\b[a-zA-Z]+\b'
REGEX_DIGITS = r'-?\d+'
