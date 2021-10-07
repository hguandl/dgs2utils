import argparse
import json
import os
import re
from typing import Tuple

from .gmd import GMD, GMDSection

parser = argparse.ArgumentParser(
    prog='python3 -m gmd',
    description='Pack and unpack GMD files.'
)

command_parsers = parser.add_subparsers(title='commands', dest='command',
                                        help='GMD process')
unpack_parser = command_parsers.add_parser('unpack', help='Unpack GMD files')
repack_parser = command_parsers.add_parser('repack', help='Repack to GMD')

unpack_parser.add_argument('gmd', metavar='gmd_dir', type=str, nargs=1,
                           help='GMD files directory')

unpack_parser.add_argument('-o', metavar='output_dir', type=str, nargs=1,
                           help='Output directory', required=True)

repack_parser.add_argument('res', metavar='res_dir', type=str, nargs=1,
                           help='Directories to repack')

repack_parser.add_argument('-o', metavar='output_dir', type=str, nargs=1,
                           help='Output directory', required=True)


def unpack_gmds(gmd_dir: str, unpack_dir: str) -> None:
    for file in os.listdir(gmd_dir):
        if not file.endswith('.gmd'):
            continue
        if file == "_sce08_c000_0000_jpn.gmd":
            continue

        pack_name = os.path.join(gmd_dir, file)
        with open(pack_name, 'rb') as f:
            print(f"Unpacking {file}...")
            gmd = GMD.load(f)
            gmd.export(os.path.join(unpack_dir, file))


def repack_gmds(unpack_dir: str, pack_dir: str):
    os.makedirs(pack_dir, exist_ok=True)

    for file in os.listdir(unpack_dir):
        gmd_file = os.path.join(unpack_dir, file)
        if not gmd_file.endswith('.gmd'):
            continue
        if not os.path.isdir(gmd_file):
            continue

        gmd = GMD()
        with open(os.path.join(gmd_file, 'info.json'), 'r') as f:
            gmd_info = json.load(f)
        gmd.name = gmd_info['name']
        gmd.padding = gmd_info['padding']

        scripts = list[Tuple[int, str, str]]()
        for section_file in os.listdir(gmd_file):
            if not section_file.endswith('.txt'):
                continue
            regex = re.compile(r"(\d+)-(.+).txt")
            result = re.match(regex, section_file)
            section_id = int(result.group(1))
            section_name = result.group(2)

            scripts.append((section_id,
                            section_name,
                            os.path.join(gmd_file, section_file)))

        scripts.sort(key=lambda s: s[0])

        for script in scripts:
            with open(script[2], 'rb') as f:
                gmd.add_section(GMDSection(script[0], script[1], f.read()))

        gmd.pack(pack_dir, file)


if __name__ == "__main__":
    args = parser.parse_args()
    if args.command == 'unpack':
        unpack_gmds(args.gmd[0], args.o[0])
    elif args.command == 'repack':
        repack_gmds(args.res[0], args.o[0])
    else:
        parser.print_help()
