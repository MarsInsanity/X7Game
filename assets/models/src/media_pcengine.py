# SPDX-License-Identifier: GPL-3.0-or-later
"""TurboGrafx-16 TurboChip / PC Engine HuCard: a thin credit-card-sized
card (54 x 85 x 2.8 mm) standing on its contact edge, label facing +Z.

The front and back faces are built as a mosaic of non-overlapping coplanar
cells (rim, label frame, colour bands, contact fingers) instead of stacked
decals: on a card this thin, stacked decals over big triangles z-fight in
an affine-depth rasteriser. Plain colour areas only: no text or artwork."""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

W, H, T = 5.4, 8.5, 0.28          # portrait, contacts at the bottom (y = 0)
X0, X1 = -W / 2, W / 2
Z0, Z1 = -T / 2, T / 2
R = 0.45                          # top corner radius
YR = H - R                        # where the rounded top starts

CARD = (214, 216, 222)            # pale silver-white plastic
EDGE = (150, 152, 160)            # card edges
BACK = (184, 186, 194)
PANEL = (128, 130, 140)           # back: moulded panel
BORDER = (110, 114, 128)          # silver label frame
HEADER = (240, 112, 24)           # orange header band
HEADER2 = (20, 20, 28)            # black strip under the header
ART = (40, 72, 176)               # artwork: deep blue sky
ART2 = (60, 168, 72)              # artwork: green ground
SUN = (248, 216, 48)              # artwork: yellow highlight
FOOT = (200, 32, 40)              # red footer band
SLOT = (36, 36, 42)               # contact window
GOLD = (224, 180, 56)             # contact fingers

m = Model('pcengine', 'media')


def top_corners():
    """Rounded top edge, from (X1, YR) round to (X0, YR)."""
    pts = []
    for cx, a0 in ((X1 - R, 0), (X0 + R, 90)):
        for s in range(4):
            a = math.radians(a0 + 30 * s)
            pts.append((cx + R * math.cos(a), YR + R * math.sin(a)))
    return pts


# card edges (the faces are built below)
m.extrude_xy([(X0, 0.0), (X1, 0.0)] + top_corners(), Z0, Z1, CARD, front=False, back=False, side=EDGE)


def lab(*inner):
    """A label row: card rim, frame, inner cells, frame, card rim."""
    return [(-2.35, CARD), (-2.2, BORDER)] + list(inner) + [(2.35, BORDER), (X1, CARD)]


# contact fingers: 10 gold fingers with dark gaps in the window -2.3..2.3
fingers = [(-2.3, CARD)]
pitch = 4.2 / 10
for i in range(10):
    cx = -2.1 + pitch * (i + 0.5)
    fingers += [(cx - pitch * 0.3, SLOT), (cx + pitch * 0.3, GOLD)]
fingers += [(2.3, SLOT), (X1, CARD)]
window = [(-2.3, CARD), (2.3, SLOT), (X1, CARD)]

# sun: an octagon in the sky, cut out of the sky cells
SX, SY, SR = 0.9, 5.6, 0.55
front_rows = [
    (0.0, 0.12, [(X1, CARD)]),
    (0.12, 0.2, window),
    (0.2, 1.05, fingers),
    (1.05, 1.15, window),
    (1.15, 1.55, [(X1, CARD)]),
    (1.55, 1.7, lab((2.2, BORDER))),
    (1.7, 2.2, lab((2.2, FOOT))),
    (2.2, 2.35, lab((2.2, BORDER))),
    (2.35, 3.4, lab((2.2, ART2))),
    (3.4, SY - SR, lab((2.2, ART))),
    (SY - SR, SY + SR, lab((SX - SR, ART), (SX + SR, None), (2.2, ART))),
    (SY + SR, 6.85, lab((2.2, ART))),
    (6.85, 7.0, lab((2.2, BORDER))),
    (7.0, 7.25, lab((2.2, HEADER2))),
    (7.25, 7.9, lab((2.2, HEADER))),
    (7.9, 8.05, lab((2.2, BORDER))),
    (8.05, YR, [(X1, CARD)]),
]


def face_rows(z, normal, rows):
    for y0, y1, cells in rows:
        x = X0
        for xe, col in cells:
            if col is not None:
                m.polygon([(x, y0, z), (xe, y0, z), (xe, y1, z), (x, y1, z)], col, normal=normal)
            x = xe
    m.polygon([(x, y, z) for x, y in top_corners()], CARD if normal[2] > 0 else BACK, normal=normal)


face_rows(Z1, (0, 0, 1), front_rows)

# the sun's square: octagon plus four sky darts in the corners
octo = [(SX + SR * math.cos(math.pi * i / 4), SY + SR * math.sin(math.pi * i / 4)) for i in range(8)]
m.polygon([(x, y, Z1) for x, y in octo], SUN, normal=(0, 0, 1))
for k in range(4):
    a, d, b = octo[2 * k], octo[2 * k + 1], octo[(2 * k + 2) % 8]
    corner = (SX + SR * (1 if k in (0, 3) else -1), SY + SR * (1 if k in (0, 1) else -1))
    m.polygon([(x, y, Z1) for x, y in (a, corner, b, d)], ART, normal=(0, 0, 1))

# back: plain card with the contact window and a moulded panel
back_rows = [
    (0.0, 0.12, [(X1, BACK)]),
    (0.12, 1.15, [(-2.3, BACK), (2.3, SLOT), (X1, BACK)]),
    (1.15, 3.0, [(X1, BACK)]),
    (3.0, 6.6, [(-1.6, BACK), (1.6, PANEL), (X1, BACK)]),
    (6.6, YR, [(X1, BACK)]),
]
face_rows(Z0, (0, 0, -1), back_rows)

print(m.stats())
m.save()
