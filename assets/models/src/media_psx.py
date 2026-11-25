# SPDX-License-Identifier: GPL-3.0-or-later
"""PlayStation game disc in its CD jewel case, standing upright, front to +Z.

Real size ~14.2 x 12.5 x 1.0 cm. Signature features: the clear case (light
blue-grey edges and a raised frame around the lid), the ridged hinge strip
down the left side, the black vertical band down the left of the front cover
(the classic PlayStation cover layout) with four small coloured blocks at its
top, a light cover behind the lid, and the distinctive black-bottom disc: a
near-black data side with a silver inner ring, clear hub and centre hole.
The back carries the rear insert and the black spine.
"""
import math
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

CLEAR = (178, 190, 204)      # clear plastic edges / lid frame
HINGE = (214, 222, 232)      # hinge strip (thicker clear plastic, catches light)
HINGE_D = (120, 132, 148)    # hinge ridges
COVER = (196, 200, 206)      # light cover insert behind the lid
DISC = (40, 32, 56)          # black-bottom disc data side (slight purple sheen)
SILVER = (226, 230, 238)     # mirror ring around the hub
HUB = (140, 148, 162)        # clear hub of the disc
BAND = (14, 14, 16)          # black cover band / spine / centre hole
RED = (224, 40, 40)          # coloured blocks at the top of the band
YELLOW = (240, 200, 20)
GREEN = (30, 170, 90)
BLUE = (40, 90, 210)
BACK = (70, 80, 110)         # rear insert artwork area

W, H = 14.2, 12.5
X0, X1 = -W / 2, W / 2
ZB, ZF = -0.5, 0.42          # case body back / tray face
ZL = 0.5                     # raised lid frame / hinge front
HW = 1.0                     # hinge strip width on the left
F = 0.35                     # lid frame width
BW = 2.0                     # black cover band width
BX = X0 + HW + BW            # right edge of the band

m = Model('psx', 'media')

# case body: cover face on the front, clear sides, black spine on the left
m.box(X0, 0, ZB, X1, H, ZF, CLEAR, faces={'front': COVER, 'back': BAND, 'left': BAND})

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


def clip_right_of(poly, xmin):
    """Clip a convex outline to x >= xmin (the disc runs under the band, and
    stacked decals over long thin triangles z-fight, so keep them apart)."""
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ina, inb = a[0] >= xmin, b[0] >= xmin
        if ina:
            out.append(a)
        if ina != inb:
            t = (xmin - a[0]) / (b[0] - a[0])
            out.append((xmin, a[1] + t * (b[1] - a[1])))
    return out


# black vertical cover band down the left of the front, full height inside
# the frame, with four coloured blocks near its top (side by side at one depth)
YB = H - F - 2.2                     # bottom of the coloured blocks
m.decal_xy([(X0 + HW, F), (BX, F), (BX, YB), (X0 + HW, YB)], ZF, BAND, lift=0.06)
bh = 0.55
cols = (BLUE, GREEN, YELLOW, RED)   # bottom to top
for k, col in enumerate(cols):
    ya = YB + k * bh
    m.decal_xy([(X0 + HW, ya), (BX, ya), (BX, ya + bh), (X0 + HW, ya + bh)], ZF, BAND, lift=0.06)
    m.decal_xy([(X0 + HW + 0.45, ya + 0.1), (BX - 0.45, ya + 0.1), (BX - 0.45, ya + bh - 0.1),
                (X0 + HW + 0.45, ya + bh - 0.1)], ZF, col, lift=0.10)
yt = YB + 4 * bh
m.decal_xy([(X0 + HW, yt), (BX, yt), (BX, H - F), (X0 + HW, H - F)], ZF, BAND, lift=0.06)

# the black-bottom disc behind the lid, its left edge running under the band
DCX, DCY = X1 - F - 5.75, H / 2
m.decal_xy(clip_right_of(circle(DCX, DCY, 5.7, 22), BX), ZF, DISC, lift=0.06)
m.decal_xy(circle(DCX, DCY, 2.3, 14), ZF, SILVER, lift=0.10)
m.decal_xy(circle(DCX, DCY, 1.6, 12), ZF, HUB, lift=0.14)
m.decal_xy(circle(DCX, DCY, 0.72, 8), ZF, BAND, lift=0.18)

# back insert: artwork panel on the rear, with a black band down its left
ZK = ZB - 0.02
m.polygon([(X1 - 0.7, 0.9, ZK), (X0 + 2.6, 0.9, ZK), (X0 + 2.6, H - 0.9, ZK), (X1 - 0.7, H - 0.9, ZK)],
          BACK, normal=(0, 0, -1))
m.polygon([(X1 - 0.7, H - 2.0, ZK - 0.02), (X0 + 2.6, H - 2.0, ZK - 0.02), (X0 + 2.6, H - 1.6, ZK - 0.02),
           (X1 - 0.7, H - 1.6, ZK - 0.02)], COVER, normal=(0, 0, -1))
# spine: a light band near the top of the black spine
m.polygon([(X0 - 0.02, H - 2.4, ZB + 0.05), (X0 - 0.02, H - 2.4, ZF - 0.05),
           (X0 - 0.02, H - 1.6, ZF - 0.05), (X0 - 0.02, H - 1.6, ZB + 0.05)], COVER, normal=(-1, 0, 0))

print(m.stats())
m.save()
