# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly Game Boy Color ("Grape" purple) for the X7 Game frontend.

Real size about 7.5 x 13.3 x 2.7 cm. Portrait handheld, screen facing +Z,
standing on its curved bottom edge.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (112, 62, 166)       # grape purple
BODY_DARK = (70, 36, 112)   # battery cover / back details
BEZEL = (44, 44, 54)        # dark screen bezel
SCREEN = (120, 150, 140)    # unlit LCD, grey-green
BUTTON = (26, 24, 32)       # D-pad, A/B
RUBBER = (62, 60, 74)       # Start / Select
HOLE = (34, 18, 56)         # speaker holes, slots
LED = (230, 40, 40)         # power lamp
SWITCH = (200, 200, 210)    # power switch

W2 = 3.75      # half width
H = 13.3       # height
SAG = 0.55     # how far the curved bottom dips below its ends
ZF = 1.35      # front face
ZB = -0.75     # back face of the main shell (battery bulge goes further)
BEV = 0.14     # edge bevel


def outline(d):
    """Front silhouette, inset by d: flat top with rounded corners, curved
    bottom edge with rounded corners. Counter-clockwise from +Z."""
    w = W2 - d
    top = H - d
    rt = 0.55 - d * 0.5           # top corner radius
    rb = 0.9 - d * 0.5            # bottom corner radius
    pts = []
    # curved bottom: a shallow arc from left to right, lowest point y = d
    ends = SAG + d                # y of the arc at x = +-(w - rb)
    xa = w - rb
    n = 6
    for i in range(n + 1):
        x = -xa + 2 * xa * i / n
        t = x / xa
        pts.append((x, d + (ends - d) * t * t))
    # bottom-right corner up to the right side
    for a in (-60, -30):
        r = math.radians(a)
        pts.append((xa + rb * math.cos(r), ends + rb + rb * math.sin(r)))
    pts.append((w, ends + rb))
    # right side up to the top-right corner
    for a in (0, 45, 90):
        r = math.radians(a)
        pts.append((w - rt + rt * math.cos(r), top - rt + rt * math.sin(r)))
    for a in (90, 135, 180):
        r = math.radians(a)
        pts.append((-w + rt + rt * math.cos(r), top - rt + rt * math.sin(r)))
    pts.append((-w, ends + rb))
    for a in (210, 240):
        r = math.radians(a)
        pts.append((-xa + rb * math.cos(r), ends + rb + rb * math.sin(r)))
    # drop duplicates
    out = []
    for p in pts:
        if not out or abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) > 1e-6:
            out.append(p)
    return out


def loft(m, outer, zo, inner, zi, color, facing):
    """Ring of quads between two outlines (same point count). facing +1:
    the ring faces +Z (outer at zo behind inner at zi), -1: faces -Z."""
    n = len(outer)
    for i in range(n):
        a0 = (outer[i][0], outer[i][1], zo)
        a1 = (outer[(i + 1) % n][0], outer[(i + 1) % n][1], zo)
        b0 = (inner[i][0], inner[i][1], zi)
        b1 = (inner[(i + 1) % n][0], inner[(i + 1) % n][1], zi)
        if facing > 0:
            m.quad(a0, a1, b1, b0, color)
        else:
            m.quad(a1, a0, b0, b1, color)


def ccw(pts):
    s = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
            for i in range(len(pts)))
    return pts if s > 0 else pts[::-1]


def rot2(pts, deg, cx, cy):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def build():
    m = Model('gbc', 'console')
    outer = ccw(outline(0.0))
    inner = ccw(outline(BEV))

    # ---- shell: straight sides, bevelled front and back edges
    m.extrude_xy(outer, ZB + BEV, ZF - BEV, BODY, front=False, back=False)
    loft(m, outer, ZF - BEV, inner, ZF, BODY, +1)
    m.polygon([(x, y, ZF) for x, y in inner], BODY, normal=(0, 0, 1))
    loft(m, outer, ZB + BEV, inner, ZB, BODY, -1)
    m.polygon([(x, y, ZB) for x, y in inner], BODY, normal=(0, 0, -1))

    # ---- battery bulge on the lower back
    bat = Model.rounded_rect(-3.1, 1.0, 3.1, 6.2, 0.6, segments=2)
    m.extrude_xy(bat, -1.35, ZB, BODY_DARK, front=False)
    # cartridge back edge ridge on the upper back
    m.box(-3.0, 9.4, ZB - 0.25, 3.0, 12.6, ZB, BODY, faces={'front': None})

    # ---- front: bezel, screen, power lamp
    bz = Model.rounded_rect(-3.2, 7.05, 3.2, 12.75, 0.45, segments=2)
    m.decal_xy(bz, ZF, BEZEL, lift=0.03)
    m.decal_xy([(-2.2, 7.65), (2.35, 7.65), (2.35, 12.2), (-2.2, 12.2)], ZF, SCREEN, lift=0.06)
    led = [(-2.75 + 0.13 * math.cos(math.radians(a)), 10.6 + 0.13 * math.sin(math.radians(a)))
           for a in range(0, 360, 60)]
    m.decal_xy(led, ZF, LED, lift=0.06)
    # a thin coloured band under the bezel where the badge sits (no text)
    m.decal_xy([(-1.6, 6.55), (1.6, 6.55), (1.6, 6.75), (-1.6, 6.75)], ZF, BODY_DARK, lift=0.03)

    # ---- D-pad
    a, b = 0.33, 1.0
    cross = [(a, -b), (a, -a), (b, -a), (b, a), (a, a), (a, b),
             (-a, b), (-a, a), (-b, a), (-b, -a), (-a, -a), (-a, -b)]
    cross = [(x - 2.05, y + 4.35) for x, y in cross]
    m.extrude_xy(cross, ZF, ZF + 0.25, BUTTON, back=False)

    # ---- B and A buttons (A higher and to the right)
    m.cylinder_z(1.35, 3.95, 0.48, ZF, ZF + 0.22, BUTTON, segments=10, back=False)
    m.cylinder_z(2.75, 4.6, 0.48, ZF, ZF + 0.22, BUTTON, segments=10, back=False)

    # ---- Select / Start: slanted rubber pills
    pill = Model.rounded_rect(-0.45, -0.14, 0.45, 0.14, 0.12, segments=1)
    for cx in (-0.75, 0.45):
        m.extrude_xy(rot2(pill, 25, cx, 1.85), ZF, ZF + 0.12, RUBBER, back=False)

    # ---- speaker holes, bottom right: a small hexagonal cluster
    hexa = [(0.13 * math.cos(math.radians(t)), 0.13 * math.sin(math.radians(t))) for t in range(30, 390, 60)]
    sc = (2.45, 1.75)
    holes = [(0, 0)] + [(0.45 * math.cos(math.radians(t)), 0.45 * math.sin(math.radians(t)))
                        for t in range(0, 360, 60)]
    for hx, hy in holes:
        m.decal_xy([(sc[0] + hx + x, sc[1] + hy + y) for x, y in hexa], ZF, HOLE, lift=0.03)

    # ---- top: cartridge slot, power switch, IR window
    m.decal_xz([(-3.0, -0.55), (3.0, -0.55), (3.0, -0.05), (-3.0, -0.05)], H, HOLE, lift=0.02)
    m.box(-3.2, H, 0.25, -2.4, H + 0.22, 0.75, SWITCH)
    m.decal_xz([(1.6, 0.35), (2.8, 0.35), (2.8, 0.95), (1.6, 0.95)], H, (30, 30, 36), lift=0.02)

    # ---- sides: volume wheel (left), link port (right), headphone jack (bottom)
    m.box(-W2 - 0.15, 2.6, -0.1, -W2 + 0.05, 3.6, 0.5, BODY_DARK, faces={'right': None})
    m.polygon([(W2 + 0.02, 4.6, 0.6), (W2 + 0.02, 4.6, -0.3), (W2 + 0.02, 5.8, -0.3), (W2 + 0.02, 5.8, 0.6)],
              HOLE, normal=(1, 0, 0))
    return m


if __name__ == '__main__':
    model = build()
    print(model.stats())
    print(model.save())
