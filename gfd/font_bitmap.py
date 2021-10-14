from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont

from .glyph_entry import GlyphEntry


class FontBitmap(object):
    global_offset = 20

    def __init__(self, ) -> None:
        self.__image = Image.new('RGBA', (512, 512), (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.__image)

        self.offset_x = 0
        self.offset_y = 0
        self.full = False

    def push(self, txt: str, idx: int,
             font: ImageFont.FreeTypeFont) -> GlyphEntry:
        self.draw.text(
            xy=(self.offset_x, self.offset_y),
            text=txt,
            font=font,
            fill='white'
        )

        txt_size = font.getsize(txt)
        entry = GlyphEntry(
            char=txt,
            tex=idx,
            pos=(self.offset_x, self.offset_y),
            size=txt_size,
            pos_off=(txt_size[0], 18),
            pos_add=(0, 0),
            offset=FontBitmap.global_offset
        )

        self.__forward_pos()

        return entry

    def __forward_pos(self) -> None:
        # Next column
        self.offset_x += FontBitmap.global_offset

        # Next row
        if self.offset_x + FontBitmap.global_offset >= 511:
            self.offset_y += FontBitmap.global_offset
            self.offset_x = 0

        # Next bitmap
        if self.offset_y + FontBitmap.global_offset >= 511:
            self.full = True

    def save(self, *args, **kwargs) -> None:
        return self.__image.save(*args, **kwargs)

    def getdata(self) -> List[Tuple[int, ...]]:
        return list(self.__image.getdata())
