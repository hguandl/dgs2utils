from __future__ import annotations

import struct
from typing import Tuple


class GlyphEntry(object):
    def __init__(self,
                 char: str,
                 tex: int,
                 pos: Tuple[int, int],
                 size: Tuple[int, int],
                 pos_off: Tuple[int, int],
                 pos_add: Tuple[int, int],
                 offset: int) -> None:
        self.char = char
        self.tex = tex
        self.pos = pos
        self.size = size
        self.pos_off = pos_off
        self.pos_add = pos_add
        self.offset = offset

    @staticmethod
    def __split_1_5_bytes(x: bytes) -> Tuple[int, int]:
        a = x[2] * 0x10 + x[1] // 0x10
        b = (x[1] % 0x10) * 0x100 + x[0]
        return b, a

    @staticmethod
    def __union_3_bytes(b: int, a: int) -> bytes:
        x0 = b % 0x100
        x2 = a // 0x10
        x1 = (a % 0x10) * 0x10 + b // 0x100
        return bytes([x0, x1, x2])

    @staticmethod
    def load(blob: bytes) -> GlyphEntry:
        parts = struct.unpack_from('<H18B', blob)
        char = chr(parts[0])
        tex = parts[3]
        pos = GlyphEntry.__split_1_5_bytes(parts[4:7])
        size = GlyphEntry.__split_1_5_bytes(parts[7:10])
        pos_off = GlyphEntry.__split_1_5_bytes(parts[11:14])
        offset = parts[14]
        pos_add = parts[15], parts[16]
        return GlyphEntry(char, tex, pos, size, pos_off, pos_add, offset)

    def __str__(self) -> str:
        return (
            f"\"{self.char}\" in {self.tex}:"
            f" {self.pos}"
            f" {self.size}"
            f" -{self.pos_off}"
            f" +{self.pos_add}"
            f" {self.offset}"
            f" \t{self.raw}"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def dump(self) -> bytes:
        blob = bytes()
        blob += struct.pack('<H', ord(self.char))
        blob += struct.pack('2B', 0, 0)
        blob += struct.pack('B', self.tex)
        blob += struct.pack('3B', *GlyphEntry.__union_3_bytes(*self.pos))
        blob += struct.pack('3B', *GlyphEntry.__union_3_bytes(*self.size))
        blob += struct.pack('B', 0)
        blob += struct.pack('3B', *GlyphEntry.__union_3_bytes(*self.pos_off))
        blob += struct.pack('B', self.offset)
        blob += struct.pack('2B', *self.pos_add)
        blob += struct.pack('2B', 0xff, 0xff)
        return blob
