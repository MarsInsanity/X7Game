# SPDX-License-Identifier: GPL-3.0-or-later
"""Super Nintendo cartridge (North American Game Pak), low-poly.

Standing upright like on a shelf: label facing +Z, connector edge at y = 0.
13.0 cm wide, 8.6 cm tall, 2.0 cm thick (front panel included), a landscape
slab like the real one. Signature features (from photos): the raised
central front panel carrying the big landscape label at its top and the
recessed U below it with the centre tongue; the two side "wings" set back
behind the panel with their horizontal grip grooves (six slats each) and
the two screws at the bottom corners; the wide dark connector opening in
the bottom edge; the two locking notches at the back bottom; horizontal
ribs and a sticker on the back.

The label is the picture area (the game's picture is drawn there).

Insertion (top slot of the console, straight down, label to +Z): the whole
cartridge is a closed box-like shape, 13.0 x 8.6 x 2.0, x centred, the
bottom edge at y = 0. Cross-section that enters the slot: the body
x -6.5..6.5, z -1.0..0.8 plus the front panel x -4.35..4.35, z 0.8..1.0.
On the real console about the lower 4.2 cm goes in.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
import math

from x7model import Model

SHELL = (172, 172, 182)       # light grey with the slight lilac cast
SHELL_LT = (196, 196, 204)    # front panel, a touch lighter than the wings
GROOVE = (92, 92, 104)        # grip grooves, back ribs
RECESS = (140, 140, 152)      # U recess below the label
SCREW = (58, 56, 52)          # screw heads
SLOT = (24, 24, 28)           # connector opening, notches
STICKER = (88, 78, 84)        # dark warning sticker on the back
CONTACT = (176, 152, 72)     # gold contacts on the board edge
LABEL = (34, 34, 38)          # plain label colour (NA labels are black-framed)

W2 = 6.5          # half width
H = 8.6           # height
ZB = -1.0         # back
ZW = 0.8          # front of the wings
ZF = 1.0          # front of the raised central panel
PX = 4.35         # half width of the central panel

m = Model('snes', 'media')

# ---- body: the full-width slab, small rounded top corners seen from the front.
# Built face by face so the bottom can hold the real connector opening and
# the back the two locking notches (real cavities, nothing pokes below y = 0).
NX0, NX1, NH, ND = 5.25, 5.8, 1.1, 0.5        # notches: x range, height, depth
OX, OZ0, OZ1, OH = 4.9, -0.45, 0.6, 1.2       # connector opening: half width, z range, depth
top = []
r = 0.5
for k in range(3):                       # top right corner
    a = math.radians(90 * k / 2)
    top.append((W2 - r + r * math.cos(a), H - r + r * math.sin(a)))
for k in range(3):                       # top left corner
    a = math.radians(90 + 90 * k / 2)
    top.append((-W2 + r + r * math.cos(a), H - r + r * math.sin(a)))
outline = [(-W2, 0.0), (W2, 0.0)] + top
m.polygon([(x, y, ZW) for x, y in outline], SHELL, normal=(0, 0, 1))          # front (wings)
back = [(-W2, 0.0), (-NX1, 0.0), (-NX1, NH), (-NX0, NH), (-NX0, 0.0),
        (NX0, 0.0), (NX0, NH), (NX1, NH), (NX1, 0.0), (W2, 0.0)] + top
m.polygon([(x, y, ZB) for x, y in back], SHELL, normal=(0, 0, -1))
ring = [(W2, 0.0)] + top + [(-W2, 0.0)]       # right side, top, left side
for (xa, ya), (xb, yb) in zip(ring, ring[1:]):
    m.quad((xa, ya, ZW), (xa, ya, ZB), (xb, yb, ZB), (xb, yb, ZW), SHELL)


def floor(x0, x1, z0, z1):                    # a bottom tile facing -Y
    m.quad((x0, 0.0, z0), (x1, 0.0, z0), (x1, 0.0, z1), (x0, 0.0, z1), SHELL)


floor(-W2, -NX1, ZB, ZB + ND)
floor(-NX0, NX0, ZB, ZB + ND)
floor(NX1, W2, ZB, ZB + ND)
floor(-W2, W2, ZB + ND, OZ0)
floor(-W2, -OX, OZ0, OZ1)
floor(OX, W2, OZ0, OZ1)
floor(-W2, W2, OZ1, ZW)


def face(pts, normal, col):                   # a flat quad turned to face `normal`
    m.polygon(list(pts), col, normal=normal)


# connector opening: dark walls, the board edge with its contacts at the top
face(((-OX, 0.0, OZ0), (-OX, OH, OZ0), (OX, OH, OZ0), (OX, 0.0, OZ0)), (0, 0, 1), SLOT)  # wall facing +Z
face(((OX, 0.0, OZ1), (OX, OH, OZ1), (-OX, OH, OZ1), (-OX, 0.0, OZ1)), (0, 0, -1), SLOT)  # wall facing -Z
face(((-OX, 0.0, OZ1), (-OX, OH, OZ1), (-OX, OH, OZ0), (-OX, 0.0, OZ0)), (1, 0, 0), SLOT)  # wall facing +X
face(((OX, 0.0, OZ0), (OX, OH, OZ0), (OX, OH, OZ1), (OX, 0.0, OZ1)), (-1, 0, 0), SLOT)  # wall facing -X
face(((-OX, OH, OZ0), (OX, OH, OZ0), (OX, OH, OZ1), (-OX, OH, OZ1)), (0, -1, 0), SLOT)  # ceiling, faces -Y
face(((-3.0, OH - 0.02, -0.02), (3.0, OH - 0.02, -0.02), (3.0, OH - 0.02, 0.18), (-3.0, OH - 0.02, 0.18)), (0, -1, 0), CONTACT)
# the locking notches: open to the bottom and the back
for sx in (-1, 1):
    xa, xb = sorted((sx * NX0, sx * NX1))
    zi = ZB + ND
    face(((xa, NH, ZB), (xa, NH, zi), (xb, NH, zi), (xb, NH, ZB)), (0, -1, 0), SLOT)  # ceiling, faces -Y
    face(((xa, 0.0, zi), (xb, 0.0, zi), (xb, NH, zi), (xa, NH, zi)), (0, 0, -1), SLOT)  # inner wall, faces -Z
    face(((xa, 0.0, ZB), (xa, 0.0, zi), (xa, NH, zi), (xa, NH, ZB)), (1, 0, 0), SLOT)  # faces +X
    face(((xb, 0.0, zi), (xb, 0.0, ZB), (xb, NH, ZB), (xb, NH, zi)), (-1, 0, 0), SLOT)  # faces -X

# ---- raised central front panel (its back sits on the body front)
m.box(-PX, 0.0, ZW, PX, H, ZF, SHELL_LT, faces={'back': None})

# ---- the label = picture area at the top of the panel
LX, LY0, LY1 = 4.0, 4.85, 8.35
m.image_xy(-LX, LY0, LX, LY1, ZF, fallback=LABEL, lift=0.03)

# ---- recessed U below the label, open at the bottom, with the centre tongue
UX, UY, TX, TY, UR = 3.95, 3.6, 1.15, 3.25, 0.35
UB = 0.04                                     # keep the decal off the bottom edge
u_out = [(-UX, UB), (-TX, UB), (-TX, TY), (TX, TY), (TX, UB), (UX, UB),
         (UX, UY - UR), (UX - UR * 0.3, UY - UR * 0.3), (UX - UR, UY),
         (-UX + UR, UY), (-UX + UR * 0.3, UY - UR * 0.3), (-UX, UY - UR)]
m.decal_xy(u_out, ZF, RECESS, lift=0.03)

# ---- grip grooves across both wings: six slats per wing
GW = 0.13
for k in range(1, 6):
    y = H * k / 6.0
    for x0, x1 in ((-W2, -PX), (PX, W2)):
        m.decal_xy([(x0, y - GW), (x1, y - GW), (x1, y + GW * 0.3), (x0, y + GW * 0.3)], ZW, GROOVE, lift=0.03)

# ---- screws at the bottom of the wings
for sx in (-1, 1):
    cx, cy, rs = sx * 5.42, 0.72, 0.2
    pts = [(cx + rs * math.cos(math.radians(60 * i)), cy + rs * math.sin(math.radians(60 * i))) for i in range(6)]
    m.decal_xy(pts, ZW, SCREW, lift=0.03)

# ---- back: horizontal ribs across the whole width, the dark sticker
ZBK = ZB - 0.02
SX, SY0, SY1 = 3.6, 3.3, 5.7


def back_strip(x0, x1, y0, y1, col):
    m.polygon([(x0, y0, ZBK), (x1, y0, ZBK), (x1, y1, ZBK), (x0, y1, ZBK)], col, normal=(0, 0, -1))


m.polygon([(-SX, SY0, ZBK), (SX, SY0, ZBK), (SX, SY1, ZBK), (-SX, SY1, ZBK)], STICKER, normal=(0, 0, -1))
for k in range(8):
    y = 1.5 + 0.85 * k
    y0, y1 = y - 0.06, y + 0.06
    if SY0 - 0.1 < y < SY1 + 0.1:          # passes behind the sticker: two pieces
        back_strip(-W2 + 0.15, -SX, y0, y1, GROOVE)
        back_strip(SX, W2 - 0.15, y0, y1, GROOVE)
    else:
        back_strip(-W2 + 0.15, W2 - 0.15, y0, y1, GROOVE)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
