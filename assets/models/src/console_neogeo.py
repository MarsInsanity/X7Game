# SPDX-License-Identifier: GPL-3.0-or-later
"""SNK Neo Geo AES (home console): low-poly console model.

Big black slab (~32.5 x 6 x 23.7 cm) with chamfered front edge and slightly
bevelled sides, the raised cartridge housing at the back of the top with the
very wide slot and its grey dust flap, the power slider with the red LED and
the reset button on the top front, two large trapezoid controller ports and
the memory card slot on the front face, and the gold / red accent lines.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

BODY = (36, 36, 40)        # black plastic, lifted a little so it shades
HOUSING = (60, 60, 68)     # raised cartridge housing
GROOVE = (10, 10, 12)      # seams, vents, recesses
SLOT = (0, 0, 0)           # slot opening
FLAP = (104, 104, 112)     # dust flap / slider knob
PORT = (156, 156, 164)     # controller port surrounds (metal)
PIN = (22, 22, 26)         # port insides
GOLD = (214, 172, 58)      # gold accents
RED = (224, 32, 32)        # red accent stripe and LED
BOTTOM = (16, 16, 18)

W, D = 32.5, 23.7
H_FRONT = 3.6              # front face height before the chamfer
H_TOP = 5.0                # main top surface
CH = 2.6                   # front chamfer depth
BEV = 0.6                  # side bevel inset
Y0 = 0.35                  # base plinth height

m = Model('neogeo', 'console')


def ccw_top(pts):
    s = 0.0
    for i in range(len(pts)):
        x0, z0 = pts[i]
        x1, z1 = pts[(i + 1) % len(pts)]
        s += x0 * (-z1) - x1 * (-z0)
    return pts if s > 0 else pts[::-1]


def loft(a, ya, b, yb, color):
    """side band between outline a at height ya and outline b at yb (same
    point count and order)"""
    a, b = ccw_top(a), ccw_top(b)
    out = []
    n = len(a)
    for i in range(n):
        j = (i + 1) % n
        out += m.quad((a[i][0], ya, a[i][1]), (a[j][0], ya, a[j][1]),
                      (b[j][0], yb, b[j][1]), (b[i][0], yb, b[i][1]), color)
    return out


def chamfer_rect(x0, z0, x1, z1, c):
    """rectangle in XZ with 45-degree cut corners (8 points)"""
    return [(x0 + c, z0), (x1 - c, z0), (x1, z0 + c), (x1, z1 - c),
            (x1 - c, z1), (x0 + c, z1), (x0, z1 - c), (x0, z0 + c)]


def rect_xz(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def rect_xy(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ---------------------------------------------------------------- body
ZF = D / 2
outer = chamfer_rect(-W / 2, -D / 2, W / 2, D / 2, 0.8)
top = chamfer_rect(-W / 2 + BEV, -D / 2 + BEV, W / 2 - BEV, D / 2 - CH, 0.5)
m.prism(outer, Y0, H_FRONT, BODY, top=False, bottom=False)
loft(outer, H_FRONT, top, H_TOP, BODY)
m.polygon([(x, H_TOP, z) for x, z in ccw_top(top)], BODY, normal=(0, 1, 0))
base = chamfer_rect(-W / 2 + 0.6, -D / 2 + 0.6, W / 2 - 0.6, D / 2 - 0.6, 0.6)
m.prism(base, 0.0, Y0, BOTTOM, top=False)
loft(base, Y0, outer, Y0, BOTTOM)

# ---------------------------------------------------------------- cartridge housing
# raised block over the rear part of the top, front edge sloped
HX = 13.4                  # half width
HZ0, HZ1 = -D / 2 + BEV + 0.6, -0.6
HY = H_TOP + 1.0
hb = chamfer_rect(-HX, HZ0, HX, HZ1, 0.6)
ht = chamfer_rect(-HX + 0.4, HZ0 + 0.3, HX - 0.4, HZ1 - 1.1, 0.4)
loft(hb, H_TOP, ht, HY, HOUSING)
m.polygon([(x, HY, z) for x, z in ccw_top(ht)], HOUSING, normal=(0, 1, 0))

# the wide slot (Neo Geo carts are big) and its grey dust flap
SCZ = (HZ0 + HZ1 - 0.8) / 2
SX, SD = 10.8, 1.7
m.decal_xz(rect_xz(-SX - 0.35, SCZ - SD / 2 - 0.35, SX + 0.35, SCZ + SD / 2 + 0.35), HY, GROOVE, lift=0.03)
m.decal_xz(rect_xz(-SX, SCZ - SD / 2, SX, SCZ + SD / 2), HY, FLAP, lift=0.06)
m.decal_xz(rect_xz(-SX + 0.2, SCZ - 0.1, SX - 0.2, SCZ + 0.1), HY, SLOT, lift=0.09)
# vent grooves on the housing either side of the slot area, front and back
for zz in (HZ0 + 0.8, HZ1 - 1.9):
    m.decal_xz(rect_xz(-SX, zz, SX, zz + 0.18), HY, GROOVE, lift=0.03)

# ---------------------------------------------------------------- top front controls
# power slider (left) with the red LED, reset button next to it
m.decal_xz(rect_xz(-13.6, 3.2, -9.6, 4.6), H_TOP, GROOVE, lift=0.03)
m.box(-13.2, H_TOP, 3.4, -11.6, H_TOP + 0.5, 4.4, FLAP, faces={'bottom': None})
m.box(-8.8, H_TOP, 3.6, -8.0, H_TOP + 0.22, 4.2, RED, faces={'bottom': None})
m.decal_xz(rect_xz(-6.9, 3.2, -4.7, 4.6), H_TOP, GROOVE, lift=0.03)
m.box(-6.6, H_TOP, 3.45, -5.0, H_TOP + 0.4, 4.35, FLAP, faces={'bottom': None})
# gold accent plate on the top right (plain, no text)
m.decal_xz(rect_xz(6.2, 2.6, 13.6, 5.2), H_TOP, GOLD, lift=0.03)
m.decal_xz(rect_xz(6.6, 3.0, 13.2, 4.8), H_TOP, BODY, lift=0.06)
m.decal_xz(rect_xz(6.6, 3.7, 13.2, 4.1), H_TOP, RED, lift=0.09)

# ---------------------------------------------------------------- front face
# gold and red accent lines along the front
m.decal_xy(rect_xy(-W / 2 + 1.2, 3.02, W / 2 - 1.2, 3.32), ZF, GOLD, lift=0.03)
m.decal_xy(rect_xy(-W / 2 + 1.2, 2.8, W / 2 - 1.2, 2.95), ZF, RED, lift=0.03)
# memory card slot (left)
m.decal_xy(rect_xy(-13.2, 1.3, -6.0, 2.2), ZF, GROOVE, lift=0.03)
m.decal_xy(rect_xy(-12.8, 1.6, -6.4, 1.9), ZF, SLOT, lift=0.06)
# two big trapezoid controller ports (right of centre)
for px in (3.6, 9.6):
    outer_t = [(px - 2.4, 2.45), (px + 2.4, 2.45), (px + 2.0, 0.85), (px - 2.0, 0.85)]
    m.extrude_xy(outer_t, ZF - 0.1, ZF + 0.3, PORT, back=False)
    in_t = [(px - 1.95, 2.15), (px + 1.95, 2.15), (px + 1.65, 1.15), (px - 1.65, 1.15)]
    m.decal_xy(in_t, ZF + 0.3, PIN, lift=0.03)
# shell seam round the sides
for sx in (-1, 1):
    x = sx * (W / 2 + 0.03)
    m.polygon([(x, 2.85, -D / 2 + 0.9), (x, 2.85, D / 2 - 0.9), (x, 3.05, D / 2 - 0.9), (x, 3.05, -D / 2 + 0.9)],
              GROOVE, normal=(sx, 0, 0))

# side vents (rows of short slots near the back of each side)
for sx in (-1, 1):
    x = sx * (W / 2 + 0.03)
    for k in range(5):
        z0 = -D / 2 + 2.4 + k * 1.1
        m.polygon([(x, 1.2, z0), (x, 1.2, z0 + 0.45), (x, 2.4, z0 + 0.45), (x, 2.4, z0)],
                  GROOVE, normal=(sx, 0, 0))

# ---------------------------------------------------------------- back panel
ZB = -D / 2
for x0, x1 in ((-11.0, -8.6), (-6.0, -3.0), (4.0, 5.2), (6.4, 7.6)):
    m.polygon([(x1, 1.2, ZB - 0.03), (x0, 1.2, ZB - 0.03), (x0, 2.4, ZB - 0.03), (x1, 2.4, ZB - 0.03)],
              GROOVE, normal=(0, 0, -1))
m.polygon([(-3.6, 1.5, ZB - 0.06), (-5.4, 1.5, ZB - 0.06), (-5.4, 2.1, ZB - 0.06), (-3.6, 2.1, ZB - 0.06)],
          PORT, normal=(0, 0, -1))

print(m.stats())
m.save()
