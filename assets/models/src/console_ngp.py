# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly SNK Neo Geo Pocket (monochrome, carbon black), handheld, standing
upright, screen facing +Z.

Real size 13.0 x 7.9 x 2.5 cm (body; the buttons stand a little proud).
Measured from Wikimedia Commons photos (flat front, flat back, the four
edges): a landscape slab with a flat top edge, small top corners and big
elliptical bottom corners; the large, almost square black screen bezel
filling the middle up to the top edge (slightly left of centre); the micro-
switched stick in a round gate upper left with the 4 x 4 speaker holes under
it; the pill-shaped power switch and lamp top left; A (lower left) and B
(upper right) on the right with the small option button above B and 3 x 3
little bumps below. Back: the cartridge window (a pocket at the top centre
that shows the inserted card), the AA battery cover on the right half (seen
from behind: left), the round coin-cell cover lower left (seen from behind:
right), the grey rating sticker in the middle and the finger notch at the
bottom centre. Top edge: the cartridge slot along the back and the link
port.

Insertion: the cartridge (5.7 x 4.6 x 0.6) goes straight DOWN into the slot
at the top back, label facing the back (-Z); its top stands 0.35 cm proud
and its upper part shows through the back pocket. No moving parts.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (70, 73, 90)         # carbon-pattern shell, dark blue-grey
COVER = (44, 46, 56)        # battery cover / pocket walls, darker
BEZEL = (16, 16, 20)        # black glass around the LCD
LCD = (138, 146, 132)       # monochrome LCD, grey-green
BTN = (28, 28, 32)          # black buttons, stick, power switch
CAP = (54, 54, 62)          # stick cap top
GATE = (86, 88, 102)      # grey stick gate ring
HOLE = (10, 10, 12)         # slot cavity, speaker holes, ports, screws
LED = (170, 44, 34)         # power lamp
STICKER = (176, 178, 184)   # rating sticker on the back
COIN = (78, 80, 94)         # coin-cell cover

m = Model('ngp', 'console')

W, H, D = 13.0, 7.9, 2.5
X0, X1 = -W / 2, W / 2
ZB, ZF = -D / 2, D / 2
BEV = 0.3                   # rounded front edge
RT = 0.5                    # top corner radius
RX, RY = 1.6, 2.6           # elliptical bottom corners

# slot (cartridge 5.7 x 4.6 x 0.6, seated with its bottom at YS)
SW = 2.95                   # slot half width (card half width 2.85)
ZS0, ZS1 = -1.0, -0.2       # slot back / front wall (card z -0.9 .. -0.3)
YS = 3.65                   # slot floor
YP = 6.2                    # ledge of the back pocket (window onto the card)
# finger notch at the bottom of the back
NW, NH, ND, NR = 2.6, 2.2, 0.55, 0.6


def arc(cx, cy, rx, ry, a0, a1, n):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def outline(inset=0.0):
    """Front outline (CCW), optionally inset (for the front face)."""
    rt, rx, ry = RT - inset, RX - inset, RY - inset
    return (arc(X1 - RX, RY, rx, ry, 270, 360, 4) + arc(X1 - RT, H - RT, rt, rt, 0, 90, 2)
            + arc(X0 + RT, H - RT, rt, rt, 90, 180, 2) + arc(X0 + RX, RY, rx, ry, 180, 270, 4))


def sides(pts, z0, z1, col, skip=(), zfn=None):
    """Side walls of a CCW XY outline from z0 to z1 (edge i = pts[i] -> pts[i+1]);
    edges in `skip` are left out; zfn(i) may give another (z0, z1)."""
    n = len(pts)
    for i in range(n):
        if i in skip:
            continue
        a, b = pts[i], pts[(i + 1) % n]
        za, zb = zfn(i) if zfn and zfn(i) else (z0, z1)
        dx, dy = b[0] - a[0], b[1] - a[1]
        m.polygon([(a[0], a[1], za), (b[0], b[1], za), (b[0], b[1], zb), (a[0], a[1], zb)], col,
                  normal=(dy, -dx, 0))


def face(pts, z, col, normal):
    m.polygon([(x, y, z) for x, y in pts], col, normal=(0, 0, normal))


def back_decal(pts, col, lift=0.02, z=ZB):
    face(pts, z - lift, col, -1)


def ngon(cx, cy, r, n, rot=0.0):
    return [(cx + r * math.cos(math.radians(rot + 360 * i / n)), cy + r * math.sin(math.radians(rot + 360 * i / n)))
            for i in range(n)]


def ring(outer, oz, inner, iz, color):
    """Bevel band between two matching outlines (CCW seen from +Z)."""
    n = len(outer)
    for i in range(n):
        a, b = outer[i], outer[(i + 1) % n]
        c, d = inner[(i + 1) % n], inner[i]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        m.polygon([(a[0], a[1], oz), (b[0], b[1], oz), (c[0], c[1], iz), (d[0], d[1], iz)], color,
                  normal=(dy / l, -dx / l, 1.0))


# ---------------------------------------------------------------- body
# front slab: full outline from the slot's front wall to the screen face
out = outline()
inn = outline(BEV)
sides(out, ZS1, ZF - BEV, BODY)
ring(out, ZF - BEV, inn, ZF, BODY)
face(inn, ZF, BODY, 1)

# lower back (below the slot floor), with the finger notch at the bottom
lower = ([(X0, YS)] + arc(X0 + RX, RY, RX, RY, 180, 270, 4) + [(-NW, 0), (NW, 0)]
         + arc(X1 - RX, RY, RX, RY, 270, 360, 4) + [(X1, YS)])
top_edge = len(lower) - 1
notch_edge = lower.index((-NW, 0))
sides(lower, ZB, ZS1, BODY, skip=(top_edge,),
      zfn=lambda i: (ZB + ND, ZS1) if i == notch_edge else None)
notch = ([(NW, 0)] + arc(NW - NR, NH - NR, NR, NR, 0, 90, 2) + arc(-NW + NR, NH - NR, NR, NR, 90, 180, 2)
         + [(-NW, 0)])
# back face = lower outline minus the notch (U shape)
u = lower[:notch_edge + 1] + notch[::-1][1:-1] + lower[notch_edge + 1:]
face(u, ZB, BODY, -1)
# notch walls (seen from behind they face inwards) and floor
for i in range(len(notch) - 1):
    a, b = notch[i], notch[i + 1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    m.polygon([(a[0], a[1], ZB), (b[0], b[1], ZB), (b[0], b[1], ZB + ND), (a[0], a[1], ZB + ND)], BODY,
              normal=(-dy, dx, 0))
face(notch, ZB + ND, COVER, -1)

# upper back blocks either side of the slot
left = [(X0, YS), (-SW, YS), (-SW, H)] + arc(X0 + RT, H - RT, RT, RT, 90, 180, 2)
right = [(SW, YS), (X1, YS)] + arc(X1 - RT, H - RT, RT, RT, 0, 90, 2) + [(SW, H)]
sides(left, ZB, ZS1, BODY, skip=(0, 1))
sides(right, ZB, ZS1, BODY, skip=(0, 5))
face(left, ZB, BODY, -1)
face(right, ZB, BODY, -1)

# back wall under the pocket (its top is the ledge)
m.box(-SW, YS, ZB, SW, YP, ZS0, BODY,
      faces={'top': COVER, 'front': HOLE, 'bottom': None, 'left': None, 'right': None})

# slot / pocket insides
for sx, nx in ((-SW, 1), (SW, -1)):
    m.polygon([(sx, YS, ZS0), (sx, YS, ZS1), (sx, H, ZS1), (sx, H, ZS0)], HOLE, normal=(nx, 0, 0))
    m.polygon([(sx, YP, ZB), (sx, YP, ZS0), (sx, H, ZS0), (sx, H, ZB)], COVER, normal=(nx, 0, 0))
m.polygon([(-SW, YS, ZS1), (SW, YS, ZS1), (SW, YP, ZS1), (-SW, YP, ZS1)], HOLE, normal=(0, 0, -1))
m.polygon([(-SW, YP, ZS1), (SW, YP, ZS1), (SW, H, ZS1), (-SW, H, ZS1)], COVER, normal=(0, 0, -1))
m.polygon([(-SW, YS, ZS0), (SW, YS, ZS0), (SW, YS, ZS1), (-SW, YS, ZS1)], HOLE, normal=(0, 1, 0))

# ---------------------------------------------------------------- front
# screen: black bezel almost reaching the top edge, grey-green LCD
m.decal_xy(Model.rounded_rect(-3.25, 1.45, 3.0, 7.62, 0.3, 2), ZF, BEZEL, lift=0.02)
m.decal_xy([(-2.7, 2.15), (2.65, 2.15), (2.65, 7.08), (-2.7, 7.08)], ZF, LCD, lift=0.04)

# power switch (pill), line to the lamp, lamp
m.decal_xy(Model.rounded_rect(-5.9, 6.8, -4.95, 7.2, 0.19, 2), ZF, BTN, lift=0.04)
m.decal_xy([(-4.95, 6.97), (-4.2, 6.97), (-4.2, 7.03), (-4.95, 7.03)], ZF, BTN, lift=0.03)
m.decal_xy(ngon(-4.06, 7.0, 0.11, 6), ZF, LED, lift=0.03)

# stick: grey gate ring, dark well, black stick with a lighter cap
JX, JY = -4.57, 5.0
m.decal_xy(ngon(JX, JY, 1.22, 8, 22.5), ZF, GATE, lift=0.02)
m.decal_xy(ngon(JX, JY, 0.98, 8, 22.5), ZF, HOLE, lift=0.04)
m.cylinder_z(JX, JY, 0.74, ZF, ZF + 0.42, BTN, segments=8, back=False)
m.decal_xy(ngon(JX, JY, 0.42, 8, 22.5), ZF + 0.42, CAP, lift=0.02)

# speaker: 4 x 4 holes under the stick
for i in range(4):
    for j in range(4):
        x, y = JX - 0.45 + 0.3 * i, 1.88 + 0.3 * j
        m.decal_xy([(x - 0.07, y - 0.07), (x + 0.07, y - 0.07), (x + 0.07, y + 0.07), (x - 0.07, y + 0.07)],
                   ZF, HOLE, lift=0.02)

# A (lower left), B (upper right), option (small, above B)
m.cylinder_z(4.17, 4.54, 0.52, ZF, ZF + 0.28, BTN, segments=8, back=False)
m.cylinder_z(5.51, 5.46, 0.52, ZF, ZF + 0.28, BTN, segments=8, back=False)
m.cylinder_z(5.63, 7.0, 0.3, ZF, ZF + 0.16, BTN, segments=6, back=False)

# 3 x 3 little bumps below the buttons
for x in (3.94, 4.82, 5.67):
    for y in (1.27, 2.26, 3.17):
        m.decal_xy(ngon(x, y, 0.09, 4, 45), ZF, BTN, lift=0.02)

# ---------------------------------------------------------------- top edge
m.decal_xz([(3.65, 0.7), (4.95, 0.7), (4.95, 0.2), (3.65, 0.2)], H, HOLE, lift=0.02)   # link port

# ---------------------------------------------------------------- back
# (x is mirrored seen from behind: +x is on the left)
back_decal([(3.3, 1.3), (6.1, 1.3), (6.1, 7.2), (3.3, 7.2)], COVER)               # AA battery cover
back_decal([(3.95, 3.3), (5.45, 3.3), (5.45, 5.95), (3.95, 5.95)], BODY, lift=0.04)  # its inset grip
back_decal(ngon(-4.74, 2.33, 1.4, 10), COIN)                                    # coin-cell cover
back_decal([(-5.5, 2.25), (-4.0, 2.25), (-4.0, 2.41), (-5.5, 2.41)], HOLE, lift=0.04)
back_decal([(-2.75, 2.9), (2.75, 2.9), (2.75, 5.5), (-2.75, 5.5)], STICKER)        # rating sticker
for x, y in ((-3.6, 6.9), (-5.72, 3.95), (-3.2, 0.92), (3.35, 0.85)):           # screws
    back_decal(ngon(x, y, 0.2, 6), HOLE)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
