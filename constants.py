from operator import add, mul, sub, truediv, floordiv
from string import ascii_lowercase

ADVENT_URI = 'https://adventofcode.com/'

INPUTS_PATH = 'inputs/'

TESTS_PATH = 'tests/'


DIRECTIONS = tuple((i, j) for i in range(-1, 2)
                   for j in range(-1, 2) if not i == j == 0)


CARDINAL_DIRECTIONS = tuple((i, j) for i, j in DIRECTIONS
                            if not abs(i) == abs(j))

NUMS_TO_ALPHAS = {i: v for i, v in enumerate(ascii_lowercase)}
ALPHAS_TO_NUMS = {v: i for i, v in enumerate(ascii_lowercase)}

OPS_DICT = {'+': add, '*': mul, '-': sub, '/': truediv, '//': floordiv}

REGEX_WORDS = r'\b[a-zA-Z]+\b'
REGEX_DIGITS = r'-?\d+'
