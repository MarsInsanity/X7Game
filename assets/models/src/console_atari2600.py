# SPDX-License-Identifier: GPL-3.0-or-later
"""Atari 2600 (four-switch wood-grain model), low-poly.

A long low wedge: black body, sloped wood-grain front panel carrying four
silver/black toggle switches, ribbed black top rising to the back, a raised
cartridge slot bezel in the top centre, two controller ports on the back.
About 34.5 x 9 x 23 cm.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

BODY = (34, 32, 32)
RIB = (70, 68, 66)
WOOD = (150, 92, 46)
GRAIN = (92, 52, 24)
GRAIN2 = (118, 70, 34)
SILVER = (200, 200, 206)
LEVER = (14, 14, 14)
SLOT = (0, 0, 0)
BEZEL = (58, 56, 56)
PORT = (120, 120, 124)

m = Model('atari2600', 'console')

W = 34.5
HX = W / 2
ZF, ZB = 11.5, -11.5          # front / back
LIP = 1.0                     # black lip under the wood panel
A = (ZF, LIP)                 # bottom of the wood slope (z, y)
B = (8.0, 5.0)                # top of the wood slope
YB = 7.8                      # body height at the back


def top_y(z):
    """height of the black top surface at depth z"""
    return B[1] + (B[0] - z) * (YB - B[1]) / (B[0] - ZB)


# ---- main body (side profile, extruded along X)
m.extrude_yz([(ZF, 0), A, B, (ZB, YB), (ZB, 0)], -HX, HX, BODY)

# ---- wood-grain panel: a thin slab on the front slope
dz, dy = B[0] - A[0], B[1] - A[1]
L = math.hypot(dz, dy)
uz, uy = dz / L, dy / L                 # up the slope
nz, ny = -uy, -uz                       # outward normal (z, y)
if nz < 0:
    nz, ny = -nz, -ny
T = 0.2                                  # slab thickness
WX = HX - 0.25


def panel(x, v, off):
    """3D point on the panel: x across, v up the slope, off along the normal"""
    return (x, A[1] + v * uy + off * ny, A[0] + v * uz + off * nz)


p0, p1 = panel(0, 0, 0), panel(0, L, 0)
p2, p3 = panel(0, L, T), panel(0, 0, T)
m.extrude_yz([(p0[2], p0[1] + 0.0), (p1[2], p1[1]), (p2[2], p2[1]), (p3[2], p3[1])],
             -WX, WX, WOOD)


def panel_rect(x0, x1, v0, v1, color, off=T + 0.03):
    m.polygon([panel(x0, v0, off), panel(x1, v0, off), panel(x1, v1, off), panel(x0, v1, off)],
              color, normal=(0, ny, nz))


# grain: long darker streaks of differing lengths across the panel
for x0, x1, v, h, c in [(-WX, -3.5, 0.55, 0.22, GRAIN), (-1.0, WX, 0.75, 0.18, GRAIN2),
                        (-WX, 5.5, 1.55, 0.16, GRAIN2), (8.5, WX, 1.40, 0.24, GRAIN),
                        (-WX, -9.5, 3.70, 0.20, GRAIN), (-5.0, WX, 3.95, 0.20, GRAIN),
                        (-WX, 1.5, 4.45, 0.18, GRAIN2), (4.0, WX, 4.55, 0.16, GRAIN2)]:
    panel_rect(x0, x1, v, v + h, c)

# ---- four toggle switches (two left, two right) and a centre badge plate
ang = -math.degrees(math.atan2(ny, nz))     # turn a +Z-facing part onto the slope
VC = L * 0.47
for sx in (-11.5, -6.5, 6.5, 11.5):
    ids = m.box(-1.15, -1.5, 0, 1.15, 1.5, 0.35, SILVER)
    ids += m.decal_xy([(-0.35, -1.1), (0.35, -1.1), (0.35, 1.1), (-0.35, 1.1)], 0.35, SLOT, lift=0.03)
    # lever: chunky black cap, pushed up in its slot, leaning outward
    lev = m.box(-0.55, -0.45, 0.0, 0.55, 0.45, 1.7, LEVER)
    m.transform(lev, Model.rot_x(-28))
    m.transform(lev, Model.move(0, 0.45, 0.33))
    ids += lev
    c = panel(sx, VC, T)
    m.transform(ids, Model.rot_x(ang))
    m.transform(ids, Model.move(c[0], c[1], c[2]))
panel_rect(-2.6, 2.6, VC - 0.8, VC + 0.8, LEVER, off=T + 0.04)

# ---- raised cartridge slot bezel (top centre, towards the back)
HZ0, HZ1, HXW, HY = -1.6, -10.2, 6.0, 9.0
m.extrude_yz([(HZ0, top_y(HZ0) - 0.5), (HZ0, HY - 0.25), (HZ0 - 0.4, HY), (HZ1 + 0.4, HY),
              (HZ1, HY - 0.25), (HZ1, top_y(HZ1) - 0.5)], -HXW, HXW, BODY)
m.decal_xz([(-5.4, HZ0 - 0.7), (5.4, HZ0 - 0.7), (5.4, HZ1 + 0.7), (-5.4, HZ1 + 0.7)], HY, BEZEL)
m.decal_xz([(-4.4, -4.6), (4.4, -4.6), (4.4, -7.0), (-4.4, -7.0)], HY, SLOT, lift=0.05)

# ---- ribs across the top (full width in front of the bezel, beside it behind)
RD, RH = 0.6, 0.28


def rib(z, x0, x1):
    za, zb = z, z - RD
    m.extrude_yz([(za, top_y(za) - 0.1), (za, top_y(za) + RH), (zb, top_y(zb) + RH), (zb, top_y(zb) - 0.1)],
                 x0, x1, RIB)


z = 6.6
while z - RD > ZB + 0.6:
    if z - RD > HZ0 + 0.1:
        rib(z, -HX + 0.7, HX - 0.7)
    else:
        rib(z, -HX + 0.7, -HXW - 0.5)
        rib(z, HXW + 0.5, HX - 0.7)
    z -= 1.4

# ---- back: two controller ports
for px in (-9.0, -4.5):
    m.polygon([(px + 1.6, 3.0, ZB - 0.03), (px - 1.6, 3.0, ZB - 0.03), (px - 1.2, 1.9, ZB - 0.03),
               (px + 1.2, 1.9, ZB - 0.03)], PORT, normal=(0, 0, -1))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
