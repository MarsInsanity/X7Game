# SPDX-License-Identifier: GPL-3.0-or-later
"""NEC TurboGrafx-CD (interface unit + CD-ROM player), low poly.

A wide, low black interface unit (31 x 22 cm, 5.5 cm tall) with a chamfered
front edge, an orange accent stripe across the front, a dark console bay
opening at the front left and vent ribs on the left deck. On its right half
sits the square top-loading CD-ROM player: a charcoal box with a flip-up lid
(hinge bar at the back, seam around the edge), a round smoked disc window
showing a silver disc and hub, an orange open button and a red LED.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BASE = (40, 40, 48)         # interface unit shell
DECK = (58, 58, 66)         # chamfer / deck tone
RIB = (88, 88, 98)          # vent ribs
CDBODY = (72, 72, 82)       # CD player body
LID = (46, 46, 54)          # CD lid
WINDOW = (16, 16, 22)       # smoked disc window
DISC = (160, 166, 184)      # silver disc
HUB = (104, 106, 120)       # disc hub
SLOT = (10, 10, 12)         # openings
ORANGE = (240, 120, 24)     # TurboGrafx accent
LED = (230, 36, 30)

m = Model('pcenginecd', 'console')

# ---------------------------------------------------------------- interface unit
W = 15.5                    # half width
D = 11.0                    # half depth
H = 5.5                     # height
profile = [(-D, 0.0), (D, 0.0), (D, H - 1.2), (D - 1.2, H), (-D + 0.4, H), (-D, H - 0.4)]
m.extrude_yz(profile, -W, W, BASE)
# chamfered front edge repainted a lighter deck tone (lifted along its normal)
n = 0.03 / 2 ** 0.5        # lift along the chamfer normal, kept inside its edges


def ch(t):                  # point on the chamfer, t = 0 bottom edge .. 1 top edge
    return (H - 1.2 + 1.2 * t + n, D - 1.2 * t + n)


(ya, za), (yb, zb) = ch(0.04), ch(0.92)
m.polygon([(-W + 0.05, ya, za), (W - 0.05, ya, za), (W - 0.05, yb, zb), (-W + 0.05, yb, zb)], DECK)
# orange accent stripe across the front face
m.decal_xy([(-W + 0.3, 2.5), (W - 0.3, 2.5), (W - 0.3, 2.9), (-W + 0.3, 2.9)], D, ORANGE)
# console bay opening at the front left (where the console docks)
m.decal_xy([(-W + 0.9, 0.3), (-1.3, 0.3), (-1.3, 2.3), (-W + 0.9, 2.3)], D, DECK)
m.decal_xy([(-W + 1.2, 0.55), (-1.6, 0.55), (-1.6, 2.05), (-W + 1.2, 2.05)], D, SLOT, lift=0.05)
# power LED on the front right
m.decal_xy([(W - 2.0, 1.0), (W - 1.2, 1.0), (W - 1.2, 1.6), (W - 2.0, 1.6)], D, LED)

# vent ribs on the left deck, running front-back
for k in range(6):
    x0 = -W + 1.5 + k * 2.1
    m.box(x0, H, -D + 1.5, x0 + 0.9, H + 0.3, D - 2.6, RIB, faces={'bottom': None})

# ---------------------------------------------------------------- CD-ROM player
CX0, CX1 = 0.6, W - 0.6
CZ0, CZ1 = -D + 0.8, D - 2.0
CH = H + 3.0
m.box(CX0, H, CZ0, CX1, CH, CZ1, CDBODY, faces={'bottom': None})
# flip-up lid: a slightly raised slab inset from the edges
LX0, LX1, LZ0, LZ1 = CX0 + 0.35, CX1 - 0.35, CZ0 + 1.4, CZ1 - 0.35
LT = CH + 0.45
m.box(LX0, CH, LZ0, LX1, LT, LZ1, LID, faces={'bottom': None})
# hinge bar at the back of the lid
m.box(LX0 + 1.0, CH, CZ0 + 0.35, LX1 - 1.0, CH + 0.7, LZ0, SLOT, faces={'bottom': None})
# round disc window with the disc and its hub
ccx, ccz = (LX0 + LX1) / 2, (LZ0 + LZ1) / 2


def circle(cx, cz, r, n):
    return [(cx + r * math.cos(2 * math.pi * (i + 0.5) / n), cz + r * math.sin(2 * math.pi * (i + 0.5) / n))
            for i in range(n)]


m.decal_xz(circle(ccx, ccz, 5.4, 16), LT, WINDOW, lift=0.02)
m.decal_xz(circle(ccx, ccz, 4.6, 16), LT, DISC, lift=0.05)
m.decal_xz(circle(ccx, ccz, 1.5, 8), LT, HUB, lift=0.08)
m.decal_xz(circle(ccx, ccz, 0.6, 6), LT, WINDOW, lift=0.11)
# orange open button on the front of the player, red LED next to it
m.box(CX1 - 3.6, H + 1.0, CZ1, CX1 - 1.4, H + 1.9, CZ1 + 0.35, ORANGE, faces={'back': None})
m.decal_xy([(CX0 + 1.0, H + 1.3), (CX0 + 1.7, H + 1.3), (CX0 + 1.7, H + 1.8), (CX0 + 1.0, H + 1.8)], CZ1, LED)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
