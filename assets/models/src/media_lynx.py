# SPDX-License-Identifier: GPL-3.0-or-later
"""Atari Lynx game card, standing upright, label to +Z.

Real size 5.4 wide x 4.5 tall, the card itself 0.3 thick. Signature
features: the thin, almost square black card, the rounded lip along the top
edge that bulges out to the back (the grip used to pull the card out of the
slot; it is all that shows of an inserted card), the big paper label filling
most of the front, and the row of gold contacts along the bottom edge of the
back.

The label is the game's picture: one image area, a paper sticker 0.02 thick
standing on the front face (its own little closed slab, so there is no
surface under it to fight with). The front face around it is a mosaic of
non-overlapping pieces, the back likewise around the contacts.

Insertion: the flat part of the card (y = 0 .. YB, x = -2.7 .. 2.7,
z = -0.15 .. 0.15, sticker to z = 0.17) slides into the slot contacts first
(y = 0 leading); only the lip stays out.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model, _area2

SHELL = (72, 72, 78)         # black card plastic
LIP = (56, 56, 62)           # the lip (a touch darker, reads as a separate grip)
PAPER = (226, 222, 208)      # label paper (picture fallback and sticker edge)
GOLD = (214, 172, 64)        # contacts
GAP = (16, 16, 20)           # between the contacts / recess

W = 5.4
X0, X1 = -W / 2, W / 2
ZF, ZB = 0.15, -0.15         # front / back of the card
YF = 4.05                    # where the flat front ends (the top rounds over)
YB = 3.75                    # where the flat back ends (the lip bulges back)

# label (picture) on the front: nearly the full width, from just above the
# contacts to the bare plastic band under the lip
LX0, LX1 = -2.55, 2.55
LY0, LY1 = 0.82, 3.62
# gold contact fingers along the bottom of the front
CX0, CX1 = -2.35, 2.35
CY0, CY1 = 0.12, 0.70
NPAD = 14
LT = 0.02                    # sticker thickness

# side profile (z, y): flat card, lip rounding over the top and bulging back
PROFILE = [(ZF, 0.0), (ZF, YF), (0.12, 4.3), (0.02, 4.45), (-0.14, 4.5),
           (-0.30, 4.45), (-0.40, 4.30), (-0.42, 4.08),
           (-0.32, 3.86), (ZB, YB), (ZB, 0.0)]

m = Model('lynx', 'media')

# ---- side faces
m.extrude_yz(PROFILE, X0, X1, SHELL, side=False)

pts = list(PROFILE)
if _area2([(-z, y) for z, y in pts]) < 0:
    pts.reverse()                                   # CCW seen from +X


def front_rect(x0, y0, x1, y1, col, z=ZF):
    m.quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), col)


def back_rect(x0, y0, x1, y1, col, z=ZB):
    m.quad((x1, y0, z), (x0, y0, z), (x0, y1, z), (x1, y1, z), col)


def front_mosaic():
    # shell border around the label and the contact row
    front_rect(X0, 0, LX0, YF, SHELL)
    front_rect(LX1, 0, X1, YF, SHELL)
    front_rect(LX0, LY1, LX1, YF, SHELL)               # bare plastic under the lip
    front_rect(LX0, CY1, LX1, LY0, SHELL)              # strip between contacts and label
    front_rect(LX0, 0, LX1, CY0, SHELL)                # bottom edge
    front_rect(LX0, CY0, CX0, CY1, SHELL)
    front_rect(CX1, CY0, LX1, CY1, SHELL)
    # gold edge contacts (the card is a circuit board, fingers bare at the bottom)
    pitch = (CX1 - CX0) / NPAD
    for i in range(NPAD):
        xa = CX0 + i * pitch
        front_rect(xa, CY0, xa + pitch * 0.62, CY1, GOLD)
        front_rect(xa + pitch * 0.62, CY0, xa + pitch, CY1, GAP)
    # the label: a thin paper slab, its face the picture
    zt = ZF + LT
    m.image_xy(LX0, LY0, LX1, LY1, zt, fallback=PAPER, lift=0.0)
    m.quad((LX0, LY0, ZF), (LX1, LY0, ZF), (LX1, LY0, zt), (LX0, LY0, zt), PAPER)   # bottom edge
    m.quad((LX1, LY1, ZF), (LX0, LY1, ZF), (LX0, LY1, zt), (LX1, LY1, zt), PAPER)   # top edge
    m.quad((LX0, LY1, ZF), (LX0, LY0, ZF), (LX0, LY0, zt), (LX0, LY1, zt), PAPER)   # left edge
    m.quad((LX1, LY0, ZF), (LX1, LY1, ZF), (LX1, LY1, zt), (LX1, LY0, zt), PAPER)   # right edge


def back_mosaic():
    back_rect(X0, 0, X1, YB, SHELL)


for i in range(len(pts)):
    (za, ya), (zb, yb) = pts[i], pts[(i + 1) % len(pts)]
    if za == zb == ZF:
        front_mosaic()
    elif za == zb == ZB:
        back_mosaic()
    else:
        col = SHELL if ya < 0.01 and yb < 0.01 else LIP
        m.quad((X1, ya, za), (X0, ya, za), (X0, yb, zb), (X1, yb, zb), col)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
