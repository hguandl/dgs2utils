from typing import List, Tuple


def change_bit_depth(value: int, bd_from: int, bd_to: int) -> int:
    if bd_from < bd_to:
        from_max = (1 << bd_from) - 1
        to_max = (1 << bd_to) - 1

        div = 1
        while to_max % from_max != 0:
            div <<= 1
            to_max = ((to_max + 1) << 1) - 1

        return value * (to_max // from_max) // div
    else:
        from_max = 1 << bd_from
        to_max = 1 << bd_to

        limit = from_max // to_max

        return value // limit


def la04_loader(tex: bytes) -> List[Tuple[int, int, int]]:
    ret: List[Tuple[int, int, int]] = list()
    bit_depth = 4 + 0
    l_depth = 0
    a_depth = 4

    assert bit_depth == 4
    assert l_depth == 0

    a_bit_mask = (1 << a_depth) - 1
    ptr = 0
    nibble = 0
    while ptr < len(tex):
        if nibble == 0:
            value = tex[ptr] % 16
        else:
            value = tex[ptr] // 16
            ptr += 1

        nibble ^= 1

        ret.append((
            255, 255, 255,
            change_bit_depth((value & a_bit_mask), a_depth, 8)
        ))
    return ret


def la04_encode(bmp: Tuple[int, int, int, int]) -> bytes:
    ret: List[int] = list()
    nibble = 0
    for px in bmp:
        alpha = change_bit_depth(px[3], 8, 4)
        if nibble == 0:
            value = alpha
        else:
            value = value + alpha * 0x10
            ret.append(value)
        nibble ^= 1

    return bytes(ret)
