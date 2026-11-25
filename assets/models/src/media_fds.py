# SPDX-License-Identifier: GPL-3.0-or-later
"""Famicom Disk System disk card (7.6 x 9.0 x 0.5 cm), standing upright like
on a shelf, side A facing +Z.

As on the real card: the head window (a narrow vertical slot) and the hub
sit in a U-shaped recess that runs from the top edge (the end that goes
into the drive first); the label recess (the game's picture) is below the
hub, and the embossed grip band runs along the bottom edge (the end that
stays out of the drive). Write-protect holes in the two top corners,
latch notches in both sides near the top, small steps near the bottom.

Insertion: lay the card flat, label up (rotate -90 degrees about X: the top
edge y = 9 goes to -Z), and slide it window end first into the drive."""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

YELLOW = (255, 198, 22)      # the shell
EDGE = (200, 136, 8)         # shell edges: darker so the card reads as solid
SHADE = (228, 158, 12)       # recessed areas (U recess, label recess, grip band)
HI = YELLOW                  # raised grip blocks (the embossed lettering, no text)
LABEL = (238, 232, 212)      # plain label: the picture's fallback, side B label
WINDOW = (92, 78, 60)        # exposed brown-grey magnetic disk
HUB = (236, 232, 218)        # off-white hub ring
METAL = (160, 162, 170)      # metal hub centre
HOLE = (34, 26, 12)          # spindle hole, write-protect holes

W, H, T = 7.6, 9.0, 0.5
X0, X1 = -W / 2, W / 2
Z0, Z1 = -T / 2, T / 2

m = Model('fds', 'media')

# ---------------------------------------------------------------- shell
c = 0.25                       # bottom corner chamfer
ct = 0.15                      # top corner chamfer
ny0, ny1, nd = 7.55, 8.1, 0.22     # latch notches near the top
sy0, sy1, sd = 1.2, 1.6, 0.12      # small steps near the bottom
outline = [
    (X0 + c, 0), (X1 - c, 0), (X1, c),
    (X1, sy0), (X1 - sd, sy0), (X1 - sd, sy1), (X1, sy1),
    (X1, ny0), (X1 - nd, ny0), (X1 - nd, ny1), (X1, ny1),
    (X1, H - ct), (X1 - ct, H), (X0 + ct, H), (X0, H - ct),
    (X0, ny1), (X0 + nd, ny1), (X0 + nd, ny0), (X0, ny0),
    (X0, sy1), (X0 + sd, sy1), (X0 + sd, sy0), (X0, sy0),
    (X0, c),
]
m.extrude_xy(outline, Z0, Z1, YELLOW, front=YELLOW, back=YELLOW, side=EDGE)


# ---------------------------------------------------------------- faces
def circle(cx, cy, r, seg, phase=0.5):
    return [(cx + r * math.cos(2 * math.pi * (k + phase) / seg),
             cy + r * math.sin(2 * math.pi * (k + phase) / seg)) for k in range(seg)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


HX, HY = 0.0, 5.1              # hub centre
UR = 1.55                      # half width of the U recess
LX0, LY0, LX1, LY1 = -2.85, 1.45, 2.85, 3.75    # label recess
IX0, IY0, IX1, IY1 = -2.72, 1.56, 2.72, 3.64    # the label (picture) in it


def side(sign):
    """the details of one face: sign +1 = side A (front, +Z), -1 = side B.
    Layers: recesses at 0.02 cm, things on them at 0.04, 0.05, 0.06."""
    z = Z1 if sign > 0 else Z0

    def d(pts, col, lift):
        # side B is seen from behind: mirror x so the layout matches side A
        m.polygon([(x * sign, y, z + lift * sign) for x, y in pts], col, normal=(0, 0, sign))

    # U-shaped recess from the top edge around the hub
    u = [(-UR, H - 0.02), (-UR, HY)]
    for k in range(1, 8):
        a = math.pi + math.pi * k / 8
        u.append((HX + UR * math.cos(a), HY + UR * math.sin(a)))
    u += [(UR, HY), (UR, H - 0.02)]
    d(u, SHADE, 0.02)
    # head window and hub
    d(rect(-0.36, 6.15, 0.36, 8.6), WINDOW, 0.04)
    d(circle(HX, HY, 0.78, 10), HUB, 0.04)
    d(circle(HX, HY, 0.38, 8), METAL, 0.05)
    d(circle(HX, HY, 0.13, 6, 0.0), HOLE, 0.06)
    # write-protect holes in the top corners
    for s in (-1, 1):
        d(rect(s * 3.35 - 0.17, 8.12, s * 3.35 + 0.17, 8.55), HOLE, 0.02)
    # label recess
    d(rect(LX0, LY0, LX1, LY1), SHADE, 0.02)
    if sign < 0:
        d(rect(IX0, IY0, IX1, IY1), LABEL, 0.04)
    # grip band with raised blocks (the embossed name, as plain blocks)
    d(rect(-3.5, 0.2, 3.5, 1.08), SHADE, 0.02)
    n, bw, gap = 8, 0.7, 0.14
    x = -(n * bw + (n - 1) * gap) / 2
    for k in range(n):
        d(rect(x, 0.32, x + bw, 0.96), HI, 0.04)
        x += bw + gap


side(+1)
side(-1)

# the picture: the label on side A, upright (u left to right, v bottom to top)
m.image_xy(IX0, IY0, IX1, IY1, Z1, fallback=LABEL, lift=0.04)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
