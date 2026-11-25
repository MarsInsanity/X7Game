# SPDX-License-Identifier: GPL-3.0-or-later
"""Atari Lynx (first model): a big black landscape handheld with large
rounded grips that reach lower than the middle, a raised dark bezel with the
screen in the centre, a round D-pad well on the left with ON/OFF above it,
two diagonal pairs of A/B buttons on the right (the second pair is for
left-handed play, turned upside down), the Option 1 / Pause / Option 2 row
under the screen, speaker slots, and thick battery bulges behind the grips.
Real size about 27.3 x 10.8 x 4.3 cm. Stands upright, screen facing +Z."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (56, 56, 62)
BODY_EDGE = (36, 36, 40)
BEZEL = (18, 18, 20)
SCREEN = (58, 92, 104)
SHINE = (110, 150, 160)
WELL = (10, 10, 12)
DPAD = (92, 92, 100)
BUTTON = (120, 120, 128)
BUTTON_SIDE = (66, 66, 72)
SMALL = (150, 150, 158)
LED = (230, 50, 30)
SLOT = (8, 8, 10)

W, H = 27.3, 10.8
ZF, ZB = 1.3, -0.9          # main body front / back (middle part)
ZG = -3.0                   # back of the battery bulges behind the grips
BEVEL = 0.4


def ring(cx, cy, r, n, a0=0.0):
    return [(cx + r * math.cos(2 * math.pi * i / n + a0), cy + r * math.sin(2 * math.pi * i / n + a0))
            for i in range(n)]


def body_outline(inset=0.0):
    """Front silhouette, counter-clockwise from +Z: flat top, big rounded
    ends, grips reaching the table, the middle of the bottom edge raised."""
    d = inset
    pts = []
    # right end: from the bottom of the grip round up to the top corner
    rb, rt = 4.6 - d, 3.0 - d
    cx, cy = W / 2 - 4.6, 4.6
    for s in range(5):                      # bottom right arc 270 -> 360
        a = math.radians(270 + 90 * s / 4)
        pts.append((cx + rb * math.cos(a), cy + rb * math.sin(a)))
    cx, cy = W / 2 - 3.0, H - 3.0
    for s in range(1, 4):                   # top right arc 0 -> 90 (skip 0, close to last)
        a = math.radians(90 * s / 3)
        pts.append((cx + rt * math.cos(a), cy + rt * math.sin(a)))
    # mirror for the left end
    right = pts
    left = [(-x, y) for x, y in reversed(right)]
    # bottom middle: raised edge between the grips
    mid = [(-6.2 + d * 0.3, 0.75 + d), (6.2 - d * 0.3, 0.75 + d)]
    out = right + left
    # left ends at bottom-left grip (x ~ -cx, y ~ d), then the raised middle
    return out + mid


def loft(m, a, za, b, zb, color):
    n = len(a)
    for i in range(n):
        j = (i + 1) % n
        m.quad((b[i][0], b[i][1], zb), (a[i][0], a[i][1], za),
               (a[j][0], a[j][1], za), (b[j][0], b[j][1], zb), color)


m = Model('lynx', 'console')

# ---- main body with a chamfered front edge
outer = body_outline(0.0)
inner = body_outline(BEVEL)
zc = ZF - BEVEL
m.extrude_xy(outer, ZB, zc, BODY, front=False)
loft(m, outer, zc, inner, ZF, BODY_EDGE)
m.polygon([(x, y, ZF) for x, y in inner], BODY, normal=(0, 0, 1))

# ---- thick battery / grip bulges on the back of both ends, tapering back
def bulge(sx, r, xin, ylo, yhi, yin):
    cx, cy = 13.65 - 4.6, 4.6
    pts = []
    for s in range(7):
        a = math.radians(-90 + 180 * s / 6)
        pts.append((cx + r * math.cos(a), max(cy + r * math.sin(a), ylo)))
    pts += [(xin, yhi), (xin, yin)]   # inner foot follows the raised bottom edge
    pts = [(x * sx, y) for x, y in pts]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts)))
    return pts if area > 0 else pts[::-1]


for sx in (-1, 1):
    big = bulge(sx, 4.3, 7.2, 0.0, 8.9, 0.55)
    small = bulge(sx, 3.5, 8.0, 0.8, 8.1, 0.8)
    loft(m, small, ZG, big, ZB, BODY)
    m.polygon([(x, y, ZG) for x, y in small], BODY_EDGE, normal=(0, 0, -1))

# ---- raised screen bezel, screen and glare
m.extrude_xy(Model.rounded_rect(-5.9, 1.6, 5.9, 9.9, 0.9, 2), ZF, ZF + 0.25, BEZEL, back=False)
zb = ZF + 0.25
m.decal_xy([(-3.9, 3.5), (3.9, 3.5), (3.9, 8.5), (-3.9, 8.5)], zb, SCREEN, lift=0.03)
m.decal_xy([(-3.9, 7.0), (-2.4, 8.5), (-1.6, 8.5), (-3.9, 6.2)], zb, SHINE, lift=0.06)

# ---- Option 1 / Pause / Option 2 under the screen
for bx in (-2.2, 0.0, 2.2):
    m.box(bx - 0.45, 2.15, zb, bx + 0.45, 2.55, zb + 0.15, BUTTON_SIDE, faces={'back': None, 'front': SMALL})

# ---- D-pad: dark round well with a grey cross
dx, dy = -9.7, 5.0
m.decal_xy(ring(dx, dy, 2.1, 12), ZF, WELL, lift=0.03)
a, b = 0.5, 1.6
cross = [(a, -b), (a, -a), (b, -a), (b, a), (a, a), (a, b), (-a, b), (-a, a), (-b, a), (-b, -a), (-a, -a), (-a, -b)]
m.extrude_xy([(dx + x, dy + y) for x, y in cross], ZF, ZF + 0.45, DPAD, back=False)

# ---- ON / OFF buttons and the power light above the D-pad
for bx in (-11.0, -8.6):
    m.box(bx - 0.5, 8.3, ZF, bx + 0.5, 8.75, ZF + 0.15, BUTTON_SIDE, faces={'back': None, 'front': SMALL})
m.decal_xy([(-7.3, 8.35), (-6.9, 8.35), (-6.9, 8.7), (-7.3, 8.7)], ZF, LED, lift=0.03)

# ---- two pairs of A/B buttons on the right (upper and lower)
for bx, by in ((8.6, 6.6), (10.6, 7.9), (8.6, 2.9), (10.6, 4.2)):
    m.cylinder_z(bx, by, 0.85, ZF, ZF + 0.4, BUTTON_SIDE, segments=8, front=BUTTON, back=False)

# ---- speaker slots under the D-pad
for k in range(4):
    ox = -11.2 + k * 0.6
    m.decal_xy([(ox, 1.4), (ox + 0.25, 1.4), (ox + 0.25, 2.5), (ox, 2.5)], ZF, WELL, lift=0.03)

# ---- cartridge slot and ports on the top edge
m.decal_xz([(4.6, -0.75), (10.2, -0.75), (10.2, -0.2), (5.5, -0.2)], H, SLOT, lift=0.03)
m.decal_xz([(-10.5, -0.55), (-9.6, -0.55), (-9.6, 0.15), (-10.5, 0.15)], H, SLOT, lift=0.03)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
