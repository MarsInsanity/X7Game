# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega Game Gear (1990): charcoal-grey landscape handheld, about
21.0 x 11.3 x 3.6 cm. Stands upright, screen facing +Z.

Measured from Commons photos (a straight-on front view and several
three-quarter views of the front, the back and the top edge), in cm from
the bottom centre of the front face:
  * outline: a long slab with big rounded corners (top 1.8, bottom 2.2),
    every edge chamfered so the slab reads as rounded
  * glossy black screen panel: a trapezoid 15.6 cm wide at the top edge
    (y 10.8), 7.6 cm wide at the bottom (y 2.8), rounded lower corners
  * screen: grey frame x -4.0..3.9, y 4.0..10.2, dark LCD inside it
  * D-pad: a round black rocker disc, centre (-8.5, 6.8), radius 1.25,
    sitting in a darker well, a lighter cross on it
  * buttons 1 and 2: black, radius 0.68, at (7.4, 6.0) and (9.0, 7.25)
  * Start: small blue button at (7.6, 9.1), in a notch of the panel edge
  * speaker grille: a patch of dots below the D-pad, around (-7.4, 2.25)
  * back: two battery doors (one per grip) and, at the top, the cartridge
    bay: an open recess 7.0 cm wide running 3.9 cm down from the top edge,
    with the slot continuing 1.3 cm further under a lip of the back shell
  * top edge: volume wheel, headphone and extension ports on the left,
    DC jack and the orange-red power switch on the right

The cartridge goes in from the top, label facing the back, and stays
1.7 cm proud of the top edge with its label visible in the bay. No moving
parts. No text or logos."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (66, 66, 72)          # charcoal grey shell
PANEL = (16, 16, 18)         # glossy black screen panel, buttons, D-pad
FRAME = (112, 112, 118)      # grey screen frame
LCD = (46, 58, 54)           # LCD, dark grey-green
WELL = (36, 36, 40)          # D-pad well, battery door seams, grille dots
CROSS = (58, 58, 64)         # D-pad cross (a soft emboss on the black disc)
BLUE = (40, 92, 214)         # Start button
LED = (190, 36, 30)          # power lamp
CAVITY = (18, 18, 20)        # cartridge bay and slot
SWITCH = (236, 88, 44)       # power switch on the top edge
DOOR = (78, 78, 86)          # battery doors (a shade lighter than the shell)

W, H = 21.0, 11.3
ZF, ZB = 1.8, -1.8           # front / back faces
BF, BB = 0.5, 0.35           # front / back chamfer (depth = inset)
R_TOP, R_BOT = 2.0, 2.8
SEG = 4

# cartridge bay at the top of the back
BXL, BXR = -3.9, 3.1         # inner sides (cartridge 6.8 wide, centred at x = -0.4)
ZFL = -0.65                  # bay floor (towards the front)
ZSK = -1.62                  # inner face of the back-shell lip
YLIP = H - 3.9               # where the open bay ends and the lip starts
YBOT = 6.1                   # bottom of the slot


def outline(inset, seg=SEG):
    """Counter-clockwise (seen from +Z) outline of the slab, shrunk by
    `inset`, with the bay's two x positions on the top edge."""
    x0, y0, x1, y1 = -W / 2 + inset, inset, W / 2 - inset, H - inset
    rb, rt = R_BOT - inset, R_TOP - inset
    pts = []
    for cx, cy, r, a0 in ((x1 - rb, y0 + rb, rb, 270), (x1 - rt, y1 - rt, rt, 0)):
        for s in range(seg + 1):
            a = math.radians(a0 + 90 * s / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pts += [(BXR, y1), (BXL, y1)]
    for cx, cy, r, a0 in ((x0 + rt, y1 - rt, rt, 90), (x0 + rb, y0 + rb, rb, 180)):
        for s in range(seg + 1):
            a = math.radians(a0 + 90 * s / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


BAY_I = 2 * (SEG + 1)        # index of (BXR, top) in the outline; next is (BXL, top)

m = Model('gamegear', 'console')

outer = outline(0.0)
front = outline(BF)
back = outline(BB)
n = len(outer)
zfs, zbs = ZF - BF, ZB + BB  # where the straight sides meet the chamfers


def ring(a, za, b, zb, color, skip=()):
    """Quads joining outline a at depth za to outline b at depth zb (zb in
    front of za)."""
    for i in range(n):
        if i in skip:
            continue
        j = (i + 1) % n
        m.quad((b[i][0], b[i][1], zb), (a[i][0], a[i][1], za),
               (a[j][0], a[j][1], za), (b[j][0], b[j][1], zb), color)


# ---- shell: front face, chamfers, sides, back face with the bay notch
m.polygon([(x, y, ZF) for x, y in front], BODY, normal=(0, 0, 1))
ring(outer, zfs, front, ZF, BODY)                       # front chamfer
for i in range(n):                                      # straight sides
    j = (i + 1) % n
    zb = ZFL if i == BAY_I else zbs                     # over the bay only the front part
    m.quad((outer[i][0], outer[i][1], zfs), (outer[i][0], outer[i][1], zb),
           (outer[j][0], outer[j][1], zb), (outer[j][0], outer[j][1], zfs), BODY)
ring(back, ZB, outer, zbs, BODY, skip=(BAY_I,))         # back chamfer
bk = back[:BAY_I + 1] + [(BXR, YLIP), (BXL, YLIP)] + back[BAY_I + 1:]
m.polygon([(x, y, ZB) for x, y in bk], BODY, normal=(0, 0, -1))

# ---- cartridge bay and slot: a dark cavity open at the top and the back
m.polygon([(BXL, YBOT, ZFL), (BXR, YBOT, ZFL), (BXR, H, ZFL), (BXL, H, ZFL)], CAVITY, normal=(0, 0, -1))
wall = [(YLIP, ZB), (H - BB, ZB), (H, ZB + BB), (H, ZFL), (YBOT, ZFL), (YBOT, ZSK), (YLIP, ZSK)]
m.polygon([(BXL, y, z) for y, z in wall], WELL, normal=(1, 0, 0))
m.polygon([(BXR, y, z) for y, z in wall], WELL, normal=(-1, 0, 0))
m.polygon([(BXL, YBOT, ZSK), (BXR, YBOT, ZSK), (BXR, YBOT, ZFL), (BXL, YBOT, ZFL)], CAVITY, normal=(0, 1, 0))
m.polygon([(BXL, YBOT, ZSK), (BXR, YBOT, ZSK), (BXR, YLIP, ZSK), (BXL, YLIP, ZSK)], CAVITY, normal=(0, 0, 1))
m.polygon([(BXL, YLIP, ZB), (BXR, YLIP, ZB), (BXR, YLIP, ZSK), (BXL, YLIP, ZSK)], BODY, normal=(0, 1, 0))

# ---- glossy black screen panel (trapezoid, rounded lower corners)
panel = [(-7.8, 10.7), (-7.05, 10.3), (-6.5, 8.6), (-5.6, 5.6), (-4.75, 3.55), (-4.3, 3.0),
         (-3.7, 2.8), (3.7, 2.8), (4.3, 3.0), (4.75, 3.55), (5.6, 5.6), (6.5, 8.6),
         (6.9, 9.9), (7.25, 10.35), (7.8, 10.7)]
m.decal_xy(panel, ZF, PANEL, lift=0.03)
m.decal_xy([(-4.0, 4.0), (3.9, 4.0), (3.9, 10.2), (-4.0, 10.2)], ZF, FRAME, lift=0.06)
m.decal_xy([(-3.5, 4.6), (3.4, 4.6), (3.4, 9.7), (-3.5, 9.7)], ZF, LCD, lift=0.09)
m.decal_xy([(-5.2, 7.85), (-4.9, 7.85), (-4.9, 8.15), (-5.2, 8.15)], ZF, LED, lift=0.06)

# ---- D-pad: black rocker disc in a darker well, lighter cross on top
dx, dy = -8.5, 6.8
m.decal_xy([(dx + 1.5 * math.cos(2 * math.pi * (i + 0.5) / 12), dy + 1.5 * math.sin(2 * math.pi * (i + 0.5) / 12))
            for i in range(12)], ZF, WELL, lift=0.03)
m.cylinder_z(dx, dy, 1.25, ZF, ZF + 0.3, PANEL, segments=10, back=False)
a, b = 0.3, 0.95
cross = [(a, -b), (a, -a), (b, -a), (b, a), (a, a), (a, b), (-a, b), (-a, a), (-b, a), (-b, -a), (-a, -a), (-a, -b)]
m.decal_xy([(dx + x, dy + y) for x, y in cross], ZF + 0.3, CROSS, lift=0.03)

# ---- the sculpted grip creases: a crescent under the D-pad and one
# under buttons 1 and 2
def arc(cx, cy, r, a0, a1, w=0.13, seg=6):
    pts_o, pts_i = [], []
    for k in range(seg + 1):
        a = math.radians(a0 + (a1 - a0) * k / seg)
        pts_o.append((cx + (r + w) * math.cos(a), cy + (r + w) * math.sin(a)))
        pts_i.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    m.decal_xy(pts_o + pts_i[::-1], ZF, WELL, lift=0.03)


arc(dx, dy, 2.0, 228, 330)
arc(8.2, 6.6, 1.95, 200, 335)

# ---- buttons 1 and 2 (black) and the small blue Start button
for bx, by in ((7.4, 6.0), (9.0, 7.25)):
    m.cylinder_z(bx, by, 0.68, ZF, ZF + 0.35, PANEL, segments=8, back=False)
m.cylinder_z(7.6, 9.1, 0.45, ZF, ZF + 0.22, BLUE, segments=8, back=False)

# ---- speaker grille: a patch of dots below the D-pad
for r in range(4):
    for c in range(5):
        x, y = -8.4 + c * 0.42 + (0.21 if r % 2 else 0), 1.6 + r * 0.42
        s = 0.09
        m.decal_xy([(x - s, y - s), (x + s, y - s), (x + s, y + s), (x - s, y + s)], ZF, WELL, lift=0.03)

# ---- back: the two battery doors, each with a dark seam round it
for x0, x1 in ((-9.7, -4.5), (3.8, 9.7)):
    for k, col in ((0.0, WELL), (0.12, DOOR)):
        o = Model.rounded_rect(x0 + k, 1.2 + k, x1 - k, 6.9 - k, 0.7 - k, 1)
        m.polygon([(x, y, ZB - 0.03 - k * 0.2) for x, y in o], col, normal=(0, 0, -1))

# ---- top edge ports (rear half of the top face)
def top_decal(xa, xb, za, zb, col, lift=0.03):
    m.decal_xz([(xa, zb), (xb, zb), (xb, za), (xa, za)], H, col, lift=lift)


top_decal(-8.6, -7.9, -1.0, -0.2, WELL)          # volume wheel
top_decal(-7.3, -6.9, -0.8, -0.4, WELL)          # headphone jack
top_decal(-6.0, -4.6, -0.85, -0.35, WELL)        # extension port
top_decal(5.6, 6.1, -0.85, -0.35, WELL)          # DC jack
top_decal(7.4, 8.4, -0.9, -0.3, WELL)            # power switch slot
top_decal(7.5, 7.9, -0.8, -0.4, SWITCH, 0.06)    # power switch

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
