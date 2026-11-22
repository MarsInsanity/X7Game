#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Draw the X7 Game power-on picture (cubegm/xgame-logo.bmp).

  mklogo.py OUT.bmp

The bootloader shows this file at power-on. It is written in the stock
file's exact format (as NZEUS Deck's apps/bootlogo/make_bootlogo.py found):
the same 54-byte header (640x480, 32 bits, top row first), pixels as
blue, green, red, alpha=255, and the same total size (1,228,856 bytes).
No image libraries needed: the letters come from the 5x7 font below.
"""
import colorsys
import sys

W, H = 640, 480
STOCK_HEADER = bytes.fromhex(
    '424d38c012000000000036000000280000008002000020feffff01002000'
    '0000000002c01200120b0000120b00000000000000000000')
STOCK_SIZE = 1228856

FONT = {
    'X': ['10001', '10001', '01010', '00100', '01010', '10001', '10001'],
    '7': ['11111', '00001', '00010', '00100', '01000', '01000', '01000'],
    'G': ['01110', '10001', '10000', '10111', '10001', '10001', '01111'],
    'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    'M': ['10001', '11011', '10101', '10101', '10001', '10001', '10001'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'L': ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
    'O': ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    'D': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
    'I': ['01110', '00100', '00100', '00100', '00100', '00100', '01110'],
    'N': ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
    '.': ['00000', '00000', '00000', '00000', '00000', '01100', '01100'],
    ' ': ['00000'] * 7,
}


def main(out):
    bg = (10, 12, 20)
    px = [[bg] * W for _ in range(H)]

    def rect(x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(H, y1)):
            row = px[y]
            for x in range(max(0, x0), min(W, x1)):
                row[x] = color

    def text(s, scale, y, color_at):
        width = len(s) * 6 * scale - scale
        x0 = (W - width) // 2
        for i, ch in enumerate(s):
            for gy, line in enumerate(FONT[ch]):
                for gx, bit in enumerate(line):
                    if bit == '1':
                        x = x0 + (i * 6 + gx) * scale
                        yy = y + gy * scale
                        rect(x, yy, x + scale, yy + scale, color_at(x, yy))

    def accent(x, y):          # warm-to-cool gradient across the big letters
        h = 0.95 - 0.35 * (x / W)
        r, g, b = colorsys.hsv_to_rgb(h % 1.0, 0.75, 1.0)
        return (int(r * 255), int(g * 255), int(b * 255))

    text('X7', 22, 70, accent)
    text('GAME', 9, 250, lambda x, y: (235, 238, 245))
    # full-colour strip: every hue, then a grey ramp (shows 24-bit colour works)
    for x in range(64, W - 64):
        t = (x - 64) / (W - 128)
        r, g, b = colorsys.hsv_to_rgb(t, 1.0, 1.0)
        rect(x, 352, x + 1, 366, (int(r * 255), int(g * 255), int(b * 255)))
        v = int(t * 255)
        rect(x, 366, x + 1, 374, (v, v, v))
    text('LOADING...', 3, 412, lambda x, y: (140, 150, 165))

    data = bytearray(STOCK_HEADER)
    for row in px:                      # top row first, like the stock file
        for r, g, b in row:
            data += bytes((b, g, r, 255))
    data += bytes(STOCK_SIZE - len(data))
    assert len(data) == STOCK_SIZE
    with open(out, 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    main(sys.argv[1])
