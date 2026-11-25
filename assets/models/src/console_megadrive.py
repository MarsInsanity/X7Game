# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega Genesis / Mega Drive (first model): low-poly console model.

Black wedge-free slab (~28 x 7 x 21 cm) with the big raised round disc
around the cartridge slot, a smaller stepped ring inside it, the power
slider + red LED front left and reset button front right on top, the
volume slider and headphone jack on the front left, two controller ports
on the front, and the vent grooves on the top surface either side of
the disc.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

BODY = (34, 34, 38)        # the black plastic (a touch lifted so it shades)
DISC = (48, 48, 54)        # raised disc, a little lighter
RING = (66, 66, 74)        # inner stepped ring
GROOVE = (12, 12, 14)      # grooves and recesses
SLOT = (4, 4, 4)           # cartridge slot opening
FLAP = (84, 84, 92)        # slot frame
PORT = (96, 96, 104)       # controller port surrounds
PIN = (20, 20, 22)         # port insides
GREY = (140, 140, 148)     # power slider knob, reset button, volume knob
LED = (230, 24, 24)        # power LED
JACK = (170, 170, 176)     # headphone jack ring
BOTTOM = (22, 22, 24)

W, D = 28.0, 21.2          # width, depth
H_SIDE = 4.4               # vertical side height
H_TOP = 5.2                # top surface after the bevel
BEV = 0.9                  # bevel inset

m = Model('megadrive', 'console')


def plan(x0, z0, x1, z1, r, seg=2):
    """rounded rectangle in XZ"""
    return Model.rounded_rect(x0, z0, x1, z1, r, seg)


def ccw_top(pts):
    s = 0.0
    for i in range(len(pts)):
        x0, z0 = pts[i]
        x1, z1 = pts[(i + 1) % len(pts)]
        s += x0 * (-z1) - x1 * (-z0)
    return pts if s > 0 else pts[::-1]


def loft(a, ya, b, yb, color):
    """side band between outline a at height ya and outline b at yb (same
    point count, matching order)"""
    a, b = ccw_top(a), ccw_top(b)
    out = []
    n = len(a)
    for i in range(n):
        j = (i + 1) % n
        out += m.quad((a[i][0], ya, a[i][1]), (a[j][0], ya, a[j][1]),
                      (b[j][0], yb, b[j][1]), (b[i][0], yb, b[i][1]), color)
    return out


def circle(cx, cz, r, seg):
    return [(cx + r * math.cos(2 * math.pi * (i + 0.5) / seg),
             cz + r * math.sin(2 * math.pi * (i + 0.5) / seg)) for i in range(seg)]


def annulus(cx, cz, r0, r1, y, seg, color):
    a, b = circle(cx, cz, r0, seg), circle(cx, cz, r1, seg)
    out = []
    for i in range(seg):
        j = (i + 1) % seg
        out += m.polygon([(a[i][0], y, a[i][1]), (a[j][0], y, a[j][1]),
                          (b[j][0], y, b[j][1]), (b[i][0], y, b[i][1])], color, normal=(0, 1, 0))
    return out


# ---------------------------------------------------------------- body
outer = plan(-W / 2, -D / 2, W / 2, D / 2, 1.6)
inner = plan(-W / 2 + BEV, -D / 2 + BEV, W / 2 - BEV, D / 2 - BEV, 1.0)
m.prism(outer, 0.35, H_SIDE, BODY, top=False, bottom=False)
loft(outer, H_SIDE, inner, H_TOP, BODY)
m.polygon([(x, H_TOP, z) for x, z in ccw_top(inner)], BODY, normal=(0, 1, 0))
# recessed base so it stands on a darker plinth
base = plan(-W / 2 + 0.5, -D / 2 + 0.5, W / 2 - 0.5, D / 2 - 0.5, 1.2)
m.prism(base, 0.0, 0.35, BOTTOM, top=False)
loft(base, 0.35, outer, 0.35, BOTTOM)   # flat ring underneath the overhang

# ---------------------------------------------------------------- disc
CX, CZ = 0.0, -0.6
R_DISC, R_STEP = 8.6, 6.9
Y_DISC, Y_STEP = H_TOP + 0.55, H_TOP + 1.15
SEG = 20
m.prism(circle(CX, CZ, R_DISC, SEG), H_TOP, Y_DISC, DISC, bottom=False, top=False)
annulus(CX, CZ, R_DISC, R_STEP, Y_DISC, SEG, DISC)
annulus(CX, CZ, 8.1, 7.7, Y_DISC + 0.03, SEG, GROOVE)          # groove on the outer step
m.prism(circle(CX, CZ, R_STEP, SEG), Y_DISC, Y_STEP, RING, bottom=False, top=False)
annulus(CX, CZ, R_STEP, 5.2, Y_STEP, SEG, RING)
annulus(CX, CZ, 5.2, 4.6, Y_STEP + 0.03, SEG, GROOVE)          # the smaller ring
m.polygon([(x, Y_STEP, z) for x, z in ccw_top(circle(CX, CZ, 5.2, SEG))], DISC, normal=(0, 1, 0))

# cartridge slot: raised frame with the black opening and the flap seam
SW, SD = 13.6, 2.6
m.box(CX - SW / 2 - 0.4, Y_STEP, CZ - SD / 2 - 0.4, CX + SW / 2 + 0.4, Y_STEP + 0.35,
      CZ + SD / 2 + 0.4, FLAP, faces={'bottom': None})
m.decal_xz([(CX - SW / 2, CZ - SD / 2), (CX + SW / 2, CZ - SD / 2),
            (CX + SW / 2, CZ + SD / 2), (CX - SW / 2, CZ + SD / 2)], Y_STEP + 0.35, SLOT, lift=0.03)
m.decal_xz([(CX - SW / 2 + 0.3, CZ - 0.13), (CX + SW / 2 - 0.3, CZ - 0.13),
            (CX + SW / 2 - 0.3, CZ + 0.13), (CX - SW / 2 + 0.3, CZ + 0.13)], Y_STEP + 0.35, FLAP, lift=0.06)

# ---------------------------------------------------------------- top grooves
# rows of thin vent grooves on the flat top, left and right of the disc
for side in (-1, 1):
    xa, xb = side * 9.4, side * (W / 2 - BEV - 0.8)
    x0, x1 = min(xa, xb), max(xa, xb)
    for k in range(6):
        z = -8.2 + k * 1.0
        m.decal_xz([(x0, z), (x1, z), (x1, z + 0.35), (x0, z + 0.35)], H_TOP, GROOVE, lift=0.03)

# ---------------------------------------------------------------- controls on top
# power slider (front left): recess track, grey knob, red LED
m.decal_xz([(-12.0, 6.6), (-8.4, 6.6), (-8.4, 7.8), (-12.0, 7.8)], H_TOP, GROOVE, lift=0.03)
m.box(-11.7, H_TOP, 6.75, -10.3, H_TOP + 0.55, 7.65, GREY, faces={'bottom': None})
m.box(-7.6, H_TOP, 6.9, -6.9, H_TOP + 0.25, 7.5, LED, faces={'bottom': None})
# reset button (front right)
m.decal_xz([(8.6, 6.4), (11.6, 6.4), (11.6, 8.0), (8.6, 8.0)], H_TOP, GROOVE, lift=0.03)
m.box(8.9, H_TOP, 6.65, 11.3, H_TOP + 0.5, 7.75, GREY, faces={'bottom': None})

# ---------------------------------------------------------------- front panel
ZF = D / 2
# shell seam: a groove line round the front and both sides
YS0, YS1 = 3.75, 3.95
m.decal_xy([(-W / 2 + 1.6, YS0), (W / 2 - 1.6, YS0), (W / 2 - 1.6, YS1), (-W / 2 + 1.6, YS1)], ZF, GROOVE, lift=0.03)
for sx in (-1, 1):
    x = sx * (W / 2 + 0.03)
    m.polygon([(x, YS0, -D / 2 + 1.6), (x, YS0, D / 2 - 1.6), (x, YS1, D / 2 - 1.6), (x, YS1, -D / 2 + 1.6)],
              GROOVE, normal=(sx, 0, 0))
# controller ports: D-shaped (trapezoid) surrounds standing proud of the front
for px in (-0.6, 4.6):
    outer_t = [(px - 1.9, 2.9), (px + 1.9, 2.9), (px + 1.5, 1.2), (px - 1.5, 1.2)]
    m.extrude_xy(outer_t, ZF - 0.1, ZF + 0.3, PORT, back=False)
    in_t = [(px - 1.45, 2.6), (px + 1.45, 2.6), (px + 1.15, 1.5), (px - 1.15, 1.5)]
    m.decal_xy(in_t, ZF + 0.3, PIN, lift=0.03)
# volume slider + headphone jack (front left)
m.decal_xy([(-12.2, 2.3), (-8.6, 2.3), (-8.6, 2.9), (-12.2, 2.9)], ZF, GROOVE, lift=0.03)
m.box(-10.9, 2.15, ZF, -10.1, 3.05, ZF + 0.35, GREY, faces={'back': None})
m.cylinder_z(-6.6, 2.6, 0.45, ZF - 0.1, ZF + 0.2, JACK, segments=8, back=False)
m.cylinder_z(-6.6, 2.6, 0.22, ZF + 0.2, ZF + 0.25, SLOT, segments=6, back=False, side=False)

print(m.stats())
m.save()
