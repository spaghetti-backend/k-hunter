from typing import NamedTuple


class Keystroke(NamedTuple):
    key: str
    is_matched: bool
    elapsed_time_ms: int
