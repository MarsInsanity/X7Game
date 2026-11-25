# SPDX-License-Identifier: GPL-3.0-or-later
"""Famicom Disk System disk card: the yellow double-sided disk standing
upright like on a shelf, side A facing +Z."""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

YELLOW = (244, 200, 30)
EDGE = (196, 150, 16)        # shell edges: darker so the card reads as solid
EMBOSS = (214, 166, 22)      # recessed brand band at the bottom (no text)
LABEL = (242, 238, 222)
BAND_R = (210, 40, 40)
BAND_B = (40, 70, 170)
RIM = (150, 108, 10)         # window bevel
MEDIA = (92, 52, 26)         # exposed brown magnetic disk
HUB = (176, 178, 188)
HUB_IN = (64, 64, 72)

W, H, T = 7.6, 9.0, 0.5
X0, X1 = -W / 2, W / 2
Z0, Z1 = -T / 2, T / 2

m = Model('fds', 'media')

# shell outline (XY): chamfered corners, two notches on each side near the top
c = 0.35                  # corner chamfer
ny0, ny1, nd = 6.9, 7.5, 0.3   # side notch height range and depth
outline = [
    (X0 + c, 0), (X1 - c, 0), (X1, c),
    (X1, ny0), (X1 - nd, ny0), (X1 - nd, ny1), (X1, ny1),
    (X1, H - c), (X1 - c, H), (X0 + c, H), (X0, H - c),
    (X0, ny1), (X0 + nd, ny1), (X0 + nd, ny0), (X0, ny0),
    (X0, c),
]
m.extrude_xy(outline, Z0, Z1, YELLOW, front=False, back=False, side=EDGE)
# the big faces are built from horizontal bands so every triangle stays
# small and well shaped (long thin slivers from a concave outline make the
# depth of the decals on top of them unreliable)
bands = [
    [(X0 + c, 0), (X1 - c, 0), (X1, c), (X0, c)],
    [(X0, c), (X1, c), (X1, 3.4), (X0, 3.4)],
    [(X0, 3.4), (X1, 3.4), (X1, ny0), (X1 - nd, ny0), (X0 + nd, ny0), (X0, ny0)],
    [(X0 + nd, ny0), (X1 - nd, ny0), (X1 - nd, ny1), (X0 + nd, ny1)],
    [(X0, ny1), (X0 + nd, ny1), (X1 - nd, ny1), (X1, ny1), (X1, H - c), (X0, H - c)],
    [(X0, H - c), (X1, H - c), (X1 - c, H), (X0 + c, H)],
]
for b in bands:
    m.polygon([(x, y, Z1) for x, y in b], YELLOW, normal=(0, 0, 1))
    m.polygon([(x, y, Z0) for x, y in b], YELLOW, normal=(0, 0, -1))


def stadium(cx, cy, w, h, seg=3):
    """horizontal rounded slot outline"""
    r = h / 2
    pts = []
    for k in range(seg + 1):                       # right cap
        a = -math.pi / 2 + math.pi * k / seg
        pts.append((cx + w / 2 - r + r * math.cos(a), cy + r * math.sin(a)))
    for k in range(seg + 1):                       # left cap
        a = math.pi / 2 + math.pi * k / seg
        pts.append((cx - w / 2 + r + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def circle(cx, cy, r, seg):
    return [(cx + r * math.cos(2 * math.pi * k / seg + math.pi / seg),
             cy + r * math.sin(2 * math.pi * k / seg + math.pi / seg)) for k in range(seg)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def side_details(sign):
    """decals for one face: sign +1 = front (side A), -1 = back (side B,
    seen mirrored). Decals never overlap each other (rings and strips are
    built side by side), so nothing can z-fight."""
    z = Z1 if sign > 0 else Z0
    lift = 0.04

    def P(x, y):
        return (x, y, z + lift * sign)

    def d(pts, col):
        m.polygon([P(x, y) for x, y in pts], col, normal=(0, 0, sign))

    def ring(outer, inner, col):
        n = len(outer)
        for k in range(n):
            a, b = outer[k], outer[(k + 1) % n]
            ci, di = inner[(k + 1) % n], inner[k]
            m.polygon([P(*a), P(*b), P(*ci), P(*di)], col, normal=(0, 0, sign))

    # label on the upper part: white strips with a red band near the top
    # and a thin blue (side A) / red (side B) rule near the bottom
    lx0, lx1 = -3.0, 3.0
    strips = [(5.7, 6.05, LABEL), (6.05, 6.25, BAND_B if sign > 0 else BAND_R),
              (6.25, 7.85, LABEL), (7.85, 8.25, BAND_R), (8.25, 8.6, LABEL)]
    for y0, y1, col in strips:
        d(rect(lx0, y0, lx1, y1), col)
    # centre hub: bevel ring, silver hub, dark spindle hole
    hx, hy = 0.0, 4.15
    ring(circle(hx, hy, 0.95, 10), circle(hx, hy, 0.78, 10), RIM)
    ring(circle(hx, hy, 0.78, 10), circle(hx, hy, 0.3, 10), HUB)
    d(circle(hx, hy, 0.3, 10), HUB_IN)
    # exposed disk window below the hub, with a bevel ring
    ring(stadium(0.0, 2.2, 5.0, 1.0), stadium(0.0, 2.2, 4.7, 0.72), RIM)
    d(stadium(0.0, 2.2, 4.7, 0.72), MEDIA)
    # recessed band for the embossed brand name along the bottom edge
    d(rect(-2.6, 0.35, 2.6, 1.15), EMBOSS)


side_details(+1)
side_details(-1)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
