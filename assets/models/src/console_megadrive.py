# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega Genesis / Mega Drive (first model): low-poly console model.

Real size about 28.0 x 7.0 x 21.2 cm (w x h x d). From photos (Wikimedia
Commons, see the notes at the bottom):
  * a black slab 5.5 cm high with softly chamfered edges; the front third of
    the top runs down in a broad slope to a short vertical band (headphone
    jack left, two controller ports right)
  * the big raised round disc right of centre (diameter 16.4, centre 2.9 cm
    right of the middle, near the back edge), its rim a bright ring; the
    back half is flat and carries the cartridge slot, the front half runs
    down the slope with the raised "16-bit" tongue and the red power strip
  * the recessed control panel front left on the slope: volume slider,
    power switch with its red mark, light grey reset button
  * the slatted vent grille top left near the back
Moving parts: the two spring dust flaps in the slot (flap_front,
flap_back), hinged on the long edges of the opening, swinging down into
pockets either side of the cartridge.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

BODY = (40, 40, 44)        # black plastic (lifted so it shades)
DISC = (30, 30, 34)        # disc top
RING = (96, 96, 106)        # the bright rim of the disc
GROOVE = (14, 14, 16)      # recesses, grille floor, plinth
VOID = (4, 4, 4)           # inside the slot
FLAP = (54, 54, 60)        # dust flaps
TONGUE = (46, 46, 52)      # the raised "16-bit" tongue
RED = (186, 36, 40)        # power strip, switch mark
LIGHT = (200, 200, 196)    # reset button, port pins, jack ring
KNOB = (62, 62, 68)        # slider knobs
SLAT = (74, 74, 82)        # vent slats
BAND = (26, 26, 29)        # the short vertical front band (ports)
LED = (255, 90, 60)

W, D = 28.0, 21.2
X0, X1 = -W / 2, W / 2
ZB, ZF = -D / 2, D / 2
BEV = 0.9                  # side chamfer
YB = 0.4                   # plinth height
YT = 5.5                   # top surface

m = Model('megadrive', 'console')

# ------------------------------------------------------------ the disc and slot (plan)
CX, CZ = 2.9, -2.0
R_OUT, R_TOP = 8.2, 7.3    # disc foot radius / top radius (the bevel between is the ring)
SEG = 24
SZ = -5.6                  # slot centre (z)
SW, SD = 11.1, 2.3         # slot opening (cartridge 10.8 x 2.0)
SZ0, SZ1 = SZ - SD / 2, SZ + SD / 2
PK = 1.4                   # pocket half-depth below the lip (flaps fold into it)
Y_DISC = 6.85              # flat disc top
Z_DFLAT = -1.6             # disc is flat behind this, slopes down in front
Y_DFRONT = 5.0             # disc top height at its front edge (z = CZ + R_TOP)
Y_LIP = Y_DISC - 0.35              # underside of the slot lip
Y_FLOOR = 1.0              # cavity floor (cartridge bottom when seated)

# control panel recess (front left, on the slope)
PX0, PX1 = -11.7, -4.6
PZ0, PZ1 = 1.6, 9.4

# body side profile (z, y) along the top, back to front; extra points are
# the edges of the slot pocket and the control panel
BASE = [(-10.6, 5.0), (-10.2, YT), (2.0, YT), (4.0, 5.2), (8.8, 3.6), (10.3, 2.9), (10.6, 2.2)]


def ybody(z):
    if z <= BASE[0][0]:
        return BASE[0][1]
    for (za, ya), (zb, yb) in zip(BASE, BASE[1:]):
        if za <= z <= zb:
            return ya + (yb - ya) * (z - za) / (zb - za)
    return BASE[-1][1]


def ydisc(z):
    if z <= Z_DFLAT:
        return Y_DISC
    return Y_DISC + (Y_DFRONT - Y_DISC) * (z - Z_DFLAT) / (CZ + R_TOP - Z_DFLAT)


extra = [PZ0, PZ1, SZ - PK, SZ + PK]
prof = sorted(set([p[0] for p in BASE] + extra))
TOP = [(z, ybody(z)) for z in prof]           # top line, back to front
OUTLINE = [(ZB, YB)] + TOP + [(ZF, YB)]


def outer_profile(pts):
    """the side cap outline: the profile pulled in by BEV front and back
    (z scaled about the middle) and lowered by 0.7 BEV along the top"""
    k = (D - 2 * BEV) / D
    out = []
    for i, (z, y) in enumerate(pts):
        zz = z * k
        out.append((zz, YB if i in (0, len(pts) - 1) else y - 0.7 * BEV))
    return out


INNER = OUTLINE
OUTER = outer_profile(OUTLINE)         # the side caps (x = +-14)

XI0, XI1 = X0 + BEV, X1 - BEV

# side caps
for x, sgn in ((X0, -1), (X1, 1)):
    # vertical strips (well-shaped triangles, no long slivers)
    for (za, ya), (zb, yb) in zip(OUTER[1:-2], OUTER[2:-1]):
        m.polygon([(x, YB, za), (x, YB, zb), (x, yb, zb), (x, ya, za)], BODY, normal=(sgn, 0, 0))
# chamfer bands between the caps and the full-width top (every profile edge)
n = len(OUTLINE)
for i in range(n - 1):
    (za, ya), (zb, yb) = OUTLINE[i], OUTLINE[i + 1]
    (oa, pa), (ob, pb) = OUTER[i], OUTER[i + 1]
    # right side: inner at XI1, outer at X1
    m.polygon([(XI1, ya, za), (X1, pa, oa), (X1, pb, ob), (XI1, yb, zb)], BODY,
              normal=(0.7, (zb - za), -(yb - ya)))
    m.polygon([(XI0, yb, zb), (X0, pb, ob), (X0, pa, oa), (XI0, ya, za)], BODY,
              normal=(-0.7, (zb - za), -(yb - ya)))

# bottom
m.polygon([(XI0, YB, ZB), (XI1, YB, ZB), (XI1, YB, ZF), (XI0, YB, ZF)], GROOVE, normal=(0, -1, 0))
m.polygon([(XI1, YB, ZB), (X1, YB, OUTER[0][0]), (X1, YB, OUTER[-1][0]), (XI1, YB, ZF)], GROOVE, normal=(0, -1, 0))
m.polygon([(XI0, YB, ZF), (X0, YB, OUTER[-1][0]), (X0, YB, OUTER[0][0]), (XI0, YB, ZB)], GROOVE, normal=(0, -1, 0))


def strip(za, ya, zb, yb, x0, x1, color=BODY):
    """the top surface between two profile points, from x0 to x1"""
    if x1 - x0 < 1e-6:
        return []
    return m.polygon([(x0, ya, za), (x0, yb, zb), (x1, yb, zb), (x1, ya, za)], color,
                     normal=(0, zb - za, -(yb - ya)))


# back face and front face (full width between the chamfers)
m.polygon([(XI0, YB, ZB), (XI0, OUTLINE[1][1], ZB), (XI1, OUTLINE[1][1], ZB), (XI1, YB, ZB)], BODY, normal=(0, 0, -1))
m.polygon([(XI1, YB, ZF), (XI1, OUTLINE[-2][1], ZF), (XI0, OUTLINE[-2][1], ZF), (XI0, YB, ZF)], BAND, normal=(0, 0, 1))

# top line: holes for the slot pocket (under the disc) and the control panel
SX0, SX1 = CX - SW / 2, CX + SW / 2
for (za, ya), (zb, yb) in zip(TOP, TOP[1:]):
    zm = (za + zb) / 2
    holes = []
    if SZ - PK <= zm <= SZ + PK:
        holes.append((SX0, SX1))
    if PZ0 <= zm <= PZ1:
        holes.append((PX0, PX1))
    xs = [XI0]
    for h0, h1 in sorted(holes):
        xs += [h0, h1]
    xs.append(XI1)
    for k in range(0, len(xs), 2):
        strip(za, ya, zb, yb, xs[k], xs[k + 1])

# plinth (the darker foot the body stands on)
m.box(X0 + 1.0, 0.0, ZB + 1.0, X1 - 1.0, YB, ZF - 1.0, GROOVE, faces={'top': None})

# ------------------------------------------------------------ control panel recess
PD_BACK, PD_FRONT = 0.6, 0.35       # depth below the surface at the back / front edge
fy0 = ybody(PZ0) - PD_BACK
fy1 = ybody(PZ1) - PD_FRONT
m.polygon([(PX0, fy0, PZ0), (PX0, fy1, PZ1), (PX1, fy1, PZ1), (PX1, fy0, PZ0)], GROOVE,
          normal=(0, PZ1 - PZ0, -(fy1 - fy0)))
panel_top = [(z, y) for z, y in TOP if PZ0 <= z <= PZ1]
# side walls follow the profile
m.polygon([(PX0, y, z) for z, y in panel_top] + [(PX0, fy1, PZ1), (PX0, fy0, PZ0)], BODY, normal=(1, 0, 0))
m.polygon([(PX1, y, z) for z, y in panel_top] + [(PX1, fy1, PZ1), (PX1, fy0, PZ0)], BODY, normal=(-1, 0, 0))
m.quad((PX0, fy0, PZ0), (PX1, fy0, PZ0), (PX1, ybody(PZ0), PZ0), (PX0, ybody(PZ0), PZ0), BODY)   # back wall faces +z
m.quad((PX1, fy1, PZ1), (PX0, fy1, PZ1), (PX0, ybody(PZ1), PZ1), (PX1, ybody(PZ1), PZ1), BODY)   # front wall faces -z


def on_panel(z):
    """height of the panel floor at z"""
    return fy0 + (fy1 - fy0) * (z - PZ0) / (PZ1 - PZ0)


SL = math.atan2(fy0 - fy1, PZ1 - PZ0)          # floor tilt


def panel_box(x0, x1, z0, z1, h, color):
    """a block standing on the tilted panel floor, height h"""
    out = m.box(x0, 0, z0, x1, h, z1, color, faces={'bottom': None})
    zc = (z0 + z1) / 2
    ang = math.degrees(SL)
    m.transform(out, lambda p: (p[0], on_panel(zc) + p[1] * math.cos(SL) + (p[2] - zc) * math.sin(SL) - 0.02,
                                 zc + (p[2] - zc) * math.cos(SL) + p[1] * math.sin(SL)))
    return out


def panel_decal(x0, x1, z0, z1, color, lift=0.03):
    return m.polygon([(x0, on_panel(z0) + lift, z0), (x0, on_panel(z1) + lift, z1),
                      (x1, on_panel(z1) + lift, z1), (x1, on_panel(z0) + lift, z0)], color,
                     normal=(0, PZ1 - PZ0, -(fy1 - fy0)))


# volume slider: a long slot, the knob near its middle
panel_decal(-10.9, -10.0, 2.4, 7.4, VOID)
panel_box(-11.1, -9.8, 4.4, 5.8, 0.55, KNOB)
# power switch: a short horizontal slot, knob and red mark
panel_decal(-8.6, -5.5, 2.6, 3.9, VOID)
panel_box(-7.6, -6.4, 2.75, 3.75, 0.45, KNOB)
panel_box(-7.15, -6.85, 2.9, 3.6, 0.48, RED)
# reset button
panel_box(-8.4, -5.9, 5.6, 7.0, 0.35, LIGHT)

# ------------------------------------------------------------ vent grille (top, back left)
GX0, GX1, GZ0, GZ1 = -13.3, -8.1, -9.6, 0.4
m.decal_xz([(GX0, GZ0), (GX1, GZ0), (GX1, GZ1), (GX0, GZ1)], YT, GROOVE, lift=0.03)
NS = 14
for k in range(NS):
    z0 = GZ0 + 0.35 + k * (GZ1 - GZ0 - 0.35) / NS
    m.decal_xz([(GX0 + 0.3, z0), (GX1 - 0.3, z0), (GX1 - 0.3, z0 + 0.32), (GX0 + 0.3, z0 + 0.32)], YT, SLAT, lift=0.05)

# ------------------------------------------------------------ front band: jack and ports
YP = 1.3
m.decal_xy([(-8.6 + 0.32 * math.cos(a), YP + 0.32 * math.sin(a)) for a in [i * math.pi / 3 for i in range(6)]], ZF, LIGHT)
m.decal_xy([(-8.6 + 0.16 * math.cos(a), YP + 0.16 * math.sin(a)) for a in [i * math.pi / 3 for i in range(6)]], ZF, VOID, lift=0.04)
for px in (5.7, 8.9):
    m.decal_xy([(px - 1.05, YP + 0.45), (px + 1.05, YP + 0.45), (px + 0.85, YP - 0.45), (px - 0.85, YP - 0.45)], ZF, VOID)
    m.decal_xy([(px - 0.7, YP - 0.1), (px + 0.7, YP - 0.1), (px + 0.7, YP + 0.12), (px - 0.7, YP + 0.12)], ZF, LIGHT, lift=0.04)


# ------------------------------------------------------------ the disc
def circle(r, seg=SEG):
    return [(CX + r * math.cos(2 * math.pi * (i + 0.5) / seg), CZ + r * math.sin(2 * math.pi * (i + 0.5) / seg))
            for i in range(seg)]


def with_split(pts, zsplit):
    """insert points where the closed outline crosses z = zsplit"""
    out = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        out.append(a)
        if (a[1] - zsplit) * (b[1] - zsplit) < 0:
            t = (zsplit - a[1]) / (b[1] - a[1])
            out.append((a[0] + (b[0] - a[0]) * t, zsplit))
    return out


def clip(poly, fn):
    """Sutherland-Hodgman: keep the part where fn(p) >= 0 (fn linear)"""
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        fa, fb = fn(a), fn(b)
        if fa >= 0:
            out.append(a)
        if fa * fb < 0:
            t = fa / (fa - fb)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


# the disc outline, with extra points where the slot edges and the start of
# the slope cross it (so the ring and the top share their vertices)
ANG = [2 * math.pi * (i + 0.5) / SEG for i in range(SEG)]
for zl in (SZ0, SZ1, Z_DFLAT):
    a = math.asin((zl - CZ) / R_TOP)
    ANG += [a % (2 * math.pi), (math.pi - a) % (2 * math.pi)]
ANG.sort()
top_c = [(CX + R_TOP * math.cos(a), CZ + R_TOP * math.sin(a)) for a in ANG]
out_c = [(CX + R_OUT * math.cos(a), CZ + R_OUT * math.sin(a)) for a in ANG]
# disc foot (vertical band from inside the body up to the ring) and the ring bevel
Y_RING = 0.45          # height of the bevel
n = len(ANG)
for i in range(n):
    j = (i + 1) % n
    (ax, az), (bx, bz) = out_c[i], out_c[j]
    (cx_, cz_), (dx, dz) = top_c[i], top_c[j]
    ya_top, yb_top = ydisc(az) - Y_RING, ydisc(bz) - Y_RING
    # foot wall, outward facing: wound counter-clockwise seen from outside
    m.polygon([(ax, ybody(az) - 0.3, az), (bx, ybody(bz) - 0.3, bz), (bx, yb_top, bz), (ax, ya_top, az)], BODY,
              normal=((ax + bx) / 2 - CX, 0, (az + bz) / 2 - CZ))
    nrm = ((ax + bx) / 2 - CX, 0.9 * R_OUT, (az + bz) / 2 - CZ)
    for tri in (((ax, ya_top, az), (bx, yb_top, bz), (dx, ydisc(dz), dz)),
                ((ax, ya_top, az), (dx, ydisc(dz), dz), (cx_, ydisc(cz_), cz_))):
        m.polygon(list(tri), RING, normal=nrm)

# disc top: flat part (behind Z_DFLAT) with the slot opening, sloped part in front


def disc_top(poly2d, color=DISC):
    pts = [(x, ydisc(z), z) for x, z in poly2d]
    if len(pts) >= 3:
        m.polygon(pts, color, normal=(0, 1, 0) if all(z <= Z_DFLAT + 1e-6 for _, _, z in pts)
                  else (0, CZ + R_TOP - Z_DFLAT, Y_DISC - Y_DFRONT))


flat = clip(top_c, lambda p: Z_DFLAT - p[1])
slope = clip(top_c, lambda p: p[1] - Z_DFLAT)
disc_top(clip(flat, lambda p: SZ0 - p[1]))                                   # behind the slot
mid = clip(clip(flat, lambda p: p[1] - SZ0), lambda p: SZ1 - p[1])
disc_top(clip(mid, lambda p: SX0 - p[0]))                                     # left of the slot
disc_top(clip(mid, lambda p: p[0] - SX1))                                     # right of the slot
disc_top(clip(flat, lambda p: p[1] - SZ1))                                    # in front of the slot
disc_top(slope)

# the thin groove ring inside the rim
g0, g1 = circle(R_TOP - 0.55), circle(R_TOP - 0.3)
for i in range(SEG):
    j = (i + 1) % SEG
    q = [g0[i], g0[j], g1[j], g1[i]]
    if any(SZ0 - 0.05 < z < SZ1 + 0.05 and SX0 - 0.05 < x < SX1 + 0.05 for x, z in q):
        continue
    m.polygon([(x, ydisc(z) + 0.03, z) for x, z in q], GROOVE,
              normal=(0, 1, 0) if all(z <= Z_DFLAT for _, z in q) else (0, CZ + R_TOP - Z_DFLAT, Y_DISC - Y_DFRONT))

# the raised tongue on the sloped front half, with the red power strip
TX0, TX1 = CX - 3.1, CX + 3.1
TZ0, TZ1 = Z_DFLAT + 0.4, CZ + R_TOP - 1.4
TH = 0.25
t0, t1 = ydisc(TZ0) + TH, ydisc(TZ1) + TH
nrm_s = (0, CZ + R_TOP - Z_DFLAT, Y_DISC - Y_DFRONT)
m.polygon([(TX0, t0, TZ0), (TX0, t1, TZ1), (TX1, t1, TZ1), (TX1, t0, TZ0)], TONGUE, normal=nrm_s)
m.quad((TX0, ydisc(TZ1) - 0.05, TZ1), (TX1, ydisc(TZ1) - 0.05, TZ1), (TX1, t1, TZ1), (TX0, t1, TZ1), TONGUE)
m.quad((TX1, ydisc(TZ0) - 0.05, TZ0), (TX0, ydisc(TZ0) - 0.05, TZ0), (TX0, t0, TZ0), (TX1, t0, TZ0), TONGUE)
m.polygon([(TX0, ydisc(TZ0) - 0.05, TZ0), (TX0, ydisc(TZ1) - 0.05, TZ1), (TX0, t1, TZ1), (TX0, t0, TZ0)], TONGUE, normal=(-1, 0, 0))
m.polygon([(TX1, ydisc(TZ0) - 0.05, TZ0), (TX1, ydisc(TZ1) - 0.05, TZ1), (TX1, t1, TZ1), (TX1, t0, TZ0)], TONGUE, normal=(1, 0, 0))
RS = TZ1 - 1.2
yr0 = t0 + (t1 - t0) * (RS - TZ0) / (TZ1 - TZ0)
m.polygon([(TX0 + 0.1, yr0 + 0.03, RS), (TX0 + 0.1, t1 + 0.03, TZ1 - 0.1), (TX1 - 0.1, t1 + 0.03, TZ1 - 0.1),
           (TX1 - 0.1, yr0 + 0.03, RS)], RED, normal=nrm_s)
lz = RS + 0.55
ly = t0 + (t1 - t0) * (lz - TZ0) / (TZ1 - TZ0) + 0.06
m.polygon([(CX - 0.18, ly, lz - 0.18), (CX - 0.18, ly, lz + 0.18), (CX + 0.18, ly, lz + 0.18), (CX + 0.18, ly, lz - 0.18)], LED,
          normal=nrm_s)

# ------------------------------------------------------------ the slot: lip, pockets, cavity
# lip walls (the opening through the disc top plate)
m.quad((SX0, Y_LIP, SZ0), (SX1, Y_LIP, SZ0), (SX1, Y_DISC, SZ0), (SX0, Y_DISC, SZ0), GROOVE)      # back lip wall, faces +z
m.quad((SX1, Y_LIP, SZ1), (SX0, Y_LIP, SZ1), (SX0, Y_DISC, SZ1), (SX1, Y_DISC, SZ1), GROOVE)      # front lip wall, faces -z
m.quad((SX0, Y_LIP, SZ1), (SX0, Y_LIP, SZ0), (SX0, Y_DISC, SZ0), (SX0, Y_DISC, SZ1), GROOVE)      # left, faces +x
m.quad((SX1, Y_LIP, SZ0), (SX1, Y_LIP, SZ1), (SX1, Y_DISC, SZ1), (SX1, Y_DISC, SZ0), GROOVE)      # right, faces -x
# pocket ceilings (underside of the lip, front and back)
QZ0, QZ1 = SZ - PK, SZ + PK
m.quad((SX0, Y_LIP, SZ1), (SX1, Y_LIP, SZ1), (SX1, Y_LIP, QZ1), (SX0, Y_LIP, QZ1), VOID)   # faces -y
m.quad((SX0, Y_LIP, QZ0), (SX1, Y_LIP, QZ0), (SX1, Y_LIP, SZ0), (SX0, Y_LIP, SZ0), VOID)
# cavity walls (inward facing) and floor
m.quad((SX1, Y_FLOOR, QZ1), (SX0, Y_FLOOR, QZ1), (SX0, Y_LIP, QZ1), (SX1, Y_LIP, QZ1), VOID)     # front wall faces -z
m.quad((SX0, Y_FLOOR, QZ0), (SX1, Y_FLOOR, QZ0), (SX1, Y_LIP, QZ0), (SX0, Y_LIP, QZ0), VOID)     # back wall faces +z
m.quad((SX0, Y_FLOOR, QZ1), (SX0, Y_FLOOR, QZ0), (SX0, Y_LIP, QZ0), (SX0, Y_LIP, QZ1), VOID)     # left faces +x
m.quad((SX1, Y_FLOOR, QZ0), (SX1, Y_FLOOR, QZ1), (SX1, Y_LIP, QZ1), (SX1, Y_LIP, QZ0), VOID)     # right faces -x
m.quad((SX0, Y_FLOOR, QZ1), (SX1, Y_FLOOR, QZ1), (SX1, Y_FLOOR, QZ0), (SX0, Y_FLOOR, QZ0), VOID)  # floor faces +y

# dust flaps, closed: thin plates just under the lip, meeting in the middle
FT = 0.08
FX0, FX1 = SX0 + 0.04, SX1 - 0.04
with m.part('flap_front'):
    m.box(FX0, Y_LIP - FT, SZ + 0.02, FX1, Y_LIP, SZ1, FLAP)
with m.part('flap_back'):
    m.box(FX0, Y_LIP - FT, SZ0, FX1, Y_LIP, SZ - 0.02, FLAP)

print(m.stats())
m.save()

# Hinges for the system file: flap_front turns about its front edge
#   pivot (CX, Y_LIP - FT/2, SZ1), axis x, angle -90 (free edge swings down);
# flap_back about its back edge: pivot (CX, Y_LIP - FT/2, SZ0), angle +90.
print('slot centre x %.2f z %.2f, opening %.2f x %.2f, lip %.2f, floor %.2f, top %.2f'
      % (CX, SZ, SW, SD, Y_LIP, Y_FLOOR, Y_DISC))
print('flap pivots: front (%.2f, %.3f, %.3f) back (%.2f, %.3f, %.3f)'
      % (CX, Y_LIP - FT / 2, SZ1, CX, Y_LIP - FT / 2, SZ0))
