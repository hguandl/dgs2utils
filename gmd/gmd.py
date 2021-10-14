from __future__ import annotations

import json
import os
import struct

from .crc32 import Crc32
from .xor import XOR


class GMDSection(object):
    def __init__(self, section_id: int,
                 section_name: str, section_text: bytes) -> None:
        self.id = section_id
        self.name = section_name
        self.text = section_text

    def __str__(self) -> str:
        return (
            f"{self.id} - {self.name}:"
            f" {len(self.text)}"
        )

    def __repr__(self) -> str:
        return self.__str__()


class GMD(object):
    class _Header(object):
        def __init__(self,
                     magic: bytes,
                     version: bytes,
                     language: int,
                     padding: int,
                     label_count: int,
                     section_count: int,
                     label_size: int,
                     section_size: int,
                     name_size: int) -> None:
            self.magic = magic
            self.version = version
            self.language = language
            self.padding = padding
            self.label_count = label_count
            self.section_count = section_count
            self.label_size = label_size
            self.section_size = section_size
            self.name_size = name_size

        @staticmethod
        def load(data) -> GMD._Header:
            return GMD._Header(*struct.unpack_from('<4s4siqiiiii', data))

        def dump(self) -> bytes:
            return struct.pack(
                '<4s4siqiiiii',
                self.magic,
                self.version,
                self.language,
                self.padding,
                self.label_count,
                self.section_count,
                self.label_size,
                self.section_size,
                self.name_size
            )

    class _Label(object):
        def __init__(self,
                     section_id: int,
                     hash1: int,
                     hash2: int,
                     label_offset: int,
                     list_link: int) -> None:
            self.section_id = section_id
            self.hash1 = hash1
            self.hash2 = hash2
            self.label_offset = label_offset
            self.list_link = list_link

        @staticmethod
        def create(section_id: int, section_name: str,
                   label_offset: int) -> GMD._Label:
            return GMD._Label(
                section_id,
                ~Crc32.create(section_name * 2),
                ~Crc32.create(section_name * 3),
                label_offset,
                0
            )

        @staticmethod
        def load(data) -> GMD._Label:
            return GMD._Label(*struct.unpack_from('<iIIii', data))

        def dump(self) -> bytes:
            return struct.pack(
                '<iIIii',
                self.section_id,
                self.hash1,
                self.hash2,
                self.label_offset,
                self.list_link
            )

        def __str__(self) -> str:
            return (
                f'[Section ID: {self.section_id}'
                f', Hash 1: {self.hash1}'
                f', Hash 2: {self.hash2}'
                f', Label offset: {self.label_offset}'
                f', List link: {self.list_link}]'
            )

        def __repr__(self) -> str:
            return self.__str__()

    def __init__(self) -> None:
        self.name = None
        self.header = None
        self.padding = 0
        self.labels = list()
        self.sections = list()
        self.buckets = [0 for _ in range(0x100)]
        self.__label_offset = 0

    @staticmethod
    def __read_cstr(data: bytes, offset: int):
        end_offset = offset
        while data[end_offset] != 0x00:
            end_offset += 1
        return data[offset:end_offset]

    @staticmethod
    def load(f) -> GMD:
        gmd = GMD()
        content = f.read()
        offset = 0

        gmd.header = GMD._Header.load(content)
        gmd.padding = gmd.header.padding
        offset += 40

        gmd.name = content[offset:offset+gmd.header.name_size].decode('UTF-8')
        offset += gmd.header.name_size + 1

        for _ in range(gmd.header.label_count):
            gmd.labels.append(GMD._Label.load(content[offset:]))
            offset += 20

        bucket_size = 0x100 if gmd.header.label_count > 0 else 0
        gmd.buckets = list()
        for _ in range(bucket_size):
            gmd.buckets.append(struct.unpack_from('<i', content[offset:])[0])
            offset += 4
        label_data_offset = offset

        text_offset = (
            + 0x28
            + (gmd.header.name_size + 1)
            + (gmd.header.label_count * 0x14)
            + bucket_size * 4
            + gmd.header.label_size
        )
        offset = text_offset
        obfs_text = content[offset:offset+gmd.header.section_size]
        raw_text = XOR.dexor(obfs_text)

        section_offset = 0
        no_name_count = 0
        for i in range(gmd.header.section_count):
            section_text = GMD.__read_cstr(raw_text, section_offset)
            section_offset += len(section_text) + 1

            has_name = False
            for label in filter(lambda l: l.section_id == i, gmd.labels):
                has_name = True
                pos = label.label_offset
                label_name = GMD.__read_cstr(content, label_data_offset + pos)
                label_name = label_name.decode('UTF-8')

            if not has_name:
                label_name = f"no_name_{no_name_count}"
                no_name_count += 1

            gmd.sections.append(GMDSection(i, label_name, section_text))

        return gmd

    def export(self, dump_name) -> None:
        os.makedirs(dump_name, exist_ok=True)

        dump_info = {
            'name': self.name,
            'padding': self.padding
        }
        with open(os.path.join(dump_name, 'info.json'), 'w') as f:
            json.dump(dump_info, f)

        for s in self.sections:
            file_name = f"{s.id}-{s.name}.txt"
            with open(os.path.join(dump_name, file_name), 'wb') as f:
                f.write(s.text)

    def add_section(self, section: GMDSection) -> None:
        counter = len(self.sections)
        if counter == 0:
            counter = -1
        self.sections.append(section)

        if section.name.startswith('no_name_'):
            return

        label = GMD._Label.create(section.id,
                                  section.name,
                                  self.__label_offset)
        self.__label_offset += len(section.name) + 1
        self.labels.append(label)

        bucket = ~Crc32.create(section.name) & 0xff
        if self.buckets[bucket] > 0:
            self.labels[self.buckets[bucket]].list_link = counter
        else:
            self.buckets[bucket] = counter

    def pack(self, pack_path: str, pack_name: str) -> None:
        text_blob = b''.join(
            [s.text + b'\x00' for s in self.sections]
        )
        text_blob = text_blob.replace(b'\r\n', b'\n')
        text_blob = text_blob.replace(b'\n', b'\r\n')
        text_blob = XOR.rexor(text_blob)

        label_blob = b''.join(
            [s.name.encode('UTF-8') + b'\x00' for s in self.sections]
        )
        if len(self.labels) == 0:
            label_blob = b''

        self.header = GMD._Header(
            magic=b'GMD\x00',
            version=b'\x02\x03\x01\x00',
            language=0,
            padding=self.padding,
            label_count=len(self.labels),
            section_count=len(self.sections),
            label_size=len(label_blob),
            section_size=len(text_blob),
            name_size=len(self.name)
        )

        print(pack_name)
        with open(os.path.join(pack_path, pack_name), 'wb') as f:
            f.write(self.header.dump())

            f.write(self.name.encode('UTF-8'))
            f.write(b'\x00')

            for label in self.labels:
                f.write(label.dump())

            # print(self.buckets)
            if self.header.label_count > 0:
                f.write(struct.pack('<256i', *self.buckets))

            if self.header.label_count > 0:
                f.write(label_blob)

            f.write(text_blob)
