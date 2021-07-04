from functools import reduce
from typing import ByteString

from .util import slice_by


ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'


def b45decode(s: str) -> bytes:
    output = bytearray()

    for chunk in slice_by(s, 3):
        if not 2 <= len(chunk) <= 3:
            raise ValueError(f'Chunk "{chunk}" of unexpected length')

        accumulator = reduce(
            lambda acc, val: acc + val[1] * (45 ** val[0]),
            enumerate(ALPHABET.index(c) for c in chunk),
            0
        )

        if not 0 <= accumulator <= 0xffff:
            raise ValueError(f'Chunk "{chunk}" got accumulator 0x{accumulator:x}')

        if len(chunk) == 3:
            output.append(accumulator >> 8)
        output.append(accumulator & 0xff)

    return bytes(output)


def b45encode(b: ByteString) -> str:
    output = ''

    for chunk in slice_by(b, 2):
        chunk_encoded = ''

        accumulator = reduce(
            lambda acc, val: acc + val[1] * (256 ** val[0]),
            enumerate(chunk[::-1]),
            0
        )

        while accumulator:
            accumulator, value = divmod(accumulator, 45)
            chunk_encoded += ALPHABET[value]

        chunk_encoded = chunk_encoded.ljust(len(chunk) + 1, '0')
        output += chunk_encoded

    return output


