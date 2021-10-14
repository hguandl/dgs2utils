from typing import List, Tuple
from bidict import bidict


class MasterSwizzle(object):
    def __init__(self, stride: int,
                 init_pt: Tuple[int, int],
                 bit_field_coords: List[Tuple[int, int]]) -> None:
        self.stride = stride
        self.init_pt = init_pt
        self.bit_field_coords = bit_field_coords

        macro_tile_width = bit_field_coords[0][0]
        macro_tile_height = bit_field_coords[0][1]

        for coord in bit_field_coords[1:]:
            macro_tile_width |= coord[0]
            macro_tile_height |= coord[1]

        self.macro_tile_width = macro_tile_width + 1
        self.macro_tile_height = macro_tile_height + 1

        self.width_in_tiles = \
            (stride + self.macro_tile_width - 1) // self.macro_tile_width

    def get(self, cnt: int) -> Tuple[int, int]:
        macro_tile_cnt = cnt // self.macro_tile_width // self.macro_tile_height
        macro_x, macro_y = macro_tile_cnt % self.width_in_tiles, \
            macro_tile_cnt // self.width_in_tiles

        ret = [(macro_x * self.macro_tile_width,
               macro_y * self.macro_tile_height)]
        for j in range(len(self.bit_field_coords)):
            if (cnt >> j) % 2 == 1:
                ret.append(self.bit_field_coords[j])

        ret_x, ret_y = self.init_pt
        for pt in ret:
            ret_x ^= pt[0]
            ret_y ^= pt[1]

        return ret_x, ret_y

    def swizzle_bidict(self, width: int, height: int) -> bidict[int, int]:
        px_cnt = width * height
        ret = bidict()
        for tex_idx in range(px_cnt):
            x, y = self.get(tex_idx)
            bmp_idx = x + y * width
            ret[tex_idx] = bmp_idx
        return ret


def ctr_swizzle(width: int, height: int) -> bidict[int, int]:
    swizzle = MasterSwizzle(width, (0, 0),
                            [(1, 0), (0, 1), (2, 0), (0, 2), (4, 0), (0, 4)])

    return swizzle.swizzle_bidict(width, height)
