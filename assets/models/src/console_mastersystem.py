# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega Master System (first model): low-poly console for the X7 Game frontend.

Real size 36.5 x 7.0 x 17.0 cm (W x H x D). Shape from photos of the real
console:
  * a black base box (vertical walls, about 4 cm high) on a dark inset
    plinth; the front has a recessed lower band with the power button at
    the far left, the two controller ports left of centre and the card slot
    (opening above a lip) right of centre, with small labels above them
  * on top a "hip roof": a flat top that rises from the front (4.45 cm) to
    the back (7.0 cm), big grey chamfers at both ends (narrow at the front,
    wide at the back) and a wide grey vented slope at the back
  * a thin red pinstripe along the top front edge
  * right of centre a recessed channel runs from the front edge to the back:
    the red control panel (RESET / PAUSE bars, the black power-on triangle,
    the TV-system box) on its sloped floor and, at its back, the cartridge
    slot: a well with a grey dust flap (part "flap", hinged on its back
    edge, swings down into the well when the cartridge goes in)
  * vertical vent slits on both end walls, ports on the back
The cartridge goes straight down into the slot, label to the front.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (41, 41, 44)        # black plastic: top, base walls
LOWER = (25, 26, 28)       # recessed lower front band
FACET = (74, 73, 80)       # grey end chamfers, back slope, channel walls
DARK = (12, 12, 14)        # holes, vents, ports, slot well, plinth
RED = (198, 32, 38)        # control panel, pinstripe, power label
FLAP = (124, 126, 134)     # smoky grey dust flap
LABEL = (156, 156, 162)    # the small white-framed labels

W2 = 18.25                 # half width
ZF, ZB = 8.5, -8.5         # front, back
YE = 4.0                   # eave: top of the base walls
YP = 0.45                  # top of the plinth
YS = 1.9                   # step between the lower (recessed) and upper front band
ZL = 8.2                   # lower front band depth
# top ("roof")
ZT0, YT0 = 8.1, 4.45       # front edge of the top
ZT1, YT1 = -3.6, 7.0       # back edge of the top
XT1 = 11.6                 # half width of the top's back edge
XT0 = W2 - (W2 - XT1) / (YT1 - YE) * (YT0 - YE)   # keeps the end chamfers planar
# channel (control panel + cartridge slot), right of centre
CX0, CX1 = -1.0, 10.6
XS = (CX0 + CX1) / 2       # slot centre x = 4.8
ZC0, YC0 = 0.2, 5.6        # panel floor rises from the front edge to here; slot floor flat behind
# cartridge well (media: 10.0 x 13.0 x 2.0, grooves 10.04 x 2.04)
MX = 5.12                  # well half width (0.10 clearance)
ZW0, ZW1 = -2.95, -0.60    # well back / front (flap + cartridge + clearances)
YW = 0.6                   # well floor
FT = 0.15                  # flap thickness
FY1 = YC0 - 0.25           # flap top (recessed in the well)

m = Model('mastersystem', 'console')


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def face(pts, col, out):
    """planar polygon, wound to face the `out` direction"""
    nx = ny = nz = 0.0
    for i in range(len(pts)):
        p, q = pts[i], pts[(i + 1) % len(pts)]
        nx += (p[1] - q[1]) * (p[2] + q[2])
        ny += (p[2] - q[2]) * (p[0] + q[0])
        nz += (p[0] - q[0]) * (p[1] + q[1])
    n = (nx, ny, nz)
    if n[0] * out[0] + n[1] * out[1] + n[2] * out[2] < 0:
        n = (-nx, -ny, -nz)
    return m.polygon(pts, col, normal=n)


# ------------------------------------------------------------------ base
m.box(-W2 + 0.3, 0, ZB + 0.3, W2 - 0.3, YP, ZL - 0.3, DARK, faces={'top': None})
prof = [(ZB, YP), (ZL, YP), (ZL, YS), (ZF, YS), (ZF, YE), (ZB, YE)]   # (z, y)
for sx in (-1, 1):
    face([(sx * W2, y, z) for z, y in prof], BODY, (sx, 0, 0))
face([(-W2, YP, ZB), (W2, YP, ZB), (W2, YP, ZL), (-W2, YP, ZL)], DARK, (0, -1, 0))
face([(-W2, YP, ZL), (W2, YP, ZL), (W2, YS, ZL), (-W2, YS, ZL)], LOWER, (0, 0, 1))
face([(-W2, YS, ZL), (W2, YS, ZL), (W2, YS, ZF), (-W2, YS, ZF)], DARK, (0, -1, 0))
face([(-W2, YS, ZF), (W2, YS, ZF), (W2, YE, ZF), (-W2, YE, ZF)], BODY, (0, 0, 1))
face([(-W2, YP, ZB), (W2, YP, ZB), (W2, YE, ZB), (-W2, YE, ZB)], BODY, (0, 0, -1))


# ------------------------------------------------------------------ roof
def ytop(z):
    return YT0 + (ZT0 - z) * (YT1 - YT0) / (ZT0 - ZT1)


def ychan(z):
    if z >= ZC0:
        return YT0 + (ZT0 - z) * (YC0 - YT0) / (ZT0 - ZC0)
    return YC0


# front bevel (carries the red pinstripe)
face([(-W2, YE, ZF), (W2, YE, ZF), (XT0, YT0, ZT0), (-XT0, YT0, ZT0)], BODY, (0, 1, 1))
# end chamfers
for sx in (-1, 1):
    face([(sx * W2, YE, ZF), (sx * W2, YE, ZB), (sx * XT1, YT1, ZT1), (sx * XT0, YT0, ZT0)], FACET, (sx, 1, 0))
# top, left and right of the channel
face([(-XT0, YT0, ZT0), (CX0, YT0, ZT0), (CX0, YT1, ZT1), (-XT1, YT1, ZT1)], BODY, (0, 1, 0))
face([(CX1, YT0, ZT0), (XT0, YT0, ZT0), (XT1, YT1, ZT1), (CX1, YT1, ZT1)], BODY, (0, 1, 0))
# back slope, left and right of the channel
face([(-W2, YE, ZB), (CX0, YE, ZB), (CX0, YT1, ZT1), (-XT1, YT1, ZT1)], FACET, (0, 1, -1))
face([(CX1, YE, ZB), (W2, YE, ZB), (XT1, YT1, ZT1), (CX1, YT1, ZT1)], FACET, (0, 1, -1))
# channel: panel floor, slot floor around the well, back slope, side walls
face([(CX0, YT0, ZT0), (CX1, YT0, ZT0), (CX1, YC0, ZC0), (CX0, YC0, ZC0)], BODY, (0, 1, 0))
face([(CX0, YC0, ZC0), (CX1, YC0, ZC0), (CX1, YC0, ZW1), (CX0, YC0, ZW1)], BODY, (0, 1, 0))
face([(CX0, YC0, ZW0), (CX1, YC0, ZW0), (CX1, YC0, ZT1), (CX0, YC0, ZT1)], BODY, (0, 1, 0))
face([(CX0, YC0, ZW1), (XS - MX, YC0, ZW1), (XS - MX, YC0, ZW0), (CX0, YC0, ZW0)], BODY, (0, 1, 0))
face([(XS + MX, YC0, ZW1), (CX1, YC0, ZW1), (CX1, YC0, ZW0), (XS + MX, YC0, ZW0)], BODY, (0, 1, 0))
face([(CX0, YE, ZB), (CX1, YE, ZB), (CX1, YC0, ZT1), (CX0, YC0, ZT1)], FACET, (0, 1, -1))
wall = [(ZT0, YT0), (ZT1, YT1), (ZB, YE), (ZT1, YC0), (ZC0, YC0)]
face([(CX0, y, z) for z, y in wall], FACET, (1, 0, 0))
face([(CX1, y, z) for z, y in wall], FACET, (-1, 0, 0))

# cartridge well: walls face inwards, dark
xa, xb = XS - MX, XS + MX
face([(xa, YW, ZW0), (xb, YW, ZW0), (xb, YC0, ZW0), (xa, YC0, ZW0)], DARK, (0, 0, 1))
face([(xa, YW, ZW1), (xb, YW, ZW1), (xb, YC0, ZW1), (xa, YC0, ZW1)], DARK, (0, 0, -1))
face([(xa, YW, ZW0), (xa, YW, ZW1), (xa, YC0, ZW1), (xa, YC0, ZW0)], DARK, (1, 0, 0))
face([(xb, YW, ZW0), (xb, YW, ZW1), (xb, YC0, ZW1), (xb, YC0, ZW0)], DARK, (-1, 0, 0))
face([(xa, YW, ZW0), (xb, YW, ZW0), (xb, YW, ZW1), (xa, YW, ZW1)], DARK, (0, 1, 0))

# dust flap (closed), hinged on its back bottom edge
with m.part('flap'):
    m.box(xa + 0.04, FY1 - FT, ZW0 + 0.02, xb - 0.04, FY1, ZW1 - 0.04, FLAP)


# ------------------------------------------------------------------ decals
def panel_pt(x, z, lift=0.025):
    """a point on the sloped panel floor of the channel, lifted along its normal"""
    k = (YC0 - YT0) / (ZT0 - ZC0)            # rise per cm going back
    n = (0.0, 1.0, k)
    l = math.sqrt(1 + k * k)
    return (x, ychan(z) + lift / l, z + lift * k / l)


def panel_poly(pts, col, lift=0.025):
    face([panel_pt(x, z, lift) for x, z in pts], col, (0, 1, 0.15))


def panel_rect(x0, z0, x1, z1, col, lift=0.025):
    panel_poly([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], col, lift)


# red control panel and its black shapes
panel_rect(CX0 + 0.2, 7.85, CX1 - 0.2, ZC0 + 0.15, RED)
panel_rect(CX0 + 0.4, 1.95, XS - 0.15, 1.1, DARK, 0.05)          # RESET bar
panel_rect(XS + 0.15, 1.95, CX1 - 0.4, 1.1, DARK, 0.05)          # PAUSE bar
panel_poly([(0.3, 5.55), (0.3, 3.75), (4.6, 4.65)], DARK, 0.05)  # power-on triangle
panel_rect(6.7, 5.35, 9.3, 4.35, DARK, 0.05)                    # TV-system box
panel_rect(CX0 + 0.4, 7.55, 6.8, 7.25, (120, 18, 22), 0.05)       # hatched strip

# red pinstripe on the front bevel
bz = lambda t: (ZF + (ZT0 - ZF) * t, YE + (YT0 - YE) * t)
(za, ya), (zb, yb) = bz(0.3), bz(0.7)
nl = 0.02 / math.sqrt(2)
face([(-W2 + 0.1, ya + nl, za + nl), (W2 - 0.1, ya + nl, za + nl), (W2 - 0.3, yb + nl, zb + nl),
      (-W2 + 0.3, yb + nl, zb + nl)], RED, (0, 1, 1))

# front: power button + label, controller ports + labels, card slot + label
m.box(-16.6, 0.6, ZL, -13.9, 1.75, ZL + 0.35, BODY, faces={'back': None})
m.decal_xy([(-16.6, 2.45), (-13.9, 2.45), (-13.9, 2.85), (-16.6, 2.85)], ZF, RED)
for cx in (-3.25, 0.1):
    m.decal_xy([(cx - 1.1, 0.75), (cx + 1.1, 0.75), (cx + 1.1, 1.75), (cx - 1.1, 1.75)], ZL, (16, 16, 18), 0.02)
    m.decal_xy([(cx - 0.8, 1.55), (cx + 0.8, 1.55), (cx + 0.6, 0.95), (cx - 0.6, 0.95)], ZL, DARK, 0.04)
    m.decal_xy([(cx - 1.4, 2.45), (cx + 1.4, 2.45), (cx + 1.4, 2.8), (cx - 1.4, 2.8)], ZF, LABEL)
m.box(4.4, YP, ZL, 10.2, YS, ZF, BODY, faces={'back': None, 'top': None})       # card slot lip
m.decal_xy([(4.4, YS), (10.2, YS), (10.2, 3.45), (4.4, 3.45)], ZF, DARK)            # card slot opening
m.decal_xy([(10.8, 2.45), (14.2, 2.45), (14.2, 2.8), (10.8, 2.8)], ZF, LABEL)

# vent slits on both end walls
for sx in (-1, 1):
    x = sx * (W2 + 0.02)
    for i in range(16):
        z0 = -7.4 + i * 0.86
        face([(x, 0.9, z0), (x, 0.9, z0 + 0.32), (x, 3.5, z0 + 0.32), (x, 3.5, z0)], DARK, (sx, 0, 0))


# vent rows on the back slope (main slope left and right of the channel)
def slope_pt(x, t, lift=0.025, ytop=YT1):
    """t = 0 at the top edge of the back slope (at height ytop), 1 at the eave"""
    z = ZT1 + (ZB - ZT1) * t
    y = ytop + (YE - ytop) * t
    dz, dy = ZB - ZT1, YE - ytop
    l = math.hypot(dz, dy)
    return (x, y + lift * abs(dz) / l, z - lift * abs(dy) / l)


for r in range(6):
    t0 = 0.22 + r * 0.12
    t1 = t0 + 0.06
    for xa_, xb_ in ((-12.6, -9.8), (-9.4, -6.6), (-6.2, -3.4), (-3.0, -1.3), (10.9, 12.4)):
        if xa_ < -XT1 - (W2 - XT1) * t0 + 0.4:
            continue
        face([slope_pt(xa_, t1), slope_pt(xb_, t1), slope_pt(xb_, t0), slope_pt(xa_, t0)], DARK, (0, 1, -1))


# dark frame behind the cartridge well
face([(CX0 + 0.3, YC0 + 0.02, ZW0 - 0.35), (CX1 - 0.3, YC0 + 0.02, ZW0 - 0.35), (CX1 - 0.3, YC0 + 0.02, ZW0),
      (CX0 + 0.3, YC0 + 0.02, ZW0)], DARK, (0, 1, 0))

# back ports
for cx, r in ((-3.5, 0.6), (-6.9, 0.42), (-8.8, 0.3)):
    pts = [(cx + r * math.cos(math.radians(a)), 2.1 + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    face([(x, y, ZB - 0.02) for x, y in pts], DARK, (0, 0, -1))
face([(-5.6, 1.8, ZB - 0.02), (-5.0, 1.8, ZB - 0.02), (-5.0, 2.4, ZB - 0.02), (-5.6, 2.4, ZB - 0.02)], DARK, (0, 0, -1))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
