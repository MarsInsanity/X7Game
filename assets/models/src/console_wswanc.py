# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly Bandai WonderSwan Color ("pearl blue") for the X7 Game frontend.

Real size about 12.8 x 7.4 x 2.4 cm. Landscape handheld standing upright on
its bottom edge, screen facing +Z. Signature features: wide landscape slab
with soft rounded ends, big dark screen frame in the middle, the two
four-button diamonds on the left (small Y group above the larger X group),
the A / B pair set diagonally on the right with Start below, and the
cartridge slot plus battery bulge on the back.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (140, 182, 236)      # pearl blue shell
BODY_DARK = (92, 124, 176)  # battery cover, cartridge, side details
BEZEL = (40, 44, 58)        # dark screen frame
SCREEN = (62, 84, 104)      # unlit colour LCD, dark blue-grey
GLARE = (96, 122, 146)      # a soft reflection band on the LCD
BUTTON = (74, 78, 96)       # X / Y buttons
AB = (36, 38, 50)           # A / B buttons
RUBBER = (170, 172, 184)    # Start / sound, light grey
HOLE = (28, 34, 54)         # speaker holes, slots
LED = (60, 220, 90)         # power lamp
BAND = (228, 236, 248)      # pale band under the screen (no text)

W2 = 6.4       # half width
H = 7.43       # height
ZF = 1.1       # front face
ZB = -0.5      # back face of the main slab
ZBAT = -1.3    # back of the battery bulge (total depth 2.4)
BEV = 0.16     # front edge bevel


def outline(d):
    """Front silhouette inset by d: straight top, soft top corners, big
    rounded bottom corners and a slightly bowed bottom edge."""
    w = W2 - d
    rt = 1.0 - d * 0.5
    rb = 2.0 - d * 0.5
    top = H - d
    pts = []
    # bottom edge: gently bowed, lowest at the middle (y = d)
    xa = w - rb
    for x in (-xa, 0.0, xa):
        pts.append((x, d + (0.12 if x else 0.0)))
    # bottom-right corner
    cy = d + 0.12 + rb
    for a in (-60, -30):
        r = math.radians(a)
        pts.append((xa + rb * math.cos(r), cy + rb * math.sin(r)))
    pts.append((w, cy))
    # right side straight up into the top-right corner
    for a in (0, 45, 90):
        r = math.radians(a)
        pts.append((w - rt + rt * math.cos(r), top - rt + rt * math.sin(r)))
    for a in (90, 135, 180):
        r = math.radians(a)
        pts.append((-w + rt + rt * math.cos(r), top - rt + rt * math.sin(r)))
    pts.append((-w, cy))
    for a in (210, 240):
        r = math.radians(a)
        pts.append((-xa + rb * math.cos(r), cy + rb * math.sin(r)))
    out = []
    for p in pts:
        if not out or abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) > 1e-6:
            out.append(p)
    if abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1]) < 1e-6:
        out.pop()
    return out


def ccw(pts):
    s = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
            for i in range(len(pts)))
    return pts if s > 0 else pts[::-1]


def loft_front(m, outer, zo, inner, zi, color):
    """Ring of quads facing +Z between the outer outline (at zo, behind)
    and the inset outline (at zi, in front)."""
    n = len(outer)
    for i in range(n):
        a0 = (outer[i][0], outer[i][1], zo)
        a1 = (outer[(i + 1) % n][0], outer[(i + 1) % n][1], zo)
        b0 = (inner[i][0], inner[i][1], zi)
        b1 = (inner[(i + 1) % n][0], inner[(i + 1) % n][1], zi)
        m.quad(a0, a1, b1, b0, color)


def ngon(cx, cy, rx, ry, n, rot=0.0):
    return [(cx + rx * math.cos(math.radians(rot + 360.0 * i / n)),
             cy + ry * math.sin(math.radians(rot + 360.0 * i / n))) for i in range(n)]


def build():
    m = Model('wswanc', 'console')
    outer = ccw(outline(0.0))
    inner = ccw(outline(BEV))

    # ---- shell: straight sides, bevelled front edge, flat back
    m.extrude_xy(outer, ZB, ZF - BEV, BODY, front=False)
    loft_front(m, outer, ZF - BEV, inner, ZF, BODY)
    m.polygon([(x, y, ZF) for x, y in inner], BODY, normal=(0, 0, 1))

    # ---- back: battery bulge across the lower half, cartridge in the upper half
    bat = Model.rounded_rect(-4.6, 0.55, 4.6, 3.35, 0.7, segments=1)
    m.extrude_xy(bat, ZBAT, ZB, BODY_DARK, front=False)
    # cartridge back, sitting a little proud of the shell, with a grip ridge
    m.box(-3.3, 3.75, ZB - 0.18, 3.3, 7.0, ZB, BODY_DARK, faces={'front': None})
    m.polygon([(3.3, 6.2, ZB - 0.2), (-3.3, 6.2, ZB - 0.2), (-3.3, 6.5, ZB - 0.2), (3.3, 6.5, ZB - 0.2)],
              HOLE, normal=(0, 0, -1))
    # cartridge slot opening seen on the top edge
    m.decal_xz([(-3.3, ZB + 0.1), (3.3, ZB + 0.1), (3.3, ZB + 0.45), (-3.3, ZB + 0.45)], H, HOLE, lift=0.02)

    # ---- front: screen frame, LCD, glare, power lamp, pale band
    bz = Model.rounded_rect(-3.75, 1.15, 3.75, 6.85, 0.5, segments=1)
    m.decal_xy(bz, ZF, BEZEL, lift=0.03)
    sx0, sx1, sy0, sy1 = -2.95, 2.95, 2.45, 6.25
    m.decal_xy([(sx0, sy0), (sx1, sy0), (sx1, sy1), (sx0, sy1)], ZF, SCREEN, lift=0.06)
    # a soft diagonal reflection band across the upper-left of the LCD
    m.decal_xy([(sx0 + 0.9, sy1 - 0.25), (sx0 + 1.6, sy1 - 0.25), (sx0 + 0.55, sy0 + 1.2), (sx0 - 0.15 + 0.3, sy0 + 1.2)],
               ZF, GLARE, lift=0.09)
    m.decal_xy([(-1.6, 1.6), (1.6, 1.6), (1.6, 1.95), (-1.6, 1.95)], ZF, BAND, lift=0.06)
    m.decal_xy(ngon(-3.35, 6.45, 0.12, 0.12, 6), ZF, LED, lift=0.06)

    # ---- left: small Y diamond above the larger X diamond
    def diamond(cx, cy, off, rx, ry):
        for dx, dy, along in ((0, off, False), (off, 0, True), (0, -off, False), (-off, 0, True)):
            # each key is an elongated hexagon, lying along the diamond's arm
            pts = ngon(cx + dx, cy + dy, rx if along else ry, ry if along else rx, 6, 0 if along else 90)
            m.extrude_xy(pts, ZF, ZF + 0.2, BUTTON, back=False)
    diamond(-5.0, 3.35, 0.62, 0.34, 0.26)      # X group
    diamond(-5.0, 5.9, 0.42, 0.22, 0.17)       # Y group

    # ---- right: B lower-left, A upper-right, Start and sound below
    m.cylinder_z(4.45, 3.7, 0.44, ZF, ZF + 0.22, AB, segments=10, back=False)
    m.cylinder_z(5.45, 4.45, 0.44, ZF, ZF + 0.22, AB, segments=10, back=False)
    pill = Model.rounded_rect(-0.32, -0.13, 0.32, 0.13, 0.1, segments=1)
    m.extrude_xy([(x + 5.1, y + 1.95) for x, y in pill], ZF, ZF + 0.12, RUBBER, back=False)
    m.extrude_xy(ngon(4.2, 1.95, 0.15, 0.15, 6), ZF, ZF + 0.1, RUBBER, back=False)

    # ---- speaker: a short row of slanted slots, upper right
    for i in range(3):
        cx = 4.55 + 0.4 * i
        m.decal_xy([(cx - 0.08, 5.65), (cx + 0.08, 5.65), (cx + 0.36, 6.45), (cx + 0.2, 6.45)], ZF, HOLE, lift=0.03)

    # ---- edges: power switch on the top left, link / headphone ports
    m.box(-5.3, H - 0.6, -0.05, -4.5, H + 0.18, 0.55, RUBBER, faces={'bottom': None})
    m.polygon([(W2 + 0.02, 2.6, 0.75), (W2 + 0.02, 2.6, -0.2), (W2 + 0.02, 3.4, -0.2), (W2 + 0.02, 3.4, 0.75)],
              HOLE, normal=(1, 0, 0))
    return m


if __name__ == '__main__':
    model = build()
    print(model.stats())
    print(model.save())
