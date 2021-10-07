#!/usr/bin/env python3

import argparse
import csv
import glob
import json

parser = argparse.ArgumentParser(
    prog='font_db.py',
    description='Process list of font characters.'
)

command_parsers = parser.add_subparsers(title='commands', dest='command',
                                        help='Font list process')

count_cmd = command_parsers.add_parser('count',
                                       help='Count characters from text files')

from_csv = command_parsers.add_parser('from_csv',
                                      help='Generate font list from CSV')

merge_cmd = command_parsers.add_parser('merge', help='Merge lists')

count_cmd.add_argument('-d', metavar='text_dir', type=str, nargs=1,
                       help='Texts directory', required=True)

count_cmd.add_argument('-o', metavar='output_file', type=str, nargs=1,
                       help='Output JSON file', required=True)

from_csv.add_argument('-i', metavar='csv_file', type=str, nargs=1,
                      help='CSV file', required=True)

from_csv.add_argument('-o', metavar='output_file', type=str, nargs=1,
                      help='Output JSON file', required=True)

merge_cmd.add_argument('files', metavar='file', type=str, nargs='+',
                       help='Files to merge')

merge_cmd.add_argument('-o', metavar='output_file', type=str, nargs=1,
                       help='Merged JSON file', required=True)


def count_from_dir(text_dir: str, out_file: str):
    char_set = set[int]()

    txt_files = glob.glob(f"{text_dir}/**/*.txt")

    for file in txt_files:
        if 'sce08_c003_0020' in file:
            continue
        with open(file, 'r', encoding='UTF-8') as f:
            for char in f.read():
                char_set.add(ord(char))

    if 0xa in char_set:
        char_set.remove(0xa)
    char_list = sorted(list(char_set))

    with open(out_file, 'w') as f:
        json.dump(char_list, f)

    print(f"Total: {len(char_list)}")


def csv_to_txt(csv_file: str, out_file: str):
    char_set = set[int]()

    with open(csv_file, 'r', encoding='UTF-8') as f:
        for row in csv.DictReader(f):
            char_set.add(ord(row['char']))

    if 0xa in char_set:
        char_set.remove(0xa)
    char_list = sorted(list(char_set))

    with open(out_file, 'w') as f:
        json.dump(char_list, f)

    print(f"Total: {len(char_list)}")


def merge_lists(files: list[str], out_file: str):
    char_set = set[int]()

    for file in files:
        with open(file, 'r', encoding='UTF-8') as f:
            for char_code in json.load(f):
                char_set.add(char_code)

    if 0xa in char_set:
        char_set.remove(0xa)
    char_list = sorted(list(char_set))

    with open(out_file, 'w') as f:
        json.dump(char_list, f)

    print(f"Total: {len(char_list)}")


if __name__ == "__main__":
    args = parser.parse_args()
    if args.command == 'count':
        count_from_dir(args.d[0], args.o[0])
    elif args.command == 'from_csv':
        csv_to_txt(args.i[0], args.o[0])
    elif args.command == 'merge':
        merge_lists(args.files, args.o[0])
    else:
        parser.print_help()
