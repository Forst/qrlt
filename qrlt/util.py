import pathlib
from typing import Sequence


def slice_by(s: Sequence, chunk_size: int):
    for start in range(0, len(s), chunk_size):
        yield s[start:start+chunk_size]
