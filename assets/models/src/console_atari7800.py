# SPDX-License-Identifier: GPL-3.0-or-later
"""Atari 7800 ProSystem: low-poly console model (32 x 7 x 24 cm).

From the reference photos (Wikimedia Commons, front-left, front-right,
back-left and two straight-on museum shots): a flat, dark charcoal slab
whose top rises gently from front to back, with softly bevelled edges,
sitting on a smaller black base that is set in under the shell. Its
signature is the brushed-silver band right across the top (about 0.3 to
0.55 of the depth from the back) with the rainbow stripe along its front
part, and the black cartridge well just behind the band, in the middle.
Along the front edge runs a darker lip carrying the four console keys
(power and pause on the left, select and reset on the right); a row of
vent slits runs along the back edge of the top and across the back face.
The two controller ports sit in the base's front face, under the lip.

Insertion: the cartridge goes straight down into the slot at the bottom of
the well, label to the front (+Z); about 4.5 cm of it stays above the top.
No moving parts: the 7800's slot has no door.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (66, 66, 70)        # charcoal top
SIDE = (42, 42, 46)         # side walls, front and back faces
LIP = (30, 30, 33)          # front lip, well walls
BASE = (16, 16, 18)         # the base under the shell
HOLE = (6, 6, 8)            # slot, vents, ports
SILVER = (204, 204, 210)    # brushed band
KEY = (100, 100, 106)       # console keys
RAINBOW = [(222, 44, 40), (242, 140, 30), (232, 210, 40), (60, 172, 72), (48, 96, 214), (140, 62, 176)]

XI, XO = 15.55, 16.0        # top width (inner edge of the side bevel), full width
BEV = 0.45                  # side bevel (in the profile plane)
YB = 2.2                    # shell bottom / base top
# side profile (z, y), counter-clockwise seen from +X (front to the right)
YL0 = 4.3                           # lip: from the front bumper (z 11.5) back to the crease
WX = 5.0                            # cartridge well: x +-WX
ZT_F, ZT_R, YT_F, YT_R = 10.2, -10.9, 4.5, 7.0   # main top plane: front / rear
ZBAND_F, ZBAND_R = 3.2, -2.4        # silver band
ZWELL_R = -7.0                      # cartridge well: from the band back to here
ZVENT = -9.9                        # vent row: from here to the rear edge


def top_y(z):
    return YT_F + (ZT_F - z) / (ZT_F - ZT_R) * (YT_R - YT_F)


PROF = [(12.0, YB), (12.0, 3.75), (11.5, YL0), (ZT_F, YT_F),
        (ZBAND_F, top_y(ZBAND_F)), (ZBAND_R, top_y(ZBAND_R)), (ZWELL_R, top_y(ZWELL_R)),
        (ZVENT, top_y(ZVENT)), (ZT_R, YT_R), (-12.0, 6.2), (-12.0, YB)]
EDGE_COL = [SIDE, LIP, LIP, SHELL, SILVER, SHELL, SHELL, SHELL, SIDE, SIDE, None]
WELL_ROW = 5

m = Model('atari7800', 'console')
polys = []                  # (points, colour, outward hint): T-junctions fixed at the end


def add(pts, color, hint):
    polys.append((pts, color, hint))


def inset(prof, d):
    """the profile moved inwards by d (mitred corners)"""
    n = len(prof)
    out = []
    for i in range(n):
        p0, p1, p2 = prof[i - 1], prof[i], prof[(i + 1) % n]
        ns = []
        for a, b in ((p0, p1), (p1, p2)):
            dz, dy = b[0] - a[0], b[1] - a[1]
            l = (dz * dz + dy * dy) ** 0.5
            ns.append((-dy / l, dz / l))          # inward normal (CCW profile)
        k = 1 + ns[0][0] * ns[1][0] + ns[0][1] * ns[1][1]
        out.append((p1[0] + d * (ns[0][0] + ns[1][0]) / k, p1[1] + d * (ns[0][1] + ns[1][1]) / k))
    return out


def out_n(a, b):
    """outward normal (y, z) of profile edge a -> b"""
    dz, dy = b[0] - a[0], b[1] - a[1]
    return (0.0, -dz, dy)                         # (x, y, z): -(inward)


PIN = inset(PROF, BEV)

# ---------------------------------------------------------------- shell
for sx in (1, -1):
    add([(sx * XO, y, z) for z, y in PIN], SIDE, (sx, 0, 0))
n = len(PROF)
for i in range(n):
    a, b = PROF[i], PROF[(i + 1) % n]
    ai, bi = PIN[i], PIN[(i + 1) % n]
    on = out_n(a, b)
    col = EDGE_COL[i]
    for sx in (1, -1):                            # the bevels down to the sides
        add([(sx * XI, a[1], a[0]), (sx * XO, ai[1], ai[0]), (sx * XO, bi[1], bi[0]), (sx * XI, b[1], b[0])],
            BASE if col is None else (SHELL if col == SILVER else col),
            (sx, on[1], on[2]))
    if col is None:                               # bottom: only the overhang around the base
        continue
    if i == WELL_ROW:                             # the well row: left and right of the well
        for x0, x1 in ((-XI, -WX), (WX, XI)):
            add([(x0, a[1], a[0]), (x1, a[1], a[0]), (x1, b[1], b[0]), (x0, b[1], b[0])], col, on)
        continue
    add([(-XI, a[1], a[0]), (XI, a[1], a[0]), (XI, b[1], b[0]), (-XI, b[1], b[0])], col, on)

# bottom of the shell around the base (the base is set in under it)
BX, BZ0, BZ1 = 14.0, -9.8, 10.6
for x0, z0, x1, z1 in ((-XI, BZ1, XI, 12.0), (-XI, -12.0, XI, BZ0), (-XI, BZ0, -BX, BZ1), (BX, BZ0, XI, BZ1)):
    add([(x0, YB, z0), (x1, YB, z0), (x1, YB, z1), (x0, YB, z1)], BASE, (0, -1, 0))

# ---------------------------------------------------------------- base
for pts, hint in (
        ([(-BX, 0, BZ1), (BX, 0, BZ1), (BX, YB, BZ1), (-BX, YB, BZ1)], (0, 0, 1)),
        ([(-BX, 0, BZ0), (BX, 0, BZ0), (BX, YB, BZ0), (-BX, YB, BZ0)], (0, 0, -1)),
        ([(-BX, 0, BZ0), (-BX, 0, BZ1), (-BX, YB, BZ1), (-BX, YB, BZ0)], (-1, 0, 0)),
        ([(BX, 0, BZ0), (BX, 0, BZ1), (BX, YB, BZ1), (BX, YB, BZ0)], (1, 0, 0)),
        ([(-BX, 0, BZ0), (BX, 0, BZ0), (BX, 0, BZ1), (-BX, 0, BZ1)], (0, -1, 0))):
    add(pts, BASE, hint)

# ---------------------------------------------------------------- cartridge well and slot
YW = 5.4                    # well floor
SX, SZ0, SZ1 = 4.2, -5.85, -3.55    # slot opening (cartridge 8.1 x 2.0 with 0.15 clearance)
YC = 0.12                   # cavity floor
yf, yr = top_y(ZBAND_R), top_y(ZWELL_R)
add([(-WX, YW, ZBAND_R), (WX, YW, ZBAND_R), (WX, yf, ZBAND_R), (-WX, yf, ZBAND_R)], LIP, (0, 0, -1))
add([(-WX, YW, ZWELL_R), (WX, YW, ZWELL_R), (WX, yr, ZWELL_R), (-WX, yr, ZWELL_R)], LIP, (0, 0, 1))
add([(-WX, YW, ZBAND_R), (-WX, yf, ZBAND_R), (-WX, yr, ZWELL_R), (-WX, YW, ZWELL_R)], LIP, (1, 0, 0))
add([(WX, YW, ZBAND_R), (WX, yf, ZBAND_R), (WX, yr, ZWELL_R), (WX, YW, ZWELL_R)], LIP, (-1, 0, 0))
for x0, z0, x1, z1 in ((-WX, SZ1, WX, ZBAND_R), (-WX, ZWELL_R, WX, SZ0), (-WX, SZ0, -SX, SZ1), (SX, SZ0, WX, SZ1)):
    add([(x0, YW, z0), (x1, YW, z0), (x1, YW, z1), (x0, YW, z1)], LIP, (0, 1, 0))
# the shaft down to the cavity floor
add([(-SX, YC, SZ1), (SX, YC, SZ1), (SX, YW, SZ1), (-SX, YW, SZ1)], HOLE, (0, 0, -1))
add([(-SX, YC, SZ0), (SX, YC, SZ0), (SX, YW, SZ0), (-SX, YW, SZ0)], HOLE, (0, 0, 1))
add([(-SX, YC, SZ0), (-SX, YC, SZ1), (-SX, YW, SZ1), (-SX, YW, SZ0)], HOLE, (1, 0, 0))
add([(SX, YC, SZ0), (SX, YC, SZ1), (SX, YW, SZ1), (SX, YW, SZ0)], HOLE, (-1, 0, 0))
add([(-SX, YC, SZ0), (SX, YC, SZ0), (SX, YC, SZ1), (-SX, YC, SZ1)], HOLE, (0, 1, 0))

# ---------------------------------------------------------------- emit panels
# insert every panel corner that lies on another panel's edge, so the
# software renderer shows no hairline cracks at T-junctions
allpts = {tuple(round(c, 4) for c in p) for pts, _, _ in polys for p in pts}


def on_seg(p, a, b):
    ab = [b[i] - a[i] for i in range(3)]
    ap = [p[i] - a[i] for i in range(3)]
    l2 = sum(c * c for c in ab)
    t = sum(ap[i] * ab[i] for i in range(3)) / l2
    if t <= 1e-6 or t >= 1 - 1e-6:
        return None
    d = [ap[i] - ab[i] * t for i in range(3)]
    return t if sum(c * c for c in d) < 1e-8 else None


for pts, c, hint in polys:
    pts = [tuple(round(v, 4) for v in p) for p in pts]
    out = []
    for i, a in enumerate(pts):
        b = pts[(i + 1) % len(pts)]
        out.append(a)
        out += [p for _, p in sorted((on_seg(p, a, b), p) for p in allpts if on_seg(p, a, b) is not None)]
    m.polygon(out, c, normal=hint)


# ---------------------------------------------------------------- details on the top (decals)
def top_pt(x, z, lift=0.03):
    """a point on the main top plane, lifted along its normal"""
    s = (YT_R - YT_F) / (ZT_F - ZT_R)             # rise per cm towards the back
    l = (1 + s * s) ** 0.5
    return (x, top_y(z) + lift / l, z + lift * s / l)


def top_decal(x0, z0, x1, z1, color, lift=0.03):
    pts = [top_pt(x0, z1, lift), top_pt(x1, z1, lift), top_pt(x1, z0, lift), top_pt(x0, z0, lift)]
    m.polygon(pts, color, normal=(0, 1, 0.15))


# rainbow stripe across the front part of the band (left edge to under the badge)
RZ0, RZ1 = 1.6, 2.3
xs = [-XI + 0.6 + k * (25.6 / 6) for k in range(7)]
for k, c in enumerate(RAINBOW):
    top_decal(xs[k], RZ0, xs[k + 1], RZ1, c)
# crease between the lip and the top
top_decal(-XI, ZT_F - 0.18, XI, ZT_F, HOLE, lift=0.02)
# vent slits along the back edge of the top
for k in range(20):
    x = -11.4 + k * 1.2
    top_decal(x, -10.75, x + 0.5, -10.05, HOLE)
# vent slits across the back face
for k in range(22):
    x = -12.6 + k * 1.2
    m.polygon([(x + 0.5, 3.1, -12.03), (x, 3.1, -12.03), (x, 5.4, -12.03), (x + 0.5, 5.4, -12.03)], HOLE, normal=(0, 0, -1))

# console keys on the lip: power and pause (left), select and reset (right)
lip_s = (YT_F - YL0) / (11.5 - ZT_F)
for x0, x1 in ((-12.6, -11.0), (-9.9, -8.3), (5.3, 6.9), (8.6, 10.2)):
    z0, z1 = 10.5, 11.25
    y0 = YL0 + (11.5 - z1) * lip_s - 0.05
    m.box(x0, y0, z0, x1, YL0 + (11.5 - z0) * lip_s + 0.12, z1, KEY, faces={'bottom': None})

# controller ports in the base front, under the lip; power and TV jacks at the back
for cx in (-5.0, -1.4):
    m.polygon([(cx - 1.2, 0.6, BZ1 + 0.02), (cx + 1.2, 0.6, BZ1 + 0.02), (cx + 1.2, 1.7, BZ1 + 0.02), (cx - 1.2, 1.7, BZ1 + 0.02)],
              HOLE, normal=(0, 0, 1))
for cx in (-7.0, 6.0):
    m.polygon([(cx + 0.8, 0.7, BZ0 - 0.02), (cx - 0.8, 0.7, BZ0 - 0.02), (cx - 0.8, 1.6, BZ0 - 0.02), (cx + 0.8, 1.6, BZ0 - 0.02)],
              HOLE, normal=(0, 0, -1))

print(m.stats())
print(m.save())
