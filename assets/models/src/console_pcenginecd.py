# SPDX-License-Identifier: GPL-3.0-or-later
"""NEC TurboGrafx-CD, assembled as it stands on a table: low poly.

Built from Wikimedia Commons photos of the real unit (the assembled system
front-left / front-right, the interface unit alone front-left / front-right /
back-left, and the CD-ROM player alone from three sides):

  * the interface unit: a long, low base plate (36.5 x 16.5 x 2.8 cm) with
    the POWER slide switch in the middle of its front edge, and behind it the
    tall cradle (17 x 16.4 cm, 11.8 cm high) that holds the CD player in an
    open-topped tray: side walls whose front corners slope down to the tray
    floor, slatted vents on the sloping fronts of both side walls
  * the TurboGrafx-16 console docked on the base plate (it plugs into the
    cradle at the back): tall front face, rounded front edge with four
    grooves, the HuCard pocket right of centre with its finger scoop and the
    raised hood behind it, the badge on the top left (plain colours, no
    text), its power switch above the base's, the round controller port
    low on the right
  * the CD-ROM player sitting in the cradle (14.2 x 14.2 x 3.8 cm): a black
    square box whose top is almost all a round lid (12 cm) with a dark band
    across it and two smoked windows at its ends; the round red track
    display at the front left corner, the play / stop / skip buttons at the
    front right corner, a hinge bar behind the lid

Moving part "lid": the round lid, hinged on a bar behind it (pivot behind
its back edge, on the top surface). Under it is the real disc well: a
20-sided pocket 12.4 cm across (the 12 cm disc has 0.2 cm all round), dark
walls, a floor and the spindle that goes through the disc's centre hole.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

IFU = (40, 40, 46)          # interface unit: base plate and cradle
TG = (62, 62, 68)           # the docked TurboGrafx-16
PLAYER = (50, 50, 57)       # CD-ROM player body
LID = (66, 66, 76)          # the round lid (a touch lighter, glossy)
WINDOW = (96, 98, 112)      # smoked windows at the ends of the lid band
GROOVE = (16, 16, 18)       # grooves, seams, vents, lid band, hinge bar
CAVITY = (8, 8, 10)         # well walls, slot, port, pocket floor
FLOOR = (30, 30, 36)        # well floor, lid underside
LIGHT = (112, 114, 126)     # lid windows, switches, buttons
SPINDLE = (178, 178, 186)   # spindle hub
DISPLAY = (124, 18, 24)     # red track display
ORANGE = (240, 112, 32)     # badge
RED = (214, 40, 30)         # badge disc

m = Model('pcenginecd', 'console')

# ---------------------------------------------------------------- layout (cm)
WB = 18.25                  # half width of base plate and console
ZF, ZB = 10.0, -6.5         # front / back of base plate and console
HP = 2.8                    # base plate height
HF, HE, HT = 6.0, 6.9, 7.6  # console: top of front face, end of rounded edge, top
ZE, ZS = 9.3, 6.5           # console: rounded edge ends / groove slope ends (z)

CW = 8.5                    # cradle half width
CT = 1.2                    # cradle wall thickness
CZ0, CZ1 = -22.9, ZB        # cradle back / front
HFL = 9.4                   # tray floor = player bottom
HW = 11.8                   # cradle wall top

PW = 7.1                    # player half width
PZ1 = -7.3                  # player front
PZ0 = PZ1 - 14.2            # player back
PC = (PZ0 + PZ1) / 2        # player / well centre z  (-14.8)
HPT = HFL + 3.8             # player top (13.2)
RW = 6.2                    # well radius (20-gon, vertices on the disc's)
NW = 20
HWF = HPT - 1.2             # well floor (12.0)
RL, NL = 6.05, 16           # lid radius / segments
HL0, HL1 = HPT - 0.6, HPT + 0.05   # lid bottom / top


def lift_poly(pts, color, normal, lift=0.03):
    n = normal
    l = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
    d = (n[0] / l * lift, n[1] / l * lift, n[2] / l * lift)
    return m.polygon([(p[0] + d[0], p[1] + d[1], p[2] + d[2]) for p in pts], color, normal=normal)


def circle(cx, cz, r, n, a0=0.0):
    return [(cx + r * math.cos(a0 + 2 * math.pi * i / n), cz + r * math.sin(a0 + 2 * math.pi * i / n))
            for i in range(n)]


# ================================================================ base plate
m.box(-WB, 0, ZB, WB, HP, ZF, IFU, faces={'bottom': None})
m.decal_xy([(-WB + 0.2, 0.55), (WB - 0.2, 0.55), (WB - 0.2, 0.7), (-WB + 0.2, 0.7)], ZF, GROOVE)
# POWER slide switch (the interface unit's; it works the console's switch)
m.decal_xy([(-0.9, 1.0), (0.9, 1.0), (0.9, 2.3), (-0.9, 2.3)], ZF, CAVITY)
m.box(-0.75, 1.15, ZF, 0.05, 2.15, ZF + 0.35, LIGHT, faces={'back': None, 'bottom': None})

# ================================================================ TurboGrafx-16
SX0, SX1 = 2.5, 10.2        # HuCard pocket
HZ0, HZ1 = -4.0, 1.5        # hood back / front (the slot opening)
HH = 8.3                    # hood top
main = [(ZF, HP), (ZF, HF), (ZE, HE), (ZS, HT), (-5.0, HT), (ZB, 6.6), (ZB, HP)]
m.extrude_yz(main, -WB, SX0, TG)
m.extrude_yz(main, SX1, WB, TG)
pocket = [(ZF, HP), (ZF, HF), (HZ1, HF), (HZ1, HT), (-5.0, HT), (ZB, 6.6), (ZB, HP)]
m.extrude_yz(pocket, SX0, SX1, TG)
# the D-shaped hood the card slides under: straight front over the slot, round back
_hc = (SX0 + SX1) / 2
_hr = (SX1 - SX0) / 2 + 0.3
_hood = [(_hc - _hr, HZ1), (_hc + _hr, HZ1)] +     [(_hc + _hr * math.cos(math.pi * k / 6), HZ1 - 1.2 - _hr * 0.75 * math.sin(math.pi * k / 6)) for k in range(7)]
m.prism(_hood, HT, HH, TG, bottom=False)
# pocket floor (dark) with the finger scoop at its front and the slot under the hood
m.decal_xz([(SX0 + 0.05, ZF - 0.05), (SX1 - 0.05, ZF - 0.05), (SX1 - 0.05, HZ1 + 0.05), (SX0 + 0.05, HZ1 + 0.05)],
           HF, FLOOR)
scx = (SX0 + SX1) / 2
m.decal_xz([(scx - 2.0, ZF - 0.1), (scx + 2.0, ZF - 0.1), (scx + 1.4, ZF - 1.6), (scx, ZF - 2.1), (scx - 1.4, ZF - 1.6)],
           HF, CAVITY, lift=0.04)
m.decal_xy([(scx - 2.9, HF + 0.05), (scx + 2.9, HF + 0.05), (scx + 2.9, HF + 0.45), (scx - 2.9, HF + 0.45)], HZ1, CAVITY)
# four grooves along the rounded front edge, both sides of the pocket
sl = (0, HT - HE, -(ZE - ZS))           # direction along the slope (up, back)
sn = (0, ZE - ZS, HT - HE)              # its outward normal


def slope_pt(t, x):
    return (x, HE + (HT - HE) * t, ZE - (ZE - ZS) * t)


for k in range(4):
    t0 = 0.12 + 0.21 * k
    t1 = t0 + 0.08
    for x0, x1 in ((-WB + 0.6, SX0 - 0.4), (SX1 + 0.4, WB - 0.6)):
        lift_poly([slope_pt(t0, x0), slope_pt(t0, x1), slope_pt(t1, x1), slope_pt(t1, x0)], GROOVE, sn)
# badge on the top, left of centre: dark plate, orange bar, red disc
m.decal_xz([(-10.5, 4.2), (-1.5, 4.2), (-1.5, 2.6), (-10.5, 2.6)], HT, GROOVE)
m.decal_xz([(-10.0, 3.8), (-3.6, 3.8), (-3.6, 3.0), (-10.0, 3.0)], HT, ORANGE, lift=0.04)
m.decal_xz([(x, z) for x, z in circle(-2.5, 3.4, 0.55, 6)], HT, RED, lift=0.04)
# the console's power switch, right above the base's
m.decal_xy([(-0.9, HP + 0.8), (0.9, HP + 0.8), (0.9, HP + 2.4), (-0.9, HP + 2.4)], ZF, CAVITY)
m.box(-0.75, HP + 0.95, ZF, 0.05, HP + 2.25, ZF + 0.35, LIGHT, faces={'back': None, 'bottom': None})
# controller port, low on the right of the front face
m.decal_xy(circle(13.9, HP + 1.5, 0.85, 8), ZF, LIGHT)
m.decal_xy(circle(13.9, HP + 1.5, 0.6, 8), ZF, CAVITY, lift=0.04)
# seam between the console and the base plate
m.decal_xy([(-WB + 0.1, HP), (WB - 0.1, HP), (WB - 0.1, HP + 0.15), (-WB + 0.1, HP + 0.15)], ZF, GROOVE)

# ================================================================ cradle
m.box(-CW, 0, CZ0, CW, HFL, CZ1, IFU, faces={'bottom': None})
wall = [(CZ0, HFL), (CZ1, HFL), (CZ1, HFL + 0.6), (CZ1 - 4.0, HW), (CZ0, HW)]
m.extrude_yz(wall, -CW, -CW + CT, IFU)
m.extrude_yz(wall, CW - CT, CW, IFU)
m.box(-CW + CT, HFL, CZ0, CW - CT, HW, CZ0 + CT, IFU, faces={'bottom': None, 'left': None, 'right': None})
# slatted vents on the front of both side walls (vertical slats)
for side, xf in ((1, CW), (-1, -CW)):
    nrm = (side, 0, 0)
    for k in range(8):
        z0 = CZ1 - 4.5 - 0.6 * k - (0.8 if k > 3 else 0)
        z1 = z0 - 0.3
        pts = [(xf, HFL - 1.2, z0), (xf, HFL - 1.2, z1), (xf, HW - 0.5, z1), (xf, HW - 0.5, z0)]
        lift_poly(pts, GROOVE, nrm)
# AV panel on the back
m.polygon([(x, y, CZ0 - 0.03) for x, y in ((3.0, 2.0), (7.5, 2.0), (7.5, 4.5), (3.0, 4.5))], GROOVE, normal=(0, 0, -1))

# ================================================================ CD-ROM player
# body sides (its bottom sits on the tray floor, its top is built below)
m.box(-PW, HFL, PZ0, PW, HPT, PZ1, PLAYER, faces={'bottom': None, 'top': None})
m.decal_xy([(-PW + 0.1, HFL + 1.3), (PW - 0.1, HFL + 1.3), (PW - 0.1, HFL + 1.42), (-PW + 0.1, HFL + 1.42)],
           PZ1, GROOVE)
# volume wheel on the front left
m.decal_xy([(-4.8, HFL + 0.35), (-2.9, HFL + 0.35), (-2.9, HFL + 1.0), (-4.8, HFL + 1.0)], PZ1, LIGHT)

# top: square with the round well opening (20-gon, vertices on the disc's)
wa = [2 * math.pi * i / NW for i in range(NW)]
inner = [(RW * math.cos(a), RW * math.sin(a)) for a in wa]


def ray(a):
    c, s = math.cos(a), math.sin(a)
    ts = []
    if abs(c) > 1e-9:
        ts += [t for t in ((PW) / c, (-PW) / c) if t > 0]
    if abs(s) > 1e-9:
        ts += [t for t in ((PZ1 - PC) / s, (PZ0 - PC) / s) if t > 0]
    t = min(ts)
    return (t * c, t * s)


corners = [(PW, PZ1 - PC), (-PW, PZ1 - PC), (-PW, PZ0 - PC), (PW, PZ0 - PC)]
cang = [(math.atan2(z, x) % (2 * math.pi), (x, z)) for x, z in corners]
for i in range(NW):
    a0, a1 = wa[i], wa[i + 1] if i + 1 < NW else 2 * math.pi
    outer = [ray(a0)] + [p for a, p in sorted(cang) if a0 < a < a1] + [ray(a1)]
    poly = [inner[i]] + outer + [inner[(i + 1) % NW]]
    poly = [(x, HPT, PC + z) for x, z in poly]
    m.polygon(poly, PLAYER, normal=(0, 1, 0))
# the well: dark walls facing in, floor, spindle
for i in range(NW):
    a0, a1 = wa[i], wa[(i + 1) % NW]
    p0 = (RW * math.cos(a0), PC + RW * math.sin(a0))
    p1 = (RW * math.cos(a1), PC + RW * math.sin(a1))
    am = a0 + math.pi / NW
    m.polygon([(p0[0], HWF, p0[1]), (p1[0], HWF, p1[1]), (p1[0], HPT, p1[1]), (p0[0], HPT, p0[1])], CAVITY,
              normal=(-math.cos(am), 0, -math.sin(am)))
m.polygon([(x, HWF, PC + z) for x, z in inner], FLOOR, normal=(0, 1, 0))
m.cylinder(0, PC, 0.55, HWF, HWF + 0.4, SPINDLE, segments=6, bottom=False)
# hinge bar behind the lid
m.decal_xz([(-2.6, PC - 6.35), (2.6, PC - 6.35), (2.6, PC - 7.05), (-2.6, PC - 7.05)], HPT, GROOVE)
# red track display (front left corner) with the repeat button beside it
m.decal_xz(circle(-6.0, PZ1 - 1.3, 0.8, 8), HPT, DISPLAY)
m.decal_xz([(-4.9, PZ1 - 0.5), (-3.9, PZ1 - 0.5), (-3.9, PZ1 - 0.9), (-4.9, PZ1 - 0.9)], HPT, LIGHT)
# play / stop / skip (front right corner)
m.decal_xz(circle(6.1, PZ1 - 1.35, 0.7, 8), HPT, LIGHT)
m.decal_xz(circle(6.1, PZ1 - 1.35, 0.35, 6), HPT, GROOVE, lift=0.04)
m.decal_xz([(5.6, PZ1 - 2.45), (6.6, PZ1 - 2.45), (6.6, PZ1 - 3.05), (5.6, PZ1 - 3.05)], HPT, LIGHT)
m.decal_xz([(3.6, PZ1 - 0.35), (5.0, PZ1 - 0.35), (5.0, PZ1 - 0.75), (3.6, PZ1 - 0.75)], HPT, LIGHT)

# ---------------------------------------------------------------- the lid (moving part)
with m.part('lid'):
    m.cylinder(0, PC, RL, HL0, HL1, LID, segments=NL, bottom=FLOOR)
    # dark band across the lid, a little behind its centre, with a smoked window at each end
    bz0, bz1 = PC - 1.9, PC + 0.9
    hx = math.sqrt(RL ** 2 - 1.9 ** 2) - 0.45
    m.decal_xz([(-hx, bz1), (hx, bz1), (hx, bz0), (-hx, bz0)], HL1, GROOVE)
    m.decal_xz([(-hx + 0.3, bz1 - 0.35), (-hx + 3.0, bz1 - 0.35), (-hx + 3.0, bz0 + 0.35), (-hx + 0.3, bz0 + 0.35)],
               HL1, WINDOW, lift=0.04)
    m.decal_xz([(hx - 2.4, bz1 - 0.35), (hx - 0.3, bz1 - 0.35), (hx - 0.3, bz0 + 0.35), (hx - 2.4, bz0 + 0.35)],
               HL1, WINDOW, lift=0.04)

# centre the model on z = 0 (origin at the bottom centre)
_zs = [v[2] for v in m.verts]
DZ = round(-(min(_zs) + max(_zs)) / 2, 3)
m.transform(list(range(len(m.tris))), m.move(0, 0, DZ))

if __name__ == '__main__':
    s = m.stats()
    print(s)
    print('lid hinge pivot: [0, %.2f, %.2f]' % (HL1, PC - RL - 0.6 + DZ))
    print('disc seated pos: [0, %.2f, %.2f]' % (HWF + 0.06, PC + 6.0 + DZ))
    print('well centre z: %.3f' % (PC + DZ))
    print(m.save())
