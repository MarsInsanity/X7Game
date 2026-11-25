# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega SG-1000 (first model, 1983) with its hardwired SJ-200 joystick.

Built from photos of the real console (Wikimedia Commons, Evan Amos'
Sega-SG-1000-Console FL / FR / BL / BR / Set). What makes it an SG-1000:
  * a low, wide, off-white case (about 26.6 x 15 x 4.4 cm) on a grey bottom
    shell that shows as a band round the back and sides
  * the top rises gently from a rounded front nose to a raised flat strip
    across the back (the "hump"), with a slanted back edge and chamfered ends
  * on the slope: a wide striped panel: thin blue line, a big silver field,
    a red stripe, a blue band, a thin silver line, a blue edge
  * a red "hold" button just in front of the panel, right of centre
  * on the hump: a light grey cartridge bezel in the middle (it reaches the
    hump's front edge) with a funnel down to the slot, and a white vent
    grille with six slots either side of it
  * a joystick port on the right side; power jack, power switch, the
    expansion opening, RF jack and channel switch on the back
  * the SJ-200 joystick: a long grey bar with a black stick, a light label
    patch and red fire buttons on both sides of its cable end; its cable runs
    out of the back of the console (here it lies to the left of the console)

Proportions taken from the photos (fractions of the 26.6 cm width): bezel
0.42 wide, centred; vents 0.20 wide, centred at +-0.33; panel from -0.43 to
+0.38; hold button centred at +0.21, just in front of the panel.

The cartridge (assets/models/media/sg1000.obj, 8.4 x 11.0 x 1.7 cm, label to
+Z) goes straight DOWN into the top slot, label to the front. The slot
(8.8 x 2.0 cm) has two dust flaps (parts "flap_front" / "flap_back"), hinged
on its long edges, that swing down into the cavity. The cartridge sits on the
cavity floor, 2.5 cm deep, its label above the bezel.

Running this writes the model and its system file
(assets/models/systems/sg1000.json).
"""
import json
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

WHITE = (234, 232, 222)      # case
BASE = (138, 140, 142)       # grey bottom shell
BEZEL = (176, 176, 172)      # cartridge bezel
FUNNEL = (120, 120, 120)     # bezel funnel walls
HOLE = (14, 14, 16)          # slot cavity, ports
FLAP = (72, 72, 76)          # dust flaps
SILVER = (216, 218, 222)     # panel field
BLUE = (28, 62, 172)         # panel lines / band
RED = (226, 44, 28)          # red stripe, hold button, fire buttons
RED_DK = (150, 22, 14)       # button sides
VENT = (120, 118, 112)       # vent slots
JOY = (104, 106, 110)        # joystick body, cable
JOY_LT = (168, 170, 174)     # joystick label patch
BLACK = (30, 30, 32)         # stick

m = Model('sg1000', 'console')

# ---------------------------------------------------------------- case
HW = 13.3                    # half width (26.6 cm)
B = 0.9                      # chamfer at the two ends
XI = HW - B
YB = 1.1                     # top of the grey bottom shell
# side profile (z, y), front to back; bottom edges get no chamfer
P = [
    (7.50, 0.35),            # 0 front bottom (the nose hangs over the base)
    (7.65, 1.50),            # 1 front face
    (7.35, 2.35),            # 2 rounded nose
    (6.70, 2.70),            # 3 start of the slope
    (-1.40, 3.90),           # 4 end of the slope
    (-1.60, 4.40),           # 5 hump front edge
    (-6.30, 4.40),           # 6 hump back edge
    (-7.50, 2.90),           # 7 slanted back edge -> back face
    (-7.50, YB),             # 8 back bottom, on the base
    (5.80, YB),              # 9 underside, on the base
    (5.80, 0.35),            # 10 nose underside
]
EDGE_D = [B, B, B, B, B, B, B, B, 0, 0, 0]   # chamfer of edge i (P[i] -> P[i+1])


def offset_profile(pts, d):
    """move every edge of the profile inwards by d[i]; corners by miter"""
    # work in (u, v) = (-z, y): the profile runs clockwise there; make the
    # inward normal of edge (dx, dy) point to the right: (dy, -dx)
    n = len(pts)
    uv = [(-z, y) for z, y in pts]
    area = sum(uv[i][0] * uv[(i + 1) % n][1] - uv[(i + 1) % n][0] * uv[i][1] for i in range(n))
    sgn = 1 if area < 0 else -1
    lines = []
    for i in range(n):
        (ax, ay), (bx, by) = uv[i], uv[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy)
        nx, ny = sgn * dy / ln, -sgn * dx / ln
        lines.append(((ax + nx * d[i], ay + ny * d[i]), (dx, dy)))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append((-(p1[0] + d1[0] * t), p1[1] + d1[1] * t))
    return out


Q = offset_profile(P, EDGE_D)


def face(pts, col, hint):
    """a flat polygon, wound to face the direction `hint` points to"""
    return m.polygon(pts, col, normal=_newell(pts, hint))


def _newell(pts, hint):
    nx = ny = nz = 0.0
    for i in range(len(pts)):
        p, q = pts[i], pts[(i + 1) % len(pts)]
        nx += (p[1] - q[1]) * (p[2] + q[2])
        ny += (p[2] - q[2]) * (p[0] + q[0])
        nz += (p[0] - q[0]) * (p[1] + q[1])
    if nx * hint[0] + ny * hint[1] + nz * hint[2] < 0:
        nx, ny, nz = -nx, -ny, -nz
    return (nx, ny, nz)


AREA = sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))


def edge_out(i):
    """outward direction (y, z) of profile edge i"""
    (za, ya), (zb, yb) = P[i], P[(i + 1) % len(P)]
    dz, dy = zb - za, yb - ya
    nz, ny = (dy, -dz) if AREA > 0 else (-dy, dz)     # outward normal in the (z, y) plane
    return ny, nz


# grey part of the hump front edge (the bezel reaches it), x range
BZX = 5.6
SPLITS = {
    4: [(-XI, -BZX, WHITE), (-BZX, BZX, BEZEL), (BZX, XI, WHITE)],   # hump front step
    5: [],                 # hump top: tiled below (slot, vents)
    8: [],                 # underside on the base: not drawn
}
for i in range(len(P)):
    j = (i + 1) % len(P)
    (za, ya), (zb, yb) = P[i], P[j]
    ny, nz = edge_out(i)
    for x0, x1, col in SPLITS.get(i, [(-XI, XI, WHITE)]):
        face([(x0, ya, za), (x1, ya, za), (x1, yb, zb), (x0, yb, zb)], col, (0, ny, nz))
    if i == 8:
        continue
    # chamfer strips at both ends
    for s in (1, -1):
        (qa, ra), (qb, rb) = Q[i], Q[j]
        pts = [(s * XI, ya, za), (s * XI, yb, zb), (s * HW, rb, qb), (s * HW, ra, qa)]
        face(pts, WHITE, (s * 0.7, ny, nz))
# end caps
for s in (1, -1):
    face([(s * HW, y, z) for z, y in Q], WHITE, (s, 0, 0))

# grey bottom shell
m.box(-HW + 0.2, 0, -7.3, HW - 0.2, YB, 5.8, BASE)

# ---------------------------------------------------------------- hump top, bezel, slot
YH = 4.40                    # hump top
ZH0, ZH1 = -6.30, -1.60      # hump back / front edge
BZ0 = -5.90                  # bezel back edge (front edge = hump front)
SC = (BZ0 + ZH1) / 2         # slot centre z
FX, FZ = 4.85, 1.45          # funnel top (half sizes)
SX, SZ = 4.40, 1.00          # slot opening (half sizes): cart 4.2 x 0.85
YS = 3.80                    # slot opening level
YF = 1.30                    # cavity floor = where the cartridge sits


def rect_top(x0, z0, x1, z1, y, col):
    return m.polygon([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], col, normal=(0, 1, 0))


# white hump top round the bezel
rect_top(-XI, ZH0, -BZX, ZH1, YH, WHITE)
rect_top(BZX, ZH0, XI, ZH1, YH, WHITE)
rect_top(-BZX, ZH0, BZX, BZ0, YH, WHITE)
# bezel frame (flush with the hump top), funnel top rectangle cut out
fz0, fz1 = SC - FZ, SC + FZ
rect_top(-BZX, BZ0, BZX, fz0, YH, BEZEL)
rect_top(-BZX, fz1, BZX, ZH1, YH, BEZEL)
rect_top(-BZX, fz0, -FX, fz1, YH, BEZEL)
rect_top(FX, fz0, BZX, fz1, YH, BEZEL)
# funnel walls down to the slot opening (facing up and inwards)
sz0, sz1 = SC - SZ, SC + SZ
face([(-FX, YH, fz0), (FX, YH, fz0), (SX, YS, sz0), (-SX, YS, sz0)], FUNNEL, (0, 1, 1))     # back wall
face([(FX, YH, fz1), (-FX, YH, fz1), (-SX, YS, sz1), (SX, YS, sz1)], FUNNEL, (0, 1, -1))    # front wall
face([(-FX, YH, fz1), (-FX, YH, fz0), (-SX, YS, sz0), (-SX, YS, sz1)], FUNNEL, (1, 1, 0))   # left
face([(FX, YH, fz0), (FX, YH, fz1), (SX, YS, sz1), (SX, YS, sz0)], FUNNEL, (-1, 1, 0))      # right
# the cavity under the slot: dark walls facing inwards, floor facing up
face([(-SX, YF, sz0), (SX, YF, sz0), (SX, YS, sz0), (-SX, YS, sz0)], HOLE, (0, 0, 1))
face([(-SX, YF, sz1), (SX, YF, sz1), (SX, YS, sz1), (-SX, YS, sz1)], HOLE, (0, 0, -1))
face([(-SX, YF, sz0), (-SX, YF, sz1), (-SX, YS, sz1), (-SX, YS, sz0)], HOLE, (1, 0, 0))
face([(SX, YF, sz0), (SX, YF, sz1), (SX, YS, sz1), (SX, YS, sz0)], HOLE, (-1, 0, 0))
rect_top(-SX, sz0, SX, sz1, YF, HOLE)

# dust flaps: two thin plates closing the slot, hinged on its long edges
FT = 0.08
FW = SX - 0.05
with m.part('flap_front'):
    m.box(-FW, YS - FT, SC + 0.01, FW, YS, sz1, FLAP)
with m.part('flap_back'):
    m.box(-FW, YS - FT, sz0, FW, YS, SC - 0.01, FLAP)

# vent grilles either side of the bezel: six dark slots each
VX0, VX1 = 6.30, 11.50
VZ0, VZ1 = -5.70, -2.10
for s in (1, -1):
    for k in range(6):
        z0 = VZ0 + k * (VZ1 - VZ0) / 6 + 0.12
        z1 = z0 + (VZ1 - VZ0) / 6 - 0.24
        xa, xb = sorted((s * VX0, s * VX1))
        m.decal_xz([(xa, z0), (xb, z0), (xb, z1), (xa, z1)], YH, VENT, lift=0.03)

# ---------------------------------------------------------------- slope: panel, hold button, lamp
(Z3, Y3), (Z4, Y4) = P[3], P[4]
SL = math.hypot(Z3 - Z4, Y4 - Y3)
SN = (0, (Z3 - Z4) / SL, (Y4 - Y3) / SL)     # slope normal (y, z parts)


def slope_pt(x, t, lift=0.0):
    """t = 0 at the front of the slope, 1 at its back"""
    return (x, Y3 + (Y4 - Y3) * t + SN[1] * lift, Z3 + (Z4 - Z3) * t + SN[2] * lift)


def slope_rect(x0, x1, t0, t1, col, lift=0.03):
    return m.polygon([slope_pt(x0, t0, lift), slope_pt(x1, t0, lift), slope_pt(x1, t1, lift),
                      slope_pt(x0, t1, lift)], col, normal=SN)


PX0, PX1 = -11.4, 10.1       # panel ends
PT0, PT1 = 0.17, 0.98        # panel front / back on the slope
EW = 0.30                    # blue end lines
rows = [(0.08, 'full', BLUE), (0.04, 'in', SILVER), (0.40, 'full', BLUE),
        (0.08, 'in', RED), (0.36, 'in', SILVER), (0.04, 'full', BLUE)]   # front to back
t = PT0
for frac, kind, col in rows:
    t1 = t + frac * (PT1 - PT0)
    if kind == 'full':
        slope_rect(PX0, PX1, t, t1, col)
    else:
        slope_rect(PX0, PX0 + EW, t, t1, BLUE)
        slope_rect(PX0 + EW, PX1 - EW, t, t1, col)
        slope_rect(PX1 - EW, PX1, t, t1, BLUE)
    t = t1
# power lamp: a small dark dash in front of the panel
slope_rect(-0.9, -0.5, 0.09, 0.13, HOLE)
# red hold button: a raised block on the slope, just in front of the panel
ANG = math.radians(math.degrees(math.atan2(Y4 - Y3, Z3 - Z4)))
BT0 = slope_pt(0, 0.03)      # front edge of the button


def slope_local(p):
    """button space (x, y up from the slope, z towards the front along it,
    0 at the button's front edge) -> world"""
    x, y, z = p
    return (x, BT0[1] + y * math.cos(ANG) - z * math.sin(ANG), BT0[2] + y * math.sin(ANG) + z * math.cos(ANG))


bt = m.box(4.5, -0.05, -1.25, 6.7, 0.45, 0, RED,
           faces={'bottom': None, 'left': RED_DK, 'right': RED_DK, 'front': RED_DK, 'back': RED_DK})
m.transform(bt, slope_local)


# ---------------------------------------------------------------- side and back details
# joystick port (player 2) on the right side, near the back
m.box(HW, 1.6, -5.6, HW + 0.12, 2.5, -4.2, HOLE, faces={'left': None})


def back_rect(x0, y0, x1, y1, col, z=-7.5 - 0.03):
    return m.polygon([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], col, normal=(0, 0, -1))


back_rect(-2.7, 1.15, 4.7, 2.35, HOLE)        # expansion opening
back_rect(9.8, 1.6, 10.6, 2.4, HOLE)          # power jack
back_rect(6.9, 1.6, 8.9, 2.2, HOLE)           # power switch
back_rect(-7.4, 1.6, -6.6, 2.4, HOLE)         # RF jack
back_rect(-9.1, 1.7, -8.5, 2.2, HOLE)         # channel switch

# ---------------------------------------------------------------- SJ-200 joystick
JX, JZ = -18.2, 1.0          # centre of the bar
JW, JL, JH = 4.4, 14.0, 2.2
jz0, jz1 = JZ - JL / 2, JZ + JL / 2     # cable end at the back (jz0)
m.box(JX - JW / 2, 0, jz0, JX + JW / 2, JH, jz1, JOY, faces={'bottom': None})
m.decal_xz([(JX - 1.7, jz0 + 0.5), (JX + 1.7, jz0 + 0.5), (JX + 1.7, jz0 + 2.6), (JX - 1.7, jz0 + 2.6)],
           JH, JOY_LT, lift=0.03)
# stick: a dark round seat, a shaft and a ball-ish knob
SZJ = jz0 + 5.0
m.cylinder(JX, SZJ, 1.25, JH, JH + 0.12, FLAP, segments=8)
m.cylinder(JX, SZJ, 0.32, JH + 0.12, JH + 2.6, BLACK, segments=6, top=False, bottom=False)
m.cylinder(JX, SZJ, 0.55, JH + 2.6, JH + 3.4, BLACK, segments=8, bottom=False)
# red fire buttons on both long sides of the cable end
for s in (1, -1):
    xa, xb = sorted((JX + s * JW / 2, JX + s * (JW / 2 + 0.3)))
    m.box(xa, 0.5, jz0 + 0.4, xb, 1.8, jz0 + 2.6, RED,
          faces={'bottom': None, 'left' if s > 0 else 'right': None, 'top': RED_DK, 'front': RED_DK, 'back': RED_DK})
# cable: out of the back of the console, round behind it, into the joystick
CX = -10.5
CY = 0.4
m.box(CX - 0.45, 1.3, -8.0, CX + 0.45, 2.1, -7.5, JOY, faces={'front': None})          # strain relief
m.box(CX - 0.2, 0, -8.5, CX + 0.2, 1.7, -8.0, JOY, faces={'bottom': None})              # drop to the table
m.box(JX - 0.2, 0, -8.9, CX + 0.2, CY, -8.5, JOY, faces={'bottom': None})              # along the back
m.box(JX - 0.2, 0, -8.5, JX + 0.2, CY, jz0, JOY, faces={'bottom': None, 'front': None})  # into the joystick

# ---------------------------------------------------------------- centre it
used = sorted({i for tr in m.tris for i in tr[:3]})
xs = [m.verts[i][0] for i in used]
zs = [m.verts[i][2] for i in used]
DX, DZ = -(min(xs) + max(xs)) / 2, -(min(zs) + max(zs)) / 2
m.transform(list(range(len(m.tris))), Model.move(DX, 0, DZ))
used = sorted({i for tr in m.tris for i in tr[:3]})
remap = {o: n for n, o in enumerate(used)}
m.verts = [m.verts[o] for o in used]
m.tris = [(remap[a], remap[b], remap[c], col) for a, b, c, col in m.tris]


def r(v):
    return round(v, 3)


# ---------------------------------------------------------------- system file
SLOT = (r(DX), r(SC + DZ))
system = {
    'console': '../consoles/sg1000.obj',
    'media': '../media/sg1000.obj',
    'view': [28, 34],
    'parts': {
        'flap_front': {'hinge': {'pivot': [r(DX), r(YS - FT), r(sz1 + DZ)], 'axis': [1, 0, 0], 'angle': -90}},
        'flap_back': {'hinge': {'pivot': [r(DX), r(YS - FT), r(sz0 + DZ)], 'axis': [1, 0, 0], 'angle': 90}},
    },
    'path': [
        {'pos': [SLOT[0], r(YH + 10.5), SLOT[1]], 'rot': [0, 0, 0]},     # ready: above the slot
        {'pos': [SLOT[0], r(YH + 0.4), SLOT[1]], 'rot': [0, 0, 0]},      # at the slot
        {'pos': [SLOT[0], YF, SLOT[1]], 'rot': [0, 0, 0]},               # seated on the cavity floor
    ],
    'steps': [
        {'time': 0.45, 'media': [0, 1]},
        {'time': 0.25, 'open': ['flap_front', 'flap_back']},
        {'time': 0.45, 'media': [1, 2]},
    ],
}

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
    sp = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'systems', 'sg1000.json')
    with open(sp, 'w', newline='\n') as f:
        # one line per part, pose and step
        out = []
        for k, v in system.items():
            if isinstance(v, dict):
                body = ',\n'.join('    %s: %s' % (json.dumps(a), json.dumps(b)) for a, b in v.items())
                out.append('  %s: {\n%s\n  }' % (json.dumps(k), body))
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                body = ',\n'.join('    ' + json.dumps(x) for x in v)
                out.append('  %s: [\n%s\n  ]' % (json.dumps(k), body))
            else:
                out.append('  %s: %s' % (json.dumps(k), json.dumps(v)))
        f.write('{\n' + ',\n'.join(out) + '\n}\n')
    print(os.path.normpath(sp))
