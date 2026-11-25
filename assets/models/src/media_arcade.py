# SPDX-License-Identifier: GPL-3.0-or-later
"""Generic arcade game board (PCB), low-poly.

Standing upright like on a shelf: component side facing +Z, the edge
connector at y = 0. About 30 cm wide, 25 cm tall and 3 cm deep with the
parts and stand-offs. Signature features: the green board with a darker
edge, the gold edge-connector fingers on a tab along the bottom, a long
CPU with silver pin rows, two labelled EPROMs, a square custom chip, a row
of small logic chips, a red DIP-switch block, two blue electrolytic capacitors, a few lighter
traces and the white nylon stand-offs at the four corners.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

GREEN = (24, 112, 56)         # board, solder mask
EDGE = (10, 64, 30)           # board edges
TRACE = (78, 160, 88)         # lighter copper traces under the mask
GOLD = (230, 180, 44)         # edge-connector fingers
CHIP = (30, 30, 34)           # chip tops
CHIP_SIDE = (74, 74, 84)      # chip sides
PIN = (178, 178, 188)         # pin rows, capacitor tops
LABEL = (238, 234, 216)       # EPROM stickers
CAP = (40, 70, 172)           # capacitor sleeves
NYLON = (214, 206, 176)       # stand-offs
RED = (204, 36, 36)           # DIP-switch block

W2 = 15.0                     # half width
ZF, ZB = 0.22, -0.22          # board faces (thicker than real, to read)
TAB_Y = 1.6                   # edge-connector tab height
TAB_X = 7.5                   # tab half width
H = 25.0

m = Model('arcade', 'media')

# ---- the board and its connector tab
m.box(-W2, TAB_Y, ZB, W2, H, ZF, GREEN,
      faces={'left': EDGE, 'right': EDGE, 'top': EDGE, 'bottom': EDGE, 'back': None})
# the back face in tiles: smaller triangles keep the parts on the front from
# showing through when a renderer interpolates depth across a huge triangle
XS = [-W2, 0.0, W2]
YS = [TAB_Y, 13.0, H]
for i in range(len(XS) - 1):
    for j in range(len(YS) - 1):
        m.quad((XS[i + 1], YS[j], ZB), (XS[i], YS[j], ZB), (XS[i], YS[j + 1], ZB), (XS[i + 1], YS[j + 1], ZB), GREEN)
m.box(-TAB_X, 0.0, ZB, TAB_X, TAB_Y, ZF, GOLD,
      faces={'top': None, 'left': EDGE, 'right': EDGE, 'bottom': EDGE})

# gaps between the gold fingers, front and back (7 fingers a side)
NF = 7
pitch = 2 * TAB_X / NF
for i in range(1, NF):
    x = -TAB_X + i * pitch
    g = [(x - 0.32, 0.0), (x + 0.32, 0.0), (x + 0.32, TAB_Y), (x - 0.32, TAB_Y)]
    m.decal_xy(g, ZF, GREEN, lift=0.02)
    m.polygon([(gx, gy, ZB - 0.02) for gx, gy in g], GREEN, normal=(0, 0, -1))


def chip(x0, y0, x1, y1, h, top=CHIP):
    """A chip body sitting on the board front."""
    return m.box(x0, y0, ZF, x1, y1, ZF + h, CHIP_SIDE, faces={'front': top, 'back': None})


def pad(x0, y0, x1, y1, col, lift=0.03):
    return m.decal_xy([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], ZF, col, lift=lift)


# ---- top band: CPU (long DIP with pin rows), two EPROMs, square custom chip
pad(-12.6, 19.25, -3.4, 22.25, PIN)                 # pin rows peeking out
chip(-12.4, 19.5, -3.6, 22.0, 0.5)
for y0 in (21.4, 18.2):
    chip(-1.6, y0, 4.2, y0 + 1.7, 0.45)
    pad(-0.2, y0 + 0.35, 2.4, y0 + 1.35, LABEL, lift=0.48)   # sticker on top
pad(7.4, 17.9, 12.6, 23.1, PIN)                     # pin skirt
chip(7.8, 18.3, 12.2, 22.7, 0.4)

# ---- middle band: a row of small logic chips
for i in range(6):
    x = -12.4 + i * 2.1
    chip(x, 10.6, x + 0.9, 13.6, 0.4)

# ---- red DIP-switch block near the bottom left, white switch row on top
m.box(-12.2, 4.2, ZF, -7.4, 5.8, ZF + 0.55, RED, faces={'back': None})
pad(-11.8, 4.65, -7.8, 5.35, LABEL, lift=0.58)

# ---- traces (lighter lines) linking the parts
pad(-8.0, 14.6, 10.0, 14.95, TRACE, lift=0.02)
pad(-13.0, 7.6, 8.0, 7.95, TRACE, lift=0.02)

# ---- capacitors near the edge connector (5-sided cylinders, silver tops)
for cx, cy in ((9.8, 5.0), (12.2, 8.2)):
    m.cylinder_z(cx, cy, 0.9, ZF, ZF + 1.5, CAP, segments=5, front=PIN, back=False)

# ---- stand-offs through the corner holes (nylon posts, back and a screw cap front)
for sx in (-13.7, 13.7):
    for sy in (3.0, 23.7):
        m.box(sx - 0.45, sy - 0.45, -1.35, sx + 0.45, sy + 0.45, ZF + 0.25, NYLON)

print(m.stats())
m.save()
