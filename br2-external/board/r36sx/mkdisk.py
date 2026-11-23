#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Assemble the X7 Game SD card image.

  mkdisk.py --fat boot.vfat --root rootfs.squashfs --fat-mib 48 --root-mib 487 --out x7game.img

The card layout is defined in post-image.sh (the single source of these
numbers; the kernel command line, x7-update and S05x7data follow it). Card
layout 2 (MiB); the image holds only the first three areas:
  0 .. 1        partition table (a normal MBR - the factory bootloader reads
                plain FAT32 cards: TreeFrogUI's install guide formats them on
                a PC)
  1 .. 49       MBR partition 1, FAT32 "X7GAME" (--fat-mib): the files the
                bootloader loads (cubegm/) and x7game/ (settings, logs).
  49 .. 536     system slot A (squashfs root, --root-mib), /dev/mmcblk0p2.
                NOT in the partition table; the kernel finds it through
                blkdevparts= on its command line. Only the used part is in
                the image file (rounded up to 1 MiB).
  536 .. 1024   system slot B, /dev/mmcblk0p3: not in the image and not in
                the partition table; x7-update writes it.
  1024 .. end   the data partition (exFAT "X7DATA"), not in the image: X7
                Game makes it at the first start and adds it to the partition
                table as partition 2 (for PCs); Linux sees it as
                /dev/mmcblk0p4 through blkdevparts=. Its start never moves:
                re-flashed cards keep it.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

MIB = 1024 * 1024
SECTOR = 512


def chs(lba):
    """CHS address for an MBR entry (255 heads, 63 sectors; capped like PCs do)."""
    c, rest = divmod(lba, 255 * 63)
    h, s = divmod(rest, 63)
    if c > 1023:
        return bytes((254, 255, 255))
    return bytes((h, ((c >> 2) & 0xC0) | (s + 1), c & 0xFF))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--fat', type=Path, required=True)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--fat-mib', type=int, required=True)
    ap.add_argument('--root-mib', type=int, required=True)
    ap.add_argument('--disk-id', type=lambda s: int(s, 0), default=0x58374741)   # "AG7X"
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    fat = a.fat.read_bytes()
    root = a.root.read_bytes()
    fat_start, fat_size = 1 * MIB, a.fat_mib * MIB
    root_start, root_size = fat_start + fat_size, a.root_mib * MIB
    assert len(fat) == fat_size, f'FAT image is {len(fat)} bytes, expected {fat_size}'
    assert len(root) <= root_size, f'root file system is {len(root)} bytes, only {root_size} reserved'
    # the FAT32 boot sector must describe this exact partition (like a PC format)
    assert fat[0x52:0x5A] == b'FAT32   ' and fat[510:512] == b'\x55\xaa', 'not a FAT32 image'
    hidden, total = struct.unpack_from('<II', fat, 0x1C)
    assert hidden == fat_start // SECTOR and total == fat_size // SECTOR, \
        f'FAT32 hidden/total sectors {hidden}/{total} do not match the partition'
    assert root[:4] == b'hsqs', 'root file system is not a squashfs'

    mbr = bytearray(SECTOR)
    struct.pack_into('<I', mbr, 440, a.disk_id)
    first, count = fat_start // SECTOR, fat_size // SECTOR
    entry = bytes((0x00,)) + chs(first) + bytes((0x0C,)) + chs(first + count - 1) + struct.pack('<II', first, count)
    mbr[446:462] = entry
    mbr[510:512] = b'\x55\xaa'

    image = bytearray(root_start + (len(root) + MIB - 1) // MIB * MIB)
    image[0:SECTOR] = mbr
    image[fat_start:fat_start + fat_size] = fat
    image[root_start:root_start + len(root)] = root
    a.out.write_bytes(image)
    report = dict(image=a.out.name, bytes=len(image), sha256=hashlib.sha256(image).hexdigest(),
                  fat=dict(offset=fat_start, bytes=fat_size), root=dict(offset=root_start, reserved=root_size,
                                                                         used=len(root)))
    a.out.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
