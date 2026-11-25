# SPDX-License-Identifier: GPL-3.0-or-later
"""Generic arcade game board (JAMMA-style PCB), low-poly.

Standing upright like on a shelf: component side facing +Z, the gold edge
connector at y = 0. 30 cm wide, 25 cm tall (24 cm board + a 1 cm connector
tab), the board 0.2 cm thick. Signature features, from photos of real
boards (Donkey Kong, Gorf, Namco NA-1, Moon Patrol): the green solder-mask
board with a darker edge, a protruding tab of gold fingers along the bottom
edge with the key gap, a long 64-pin CPU with silver pin rows, two EPROMs
with their silver quartz windows, a square custom chip with its pin skirt,
rows of small black logic chips, blue electrolytic capacitors, a few
lighter traces and white nylon stand-offs under the four corner holes.

The game's sticker is the picture area (4:3, upper right of the board).

Insertion: the board goes into the cabinet's back through a service door
and slides flat onto a shelf, connector first. Laid flat (rot [-90, 0, 0])
the component side faces up and the nylon stand-offs are its feet.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

GREEN = (22, 118, 58)         # board, solder mask
EDGE = (8, 58, 26)            # board edges, finger gaps
TRACE = (92, 178, 104)        # lighter traces under the mask
GOLD = (236, 184, 40)         # edge-connector fingers
CHIP = (24, 24, 28)           # chip tops
CHIP_SIDE = (70, 70, 80)      # chip sides
PIN = (184, 184, 194)         # pin rows, EPROM windows, capacitor tops
CAP = (36, 72, 186)           # capacitor sleeves
NYLON = (232, 226, 200)       # stand-offs
STICKER = (240, 236, 220)     # the game sticker (picture fallback)

W2 = 15.0                     # half width
ZF, ZB = 0.1, -0.1            # board faces (2 mm board)
TAB_Y = 1.0                   # edge-connector tab height
TAB_X = 5.7                   # tab half width (28 fingers at 3.96 mm)
H = 25.0
POST_Z = -0.9                 # stand-offs reach this far behind the board

m = Model('arcade', 'media')

# ---- the board, and the connector tab below it
m.box(-W2, TAB_Y, ZB, W2, H, ZF, GREEN,
      faces={'left': EDGE, 'right': EDGE, 'top': EDGE, 'bottom': EDGE})
m.box(-TAB_X, 0.0, ZB, TAB_X, TAB_Y, ZF, GOLD,
      faces={'top': None, 'left': EDGE, 'right': EDGE, 'bottom': EDGE})

# gaps between the gold fingers on the front: 28 positions drawn as 12
# fingers, the wider key gap between positions 6 and 7
pitch = 2 * TAB_X / 12
for i in range(1, 12):
    x = -TAB_X + i * pitch
    hw = 0.26 if i == 3 else 0.13
    m.decal_xy([(x - hw, 0.0), (x + hw, 0.0), (x + hw, TAB_Y), (x - hw, TAB_Y)], ZF, EDGE, lift=0.02)


def chip(x0, y0, x1, y1, h, top=CHIP):
    """A chip body sitting on the board front. Its downward side is left
    out: a few mm tall, it is never seen from the views the frontend uses
    (upright from above, or laid flat seen from behind)."""
    return m.box(x0, y0, ZF, x1, y1, ZF + h, CHIP_SIDE, faces={'front': top, 'back': None, 'bottom': None})


def pad(x0, y0, x1, y1, col, lift=0.02):
    return m.decal_xy([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], ZF, col, lift=lift)


# ---- the game sticker: the picture area, 4:3, upper right
m.image_xy(-2.6, 11.0, 13.0, 22.7, ZF, fallback=STICKER, lift=0.03)

# ---- upper left: the CPU (long DIP, pin rows peeking out), two EPROMs
pad(-13.4, 21.0, -4.4, 23.6, PIN)
chip(-13.2, 21.25, -4.6, 23.35, 0.45)
for x0 in (-13.2, -8.6):
    chip(x0, 17.7, x0 + 3.8, 19.3, 0.45)
    pad(x0 + 1.5, 18.1, x0 + 2.3, 18.9, PIN, lift=0.47)     # quartz window

# square custom chip with its pin skirt
pad(-12.9, 12.3, -8.5, 16.7, PIN)
chip(-12.5, 12.7, -8.9, 16.3, 0.3)

# ---- lower band: rows of small logic chips
for y0 in (7.9, 5.2):
    for i in range(5):
        x0 = -12.6 + i * 5.2
        chip(x0, y0, x0 + 3.0, y0 + 0.9, 0.4)
chip(-12.6, 2.3, -5.4, 3.6, 0.45)                   # a long sound / video chip

# ---- a trace (lighter line) along the chip rows
pad(-13.0, 9.6, 12.4, 9.85, TRACE)

# ---- electrolytic capacitors (5-sided cylinders, silver tops)
for cx, cy in ((11.6, 3.3), (-5.6, 14.6)):
    m.cylinder_z(cx, cy, 0.8, ZF, ZF + 1.3, CAP, segments=5, front=PIN, back=False)

# ---- nylon stand-offs under the four corner holes (feet when laid flat)
for sx in (-14.2, 14.2):
    for sy in (2.0, 23.8):
        m.box(sx - 0.4, sy - 0.4, POST_Z, sx + 0.4, sy + 0.4, ZB, NYLON, faces={'front': None})
        pad(sx - 0.4, sy - 0.4, sx + 0.4, sy + 0.4, NYLON, lift=0.03)    # the post's head

print(m.stats())
m.save()
