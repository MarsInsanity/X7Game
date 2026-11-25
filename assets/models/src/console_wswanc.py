# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly Bandai WonderSwan Color (crystal blue) for the X7 Game frontend.

Real size 12.8 x 7.43 x 2.4 cm. A landscape handheld standing upright on
its bottom edge, screen facing +Z. Proportions were measured from straight-
on Commons photos (front view: 65.9 px / cm):

  * silhouette: straight top edge, rounded corners (top right the roundest),
    and the typical wavy bottom edge: a low "chin" under the Sound / Start /
    Power buttons (x -2.9 .. 1.25), the left part 0.15 cm higher, the right
    part (under A / B) 0.45 cm higher
  * a big cream screen bezel slightly right of centre (x -3.47 .. 4.42,
    y 1.0 .. 7.12), its top right corner cut off, with a grey LCD frame
    (x -2.94 .. 3.89, y 1.97 .. 6.30) round the dark screen
    (x -2.71 .. 3.62, y 2.17 .. 6.11)
  * on the left two clear button discs, Y on top (centre -4.69, 5.88) and X
    below (-4.76, 2.48), each with four triangular buttons pointing to the
    middle (1 top, 2 right, 3 bottom, 4 left)
  * on the right the round speaker at the top (5.03, 6.11, r 0.83) and the
    A / B pair set diagonally (A 5.63, 2.63; B 5.03, 1.86) on a clear pad
  * Sound, Start (cream) and Power (orange) in a dark bed under the bezel
  * on the back: the cartridge bay, open at the top edge, in the upper
    middle (half the console's width), and the battery cover below it

The cartridge slides straight down into the bay, label facing the back; its
grip lip ends flush with the console's top edge (see systems/wswanc.json).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (54, 84, 196)        # crystal blue shell
CLEAR = (120, 150, 232)     # the lighter clear discs, pad and speaker
BEZEL = (244, 240, 226)     # cream screen bezel
LCDF = (150, 150, 146)      # grey frame round the LCD
SCREEN = (34, 36, 54)       # dark LCD
BUTTON = (206, 212, 226)    # X / Y / A / B buttons
BED = (26, 34, 96)          # dark bed round Sound / Start / Power, button rims
PILL = (242, 230, 200)      # Sound / Start
POWER = (234, 98, 44)       # Power
FLOOR = (30, 58, 44)        # board seen at the floor of the cartridge bay
WALL = (18, 22, 34)         # bay walls (dark cavity)
COVER = (84, 116, 214)      # battery cover on the back
GOLD = (206, 150, 70)       # the battery's copper-gold end seen through the cover

W2 = 6.4        # half width
H = 7.43        # height
ZF = 1.1        # front face
ZBK = -1.0      # back face
BV = 0.2        # front bevel depth (z)
BI = 0.18       # front bevel inset (xy)
BVB = 0.3       # back bevel depth: the back is rounder than the front
BIB = 0.3       # back bevel inset

# cartridge bay (cart slab 6.4 x 3.6 x 0.6, grip lip 0.7 above it)
BX = 3.25       # half width (0.05 clearance each side)
BY = H - 4.3    # bay bottom: the seated cart's top is flush with the top
BZ = ZBK + 0.65  # bay floor (cart slab 0.6 thick, label flush with the back)


def arc(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def outline():
    """Front silhouette, counter-clockwise seen from the front."""
    pts = [(-2.9, 0.0), (1.25, 0.0), (1.65, 0.3), (2.05, 0.45)]
    pts += arc(W2 - 1.1, 0.45 + 1.1, 1.1, 270, 360, 3)          # bottom right
    pts += arc(W2 - 1.2, H - 1.2, 1.2, 0, 90, 3)                # top right
    pts += [(BX, H), (-BX, H)]                                   # bay opening
    pts += arc(-W2 + 1.0, H - 1.0, 1.0, 90, 180, 3)             # top left
    pts += arc(-W2 + 1.05, 0.15 + 1.05, 1.05, 180, 270, 3)      # bottom left
    pts += [(-3.3, 0.15)]
    return pts


def inset(pts, d):
    """Miter offset of a CCW outline, d inwards."""
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]

        def nrm(a, b):
            dx, dy = b[0] - a[0], b[1] - a[1]
            l = math.hypot(dx, dy)
            return (-dy / l, dx / l)
        n1, n2 = nrm(p0, p1), nrm(p1, p2)
        k = 1 + n1[0] * n2[0] + n1[1] * n2[1]
        out.append((p1[0] + d * (n1[0] + n2[0]) / k, p1[1] + d * (n1[1] + n2[1]) / k))
    return out


m = Model('wswanc', 'console')

O = outline()
I = inset(O, BI)
IB = inset(O, BIB)
N = len(O)
TOPBAY = O.index((BX, H))          # edge TOPBAY -> TOPBAY+1 is the bay opening

# ---------------------------------------------------------------- shell
m.polygon([(x, y, ZF) for x, y in I], BODY, normal=(0, 0, 1))
for i in range(N):
    j = (i + 1) % N
    (xa, ya), (xb, yb) = O[i], O[j]
    (ia, ja), (ib, jb) = I[i], I[j]
    nx, ny = yb - ya, -(xb - xa)            # outward
    # front bevel
    m.polygon([(ia, ja, ZF), (xa, ya, ZF - BV), (xb, yb, ZF - BV), (ib, jb, ZF)], BODY, normal=(nx, ny, 0.5))
    if i == TOPBAY:
        # the top edge over the bay ends at the bay floor
        m.polygon([(xa, ya, ZF - BV), (xa, ya, BZ), (xb, yb, BZ), (xb, yb, ZF - BV)], BODY, normal=(nx, ny, 0))
        continue
    (ia, ja), (ib, jb) = IB[i], IB[j]
    m.polygon([(xa, ya, ZF - BV), (xa, ya, ZBK + BVB), (xb, yb, ZBK + BVB), (xb, yb, ZF - BV)], BODY, normal=(nx, ny, 0))
    m.polygon([(xa, ya, ZBK + BVB), (ia, ja, ZBK), (ib, jb, ZBK), (xb, yb, ZBK + BVB)], BODY, normal=(nx, ny, -0.5))

# back face with the bay cut out of its top middle
back = IB[:TOPBAY + 1] + [(BX, BY), (-BX, BY)] + IB[TOPBAY + 1:]
m.polygon([(x, y, ZBK) for x, y in back], BODY, normal=(0, 0, -1))

# ---------------------------------------------------------------- cartridge bay
m.quad((-BX, BY, BZ), (-BX, H, BZ), (BX, H, BZ), (BX, BY, BZ), FLOOR)          # floor, faces -Z
m.polygon([(-BX, BY, ZBK), (BX, BY, ZBK), (BX, BY, BZ), (-BX, BY, BZ)], WALL, normal=(0, 1, 0))  # bottom (connector) wall
yt = IB[TOPBAY][1]
for sx in (-1, 1):
    wall = [(sx * BX, BY, BZ), (sx * BX, BY, ZBK), (sx * BX, yt, ZBK), (sx * BX, H, ZBK + BVB), (sx * BX, H, BZ)]
    m.polygon(wall, WALL, normal=(-sx, 0, 0))

# ---------------------------------------------------------------- battery cover (back, below the bay)
cover = Model.rounded_rect(-3.5, 0.75, 3.5, BY - 0.2, 0.25, segments=1)
m.extrude_xy(cover, ZBK - 0.06, ZBK, COVER, front=False, side=BODY)
m.polygon([(x, y, ZBK - 0.08) for x, y in Model.rounded_rect(-0.7, BY - 0.5, 0.7, BY - 0.25, 0.1, 1)],
          BED, normal=(0, 0, -1))                                               # finger notch
# the AA battery seen through the clear cover (its + end towards the console's left)
m.polygon([(x, y, ZBK - 0.08) for x, y in [(-2.3, 1.2), (2.6, 1.2), (2.6, 2.45), (-2.3, 2.45)]], SCREEN, normal=(0, 0, -1))
m.polygon([(x, y, ZBK - 0.08) for x, y in [(-3.0, 1.25), (-2.3, 1.25), (-2.3, 2.4), (-3.0, 2.4)]], GOLD, normal=(0, 0, -1))

# ---------------------------------------------------------------- front: bezel and screen
bezel = [(-3.47, 1.0), (1.25, 1.0), (1.55, 1.3), (4.22, 1.3), (4.42, 1.5), (4.42, 6.55),
         (3.95, 7.12), (-3.3, 7.12), (-3.47, 6.95)]
m.decal_xy(bezel, ZF, BEZEL, lift=0.02)
m.decal_xy([(-2.94, 1.97), (3.89, 1.97), (3.89, 6.30), (-2.94, 6.30)], ZF, LCDF, lift=0.035)
m.decal_xy([(-2.71, 2.17), (3.62, 2.17), (3.62, 6.11), (-2.71, 6.11)], ZF, SCREEN, lift=0.05)

# Sound / Start / Power in their dark bed, cutting into the bezel's bottom
m.decal_xy(Model.rounded_rect(-2.5, 0.62, 1.15, 1.36, 0.3, segments=1), ZF, BED, lift=0.04)
for cx, col in ((-1.95, PILL), (-0.85, PILL), (0.4, POWER)):
    pill = [(cx - 0.38, 0.99), (cx - 0.26, 0.82), (cx + 0.26, 0.82), (cx + 0.38, 0.99),
            (cx + 0.26, 1.16), (cx - 0.26, 1.16)]
    m.extrude_xy(pill, ZF, ZF + 0.12, col, back=False, side=BED)


# ---------------------------------------------------------------- X / Y clusters
def cluster(cx, cy, r):
    s = r / 1.06
    disc = [(cx + r * math.cos(2 * math.pi * k / 10), cy + r * math.sin(2 * math.pi * k / 10)) for k in range(10)]
    m.decal_xy(disc, ZF, CLEAR, lift=0.02)
    for a in (90, 0, 270, 180):                       # 1 top, 2 right, 3 bottom, 4 left
        ux, uy = math.cos(math.radians(a)), math.sin(math.radians(a))
        px, py = -uy, ux
        tri = [(cx + ux * 0.2 * s, cy + uy * 0.2 * s),
               (cx + ux * 0.86 * s + px * 0.47 * s, cy + uy * 0.86 * s + py * 0.47 * s),
               (cx + ux * 0.86 * s - px * 0.47 * s, cy + uy * 0.86 * s - py * 0.47 * s)]
        m.extrude_xy(tri, ZF, ZF + 0.14, BUTTON, back=False, side=BED)


cluster(-4.69, 5.88, 1.02)
cluster(-4.76, 2.48, 1.1)

# ---------------------------------------------------------------- right side: speaker, A / B
spk = [(5.03 + 0.83 * math.cos(2 * math.pi * k / 10), 6.11 + 0.83 * math.sin(2 * math.pi * k / 10)) for k in range(10)]
m.decal_xy(spk, ZF, CLEAR, lift=0.02)

A, B = (5.63, 2.63), (5.03, 1.86)
dx, dy = A[0] - B[0], A[1] - B[1]
l = math.hypot(dx, dy)
ux, uy = dx / l, dy / l
pad = []
for (cx, cy), a0 in ((A, -90), (B, 90)):
    base = math.degrees(math.atan2(uy, ux))
    for k in range(4):
        a = math.radians(base + a0 + 60 * k)
        pad.append((cx + 0.6 * math.cos(a), cy + 0.6 * math.sin(a)))
m.decal_xy(pad, ZF, CLEAR, lift=0.02)
for cx, cy in (A, B):
    m.cylinder_z(cx, cy, 0.37, ZF, ZF + 0.16, BUTTON, segments=6, back=False, side=BED)

# speaker slits on the right side, level with the speaker
for k in range(4):
    z = 0.55 - 0.3 * k
    m.polygon([(W2 + 0.02, 5.35, z - 0.07), (W2 + 0.02, 5.35, z + 0.07), (W2 + 0.02, 6.0, z + 0.07),
               (W2 + 0.02, 6.0, z - 0.07)], BED, normal=(1, 0, 0))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
