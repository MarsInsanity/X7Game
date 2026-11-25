# SPDX-License-Identifier: GPL-3.0-or-later
"""Game Boy (DMG) Game Pak, standing upright, label (picture) to +Z.

Real size 5.7 x 6.5 x 0.8 cm. Matched to Commons photos of the grey DMG
cartridge: a small rectangular step cut out of the top-right corner (seen
from the front), a recessed stadium-shaped logo plate across the top with
five horizontal grip grooves on each side of it (they wrap round the side
edges), the large label recess below (the game's picture), a down-pointing
triangle under the label, and on the back two vertical ribs, a round boss,
the screw and the stepped band over the connector. The connector slot with
its contacts is in the bottom edge.

Insertion (Game Boy): the cartridge goes DOWN into the slot at the top of
the console's back, label facing the back (-Z in console space).

Envelope: everything lies inside x -2.85..2.85, y 0..6.5, z -0.4..0.4. The
solid shell is x -2.83..2.83, y 0.02..6.5, z -0.38..0.36; surface details
(drawn as lifted decals) fill the last 0.02-0.04 cm.
"""
import math
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (178, 174, 182)      # light warm grey shell
GROOVE = (112, 108, 120)     # grip grooves
PLATE = (160, 156, 168)      # recessed logo plate (stadium)
PLATE_RIM = (204, 201, 208)  # its lit bevel
RECESS = (124, 120, 132)     # label recess edge, insert arrow
RIB = (150, 146, 158)        # back ribs, connector band
DARK = (40, 40, 46)          # connector slot, screw head
BOSS = (100, 96, 108)        # round boss on the back
GOLD = (214, 172, 72)        # contacts
LABEL = (226, 226, 220)      # plain label paper (picture fallback)

XS = 2.83                    # shell half width (decals on the sides reach 2.85)
H = 6.5
Y0 = 0.02                    # shell bottom (the connector slot decal sits at y = 0)
ZB, ZF = -0.38, 0.36         # shell back / front
L1, L2 = ZF + 0.02, ZF + 0.04          # front decal levels
NX, NY = 2.35, H - 0.28                # notch: x from NX to the right edge, y from NY up

m = Model('gb', 'media')

# ---------------------------------------------------------------- shell
outline = [(-XS, Y0), (XS, Y0), (XS, NY), (NX, NY), (NX, H), (-XS, H)]
m.extrude_xy(outline, ZB, ZF, SHELL)

# ---------------------------------------------------------------- front
# label recess (darker edge) and the picture inside it
RX, RY0, RY1 = 2.17, 0.85, 4.78
m.decal_xy([(-RX, RY0), (RX, RY0), (RX, RY1), (-RX, RY1)], ZF, RECESS, lift=0.02)
IX, IY0, IY1 = 2.09, 0.93, 4.70
m.image_xy(-IX, IY0, IX, IY1, ZF, fallback=LABEL, lift=0.04)

# logo plate: a stadium with a lit bevel around it
SX, SY0, SY1 = 2.05, 5.07, 6.18


def stadium(x, y0, y1, seg=4):
    r = (y1 - y0) / 2
    cy = (y0 + y1) / 2
    pts = []
    for i in range(seg + 1):                      # right end, bottom -> top
        a = math.radians(-90 + 180 * i / seg)
        pts.append((x - r + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(seg + 1):                      # left end, top -> bottom
        a = math.radians(90 + 180 * i / seg)
        pts.append((-x + r + r * math.cos(a), cy + r * math.sin(a)))
    return pts


m.decal_xy(stadium(SX + 0.07, SY0 - 0.07, SY1 + 0.07), ZF, PLATE_RIM, lift=0.02)
m.decal_xy(stadium(SX, SY0, SY1), ZF, PLATE, lift=0.04)

# grip grooves either side of the plate, wrapping round the side edges
GY = [6.00, 5.81, 5.62, 5.43, 5.24]
GH = 0.08
for y in GY:
    for s in (-1, 1):
        xo, xi = s * XS, s * 2.22
        m.decal_xy([(min(xo, xi), y), (max(xo, xi), y), (max(xo, xi), y + GH), (min(xo, xi), y + GH)], ZF, GROOVE, lift=0.02)
        xs = s * (XS + 0.02)
        m.polygon([(xs, y, ZB), (xs, y, ZF), (xs, y + GH, ZF), (xs, y + GH, ZB)], GROOVE, normal=(s, 0, 0))

# the stepped lip along the bottom edge, over the connector
m.decal_xy([(-XS, Y0), (XS, Y0), (XS, 0.14), (-XS, 0.14)], ZF, RECESS, lift=0.02)

# insert arrow under the label, pointing down to the connector
m.decal_xy([(-0.42, 0.77), (0.42, 0.77), (0.0, 0.33)], ZF, RECESS, lift=0.02)

# ---------------------------------------------------------------- back
def back(pts, col, lift=0.02):
    m.polygon([(x, y, ZB - lift) for x, y in pts], col, normal=(0, 0, -1))


back([(-XS, Y0), (XS, Y0), (XS, 1.25), (-XS, 1.25)], RIB)              # band over the connector
for cx in (-1.5, 1.5):                                                    # vertical ribs
    back([(cx - 0.15, 1.25), (cx + 0.15, 1.25), (cx + 0.15, H - 0.06), (cx - 0.15, H - 0.06)], RIB)
hexa = lambda cx, cy, r: [(cx + r * math.cos(math.radians(60 * i)), cy + r * math.sin(math.radians(60 * i))) for i in range(6)]
back(hexa(0, 3.3, 0.2), BOSS)                                             # round boss
back(hexa(0, 1.75, 0.24), DARK)                                           # screw

# ---------------------------------------------------------------- bottom edge: connector slot with contacts
m.polygon([(-2.55, 0.01, -0.3), (2.55, 0.01, -0.3), (2.55, 0.01, 0.2), (-2.55, 0.01, 0.2)], DARK, normal=(0, -1, 0))
m.polygon([(-2.4, 0.0, -0.26), (2.4, 0.0, -0.26), (2.4, 0.0, -0.06), (-2.4, 0.0, -0.06)], GOLD, normal=(0, -1, 0))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
