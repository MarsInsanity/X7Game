# SPDX-License-Identifier: GPL-3.0-or-later
"""TurboGrafx-CD game disc in its CD jewel case, standing upright, front to +Z.

Real size ~14.2 x 12.5 x 1.0 cm. Signature features: the clear case (light
blue-grey edges and a raised frame around the lid), the ridged hinge strip
down the left side, the black tray seen through the lid, the silver 12 cm
disc with the system's orange label (black ring, silver inner ring, clear
hub, centre hole), the black cover header band across the top of the front
with an orange stripe (the TurboGrafx look), and the black spine with an
orange band.
"""
import math
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

CLEAR = (178, 190, 204)      # clear plastic edges / lid frame
HINGE = (214, 222, 232)      # hinge strip (thicker clear plastic, catches light)
HINGE_D = (120, 132, 148)    # hinge ridges
TRAY = (30, 30, 36)          # dark tray seen through the lid
SILVER = (226, 230, 238)     # disc surface
LABEL = (240, 120, 24)       # orange disc label
LABEL2 = (16, 16, 18)        # black ring on the label
HUB = (128, 136, 150)        # clear hub of the disc
HOLE = (8, 8, 10)            # centre hole
BAND = (12, 12, 14)          # black cover header band
ORANGE = (250, 140, 30)      # orange stripe under / in the band
COVER = (60, 66, 110)        # back insert artwork area
SPINE = (24, 24, 28)         # spine / back insert

W, H = 14.2, 12.5
X0, X1 = -W / 2, W / 2
ZB, ZF = -0.5, 0.3           # case body back / tray face (recessed so the disc decals sit inside the lid frame)
ZL = 0.5                     # raised lid frame / hinge front
HW = 1.0                     # hinge strip width on the left
F = 0.35                     # lid frame width

m = Model('pcenginecd', 'media')

# case body: dark tray face on the front, clear sides, black spine on the left
m.box(X0, 0, ZB, X1, H, ZF, CLEAR, faces={'front': TRAY, 'back': SPINE, 'left': SPINE})

# raised clear lid frame around the front
m.box(X0 + HW, H - F, ZF, X1, H, ZL, CLEAR, faces={'back': None})
m.box(X0 + HW, 0, ZF, X1, F, ZL, CLEAR, faces={'back': None})
m.box(X1 - F, F, ZF, X1, H - F, ZL, CLEAR, faces={'back': None, 'top': None, 'bottom': None})

# hinge strip down the left edge, with ridges at the hinge knuckles
m.box(X0, 0, ZF, X0 + HW, H, ZL + 0.04, HINGE, faces={'back': None})
for y in (0.8, 1.5, H - 1.75, H - 1.05):
    m.decal_xy([(X0 + 0.15, y), (X0 + HW - 0.15, y), (X0 + HW - 0.15, y + 0.25), (X0 + 0.15, y + 0.25)],
               ZL + 0.04, HINGE_D, lift=0.02)


def circle(cx, cy, r, n):
    return [(cx + r * math.cos(2 * math.pi * i / n + math.pi / n),
             cy + r * math.sin(2 * math.pi * i / n + math.pi / n)) for i in range(n)]


def clip_below(poly, ytop):
    """Clip a convex outline to y <= ytop (so decals never overlap the band:
    stacked decals over long thin triangles z-fight)."""
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ina, inb = a[1] <= ytop, b[1] <= ytop
        if ina:
            out.append(a)
        if ina != inb:
            t = (ytop - a[1]) / (b[1] - a[1])
            out.append((a[0] + t * (b[0] - a[0]), ytop))
    return out


# the disc behind the lid; its top runs under the header band (clipped there)
BY = H - 2.3                                   # bottom of the header band
DCX, DCY = (X0 + HW + X1 - F) / 2, (BY + F) / 2 + 0.35
m.decal_xy(clip_below(circle(DCX, DCY, 5.6, 20), BY), ZF, SILVER, lift=0.02)
m.decal_xy(clip_below(circle(DCX, DCY, 4.6, 20), BY), ZF, LABEL, lift=0.05)
m.decal_xy(circle(DCX, DCY, 2.5, 14), ZF, LABEL2, lift=0.08)
m.decal_xy(circle(DCX, DCY, 2.05, 14), ZF, SILVER, lift=0.11)
m.decal_xy(circle(DCX, DCY, 1.5, 12), ZF, HUB, lift=0.14)
m.decal_xy(circle(DCX, DCY, 0.72, 8), ZF, HOLE, lift=0.17)

# black header band across the top of the front cover with an orange stripe
# (side by side at one depth, not stacked, so nothing can z-fight)
for ya, yb, col in ((BY, BY + 0.35, BAND), (BY + 0.35, BY + 0.7, ORANGE), (BY + 0.7, H - F, BAND)):
    m.decal_xy([(X0 + HW, ya), (X1 - F, ya), (X1 - F, yb), (X0 + HW, yb)], ZF, col, lift=0.04)

# back insert: artwork panel and the black band with orange stripe
ZK = ZB - 0.02
m.polygon([(X1 - 0.7, 0.9, ZK), (X0 + 1.2, 0.9, ZK), (X0 + 1.2, H - 3.0, ZK), (X1 - 0.7, H - 3.0, ZK)],
          COVER, normal=(0, 0, -1))
m.polygon([(X1 - 0.08, H - 2.2, ZK), (X0 + 0.08, H - 2.2, ZK), (X0 + 0.08, H - 1.8, ZK), (X1 - 0.08, H - 1.8, ZK)],
          ORANGE, normal=(0, 0, -1))
# spine: orange band near the top of the black spine
m.polygon([(X0 - 0.02, H - 2.4, ZB + 0.05), (X0 - 0.02, H - 2.4, ZF - 0.05),
           (X0 - 0.02, H - 1.6, ZF - 0.05), (X0 - 0.02, H - 1.6, ZB + 0.05)], ORANGE, normal=(-1, 0, 0))

print(m.stats())
m.save()
