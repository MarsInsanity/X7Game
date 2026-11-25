# SPDX-License-Identifier: GPL-3.0-or-later
"""
sheet.py - put model previews side by side on one contact sheet, each with
its name underneath. Pure Python, reads the PNGs render.py writes.

    python tools/models/sheet.py OUT.png COLUMNS "LABEL=preview.png" ...
"""
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import write_png  # noqa: E402

# 3x5 pixel font, enough for the system names
FONT = {
    'A': '010101111101101', 'B': '110101110101110', 'C': '011100100100011',
    'D': '110101101101110', 'E': '111100110100111', 'F': '111100110100100',
    'G': '011100101101011', 'H': '101101111101101', 'I': '111010010010111',
    'J': '001001001101010', 'K': '101101110101101', 'L': '100100100100111',
    'M': '101111111101101', 'N': '110101101101101', 'O': '010101101101010',
    'P': '110101110100100', 'Q': '010101101110011', 'R': '110101110101101',
    'S': '011100010001110', 'T': '111010010010010', 'U': '101101101101111',
    'V': '101101101101010', 'W': '101101111111101', 'X': '101101010101101',
    'Y': '101101010010010', 'Z': '111001010100111', '0': '111101101101111',
    '1': '010110010010111', '2': '110001010100111', '3': '110001010001110',
    '4': '101101111001001', '5': '111100110001110', '6': '011100111101111',
    '7': '111001010010010', '8': '111101111101111', '9': '111101111001110',
    '-': '000000111000000', ' ': '000000000000000', '/': '001001010100100',
}


def read_png(path):
    data = open(path, 'rb').read()
    pos, idat, w, h = 8, b'', 0, 0
    while pos < len(data):
        n, = struct.unpack('>I', data[pos:pos + 4])
        t = data[pos + 4:pos + 8]
        d = data[pos + 8:pos + 8 + n]
        if t == b'IHDR':
            w, h = struct.unpack('>II', d[:8])
        elif t == b'IDAT':
            idat += d
        pos += 12 + n
    raw = zlib.decompress(idat)
    stride = w * 3
    img, prev = [], bytearray(stride)
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):           # PNG filters (render.py writes 0)
            a = line[i - 3] if i >= 3 else 0
            b = prev[i]
            c = prev[i - 3] if i >= 3 else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        img.append([tuple(line[x * 3:x * 3 + 3]) for x in range(w)])
        prev = line
    return img


def main():
    out, cols, items = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
    tw, th, lab = 320, 240, 16
    rows = (len(items) + cols - 1) // cols
    W, H = cols * tw, rows * (th + lab)
    sheet = [[(16, 18, 24)] * W for _ in range(H)]
    for k, item in enumerate(items):
        label, path = item.split('=', 1)
        src = read_png(path)
        sx = len(src[0]) // tw
        ox, oy = (k % cols) * tw, (k // cols) * (th + lab)
        for y in range(th):
            row = src[y * sx]
            for x in range(tw):
                sheet[oy + y][ox + x] = row[x * sx]
        text = label.upper()
        px = ox + (tw - len(text) * 8) // 2
        for ch in text:
            g = FONT.get(ch, FONT[' '])
            for i, bit in enumerate(g):
                if bit == '1':
                    for dy in range(2):
                        for dx in range(2):
                            sheet[oy + th + 3 + (i // 3) * 2 + dy][px + (i % 3) * 2 + dx] = (230, 232, 240)
            px += 8
    write_png(out, sheet, 1)
    print(out)


if __name__ == '__main__':
    main()
