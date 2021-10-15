from typing import List, Tuple


def bit_cut(data: int, *bits: int) -> Tuple[int, ...]:
    assert sum(bits) <= 32
    parts: List[int] = list()

    for bit in bits:
        parts.append(data & ((1 << bit) - 1))
        data >>= bit

    return tuple(parts)


def bit_merge(bits: Tuple[int, ...], *parts: int) -> int:
    assert len(bits) == len(parts)
    assert sum(bits) <= 32
    data = 0

    bit_offset = 0
    for bit, part in zip(bits, parts):
        assert part >> bit == 0
        data += part << bit_offset
        bit_offset += bit

    return data
