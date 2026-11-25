# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega Game Gear: black landscape handheld with rounded grip ends, a big
dark screen panel in the middle, a round D-pad on the left, blue 1/2 and
Start buttons on the right and battery bulges on the back of the grips.
Real size about 21 x 11.3 x 3.8 cm. Stands upright, screen facing +Z."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (64, 64, 72)
BODY_EDGE = (46, 46, 54)
PANEL = (20, 20, 24)
SCREEN = (60, 96, 92)
SHINE = (96, 136, 130)
DPAD_DISC = (96, 96, 108)
DPAD_CROSS = (30, 30, 36)
BLUE = (48, 92, 220)
BLUE_SIDE = (26, 48, 140)
LED = (230, 40, 30)
SLOT = (12, 12, 14)

W, H = 21.0, 11.3
ZF, ZB = 1.9, -0.6          # main body front / back
BEVEL = 0.4                 # front chamfer depth and inset


def outline(x0, y0, x1, y1, r_br, r_tr, r_tl, r_bl, seg=4):
    """Counter-clockwise (seen from +Z) outline with per-corner radii."""
    pts = []
    for cx, cy, r, a0 in ((x1 - r_br, y0 + r_br, r_br, 270), (x1 - r_tr, y1 - r_tr, r_tr, 0),
                          (x0 + r_tl, y1 - r_tl, r_tl, 90), (x0 + r_bl, y0 + r_bl, r_bl, 180)):
        if r <= 0:
            pts.append((cx, cy))
            continue
        for s in range(seg + 1):
            a = math.radians(a0 + 90 * s / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def loft(m, a, za, b, zb, color):
    """Ring of quads joining outline a at depth za to outline b at depth zb
    (zb in front of za, both outlines counter-clockwise, same point count)."""
    n = len(a)
    for i in range(n):
        j = (i + 1) % n
        m.quad((b[i][0], b[i][1], zb), (a[i][0], a[i][1], za),
               (a[j][0], a[j][1], za), (b[j][0], b[j][1], zb), color)


m = Model('gamegear', 'console')

# ---- main body: rounded ends, flat bottom, chamfered front edge
R_TOP, R_BOT = 4.4, 5.0
outer = outline(-W / 2, 0, W / 2, H, R_BOT, R_TOP, R_TOP, R_BOT)
inner = outline(-W / 2 + BEVEL, BEVEL, W / 2 - BEVEL, H - BEVEL,
                R_BOT - BEVEL, R_TOP - BEVEL, R_TOP - BEVEL, R_BOT - BEVEL)
zc = ZF - BEVEL
m.extrude_xy(outer, ZB, zc, BODY, front=False)
loft(m, outer, zc, inner, ZF, BODY_EDGE)
m.polygon([(x, y, ZF) for x, y in inner], BODY, normal=(0, 0, 1))

# ---- battery bulges on the back of both grips
for sx in (-1, 1):
    xa, xb = 3.6, W / 2 - 0.5
    bo = outline(-xb, 0.0, -xa, H - 0.7, 1.4, 1.4, R_TOP - 0.6, R_BOT - 0.4, seg=3)
    if sx > 0:
        bo = [(-x, y) for x, y in bo]
    m.extrude_xy(bo, -1.9, ZB, BODY, front=False)

# ---- cartridge slot on top, towards the back
m.decal_xz([(-4.0, -0.45), (4.0, -0.45), (4.0, 0.35), (-4.0, 0.35)], H, SLOT, lift=0.03)

# ---- screen panel, screen and a glare stripe
zf = ZF
m.decal_xy(Model.rounded_rect(-5.1, 1.5, 5.1, 10.3, 1.0, 2), zf, PANEL, lift=0.04)
m.decal_xy([(-3.3, 4.1), (3.3, 4.1), (3.3, 9.0), (-3.3, 9.0)], zf, SCREEN, lift=0.08)
m.decal_xy([(-3.3, 7.4), (-1.7, 9.0), (-0.9, 9.0), (-3.3, 6.6)], zf, SHINE, lift=0.12)

# ---- D-pad: round rocker disc with a raised cross
dx, dy = -7.7, 5.9
m.decal_xy([(dx + 1.85 * math.cos(2 * math.pi * i / 12), dy + 1.85 * math.sin(2 * math.pi * i / 12))
            for i in range(12)], zf, PANEL, lift=0.04)
m.cylinder_z(dx, dy, 1.5, zf, zf + 0.22, DPAD_DISC, segments=10, back=False)
a, b = 0.42, 1.3
cross = [(a, -b), (a, -a), (b, -a), (b, a), (a, a), (a, b), (-a, b), (-a, a), (-b, a), (-b, -a), (-a, -a), (-a, -b)]
m.extrude_xy([(dx + x, dy + y) for x, y in cross], zf + 0.22, zf + 0.42, DPAD_CROSS, back=False)

# ---- power LED above the D-pad
m.decal_xy([(dx - 0.3, 8.85), (dx + 0.3, 8.85), (dx + 0.3, 9.15), (dx - 0.3, 9.15)], zf, LED, lift=0.04)

# ---- buttons 1 and 2 (diagonal) and the small Start button, all blue
for bx, by in ((6.9, 5.1), (8.7, 6.5)):
    m.cylinder_z(bx, by, 0.78, zf, zf + 0.4, BLUE_SIDE, segments=10, front=BLUE, back=False)
m.cylinder_z(8.0, 9.0, 0.42, zf, zf + 0.25, BLUE_SIDE, segments=8, front=BLUE, back=False)

# ---- speaker slots, lower right
for k in range(3):
    ox = 6.3 + k * 0.55
    m.decal_xy([(ox, 1.7), (ox + 0.22, 1.7), (ox + 0.72, 3.0), (ox + 0.5, 3.0)], zf, PANEL, lift=0.04)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
