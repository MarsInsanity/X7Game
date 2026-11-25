# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly Game Boy Advance (indigo), handheld, screen facing +Z.

Real size about 14.45 x 8.2 x 2.45 cm. Signature features: wide landscape
body with rounded wing grips, dark screen bezel in the middle, black D-pad
on the left with Start/Select below it, diagonal A/B on the right with a
speaker grille under them, grey L/R shoulder buttons on the top corners,
cartridge slot on the top back, battery hump on the back.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (70, 54, 146)        # indigo shell
BODY_DK = (46, 36, 100)     # back hump / battery cover
BEZEL = (30, 30, 38)        # screen surround
SCREEN = (112, 146, 136)    # LCD (off-ish, greenish grey)
DPAD = (40, 40, 48)
AB = (176, 168, 210)        # A/B: pale lilac grey
SMALL = (128, 128, 140)     # Start / Select
SHOULDER = (150, 150, 162)  # L / R
LED = (60, 230, 90)
HOLE = (20, 20, 26)         # speaker holes, cartridge slot

m = Model('gba', 'console')

W, H = 14.45, 7.95          # body (the shoulder buttons reach 8.2)
X0, X1 = -W / 2, W / 2
R = 3.0                     # radius of the rounded grips
HUMP = 0.35                 # battery hump depth behind the body
ZB, ZF = -0.95 + HUMP / 2, 0.95 + HUMP / 2   # body back / front; body + hump centred on z = 0
BEV = 0.28                  # bevel inset on front and back edges
SEG = 4


def ring(outer, oz, inner, iz):
    """Bevel band between two matching outlines (CCW seen from +Z)."""
    n = len(outer)
    sgn = 1 if iz > oz else -1
    for i in range(n):
        a, b = outer[i], outer[(i + 1) % n]
        c, d = inner[(i + 1) % n], inner[i]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nrm = (dy / l, -dx / l, sgn * 1.0)
        m.polygon([(a[0], a[1], oz), (b[0], b[1], oz), (c[0], c[1], iz), (d[0], d[1], iz)], BODY, normal=nrm)


# ---------------------------------------------------------------- body
outer = Model.rounded_rect(X0, 0, X1, H, R, SEG)
inner = Model.rounded_rect(X0 + BEV, BEV, X1 - BEV, H - BEV, R - BEV, SEG)
m.extrude_xy(outer, ZB + BEV, ZF - BEV, BODY, front=False, back=False)
ring(outer, ZF - BEV, inner, ZF)                       # front bevel
ring(outer, ZB + BEV, inner, ZB)                       # back bevel
m.polygon([(x, y, ZF) for x, y in inner], BODY, normal=(0, 0, 1))
m.polygon([(x, y, ZB) for x, y in inner], BODY, normal=(0, 0, -1))

# battery hump on the lower back
hump = Model.rounded_rect(-3.9, 0.12, 3.9, 4.3, 0.7, 2)
m.extrude_xy(hump, ZB - HUMP, ZB + 0.05, BODY_DK, front=False)

# ---------------------------------------------------------------- front
# screen bezel and LCD
m.decal_xy(Model.rounded_rect(-3.95, 1.85, 3.95, 7.25, 0.45, 2), ZF, BEZEL, lift=0.02)
m.decal_xy([(-3.05, 2.55), (3.05, 2.55), (3.05, 6.6), (-3.05, 6.6)], ZF, SCREEN, lift=0.05)

# D-pad (cross), raised
dx, dy, a, s = -5.35, 4.75, 0.98, 0.32
cross = [(dx + s, dy + a), (dx - s, dy + a), (dx - s, dy + s), (dx - a, dy + s),
         (dx - a, dy - s), (dx - s, dy - s), (dx - s, dy - a), (dx + s, dy - a),
         (dx + s, dy - s), (dx + a, dy - s), (dx + a, dy + s), (dx + s, dy + s)]
m.extrude_xy(cross, ZF - 0.1, ZF + 0.28, DPAD, back=False)

# A (upper right) and B (lower left), diagonal
m.cylinder_z(6.05, 5.25, 0.55, ZF - 0.1, ZF + 0.28, AB, segments=10, back=False)
m.cylinder_z(4.85, 4.45, 0.55, ZF - 0.1, ZF + 0.28, AB, segments=10, back=False)

# Start (upper) and Select (lower) under the D-pad
m.cylinder_z(-4.75, 2.55, 0.26, ZF - 0.1, ZF + 0.12, SMALL, segments=8, back=False)
m.cylinder_z(-4.75, 1.8, 0.26, ZF - 0.1, ZF + 0.12, SMALL, segments=8, back=False)

# power LED above the D-pad
m.decal_xy([(-4.75, 6.45), (-4.4, 6.45), (-4.4, 6.8), (-4.75, 6.8)], ZF, LED, lift=0.03)

# speaker grille under A/B: six small holes
for i, (hx, hy) in enumerate([(5.3, 2.75), (5.75, 2.75), (6.2, 2.75), (5.3, 2.3), (5.75, 2.3), (6.2, 2.3)]):
    h = 0.12
    m.decal_xy([(hx - h, hy - h), (hx + h, hy - h), (hx + h, hy + h), (hx - h, hy + h)], ZF, HOLE, lift=0.03)

# ---------------------------------------------------------------- top
# L / R shoulder buttons wrapping the top corners
cy = H - R
for side in (-1, 1):
    ccx = side * (W / 2 - R)
    pts_out, pts_in = [], []
    for k in range(6):
        t = math.radians(94 + 56 * k / 5)          # 94..150 deg on the left corner
        if side > 0:
            t = math.pi - t                       # mirror for the right corner
        pts_out.append((ccx + (R + 0.25) * math.cos(t), cy + (R + 0.25) * math.sin(t)))
        pts_in.append((ccx + (R - 0.3) * math.cos(t), cy + (R - 0.3) * math.sin(t)))
    m.extrude_xy(pts_out + pts_in[::-1], ZB + 0.05, 0.5, SHOULDER)

# cartridge slot on the top back
m.decal_xz([(-3.1, -0.75), (3.1, -0.75), (3.1, -0.15), (-3.1, -0.15)], H, HOLE, lift=0.02)

print(m.stats())
m.save()
