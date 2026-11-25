# SPDX-License-Identifier: GPL-3.0-or-later
"""NEC TurboGrafx-16 (North American PC Engine): low-poly console model.

Built from Wikimedia Commons photos of the real console (front-left,
front-right and rear views, with and without the rear expansion cover):

  * a long black slab (36.5 x 23 x 6.6 cm with the rear cover on): a tall
    vertical front face, a rounded front top edge, then a gently sloping
    band carrying four parallel grooves before the flat top; the same
    grooved slope runs down the rear edge to the rear cover; rounded
    vertical corners
  * the HuCard / TurboChip slot right of centre: an open pocket cut into
    the front top edge (with the finger scoop at its front) and behind it
    the raised D-shaped hood the card slides under, label up
  * the power slide switch on the front face left of the pocket (it is
    the moving part "switch": once the card is in it slides over to ON,
    as the real switch locks the card)
  * the round controller port low on the front face of the right block
  * the rear expansion cover, lower than the console, with a chamfered
    rear top edge, rounded rear corners and three panels
  * a plain orange/red stripe where the badge sits on the top (no text)
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

BODY = (54, 54, 58)        # black plastic, lifted so it shades
GROOVE = (16, 16, 18)      # grooves, seams, badge plate, underside
FLOOR = (40, 40, 44)       # card pocket floor
RIB = (72, 72, 78)         # pocket floor ribs
CAVITY = (6, 6, 8)         # inside the slot, port, jack
COVER = (60, 60, 64)       # rear expansion cover
HOOD = (70, 70, 76)        # the hood over the slot
KNOB = (78, 78, 84)        # power switch knob
PORT = (150, 150, 156)     # controller port ring
ORANGE = (240, 112, 32)    # badge stripe
RED = (214, 40, 30)        # badge disc
SCOOP = (24, 24, 26)       # finger scoop in front of the slot

W = 36.5
XL, XR = -W / 2, W / 2
ZF = 11.5                  # front face
ZR = -5.5                  # rear of the main body = front of the rear cover
ZC = -11.5                 # rear of the cover
H_FACE = 4.2               # top of the vertical front face
H_EDGE = 5.4               # end of the rounded front edge / top of the rear face
E_IN = 0.7                 # ... that far in from the front
H_TOP = 6.6                # main top
S_IN = 4.0                 # front slope (grooves) reaches the top this far in
R_IN = 3.0                 # rear slope depth
H_CB, H_CT = 3.8, 5.4      # rear cover: rear face height, top height

# card slot column (between the left main block and the right block)
SX0, SX1 = 3.0, 11.4
SCX = (SX0 + SX1) / 2      # 7.2
H_FLOOR = H_FACE           # pocket floor = bottom of the slot
Z_HOOD = ZF - 6.0          # front of the hood = the slot opening (5.5)
H_HOOD = H_TOP + 0.3       # hood top
HOOD_ZC, HOOD_RZ = -1.0, 3.4   # the hood's rounded back (half ellipse)
TX0, TX1 = SCX - 2.85, SCX + 2.85   # slot / tunnel inside: card 5.4 + 2 x 0.15
TY1 = H_FLOOR + 0.5        # tunnel ceiling (card 4.25..4.61)
TZ = Z_HOOD - 7.45         # tunnel back wall (card contacts 0.15 short of it)

m = Model('pcengine', 'console')


def arc(cx, cz, rx, rz, a0, a1, seg):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / seg)),
             cz + rz * math.sin(math.radians(a0 + (a1 - a0) * i / seg))) for i in range(seg + 1)]


def ring(side, xin, xout, zf, zr, r, seg=3):
    """Plan outline of an end block (x, z), counter-clockwise seen from
    above, open (square) at x = xin; the outer end has rounded corners.
    side = -1: left block (outer end xout < xin), +1: right block."""
    if side < 0:
        return [(xin, zr)] + arc(xout + r, zr + r, r, r, 270, 180, seg) + arc(xout + r, zf - r, r, r, 180, 90, seg) + [(xin, zf)]
    return [(xin, zf)] + arc(xout - r, zf - r, r, r, 90, 0, seg) + arc(xout - r, zr + r, r, r, 0, -90, seg) + [(xin, zr)]


def loft(rings, color, cx, cz, closed, top_color=None, skip=None):
    """Side bands between rings (same point count) and the top cap."""
    n = len(rings[0][1])
    for (ya, ra), (yb, rb) in zip(rings, rings[1:]):
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            (xa, za), (xb, zb) = ra[i], ra[j]
            (xc, zc), (xd, zd) = rb[j], rb[i]
            if skip and skip(xa, za, xb, zb, ya, yb):
                continue
            mx, mz = (xa + xb + xc + xd) / 4, (za + zb + zc + zd) / 4
            ex, ez = xb - xa, zb - za
            nx, nz = ez, -ex
            if nx * (mx - cx) + nz * (mz - cz) < 0:
                nx, nz = -nx, -nz
            l = math.hypot(nx, nz) or 1
            m.polygon([(xa, ya, za), (xb, ya, zb), (xc, yb, zc), (xd, yb, zd)], color, normal=(nx / l, 0.5, nz / l))
    m.polygon([(x, rings[-1][0], z) for x, z in rings[-1][1]], top_color or color, normal=(0, 1, 0))
    m.polygon([(x, rings[0][0], z) for x, z in rings[0][1]], GROOVE, normal=(0, -1, 0))


def end_block(side, xin, xout):
    """A main block, open square end at xin closed by its side profile."""
    rings = [
        (0.0, ring(side, xin, xout, ZF, ZR, 2.2)),
        (H_FACE, ring(side, xin, xout, ZF, ZR, 2.2)),
        (H_EDGE, ring(side, xin, xout - side * 0.35, ZF - E_IN, ZR, 2.0)),
        (H_TOP, ring(side, xin, xout - side * 0.8, ZF - S_IN, ZR + R_IN, 1.6)),
    ]
    # the straight rear face below the cover's top is hidden by the cover
    hidden = lambda xa, za, xb, zb, ya, yb: abs(za - ZR) < 1e-6 and abs(zb - ZR) < 1e-6 and yb <= H_CT + 1e-6
    loft(rings, BODY, (xin + xout) / 2, (ZF + ZR) / 2, False, skip=hidden)
    prof = [(ZF, 0.0), (ZF, H_FACE), (ZF - E_IN, H_EDGE), (ZF - S_IN, H_TOP), (ZR + R_IN, H_TOP), (ZR, H_EDGE), (ZR, 0.0)]
    m.polygon([(xin, y, z) for z, y in prof], BODY, normal=(-side, 0, 0))


def slope_strip(xa, xb, t0, t1, color, rear=False, lift=0.025):
    """A strip on the gentle front (or rear) slope, fractions t0..t1 up it."""
    if rear:
        z0, dz = ZR, R_IN
    else:
        z0, dz = ZF - E_IN, -(S_IN - E_IN)
    dy = H_TOP - H_EDGE
    ln = math.hypot(dz, dy)
    ny = abs(dz) / ln
    nz = (dy / ln) * (-1 if rear else 1)
    (za, ya), (zb, yb) = [(z0 + dz * t + nz * lift, H_EDGE + dy * t + ny * lift) for t in (t0, t1)]
    return m.polygon([(xa, ya, za), (xb, ya, za), (xb, yb, zb), (xa, yb, zb)], color, normal=(0, ny, nz))


# ---------------------------------------------------------------- body
end_block(-1, SX0, XL)        # left main block
end_block(+1, SX1, XR)        # right block (controller port)

# slot column base: front face, bottom, pocket floor, tunnel floor, notch floor
m.polygon([(SX0, 0, ZF), (SX1, 0, ZF), (SX1, H_FLOOR, ZF), (SX0, H_FLOOR, ZF)], BODY, normal=(0, 0, 1))
m.polygon([(SX0, 0, ZR), (SX1, 0, ZR), (SX1, 0, ZF), (SX0, 0, ZF)], GROOVE, normal=(0, -1, 0))
for z0, z1, c in ((Z_HOOD, ZF, FLOOR), (TZ, Z_HOOD, CAVITY), (ZR, TZ, FLOOR)):
    m.polygon([(SX0, H_FLOOR, z0), (SX1, H_FLOOR, z0), (SX1, H_FLOOR, z1), (SX0, H_FLOOR, z1)], c, normal=(0, 1, 0))
# the notch behind the hood ends at the cover: its face above the floor
m.polygon([(SX0, H_FLOOR, ZR), (SX1, H_FLOOR, ZR), (SX1, H_CT, ZR), (SX0, H_CT, ZR)], COVER, normal=(0, 0, 1))

# the hood over the slot: flat front, rounded back
hood = [(SX0, Z_HOOD), (SX1, Z_HOOD)] + arc(SCX, HOOD_ZC, (SX1 - SX0) / 2, HOOD_RZ, 0, -180, 6)
m.polygon([(x, H_HOOD, z) for x, z in hood], HOOD, normal=(0, 1, 0))
for (xa, za), (xb, zb) in zip(hood[2:], hood[3:]):
    mx, mz = (xa + xb) / 2 - SCX, (za + zb) / 2 - HOOD_ZC
    m.polygon([(xa, H_FLOOR, za), (xb, H_FLOOR, zb), (xb, H_HOOD, zb), (xa, H_HOOD, za)], BODY, normal=(mx, 0, mz))
for x, s in ((SX0, -1), (SX1, 1)):          # straight sides: the lip above the blocks
    m.polygon([(x, H_TOP, Z_HOOD), (x, H_TOP, HOOD_ZC), (x, H_HOOD, HOOD_ZC), (x, H_HOOD, Z_HOOD)], BODY, normal=(s, 0, 0))
# front of the hood around the slot opening
m.polygon([(SX0, TY1, Z_HOOD), (SX1, TY1, Z_HOOD), (SX1, H_HOOD, Z_HOOD), (SX0, H_HOOD, Z_HOOD)], BODY, normal=(0, 0, 1))
m.polygon([(SX0, H_FLOOR, Z_HOOD), (TX0, H_FLOOR, Z_HOOD), (TX0, TY1, Z_HOOD), (SX0, TY1, Z_HOOD)], BODY, normal=(0, 0, 1))
m.polygon([(TX1, H_FLOOR, Z_HOOD), (SX1, H_FLOOR, Z_HOOD), (SX1, TY1, Z_HOOD), (TX1, TY1, Z_HOOD)], BODY, normal=(0, 0, 1))
# the tunnel the card slides into (inside faces, dark)
m.polygon([(TX0, TY1, Z_HOOD), (TX1, TY1, Z_HOOD), (TX1, TY1, TZ), (TX0, TY1, TZ)], CAVITY, normal=(0, -1, 0))
m.polygon([(TX0, H_FLOOR, Z_HOOD), (TX0, TY1, Z_HOOD), (TX0, TY1, TZ), (TX0, H_FLOOR, TZ)], CAVITY, normal=(1, 0, 0))
m.polygon([(TX1, H_FLOOR, Z_HOOD), (TX1, TY1, Z_HOOD), (TX1, TY1, TZ), (TX1, H_FLOOR, TZ)], CAVITY, normal=(-1, 0, 0))
m.polygon([(TX0, H_FLOOR, TZ), (TX1, H_FLOOR, TZ), (TX1, TY1, TZ), (TX0, TY1, TZ)], CAVITY, normal=(0, 0, 1))

# pocket: the finger scoop at the front (on the floor and down the front face), ribs
m.polygon([(x, H_FLOOR + 0.02, z) for x, z in [(SCX, ZF)] + arc(SCX, ZF, 2.0, 2.0, 0, -180, 6)], SCOOP, normal=(0, 1, 0))
m.polygon([(x, H_FLOOR - 0.04 + y, ZF + 0.02) for x, y in arc(SCX, 0, 2.0, 1.5, 180, 360, 6)], SCOOP, normal=(0, 0, 1))
for x in (SCX - 2.4, SCX - 1.0, SCX + 0.4, SCX + 1.8):
    m.decal_xz([(x, Z_HOOD + 0.15), (x + 0.14, Z_HOOD + 0.15), (x + 0.14, ZF - 2.2), (x, ZF - 2.2)], H_FLOOR, RIB, lift=0.015)

# ---------------------------------------------------------------- details
# four grooves along the front slope of both blocks, three along the rear slope
for t in (0.14, 0.34, 0.54, 0.74):
    slope_strip(XL + 1.9, SX0 - 0.3, t, t + 0.09, GROOVE)
    slope_strip(SX1 + 0.3, XR - 1.9, t, t + 0.09, GROOVE)
for t in (0.2, 0.45, 0.7):
    slope_strip(XL + 2.2, SX0 - 0.3, t, t + 0.1, GROOVE, rear=True)
    slope_strip(SX1 + 0.3, XR - 2.2, t, t + 0.1, GROOVE, rear=True)

# badge on the top behind the slope: plain plate, orange stripe, red disc
BX0, BX1 = -8.4, -1.4
BZ1 = ZF - S_IN - 0.5
BZ0 = BZ1 - 1.1
BZM = (BZ0 + BZ1) / 2
m.decal_xz([(BX0, BZ0), (BX1, BZ0), (BX1, BZ1), (BX0, BZ1)], H_TOP, GROOVE, lift=0.02)
m.decal_xz([(BX0 + 0.4, BZM - 0.17), (BX1 - 1.3, BZM - 0.17), (BX1 - 1.3, BZM + 0.17), (BX0 + 0.4, BZM + 0.17)], H_TOP, ORANGE, lift=0.04)
m.decal_xz(arc(BX1 - 0.65, BZM, 0.36, 0.36, 0, 360, 6)[:-1], H_TOP, RED, lift=0.04)

# controller port low on the right block's front face
PX, PY = 13.9, 2.0
m.cylinder_z(PX, PY, 0.9, ZF - 0.01, ZF + 0.25, PORT, segments=8, back=False)
m.polygon([(PX + 0.6 * math.cos(a * math.pi / 4), PY + 0.6 * math.sin(a * math.pi / 4), ZF + 0.27)
           for a in range(8)], CAVITY, normal=(0, 0, 1))

# power switch on the front face left of the pocket: dark track, knob slides right
SWX, SWY = 0.3, 2.9
m.decal_xy([(SWX - 0.8, SWY - 0.35), (SWX + 1.9, SWY - 0.35), (SWX + 1.9, SWY + 0.35), (SWX - 0.8, SWY + 0.35)], ZF, GROOVE, lift=0.02)
with m.part('switch'):
    m.box(SWX - 0.5, SWY - 0.85, ZF + 0.02, SWX + 0.5, SWY + 0.85, ZF + 0.55, KNOB, faces={'back': None})

# AV / power jack on the left end
m.polygon([(XL - 0.02, 2.4 + 0.5 * math.sin(a * math.pi / 3), ZF - 3.5 + 0.5 * math.cos(a * math.pi / 3))
           for a in range(6)], CAVITY, normal=(-1, 0, 0))

# ---------------------------------------------------------------- rear cover
CW = XR - 0.25


def cover_ring(xh, zr, r):
    return [(-xh, ZR), (xh, ZR)] + arc(xh - r, zr + r, r, r, 0, -90, 3) + arc(-xh + r, zr + r, r, r, 270, 180, 3)


loft([(0.0, cover_ring(CW, ZC, 2.0)), (H_CB, cover_ring(CW, ZC, 2.0)), (H_CT, cover_ring(CW - 0.8, ZC + 2.0, 1.2))],
     COVER, 0.0, (ZR + ZC) / 2, True)   # its front face shows at the main body's rounded rear corners
# three panels: seams down the rear face, the chamfer and across the top
for sx in (-8.0, 8.0):
    m.polygon([(sx - 0.07, 0.5, ZC - 0.02), (sx + 0.07, 0.5, ZC - 0.02), (sx + 0.07, H_CB, ZC - 0.02),
               (sx - 0.07, H_CB, ZC - 0.02)], GROOVE, normal=(0, 0, -1))
    ln = math.hypot(2.0, H_CT - H_CB)
    ny, nz = 2.0 / ln * 0.02, -(H_CT - H_CB) / ln * 0.02
    m.polygon([(sx - 0.07, H_CB + ny, ZC + nz), (sx + 0.07, H_CB + ny, ZC + nz), (sx + 0.07, H_CT + ny, ZC + 2.0 + nz),
               (sx - 0.07, H_CT + ny, ZC + 2.0 + nz)], GROOVE, normal=(0, 2.0, -(H_CT - H_CB)))
    m.decal_xz([(sx - 0.07, ZC + 2.0), (sx + 0.07, ZC + 2.0), (sx + 0.07, ZR), (sx - 0.07, ZR)], H_CT, GROOVE, lift=0.02)

print(m.stats())
m.save()
