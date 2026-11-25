# SPDX-License-Identifier: GPL-3.0-or-later
"""Sony PlayStation (original grey model), low-poly.

Real size about 27.0 x 6.0 x 18.8 cm (W x H x D). Signature features:
the light grey wide, flat body; the big round CD lid on the top left (a
raised disc with a darker ring around it and a small hub); the large round
open button and the smaller power / reset buttons with the green LED on the
top right; the raised, grooved rear section of the top; the recessed lower
front with the two controller ports and the two memory card slots above
them in the overhanging upper front.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (192, 192, 198)      # light grey shell
LID = (214, 214, 220)       # disc lid (a touch lighter)
RING = (132, 134, 146)      # ring around the lid, hub
RECESS = (150, 150, 158)    # recessed lower front panel
BUTTON = (104, 106, 118)    # open / power / reset
GROOVE = (78, 78, 88)       # rear grooves, seams
BLACK = (24, 24, 28)        # ports, slots, rear connectors
GREEN = (40, 220, 60)       # power LED

HX, HZ = 13.5, 9.4          # half width, half depth
H = 5.2                     # height of the top surface (lid area)
HR = 5.9                    # height of the raised, grooved rear section
ZR = -5.0                   # where the raised rear section starts
FR = 8.6                    # lower front recess depth (z of the recessed panel)
YS = 2.7                    # top of the recessed lower front

m = Model('psx', 'console')

# body: one side profile (z, y), extruded across the width. Listed
# clockwise seen from +X (bottom, front, top, back).
prof = [(-HZ, 0.0), (FR, 0.0), (FR, YS), (HZ, YS + 0.35), (HZ, H - 0.6),
        (HZ - 0.6, H), (ZR, H), (ZR - 0.5, HR), (-HZ + 0.5, HR), (-HZ, HR - 0.5)]
m.extrude_yz(prof, -HX, HX, BODY, side=False)
for i in range(len(prof)):
    (za, ya), (zb, yb) = prof[i], prof[(i + 1) % len(prof)]
    col = BODY
    if (za, zb) == (FR, FR):
        col = RECESS
    elif (za, ya, zb) == (FR, YS, HZ):
        col = RECESS
    elif ya == 0.0 and yb == 0.0:
        col = GROOVE        # bottom (never seen from normal angles)
    m.quad((-HX, ya, za), (HX, ya, za), (HX, yb, zb), (-HX, yb, zb), col)

# raised rear section: grooves across the top and down its front step
for i in range(4):
    z = -HZ + 1.0 + i * 0.9
    m.decal_xz([(-HX + 0.8, z), (HX - 0.8, z), (HX - 0.8, z + 0.42), (-HX + 0.8, z + 0.42)],
               HR, GROOVE, lift=0.03)

# CD lid: a dark ring, the raised light disc on it, and the hub
LX, LZ = -4.9, 1.7
m.cylinder(LX, LZ, 6.4, H, H + 0.15, RING, segments=20, bottom=False)
m.cylinder(LX, LZ, 5.9, H + 0.15, H + 0.45, LID, segments=20, bottom=False, side=RING)
m.decal_xz([(LX + 1.1 * math.cos(a * math.pi / 4), LZ + 1.1 * math.sin(a * math.pi / 4))
            for a in range(8)], H + 0.45, RING, lift=0.03)

# top right: the big open button, power and reset buttons, green LED
m.cylinder(7.6, -0.8, 1.55, H, H + 0.35, BUTTON, segments=12, bottom=False)
m.cylinder(5.4, 5.2, 0.85, H, H + 0.3, BUTTON, segments=10, bottom=False)     # reset
m.cylinder(10.0, 5.2, 0.85, H, H + 0.3, BUTTON, segments=10, bottom=False)    # power
m.box(7.35, H, 4.95, 7.95, H + 0.12, 5.45, GREEN, faces={'bottom': None})     # LED
# a groove separating the button area from the lid
m.decal_xz([(3.0, ZR + 0.4), (3.25, ZR + 0.4), (3.25, HZ - 1.0), (3.0, HZ - 1.0)], H, GROOVE)

# front: two controller ports on the recessed panel, two memory card slots
# above them on the overhanging upper front
for cx in (-4.6, 4.6):
    m.decal_xy([(cx - 2.0, 0.6), (cx + 2.0, 0.6), (cx + 2.0, 1.6), (cx + 1.5, 2.1),
                (cx - 1.5, 2.1), (cx - 2.0, 1.6)], FR, BLACK, lift=0.03)
    m.decal_xy([(cx - 1.6, 3.55), (cx + 1.6, 3.55), (cx + 1.6, 4.0), (cx - 1.6, 4.0)],
               HZ, BLACK, lift=0.03)

# rear connectors (dark patches on the back)
for x0, x1, y0, y1 in ((-11.5, -9.5, 1.5, 3.0), (-7.0, -3.0, 1.6, 2.8), (2.0, 4.0, 1.6, 2.8),
                       (8.0, 11.0, 1.4, 3.2)):
    m.polygon([(x0, y0, -HZ - 0.03), (x0, y1, -HZ - 0.03), (x1, y1, -HZ - 0.03),
               (x1, y0, -HZ - 0.03)], BLACK, normal=(0, 0, -1))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
