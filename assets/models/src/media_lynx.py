# SPDX-License-Identifier: GPL-3.0-or-later
"""Atari Lynx game card, standing upright, label to +Z.

Real size ~5.4 x 4.5 x 0.3 cm. Signature features: the thin, almost square
black card, the curved lip along the top edge that curls over to the back
(the grip used to pull the card out of the slot), the big label filling most
of the front with a coloured title band near the top and artwork below, and
the row of gold contacts along the bottom edge of the back.

The shell is a side profile extruded across the width; its flat front and
back faces are built as mosaics of non-overlapping pieces (label, contacts)
instead of decals, so nothing fights with the face beneath it.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model, _area2

SHELL = (64, 64, 72)         # black card plastic
PAPER = (232, 228, 214)      # label paper border
BAND = (206, 40, 36)         # title band
SKY = (56, 96, 200)          # artwork, upper part
GROUND = (240, 160, 40)      # artwork, lower part
GOLD = (214, 172, 64)        # contacts
GAP = (20, 20, 24)           # between the contacts

W = 5.4
X0, X1 = -W / 2, W / 2
ZF, ZB = 0.15, -0.15         # front / back of the card
YF = 4.15                    # where the flat front ends (the top rounds over)
YB = 3.7                     # where the flat back ends (the lip bulges back)

# side profile (z, y): flat card, lip curling over the top towards the back
PROFILE = [(ZF, 0.0), (ZF, YF), (0.12, 4.33), (0.03, 4.45), (-0.12, 4.5),
           (-0.28, 4.47), (-0.40, 4.36), (-0.46, 4.18), (-0.43, 3.97),
           (-0.32, 3.80), (ZB, YB), (ZB, 0.0)]

m = Model('lynx', 'media')

# ---- side faces
m.extrude_yz(PROFILE, X0, X1, SHELL, side=False)

# ---- the profile's edges across the width (flat front / back as mosaics)
pts = list(PROFILE)
if _area2([(-z, y) for z, y in pts]) < 0:
    pts.reverse()                                   # CCW seen from +X


def front_rect(x0, y0, x1, y1, col):
    m.quad((x0, y0, ZF), (x1, y0, ZF), (x1, y1, ZF), (x0, y1, ZF), col)


def back_rect(x0, y0, x1, y1, col):
    m.quad((x1, y0, ZB), (x0, y0, ZB), (x0, y1, ZB), (x1, y1, ZB), col)


def front_mosaic():
    LX0, LX1 = -2.5, 2.5          # label edges
    MX0, MX1 = -2.35, 2.35        # artwork edges (paper margins beside)
    front_rect(X0, 0, LX0, YF, SHELL)
    front_rect(LX1, 0, X1, YF, SHELL)
    rows = [  # y0, y1, colour of the artwork column (None = full-width colour given after)
        (0.0, 0.3, SHELL, True),
        (0.3, 0.45, PAPER, True),
        (0.45, 2.95, None, False),
        (2.95, 3.1, PAPER, True),
        (3.1, 3.6, BAND, True),
        (3.6, 3.72, PAPER, True),
        (3.72, YF, SHELL, True),
    ]
    for y0, y1, col, full in rows:
        if full:
            front_rect(LX0, y0, LX1, y1, col)
        else:
            front_rect(LX0, y0, MX0, y1, PAPER)
            # artwork: a hill rising into the sky (two coplanar pieces)
            hill = [(MX0, 1.35), (-0.9, 1.35), (0.3, 2.2), (1.3, 1.55), (MX1, 1.55)]
            m.polygon([(x, y, ZF) for x, y in [(MX0, y0), (MX1, y0)] + hill[::-1]],
                      GROUND, normal=(0, 0, 1))
            m.polygon([(x, y, ZF) for x, y in hill + [(MX1, y1), (MX0, y1)]],
                      SKY, normal=(0, 0, 1))
            front_rect(MX1, y0, LX1, y1, PAPER)


def back_mosaic():
    CX0, CX1 = -2.2, 2.2          # contact row
    CY0, CY1 = 0.06, 0.6
    back_rect(X0, 0, X1, CY0, SHELL)
    back_rect(X0, CY1, X1, YB, SHELL)
    back_rect(X0, CY0, CX0, CY1, SHELL)
    back_rect(CX1, CY0, X1, CY1, SHELL)
    n = 10                        # pads, with dark gaps between
    pitch = (CX1 - CX0) / n
    for i in range(n):
        xa = CX0 + i * pitch
        back_rect(xa, CY0, xa + pitch * 0.7, CY1, GOLD)
        back_rect(xa + pitch * 0.7, CY0, xa + pitch, CY1, GAP)


for i in range(len(pts)):
    (za, ya), (zb, yb) = pts[i], pts[(i + 1) % len(pts)]
    if za == zb == ZF:
        front_mosaic()
    elif za == zb == ZB:
        back_mosaic()
    else:
        m.quad((X1, ya, za), (X0, ya, za), (X0, yb, zb), (X1, yb, zb), SHELL)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
