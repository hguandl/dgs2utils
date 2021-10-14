import argparse
import csv
import json
import os

from PIL import ImageFont

from ..tex import MTTex
from .font_bitmap import FontBitmap
from .gfd import GFD

parser = argparse.ArgumentParser(
    prog='python3 -m gfd',
    description='Processing GFD files.'
)

command_parsers = parser.add_subparsers(title='commands', dest='command',
                                        help='GFD process')
dump_parser = command_parsers.add_parser('dump', help='Unpack GMD files')
generate_parser = command_parsers.add_parser('generate', help='Repack to GMD')
export_parser = command_parsers.add_parser('export', help='Export GMD')

dump_parser.add_argument('gfd', metavar='gfd_file', type=str, nargs=1,
                         help='GFD file')

dump_parser.add_argument('-o', metavar='output_dir', type=str, nargs=1,
                         help='Output directory', required=True)

generate_parser.add_argument('-i', metavar='res_dir', type=str, nargs=1,
                             help='Resources directory', required=True)

generate_parser.add_argument('-f', metavar='font', type=str, nargs=1,
                             help='TrueType font file', required=True)

generate_parser.add_argument('-n', metavar='font', type=str, nargs=1,
                             help='GFD file index', required=True)

generate_parser.add_argument('-o', metavar='output_dir', type=str, nargs=1,
                             help='Output directory', required=True)

export_parser.add_argument('-i', metavar='gfd_file', type=str, nargs=1,
                           help='GFD file', required=True)

export_parser.add_argument('-o', metavar='output_dir', type=str, nargs=1,
                           help='Output directory', required=True)


def dump_gfd(gfd_file: str, dump_dir: str) -> None:
    if not gfd_file.endswith('.gfd'):
        raise ValueError("Not a GFD file.")

    with open(gfd_file, 'rb') as f:
        gfd = GFD.load(f)

    base_name = os.path.splitext(os.path.basename(gfd_file))[0]
    header_file = f"{base_name}_header.bin"
    with open(os.path.join(dump_dir, header_file), 'wb') as f:
        f.write(gfd.dump_header())

    map_file = f"{base_name}_map.csv"
    font_tab = [vars(g) for g in gfd.glyphs]
    with open(os.path.join(dump_dir, map_file), 'w', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=font_tab[0].keys())
        writer.writeheader()
        writer.writerows(font_tab)


def generate_gfd(font_name: str, out_dir: str, res_dir: str, font_index: str):
    os.makedirs(out_dir, exist_ok=True)

    base_name = None
    for gfd_header in os.listdir(res_dir):
        if gfd_header == f"font{font_index}_jpn_header.bin":
            base_name = gfd_header[:-11]  # len('_header.bin')
            break

    if base_name is None:
        raise ValueError(f"No GFD file with index {font_index}")

    char_list_name = f"{base_name}_list.json"
    with open(os.path.join(res_dir, char_list_name), 'r') as f:
        char_list = json.load(f)

    with open(os.path.join(res_dir, gfd_header), 'rb') as f:
        gfd = GFD.load(f)

    ttf = ImageFont.truetype(font_name, gfd.header.size_px)

    bitmaps = list()
    bitmap = FontBitmap()

    gfd_entries = list()
    for char_code in char_list:
        txt = chr(char_code)

        entry = bitmap.push(txt, len(bitmaps), ttf)

        gfd_entries.append(entry)

        # Next bitmap
        if bitmap.full:
            bitmaps.append(bitmap)
            bitmap = FontBitmap()
    bitmaps.append(bitmap)

    gfd.header.bitmap_count = len(bitmaps)
    gfd.header.entry_count = len(gfd_entries)
    gfd.glyphs = gfd_entries

    gfd_name = f"{base_name}.gfd"
    gfd.repack(os.path.join(out_dir, gfd_name))

    for i in range(len(bitmaps)):
        tex = MTTex.new((512, 512), bitmaps[i].getdata())
        tex_name = f"{base_name}_{i:02d}_AM_NOMIP.tex"
        tex.export_tex(os.path.join(out_dir, tex_name))


def export_gfd(gfd_file: str, out_dir: str) -> None:
    assert gfd_file.endswith('.gfd')

    with open(gfd_file, 'rb') as f:
        gfd = GFD.load(f)
        gfd.dump(out_dir)


if __name__ == "__main__":
    args = parser.parse_args()
    if args.command == 'dump':
        dump_gfd(args.gfd[0], args.o[0])
    elif args.command == 'generate':
        generate_gfd(
            font_name=args.f[0],
            out_dir=args.o[0],
            res_dir=args.i[0],
            font_index=args.n[0]
        )
    elif args.command == 'export':
        export_gfd(args.i[0], args.o[0])
    else:
        parser.print_help()
