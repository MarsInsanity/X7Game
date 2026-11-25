# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly Game Boy Advance (indigo), handheld standing upright, screen to +Z.

Real size 14.45 x 8.2 x 2.45 cm. Built from photos (Wikimedia Commons:
"Game Boy Advance front.jpg", "Game Boy Advance back.jpg",
"Nintendo-Game-Boy-Advance-Purple-FL.jpg"):

  * the outline: a straight top edge, near-vertical ends that round off into
    the top corners, and a bottom edge that sweeps down from the ends to a
    flat middle (the middle is 8.2 tall, the ends only about 6.5)
  * indigo shell; the big charcoal screen bezel (7.8 wide, top 0.5 below
    the top edge, square-ish top corners, big round bottom corners) with the
    grey LCD in its upper part
  * light grey D-pad upper left, the two small light grey Start / Select
    buttons below it on dark indigo pills; the two big light grey B / A
    buttons upper right (A higher and further out), the power lamp above
    them, six slanted speaker slots below them
  * light grey L / R shoulder buttons wrapping the top corners at the back,
    light grey bumpers on the lower ends
  * back: grip bulges at both ends, the battery cover in the lower middle,
    the (plain) serial sticker above it, two screws near the top, and the
    cartridge bay at the top middle

The cartridge goes down into the bay in the top middle of the back, label
facing the back. The bay is open to the top and, over its top 1.5 cm, to
the back (on the real console that part of the label stays in view); below
that it is a closed pocket (the connector). About 1.1 cm of the cartridge
stands above the top edge.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (112, 100, 214)       # indigo shell, front face
BODY_SD = (84, 74, 172)     # indigo edges, back
BACK_D = (52, 44, 118)      # darker indigo: battery cover seam, Start/Select pills
BEZEL = (44, 44, 52)        # charcoal screen surround
SCREEN = (156, 162, 156)    # LCD, off (grey)
GREY = (206, 206, 212)      # D-pad, A/B, Start/Select, L/R, end bumpers
GREY_D = (150, 150, 162)    # sides of the grey parts
SLOT = (20, 18, 28)         # inside the cartridge bay
LED = (220, 60, 40)         # power lamp
HOLE = (30, 26, 72)         # speaker slots, screw holes
STICKER = (40, 40, 44)      # serial sticker on the back (plain)
PILL = (94, 84, 186)        # the faint Start / Select label pills

m = Model('gba', 'console')

HT = 8.2                    # top edge (middle)
ZF = 1.225                  # front face
ZB = -0.85                  # back face of the middle
ZG = -1.225                 # back of the grips
ZC = -0.45                  # the grey rail on the ends runs from here to the front bevel
BEV = 0.2                   # front bevel

# cartridge bay (cartridge: 5.5 wide below its shoulders, 0.8 thick; turned
# label to the back and seated at x 0, z CZ, bottom edge at y CY)
CZ, CY = -0.35, 5.75
BX = 2.82                   # bay half width (cartridge 2.75)
BZ0, BZ1 = CZ - 0.45, CZ + 0.45   # pocket back wall / bay front wall (cartridge -0.75 .. 0.05)
BY0 = CY - 0.05             # pocket floor
LIP = HT - 1.5             # top of the lip: above it the bay is open at the back

# right half of the outline, bottom to top (measured from the front photo)
RIGHT = [(1.4, 0.0), (2.83, 0.15), (4.5, 0.37), (5.76, 0.6), (6.6, 0.85), (7.05, 1.25),
         (7.225, 2.2), (7.225, 5.0), (7.12, 6.6), (6.85, 7.2), (6.39, 7.6), (5.34, 7.94),
         (4.3, 8.2), (BX, HT)]
OUT = RIGHT + [(-x, y) for x, y in reversed(RIGHT)]     # counter-clockwise seen from +Z
N = len(OUT)
TOP_A = OUT.index((BX, HT))         # edge TOP_A -> TOP_A + 1 runs over the bay


def offset(pts, d):
    """Move every vertex of a convex CCW polygon outwards by d (inwards if d < 0)."""
    out = []
    n = len(pts)
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        e1 = (p1[0] - p0[0], p1[1] - p0[1])
        e2 = (p2[0] - p1[0], p2[1] - p1[1])
        n1 = (e1[1] / math.hypot(*e1), -e1[0] / math.hypot(*e1))
        n2 = (e2[1] / math.hypot(*e2), -e2[0] / math.hypot(*e2))
        b = (n1[0] + n2[0], n1[1] + n2[1])
        bl = math.hypot(*b)
        b = (b[0] / bl, b[1] / bl)
        k = d / max(0.3, b[0] * n1[0] + b[1] * n1[1])
        out.append((p1[0] + b[0] * k, p1[1] + b[1] * k))
    return out


def grey_edge(a, b):
    """Edges of the ends: there the middle of the side is the light grey
    rail (L / R buttons at the top corners, bumpers below)."""
    return all(abs(p[0]) >= 4.29 and (p[1] >= 5 or abs(p[0]) >= 6.5) for p in (a, b))


INN = offset(OUT, -BEV)
ZS = ZF - BEV

# ---- shell: front face, bevel, sides, back
m.polygon([(x, y, ZF) for x, y in INN], BODY, normal=(0, 0, 1))
for i in range(N):
    j = (i + 1) % N
    a, b, c, d = OUT[i], OUT[j], INN[j], INN[i]
    m.quad((a[0], a[1], ZS), (b[0], b[1], ZS), (c[0], c[1], ZF), (d[0], d[1], ZF), BODY)
    nrm = (b[1] - a[1], a[0] - b[0], 0)

    def wall(z0, z1, col):
        m.polygon([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], col, normal=nrm)
    if i == TOP_A:
        wall(BZ1, ZS, BODY_SD)             # over the bay only the front strip of the top
    elif grey_edge(a, b):
        wall(ZC, ZS, GREY)
        wall(ZB, ZC, BODY_SD)
    else:
        wall(ZB, ZS, BODY_SD)

back = OUT[:TOP_A + 1] + [(BX, LIP), (-BX, LIP)] + OUT[TOP_A + 1:]
m.polygon([(x, y, ZB) for x, y in back], BODY, normal=(0, 0, -1))

# ---- cartridge bay (dark; faces point into the bay)
m.polygon([(-BX, BY0, BZ1), (BX, BY0, BZ1), (BX, HT, BZ1), (-BX, HT, BZ1)], SLOT, normal=(0, 0, -1))   # front wall
side = [(ZB, HT), (ZB, LIP), (BZ0, LIP), (BZ0, BY0), (BZ1, BY0), (BZ1, HT)]
m.polygon([(-BX, y, z) for z, y in side], SLOT, normal=(1, 0, 0))
m.polygon([(BX, y, z) for z, y in side], SLOT, normal=(-1, 0, 0))
m.polygon([(-BX, BY0, BZ0), (BX, BY0, BZ0), (BX, BY0, BZ1), (-BX, BY0, BZ1)], SLOT, normal=(0, 1, 0))   # floor
m.polygon([(-BX, BY0, BZ0), (BX, BY0, BZ0), (BX, LIP, BZ0), (-BX, LIP, BZ0)], SLOT, normal=(0, 0, 1))    # pocket back wall
m.polygon([(-BX, LIP, ZB), (BX, LIP, ZB), (BX, LIP, BZ0), (-BX, LIP, BZ0)], BODY_SD, normal=(0, 1, 0))  # top of the lip

# ---- grips: bulges on the back of both ends, bevelled all round
GX0, GX1 = 4.3, 4.65        # inner edge of a grip: at the top / bottom, at mid height
GD = 0.5                    # the grip's back face is this much narrower on its inner side
GIN = offset(OUT, -0.35)


for s in (1, -1):
    idx = [i for i, p in enumerate(OUT) if s * p[0] >= GX0 - 0.01]
    poly = [OUT[i] for i in idx] + [(s * GX1, 4.2)]       # inner edge: top end, mid point, bottom end
    backp = [GIN[i] for i in idx] + [(s * (GX1 + GD), 4.2)]
    m.polygon([(x, y, ZG) for x, y in backp], BODY, normal=(0, 0, -1))
    n = len(poly)
    for k in range(n):
        a, b, c, d = poly[k], poly[(k + 1) % n], backp[(k + 1) % n], backp[k]
        col = BODY_SD
        m.polygon([(a[0], a[1], ZB), (b[0], b[1], ZB), (c[0], c[1], ZG), (d[0], d[1], ZG)], col,
                  normal=(b[1] - a[1], a[0] - b[0], -0.4 * math.hypot(b[0] - a[0], b[1] - a[1])))

# ---- back details: serial sticker, battery cover, latch, screws
LB = ZB - 0.02


def back_decal(pts, col, z=LB):
    m.polygon([(x, y, z) for x, y in pts], col, normal=(0, 0, -1))


back_decal([(-3.4, 4.95), (3.4, 4.95), (3.4, 6.3), (-3.4, 6.3)], STICKER)
back_decal([(-3.4, 0.3), (3.4, 0.3), (3.4, 4.8), (-3.4, 4.8)], BACK_D)
back_decal([(-3.27, 0.43), (3.27, 0.43), (3.27, 4.67), (-3.27, 4.67)], BODY, z=LB - 0.02)
back_decal([(-0.8, 4.2), (0.8, 4.2), (0.8, 5.1), (-0.8, 5.1)], BACK_D, z=LB - 0.04)
for x, y, z in ((4.75, 7.0, ZB), (-4.75, 7.0, ZB), (6.6, 2.5, ZG), (-6.6, 2.5, ZG)):
    back_decal([(x + 0.17 * math.cos(a * math.pi / 2), y + 0.17 * math.sin(a * math.pi / 2)) for a in range(4)], HOLE, z=z - 0.02)

# ---- front: bezel and screen
bez = []
for cx, cy, r, a0 in ((3.85 - 0.5, 7.2 - 0.5, 0.5, 0), (-3.85 + 0.5, 7.2 - 0.5, 0.5, 90),
                      (-3.8 + 1.3, 0.8 + 1.3, 1.3, 180), (3.8 - 1.3, 0.8 + 1.3, 1.3, 270)):
    steps = 1 if r < 1 else 3
    for k in range(steps + 1):
        a = math.radians(a0 + 90 * k / steps)
        bez.append((cx + r * math.cos(a), cy + r * math.sin(a)))
m.decal_xy(bez, ZF, BEZEL)
m.decal_xy([(-3.3, 2.4), (3.3, 2.4), (3.3, 6.7), (-3.3, 6.7)], ZF, SCREEN, lift=0.04)

# ---- D-pad
DX, DY, DA, DW = -5.8, 4.8, 1.0, 0.38
cross = [(DW, -DA), (DW, -DW), (DA, -DW), (DA, DW), (DW, DW), (DW, DA),
         (-DW, DA), (-DW, DW), (-DA, DW), (-DA, -DW), (-DW, -DW), (-DW, -DA)]
m.extrude_xy([(DX + x, DY + y) for x, y in cross], ZF, ZF + 0.28, GREY_D, front=GREY, back=False)

# ---- B / A, Start / Select on their pills
for x, y in ((4.77, 4.57), (6.2, 4.98)):
    m.cylinder_z(x, y, 0.5, ZF, ZF + 0.25, GREY_D, segments=8, front=GREY, back=False)
for x, y in ((-4.75, 2.78), (-4.75, 1.95)):
    m.decal_xy([(x - 1.15, y - 0.24), (x + 0.1, y - 0.2), (x + 0.1, y + 0.2), (x - 1.15, y + 0.24)], ZF, PILL)
    m.cylinder_z(x, y, 0.24, ZF, ZF + 0.15, GREY_D, segments=5, front=GREY, back=False)

# ---- power lamp, speaker slots
m.decal_xy([(4.72, 6.65), (4.92, 6.65), (4.92, 6.85), (4.72, 6.85)], ZF, LED)
for k in range(6):            # top slot shortest, bottom longest
    y = 3.2 - 0.22 * k
    x0 = 4.95 - 0.13 * k
    m.decal_xy([(x0, y), (6.0, y), (6.0, y + 0.11), (x0, y + 0.11)], ZF, HOLE)

m.save()
print(m.stats())
