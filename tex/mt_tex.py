from __future__ import annotations

import struct
from io import BufferedReader
from typing import List, Tuple

from PIL import Image

from .bin_util import bit_cut, bit_merge
from .img_util import la04_encode, la04_loader
from .swizzle import ctr_swizzle


class MTTex(object):
    class _Header(object):
        def __init__(self,
                     magic: bytes = b'',
                     version: int = 0,
                     unused1: int = 0,
                     unknown1: int = 0,
                     alpha_flags: int = 0,
                     map_cnt: int = 0,
                     width: int = 0,
                     height: int = 0,
                     unknown2: int = 0,
                     format: int = 0,
                     unknown3: int = 0) -> None:
            self.magic = magic
            self.version = version
            self.alpha_flags = alpha_flags
            self.map_cnt = map_cnt
            self.width, self.height = width, height
            self.format = format
            self.unknown1, self.unknown2, self.unknown3, self.unused1 = \
                unknown1, unknown2, unknown3, unused1

        @staticmethod
        def from_bytes(data: bytes) -> MTTex._Header:
            blocks = struct.unpack('<4s3I', data)
            return MTTex._Header(
                blocks[0],
                *bit_cut(blocks[1], 12, 12, 4, 4),
                *bit_cut(blocks[2], 6, 13, 13),
                *bit_cut(blocks[3], 8, 8, 16)
            )

        def to_bytes(self) -> bytes:
            block1 = bit_merge((12, 12, 4, 4),
                               self.version, self.unused1,
                               self.unknown1, self.alpha_flags)
            block2 = bit_merge((6, 13, 13),
                               self.map_cnt, self.width, self.height)
            block3 = bit_merge((8, 8, 16),
                               self.unknown2, self.format, self.unknown3)
            return struct.pack('<4s3I',
                               self.magic, block1, block2, block3)

    def __init__(self) -> None:
        self.header = MTTex._Header()
        self.bmp_data = list[Tuple[int, int, int, int]]()

    @staticmethod
    def load(f: BufferedReader) -> MTTex:
        tex = MTTex()
        tex.header = MTTex._Header.from_bytes(f.read(16))
        assert tex.header.magic == b'TEX\x00'
        assert tex.header.format == 14     # LA(0, 4)
        assert tex.header.version == 0xa6  # 3DSv3

        mip_maps = [
            struct.unpack_from('<I', f.read(4))[0]
            for _ in range(tex.header.map_cnt)
        ]
        assert len(mip_maps) == 1

        data_blob = f.read()
        px_swizzled = la04_loader(data_blob)

        assert len(px_swizzled) == tex.header.width * tex.header.height
        tex.bmp_data = [(0, 0, 0, 0) for _ in range(len(px_swizzled))]

        swizzle = ctr_swizzle(tex.header.width, tex.header.height)

        for i, px in enumerate(px_swizzled):
            tex.bmp_data[swizzle[i]] = px

        return tex

    @staticmethod
    def new(size: Tuple[int, int], bmp: List[Tuple[int, int, int]]) -> MTTex:
        tex = MTTex()
        tex.header = MTTex._Header()

        tex.header.magic = b'TEX\x00'
        tex.header.version = 0xa6
        tex.header.alpha_flags = 2
        tex.header.map_cnt = 1
        tex.header.width, tex.header.height = size
        tex.header.format = 14
        tex.header.unknown1, tex.header.unknown2, tex.header.unknown3, \
            tex.header.unused1 = 0, 1, 1, 0

        tex.bmp_data = list(bmp)
        return tex

    def export_png(self, png_name: str) -> None:
        image = Image.new(mode='RGBA',
                          size=(self.header.width, self.header.height))
        image.putdata(self.bmp_data)
        image.save(png_name)

    def export_tex(self, tex_name: str) -> None:
        swizzled_data = [(0, 0, 0, 0) for _ in range(len(self.bmp_data))]
        swizzle = ctr_swizzle(self.header.width, self.header.height)
        for i, px in enumerate(self.bmp_data):
            swizzled_data[swizzle.inverse[i]] = px

        with open(tex_name, 'wb') as f:
            f.write(self.header.to_bytes())
            f.write(struct.pack('<I', 0))
            f.write(la04_encode(swizzled_data))
