# SPDX-License-Identifier: GPL-3.0-or-later
"""Nintendo NES (North American front-loader), low-poly.

Real size about 25.6 x 8.5 x 20.3 cm (W x H x D). Signature features:
two-tone grey box (light upper shell, darker lower shell), the black band
across the top front, the dark ridged cartridge flap on the upper front,
power / reset buttons with the red LED on the front left, the two
controller ports low on the front left, ribbed vents on the top rear.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

LIGHT = (198, 198, 192)     # upper shell
DARK = (112, 112, 120)      # lower shell
FLAP = (86, 86, 94)         # cartridge flap
GROOVE = (52, 52, 58)       # flap ridges
BLACK = (22, 22, 24)        # top band, button well, ports
BUTTON = (140, 140, 148)    # power / reset
RED = (230, 30, 24)         # power LED
RIB = (170, 170, 166)       # top rear vent ribs

HX, HZ = 12.8, 10.15        # half width, half depth
H, SPLIT = 8.5, 4.0         # total height, lower / upper shell seam
B = 0.35                    # bevel on the upper shell's top edges

m = Model('nes', 'console')

# lower shell: dark grey box
m.box(-HX, 0, -HZ, HX, SPLIT, HZ, DARK)

# upper shell: light grey, top front / back edges bevelled (side profile).
# The black band across the top front is part of the top surface itself
# (its own strip of the profile), not a decal, so it never z-fights.
BAND0, BAND1 = 5.6, HZ - B - 0.25
prof = [(-HZ, SPLIT), (HZ, SPLIT), (HZ, H - B), (HZ - B, H), (BAND1, H), (BAND0, H),
        (-HZ + B, H), (-HZ, H - B)]
m.extrude_yz(prof, -HX, HX, LIGHT, side=False)
for i in range(1, len(prof)):            # edge 0 (the bottom) is hidden on the lower shell
    (za, ya), (zb, yb) = prof[i], prof[(i + 1) % len(prof)]
    # the profile runs clockwise seen from +X here, so the outward quad is
    # (x0, a) -> (x1, a) -> (x1, b) -> (x0, b)
    col = BLACK if (za, zb) == (BAND1, BAND0) else LIGHT
    m.quad((-HX, ya, za), (HX, ya, za), (HX, yb, zb), (-HX, yb, zb), col)

# ribbed vents across the top rear
for i in range(6):
    z0 = -8.6 + i * 1.15
    m.box(-10.5, H, z0, 10.5, H + 0.22, z0 + 0.6, RIB, faces={'bottom': None})

# cartridge flap on the upper front, with fine horizontal ridges
FX0, FX1, FY0, FY1, FZ = -3.4, 12.0, 4.45, 7.95, HZ + 0.2
m.box(FX0, FY0, HZ, FX1, FY1, FZ, FLAP, faces={'back': None})
for i in range(7):
    y = FY0 + 0.45 + i * 0.44
    m.decal_xy([(FX0 + 0.35, y), (FX1 - 0.35, y), (FX1 - 0.35, y + 0.16), (FX0 + 0.35, y + 0.16)],
               FZ, GROOVE, lift=0.03)

# power / reset buttons in a black well, red LED at the left
m.decal_xy([(-12.2, 5.15), (-4.3, 5.15), (-4.3, 7.25), (-12.2, 7.25)], HZ, BLACK, lift=0.03)
m.box(-9.9, 5.6, HZ, -7.7, 6.8, HZ + 0.35, BUTTON, faces={'back': None})
m.box(-6.9, 5.6, HZ, -4.7, 6.8, HZ + 0.35, BUTTON, faces={'back': None})
m.box(-11.7, 6.0, HZ, -10.9, 6.4, HZ + 0.2, RED, faces={'back': None})

# two controller ports, low on the front left (one corner chamfered)
for cx in (-9.4, -6.2):
    m.decal_xy([(cx - 1.0, 1.35), (cx + 1.0, 1.35), (cx + 1.0, 2.25), (cx + 0.6, 2.65),
                (cx - 1.0, 2.65)], HZ, BLACK, lift=0.03)

# rear connectors: RF / AV jacks and the power socket (dark patches)
for x0, x1, y0, y1 in ((4.0, 5.2, 1.4, 2.6), (6.0, 7.2, 1.4, 2.6), (8.2, 10.6, 1.2, 2.8),
                       (-10.6, -8.4, 1.2, 2.8)):
    m.polygon([(x0, y0, -HZ - 0.03), (x0, y1, -HZ - 0.03), (x1, y1, -HZ - 0.03),
               (x1, y0, -HZ - 0.03)], BLACK, normal=(0, 0, -1))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
