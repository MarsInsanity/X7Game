# SPDX-License-Identifier: GPL-3.0-or-later
"""NEC TurboGrafx-16 (North American PC Engine): low-poly console model.

Long black slab (~37 x 8 x 21 cm) with bevelled front and rear top edges,
the HuCard slot in a raised frame on the front with the power slider
above it, the single round controller port front right, orange/red accent
lines along the front bevel and on the top, the ribbed vent area over the
rear of the top, and the long expansion-port door across the back.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model, rgb565

BODY = (36, 36, 40)        # black plastic, lifted a touch so it shades
BOTTOM = (20, 20, 22)
RIB = (70, 70, 80)         # vent ribs on the top
FRAME = (84, 84, 92)       # HuCard slot frame
SLOT = (4, 4, 4)           # slot opening / connector slit
KNOB = (176, 176, 184)     # power slider knob
PORT = (120, 120, 128)     # controller port ring
PORTIN = (14, 14, 16)      # controller port inside
DOOR = (74, 74, 82)        # rear expansion door
ORANGE = (255, 128, 0)     # accent lines
RED = (224, 36, 24)        # accent line

W, D = 37.0, 21.0
X0, X1 = -W / 2, W / 2
ZF, ZB = D / 2, -D / 2
H_FRONT = 5.2              # top of the vertical front face
H_TOP = 7.6                # main top surface
Z_BEV = 8.6                # where the front bevel meets the top
H_BACK = 6.9               # top of the vertical rear face
Z_RBEV = -9.8

m = Model('pcengine', 'console')

# ---------------------------------------------------------------- body
profile = [(ZB, 0), (ZF, 0), (ZF, H_FRONT), (Z_BEV, H_TOP), (Z_RBEV, H_TOP), (ZB, H_BACK)]
body = m.extrude_yz(profile, X0, X1, BODY)
# darker bottom face
for t in body:
    ia, ib, ic, c = m.tris[t]
    if all(abs(m.verts[i][1]) < 1e-6 for i in (ia, ib, ic)):
        m.tris[t] = (ia, ib, ic, rgb565(*BOTTOM))


def bevel_band(t0, t1, xa, xb, color, lift=0.03):
    """a coloured strip on the front bevel between fractions t0..t1 of the
    way from the front face edge up to the top"""
    dz, dy = Z_BEV - ZF, H_TOP - H_FRONT
    ln = (dz * dz + dy * dy) ** 0.5
    nz, ny = dy / ln, -dz / ln            # outward normal (z, y)
    pts = []
    for t in (t0, t1):
        pts.append((ZF + dz * t + nz * lift, H_FRONT + dy * t + ny * lift))
    (za, ya), (zb, yb) = pts
    return m.polygon([(xa, ya, za), (xb, ya, za), (xb, yb, zb), (xa, yb, zb)], color, normal=(0, ny, nz))


# accent lines along the front bevel
bevel_band(0.16, 0.30, X0 + 0.6, X1 - 0.6, ORANGE)
bevel_band(0.40, 0.50, X0 + 0.6, X1 - 0.6, RED)

# ---------------------------------------------------------------- front
# HuCard slot: raised frame with the dark opening
FX0, FX1 = -11.0, 1.0
m.box(FX0, 1.2, ZF - 0.01, FX1, 4.6, ZF + 0.45, FRAME, faces={'back': None, 'bottom': None})
m.decal_xy([(FX0 + 1.0, 2.1), (FX1 - 1.0, 2.1), (FX1 - 1.0, 2.8), (FX0 + 1.0, 2.8)], ZF + 0.45, SLOT)
# power slider: dark track and a light knob above the slot
m.decal_xy([(FX0 + 1.0, 3.45), (FX0 + 6.0, 3.45), (FX0 + 6.0, 3.85), (FX0 + 1.0, 3.85)], ZF + 0.45, SLOT)
m.box(FX0 + 1.3, 3.25, ZF + 0.45, FX0 + 3.3, 4.05, ZF + 0.85, KNOB, faces={'back': None})

# single controller port, front right
m.cylinder_z(12.0, 2.7, 1.35, ZF - 0.01, ZF + 0.35, PORT, segments=10, back=False)
m.polygon([(12.0 + 0.9 * math.cos(a * math.pi / 5), 2.7 + 0.9 * math.sin(a * math.pi / 5), ZF + 0.38)
           for a in range(10)], PORTIN, normal=(0, 0, 1))

# ---------------------------------------------------------------- top
# ribbed vent area over the rear of the top
for i in range(6):
    z0 = -8.6 + i * 1.55
    m.box(X0 + 1.4, H_TOP - 0.01, z0, X1 - 1.4, H_TOP + 0.4, z0 + 0.7, RIB, faces={'bottom': None})

# accent on the front of the top: orange line across, red block (badge) left
m.decal_xz([(X0 + 1.4, 1.6), (X1 - 1.4, 1.6), (X1 - 1.4, 0.9), (X0 + 1.4, 0.9)], H_TOP, ORANGE)
m.decal_xz([(X0 + 1.4, 6.6), (X0 + 9.0, 6.6), (X0 + 9.0, 5.0), (X0 + 1.4, 5.0)], H_TOP, RED)
m.decal_xz([(X0 + 9.6, 6.6), (X0 + 11.0, 6.6), (X0 + 11.0, 5.0), (X0 + 9.6, 5.0)], H_TOP, ORANGE)

# ---------------------------------------------------------------- back
# long expansion-port door with its connector slit
m.box(-15.0, 1.0, ZB - 0.4, 15.0, 5.8, ZB + 0.01, DOOR, faces={'front': None, 'bottom': None})
m.polygon([(-13.0, 3.1, ZB - 0.43), (13.0, 3.1, ZB - 0.43), (13.0, 3.7, ZB - 0.43), (-13.0, 3.7, ZB - 0.43)],
          SLOT, normal=(0, 0, -1))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
