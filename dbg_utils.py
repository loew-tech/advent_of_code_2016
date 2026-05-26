from typing import Iterable


def print_grid(grid: Iterable[Iterable], sep='', end='') -> None:
    for row in grid:
        print(sep.join(str(i) for i in row))
    print(end=end)
