#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the files the factory bootloader loads from cubegm/ on the SD card.

  mkx7boot.py --vmlinux vmlinux --dts x7game-r36sx.dts --bootargs "..." \
              --cross mipsel-buildroot-linux-gnu- --dtc dtc --out DIR \
              [--v27-key HEX | --v27-bootloader FILE]

Writes to DIR:
  x7game.dtb          our board description (appended to the kernel)
  kernel.uImage       the kernel: gzip legacy uImage, load 0x80100000, entry
                      0x81000000 (a small shim that jumps to kernel_entry)
  avp.uImage          a 5-instruction stand-in for the AVP co-processor
                      firmware: Linux gets the AVP's memory
  kernel-v27.dll, avp-v27.dll
                      the same two files in the ChaCha20 wrapper that the
                      "bootloader protected" V2.7 consoles require (only with
                      --v27-key or --v27-bootloader)
  boot-files.json     sizes, SHA-256 and the checks that passed

The container format, the entry shim, the AVP stand-in and the V2.7 wrapper
come from NZEUS Deck (linux-port/kernel-public/package.py and
linux-port/boot-analysis/image_codec.py, GPL-3.0,
https://github.com/nzeuslab/nzeus-deck), which booted them on real consoles.
V2.6-firmware consoles load these files unencrypted (the stock R36SX V2.6
card ships plain uImages), so no key is needed for them.
"""
import argparse
import gzip
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOAD = 0x80100000          # where the kernel runs
SHIM = 0x81000000          # the bootloader jumps here; the shim jumps to kernel_entry
PAD = SHIM - LOAD          # kernel + dtb are padded to this, then the shim follows
HEAP = 0x1da0000           # the bootloader's heap starts here (stock DT bootmem)
AVP_LOAD = 0xA1100000
UIMAGE_MAGIC = 0x27051956


def run(*command):
    return subprocess.check_output([str(c) for c in command], text=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def uimage(payload, load, entry, os_id, kind, compression, name):
    header = bytearray(struct.pack('>7I4B32s', UIMAGE_MAGIC, 0, 0, len(payload), load, entry,
                                   zlib.crc32(payload), os_id, 5, kind, compression,
                                   name.encode()[:31]))
    struct.pack_into('>I', header, 4, zlib.crc32(header))
    return bytes(header) + payload


def check_uimage(image):
    magic, hcrc, _, size, load, entry, dcrc = struct.unpack('>7I', image[:28])
    header = bytearray(image[:64])
    header[4:8] = b'\0' * 4
    assert magic == UIMAGE_MAGIC and size == len(image) - 64, 'bad uImage magic or size'
    assert zlib.crc32(header) == hcrc, 'bad uImage header CRC'
    assert zlib.crc32(image[64:]) == dcrc, 'bad uImage data CRC'
    return load, entry


def assemble(cross, source, address, tmp, name):
    (tmp / f'{name}.S').write_text(source)
    (tmp / f'{name}.ld').write_text(
        'ENTRY(_start)\nSECTIONS { . = 0x%08x; .text : { *(.text) } '
        '/DISCARD/ : { *(.reginfo) *(.MIPS.abiflags) *(.pdr) *(.gnu.attributes) } }\n' % address)
    run(f'{cross}as', '-mips32r2', '-EL', '-non_shared',
        '-o', tmp / f'{name}.o', tmp / f'{name}.S')
    run(f'{cross}ld', '-EL', '-T', tmp / f'{name}.ld', '-o', tmp / f'{name}.elf', tmp / f'{name}.o')
    run(f'{cross}objcopy', '-O', 'binary', tmp / f'{name}.elf', tmp / f'{name}.bin')
    return (tmp / f'{name}.bin').read_bytes()


def kernel_symbols(vmlinux, cross, system_map):
    """Kernel symbol addresses from nm, or from System.map if nm finds none."""
    symbols = {}
    for line in run(f'{cross}nm', '-n', vmlinux).splitlines():
        parts = line.split()
        if len(parts) == 3:
            symbols[parts[2]] = int(parts[0], 16)
    if 'kernel_entry' not in symbols and system_map and system_map.exists():
        for line in system_map.read_text().splitlines():
            parts = line.split()
            if len(parts) == 3:
                symbols[parts[2]] = int(parts[0], 16)
    for name in ('kernel_entry', '__appended_dtb', '__bss_start'):
        assert name in symbols, f'kernel symbol {name} not found (no symbols in vmlinux or System.map?)'
    return symbols


def kernel_image(vmlinux, dtb, cross, tmp, system_map=None):
    elf = vmlinux.read_bytes()
    assert elf[:7] == b'\x7fELF\x01\x01\x01', 'not a 32-bit little-endian ELF'
    h = struct.unpack_from('<HHIIIIIHHHHHH', elf, 16)
    assert h[1] == 8, 'not a MIPS ELF'
    entry, phoff, phentsize, phnum = h[3], h[4], h[8], h[9]
    loads = [p for p in (struct.unpack_from('<8I', elf, phoff + i * phentsize) for i in range(phnum))
             if p[0] == 1]
    assert len(loads) == 1, f'expected one loadable segment, got {len(loads)}'
    _, offset, address, physical, size, memsize, _, _ = loads[0]
    assert address == physical == LOAD, f'kernel loads at {address:#x}, expected {LOAD:#x}'
    raw = elf[offset:offset + size]
    symbols = kernel_symbols(vmlinux, cross, system_map)
    assert symbols['kernel_entry'] == entry, 'ELF entry is not kernel_entry'
    assert symbols['__appended_dtb'] == address + size, \
        'the raw image does not end at __appended_dtb (CONFIG_MIPS_RAW_APPENDED_DTB?)'
    assert symbols['__appended_dtb'] + len(dtb) <= symbols['__bss_start'], 'DTB overlaps .bss'
    assert address + memsize < SHIM, 'kernel (with .bss) reaches the entry shim'
    assert len(raw) + len(dtb) < PAD, 'kernel + DTB too big'

    template = (HERE / 'entry.S.in').read_text()
    stub = assemble(cross, template.replace('@ENTRY_HI@', hex(entry >> 16))
                    .replace('@ENTRY_LO@', hex(entry & 0xffff)), SHIM, tmp, 'entry')
    assert 0 < len(stub) < 4096
    payload_raw = (raw + dtb).ljust(PAD, b'\0') + stub
    assert 0x100000 + len(payload_raw) < HEAP, 'kernel would overwrite the bootloader heap'
    payload = gzip.compress(payload_raw, compresslevel=9, mtime=0)
    image = uimage(payload, LOAD, SHIM, 5, 2, 1, 'X7 Game kernel')
    assert check_uimage(image) == (LOAD, SHIM)
    assert gzip.decompress(image[64:]) == payload_raw
    return image, dict(kernel_entry=hex(entry), load=hex(LOAD), entry_shim=hex(SHIM),
                       raw_bytes=len(raw), dtb_bytes=len(dtb), memsize=memsize)


def avp_stand_in(cross, tmp):
    """Five instructions: write 2 to 0xb880006b ("AVP ready") and return."""
    code = assemble(cross, '    .set noreorder\n    .set nomacro\n    .text\n    .globl _start\n_start:\n'
                    '    lui   $t0, 0xb880\n    addiu $t1, $zero, 2\n    sb    $t1, 0x6b($t0)\n'
                    '    jr    $ra\n    nop\n', AVP_LOAD, tmp, 'avp')
    assert code[:20] == struct.pack('<5I', 0x3c08b880, 0x24090002, 0xa109006b, 0x03e00008, 0) \
        and not any(code[20:]), 'unexpected AVP stand-in code'
    image = uimage(code, AVP_LOAD, AVP_LOAD, 17, 1, 0, 'X7 Game AVP stand-in')
    check_uimage(image)
    return image


# ---- V2.7 "bootloader protected" wrapper: 12-byte nonce, LE32 size, ChaCha20 ----

MASK = 0xFFFFFFFF


def _rotl(v, n):
    return ((v << n) | (v >> (32 - n))) & MASK


def chacha20_block(key, nonce, counter):
    state = list(struct.unpack('<4I', b'expand 32-byte k')) + list(struct.unpack('<8I', key)) + \
        [counter] + list(struct.unpack('<3I', nonce))
    w = state[:]
    for _ in range(10):
        for a, b, c, d in ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
                           (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)):
            w[a] = (w[a] + w[b]) & MASK; w[d] = _rotl(w[d] ^ w[a], 16)
            w[c] = (w[c] + w[d]) & MASK; w[b] = _rotl(w[b] ^ w[c], 12)
            w[a] = (w[a] + w[b]) & MASK; w[d] = _rotl(w[d] ^ w[a], 8)
            w[c] = (w[c] + w[d]) & MASK; w[b] = _rotl(w[b] ^ w[c], 7)
    return struct.pack('<16I', *[(x + y) & MASK for x, y in zip(w, state)])


def chacha20(data, key, nonce):
    out = bytearray(len(data))
    for i in range(0, len(data), 64):
        ks = chacha20_block(key, nonce, i // 64)
        chunk = data[i:i + 64]
        out[i:i + len(chunk)] = bytes(x ^ y for x, y in zip(chunk, ks))
    return bytes(out)


def chacha20_selftest():
    # RFC 8439 section 2.3.2
    expected = bytes.fromhex('10f1e7e4d13b5915500fdd1fa32071c4c7d1f4c733c068030422aa9ac3d46c4e'
                             'd2826446079faa0914c2d705d98b02a2b5129cd1de164eb9cbd083e8a2503c4e')
    assert chacha20_block(bytes(range(32)), bytes.fromhex('000000090000004a00000000'), 1) == expected


def key_from_bootloader(blob):
    """NZEUS Deck's decoding of the key table in the inspected V2.7 bootloader."""
    if sha(blob) != 'c95aa3062c308818e4572f65e8c29632ec04cd390cceac0a63d4b053fb4d0ebc':
        sys.exit('STOP: only the V2.7 factory bootloader NZEUS Deck inspected is supported; '
                 'pass --v27-key instead')
    key = bytearray()
    for i, value in enumerate(blob[0x9CC98:0x9CCB8]):
        value ^= ((0x33 + 7 * i) & 255) ^ 0x55
        key.append((((value << 5) | (value >> 3)) ^ 0xAA) & 255)
    return bytes(key)


def wrap(plain, key, tag):
    check_uimage(plain)
    nonce = hashlib.sha256(tag + plain).digest()[:12]
    wrapped = nonce + struct.pack('<I', len(plain)) + chacha20(plain, key, nonce)
    assert chacha20(wrapped[16:], key, nonce) == plain
    return wrapped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--vmlinux', type=Path, required=True)
    ap.add_argument('--system-map', type=Path, help='System.map (fallback if vmlinux has no symbols)')
    ap.add_argument('--dts', type=Path, required=True)
    ap.add_argument('--bootargs', required=True)
    ap.add_argument('--cross', required=True, help='cross tool prefix, e.g. .../mipsel-buildroot-linux-gnu-')
    ap.add_argument('--dtc', default='dtc')
    ap.add_argument('--out', type=Path, required=True)
    group = ap.add_mutually_exclusive_group()
    group.add_argument('--v27-key', help='64 hex digits: the V2.7 bootloader wrapper key')
    group.add_argument('--v27-bootloader', type=Path, help='a V2.7 factory bootloader dump')
    a = ap.parse_args()
    assert 'nzclk=900' in a.bootargs.split(), 'keep nzclk=900: the FPU is unreliable at 1188 MHz'
    a.out.mkdir(parents=True, exist_ok=True)
    report = dict(bootargs=a.bootargs)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        assert '"' not in a.bootargs and '\\' not in a.bootargs
        dts = a.dts.read_text()
        assert dts.count('bootargs = "@BOOTARGS@";') == 1, 'no bootargs placeholder in the DTS'
        dts = dts.replace('bootargs = "@BOOTARGS@";', 'bootargs = "%s";' % a.bootargs)
        (tmp / 'board.dts').write_text(dts)
        subprocess.run([a.dtc, '-q', '-I', 'dts', '-O', 'dtb', '-o', tmp / 'board.dtb', tmp / 'board.dts'],
                       check=True)
        dtb = (tmp / 'board.dtb').read_bytes()
        kernel, info = kernel_image(a.vmlinux, dtb, a.cross, tmp, a.system_map)
        avp = avp_stand_in(a.cross, tmp)
    (a.out / 'x7game.dtb').write_bytes(dtb)
    (a.out / 'kernel.uImage').write_bytes(kernel)
    (a.out / 'avp.uImage').write_bytes(avp)
    report['kernel.uImage'] = dict(bytes=len(kernel), sha256=sha(kernel), **info)
    report['avp.uImage'] = dict(bytes=len(avp), sha256=sha(avp))
    key = None
    if a.v27_key:
        key = bytes.fromhex(a.v27_key.strip())
        assert len(key) == 32, '--v27-key must be 32 bytes (64 hex digits)'
    elif a.v27_bootloader:
        key = key_from_bootloader(a.v27_bootloader.read_bytes())
    if key:
        chacha20_selftest()
        k27 = wrap(kernel, key, b'X7GAME-KERNEL-v1')
        a27 = wrap(avp, key, b'X7GAME-AVP-STUB-v1')
        (a.out / 'kernel-v27.dll').write_bytes(k27)
        (a.out / 'avp-v27.dll').write_bytes(a27)
        report['kernel-v27.dll'] = dict(bytes=len(k27), sha256=sha(k27))
        report['avp-v27.dll'] = dict(bytes=len(a27), sha256=sha(a27))
    report['v27_wrapped'] = bool(key)
    (a.out / 'boot-files.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
