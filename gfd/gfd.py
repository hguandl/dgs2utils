from __future__ import annotations

import os
import struct
from io import BufferedReader

from PIL import Image

from .glyph_entry import GlyphEntry


class GFD(object):
    class _Header(object):
        def __init__(self,
                     magic: bytes,       # b'GMD\x0'
                     version: bytes,     # 4 bytes
                     unknown1: bytes,    # 12 bytes
                     size_px: int,
                     bitmap_count: int,
                     entry_count: int,
                     unknown2: bytes,    # 28 bytes
                     name_length: int,
                     ) -> None:
            self.magic = magic
            self.version = version
            self.unknown1 = unknown1
            self.size_px = size_px
            self.bitmap_count = bitmap_count
            self.entry_count = entry_count
            self.unknown2 = unknown2
            self.name_length = name_length

        @staticmethod
        def from_bytes(data: bytes) -> GFD._Header:
            assert len(data) == 64
            return GFD._Header(*struct.unpack_from('<4s4s12s3i28si', data))

        def dump(self, name: str) -> bytes:
            assert self.name_length == len(name)
            return struct.pack(
                f"<4s4s12s3i28si{self.name_length}ss",
                self.magic,
                self.version,
                self.unknown1,
                self.size_px,
                self.bitmap_count,
                self.entry_count,
                self.unknown2,
                self.name_length,
                name.encode('UTF-8'),
                b'\x00'
            )

    def __init__(self) -> None:
        self.name = None
        self.header = None
        self.glyphs = list[GlyphEntry]()

    @staticmethod
    def load(f: BufferedReader) -> GFD:
        gfd = GFD()
        gfd.header = GFD._Header.from_bytes(f.read(0x40))
        gfd.name = f.read(gfd.header.name_length + 1)[:-1].decode('UTF-8')
        while True:
            buf = f.read(20)
            if not buf:
                break
            glyph = GlyphEntry.load(buf)
            gfd.glyphs.append(glyph)
        return gfd

    def dump(self, dump_dir: str) -> None:
        os.makedirs(dump_dir, exist_ok=True)

        cnt = 0
        for glyph in self.glyphs:
            tex_file = f"font00_jpn_0{glyph.tex}_AM_NOMIP.tex.00.png"
            tex = Image.open(tex_file)

            box = (glyph.posx,
                   glyph.posy,
                   glyph.posx + glyph.width,
                   glyph.posy + glyph.height)
            font = tex.crop(box)

            bg = Image.new('RGBA', (glyph.width, glyph.height), (0, 0, 0, 255))
            bg.paste(font, (0, 0), font)

            bg.save(os.path.join(dump_dir, f"{cnt}.png"))
            cnt += 1

    def repack(self, pack_file: str) -> None:
        with open(pack_file, 'wb') as f:
            f.write(self.header.dump(self.name))
            for g in self.glyphs:
                f.write(g.dump())

    def dump_header(self) -> bytes:
        return self.header.dump(self.name)
