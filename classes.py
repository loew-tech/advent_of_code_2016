class Bot:
    def __init__(self, value: int | None = None, low_bot: int | str | None = None, high_bot: int | str | None = None):
        self._values = [value] if value is not None else []
        self.low_nghbr = low_bot
        self.high_nghbr = high_bot

    def add_value(self, val: int) -> None:
        self._values.append(val)

    def get_high(self) -> int:
        max_index = self._values.index(max(self._values))
        return self._values.pop(max_index)

    def get_low(self) -> int:
        min_index = self._values.index(min(self._values))
        return self._values.pop(min_index)

    @property
    def low(self):
        return None if not self._values else min(self._values)

    @property
    def high(self):
        return None if not self._values else max(self._values)

    @property
    def can_proceed(self):
        return len(self._values) == 2

    def __repr__(self):
        return f'Bot(values={self._values}, low_nghbr={self.low_nghbr}, hihg_nghbr={self.high_nghbr})'