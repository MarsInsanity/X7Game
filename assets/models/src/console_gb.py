# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly Nintendo Game Boy (original DMG) for the X7 Game frontend.

Real size about 9.0 x 14.8 x 3.2 cm. Stands upright, screen facing +Z.
Signature features: portrait grey brick with the big rounded bottom-right
corner, dark grey screen bezel with two coloured stripe lines, olive-green
screen, red power LED, black cross D-pad, two maroon A/B buttons on a
slant, two slanted grey Start/Select pills, diagonal speaker slots, the
groove line across the top, contrast and volume wheels on the sides and
the battery bulge on the back.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (198, 195, 188)       # warm light grey
BODY_DARK = (150, 148, 144)  # back battery cover / grooves
BEZEL = (76, 78, 94)         # dark blue-grey screen surround
SCREEN = (150, 168, 60)      # olive green LCD
STRIPE_A = (140, 28, 72)     # maroon line
STRIPE_B = (40, 46, 124)     # navy line
DPAD = (32, 32, 36)
AB = (168, 34, 92)           # maroon/magenta buttons
PILL = (112, 112, 124)       # Start / Select rubber
SLOT = (70, 70, 78)          # speaker slots, cartridge slot
LED = (230, 30, 30)
WHEEL = (96, 96, 106)

W, H = 9.0, 14.8
ZF, ZB = 1.45, -1.45          # front / back face of the main shell
m = Model('gb', 'console')


def arc(cx, cy, r, a0, a1, seg):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / seg)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / seg))) for i in range(seg + 1)]


def gb_outline(x0, y0, x1, y1, r_small, r_big, seg_small=2, seg_big=5):
    """Rounded rect with a big radius on the bottom-right corner (CCW)."""
    pts = []
    pts += arc(x1 - r_big, y0 + r_big, r_big, 270, 360, seg_big)       # bottom-right
    pts += arc(x1 - r_small, y1 - r_small, r_small, 0, 90, seg_small)  # top-right
    pts += arc(x0 + r_small, y1 - r_small, r_small, 90, 180, seg_small)  # top-left
    pts += arc(x0 + r_small, y0 + r_small, r_small, 180, 270, seg_small)  # bottom-left
    return pts


def rotated_rect(cx, cy, w, h, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    out = []
    for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def pill(cx, cy, length, width, deg, seg=2):
    """Stadium outline rotated by deg."""
    r = width / 2
    half = length / 2 - r
    pts = arc(half, 0, r, -90, 90, seg) + arc(-half, 0, r, 90, 270, seg)
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


# ---------------------------------------------------------------- shell
# The big front and back faces are cut into a grid of compact cells
# instead of one long-sliver fan, so decals on them stay stable in a
# z-buffer that interpolates depth linearly across the screen.
GX = (-W / 2, -3.7, 0.0, 3.7, W / 2)
GY = (0.0, 0.9, 4.0, 7.6, 10.5, 12.6, H)
BULGE = (-3.7, 0.9, 3.7, 7.6)       # battery cover on the lower back


def clip(poly, xa, ya, xb, yb):
    """Sutherland-Hodgman clip of a convex polygon to a rectangle."""
    def cut(pts, inside, inter):
        out = []
        for i in range(len(pts)):
            p, q = pts[i - 1], pts[i]
            if inside(q):
                if not inside(p):
                    out.append(inter(p, q))
                out.append(q)
            elif inside(p):
                out.append(inter(p, q))
        return out

    def ix(x):
        return lambda p, q: (x, p[1] + (q[1] - p[1]) * (x - p[0]) / (q[0] - p[0]))

    def iy(y):
        return lambda p, q: (p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1]), y)
    pts = list(poly)
    for inside, inter in ((lambda p: p[0] >= xa - 1e-9, ix(xa)), (lambda p: p[0] <= xb + 1e-9, ix(xb)),
                          (lambda p: p[1] >= ya - 1e-9, iy(ya)), (lambda p: p[1] <= yb + 1e-9, iy(yb))):
        if not pts:
            break
        pts = cut(pts, inside, inter)
    # drop repeated points
    res = []
    for p in pts:
        if not res or abs(p[0] - res[-1][0]) > 1e-6 or abs(p[1] - res[-1][1]) > 1e-6:
            res.append(p)
    if len(res) > 1 and abs(res[0][0] - res[-1][0]) < 1e-6 and abs(res[0][1] - res[-1][1]) < 1e-6:
        res.pop()
    return res


def with_grid_points(poly):
    """The outline with every crossing of a grid line inserted, so the side
    walls share the cells' edge vertices (no T-junction cracks)."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        out.append(p)
        ts = []
        for x in GX:
            if (p[0] - x) * (q[0] - x) < -1e-12:
                ts.append((x - p[0]) / (q[0] - p[0]))
        for y in GY:
            if (p[1] - y) * (q[1] - y) < -1e-12:
                ts.append((y - p[1]) / (q[1] - p[1]))
        for t in sorted(ts):
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def grid_decal(poly, z, color, lift):
    """A convex front decal cut along the same grid as the face under it."""
    for i in range(len(GX) - 1):
        for j in range(len(GY) - 1):
            cell = clip(poly, GX[i], GY[j], GX[i + 1], GY[j + 1])
            if len(cell) >= 3:
                m.decal_xy(cell, z, color, lift=lift)


outline = with_grid_points(gb_outline(-W / 2, 0, W / 2, H, 0.4, 2.3))
m.extrude_xy(outline, ZB, ZF, BODY, front=False, back=False)
for i in range(len(GX) - 1):
    for j in range(len(GY) - 1):
        cell = clip(outline, GX[i], GY[j], GX[i + 1], GY[j + 1])
        if len(cell) < 3:
            continue
        m.polygon([(x, y, ZF) for x, y in cell], BODY, normal=(0, 0, 1))
        if BULGE[0] <= GX[i] < BULGE[2] and BULGE[1] <= GY[j] < BULGE[3]:
            continue                       # hidden behind the battery cover
        m.polygon([(x, y, ZB) for x, y in cell], BODY, normal=(0, 0, -1))

# battery bulge on the lower back (fills the cells left open above)
m.box(BULGE[0], BULGE[1], -1.6, BULGE[2], BULGE[3], ZB, BODY,
      faces={'back': BODY_DARK, 'front': None})
# groove line across the top of the front
m.decal_xy([(-W / 2 + 0.05, 13.95), (W / 2 - 0.05, 13.95), (W / 2 - 0.05, 14.05), (-W / 2 + 0.05, 14.05)],
           ZF, BODY_DARK)

# cartridge slot on the top edge, towards the back
m.decal_xz([(-3.3, -0.2), (3.3, -0.2), (3.3, -1.25), (-3.3, -1.25)], H, SLOT, lift=0.05)

# OFF/ON power switch nub on the top edge, left
m.box(-3.4, H, 0.2, -2.6, H + 0.2, 0.9, WHEEL, faces={'bottom': None})

# ---------------------------------------------------------------- screen area
grid_decal(gb_outline(-3.8, 8.0, 3.8, 13.6, 0.25, 1.1, 1, 3), ZF, BEZEL, 0.05)
# the two stripe lines, broken in the middle where the (omitted) caption sits
for (y0, y1, col) in ((13.22, 13.32, STRIPE_A), (13.08, 13.18, STRIPE_B)):
    for (x0, x1) in ((-3.45, -1.1), (2.7, 3.45)):
        m.decal_xy([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], ZF, col, lift=0.1)
# LCD (offset right: the power LED sits on the left of the bezel)
grid_decal([(-2.05, 8.55), (2.55, 8.55), (2.55, 12.75), (-2.05, 12.75)], ZF, SCREEN, 0.1)
# power LED
m.decal_xy([(x, y) for x, y in arc(-3.0, 11.3, 0.13, 0, 360, 6)[:-1]], ZF, LED, lift=0.1)

# ---------------------------------------------------------------- controls
# D-pad cross
cx, cy, a, b = -2.35, 5.2, 1.2, 0.4
cross = [(cx + b, cy - a), (cx + b, cy - b), (cx + a, cy - b), (cx + a, cy + b), (cx + b, cy + b),
         (cx + b, cy + a), (cx - b, cy + a), (cx - b, cy + b), (cx - a, cy + b), (cx - a, cy - b),
         (cx - b, cy - b), (cx - b, cy - a)]
m.extrude_xy(cross, ZF, ZF + 0.35, DPAD, back=False)

# A / B buttons (B lower-left, A upper-right, on a slant)
for bx, by in ((1.55, 4.75), (3.2, 5.45)):
    m.cylinder_z(bx, by, 0.62, ZF, ZF + 0.3, AB, segments=10, back=False)

# Select / Start pills, slanted
for px in (-1.0, 0.55):
    m.extrude_xy(pill(px, 2.55, 1.15, 0.32, 25), ZF, ZF + 0.12, PILL, back=False)

# speaker slots in the bottom-right corner
for i in range(6):
    sx = 1.75 + i * 0.36
    sy = 1.85 - i * 0.1
    m.decal_xy(rotated_rect(sx, sy, 0.16, 1.5, -28), ZF, SLOT, lift=0.03)

# contrast wheel (left side, upper) and volume wheel (right side, lower)
m.extrude_yz([(z, y) for z, y in arc(-0.1, 11.0, 0.75, 0, 360, 8)[:-1]], -W / 2 - 0.15, -W / 2, WHEEL,
             right=False)
m.extrude_yz([(z, y) for z, y in arc(-0.1, 5.0, 0.75, 0, 360, 8)[:-1]], W / 2, W / 2 + 0.15, WHEEL,
             left=False)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
