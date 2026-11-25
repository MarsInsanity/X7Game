# SPDX-License-Identifier: GPL-3.0-or-later
"""Neo Geo Pocket Color cartridge, standing upright, picture label to +Z,
connector edge at y = 0.

Real size about 4.8 x 4.5 x 0.8 cm. Signature features: the dark charcoal
card with a slightly wider and thicker grip lip across the top (it
overhangs the front, its top front edge is rounded off, horizontal grooves
across its face), the wide landscape label in the middle of the front, and
below it a band with two recessed plates left and right and a
down-pointing insert arrow between them. The connector contacts sit at
the bottom of the back.

Insertion: the slab below the lip (x -2.4..2.4, y 0..3.6, z -0.4..0.4) is
a plain closed box that goes into the slot on the top back of the console,
connector edge first; the lip (x -2.48..2.48, y 3.6..4.5, z -0.4..0.55)
stays outside as the grip. The back is flat from bottom to top.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

SHELL = (82, 84, 92)        # charcoal grey shell
LIP = (100, 102, 110)       # grip lip, a touch lighter so it reads as its own part
GROOVE = (34, 36, 42)       # grooves across the lip
PLATE = (64, 66, 76)        # recessed plates in the bottom band
ARROW = (40, 42, 50)        # insert arrow
LABEL = (236, 234, 228)     # plain label colour (picture fallback)
SLOT = (22, 22, 28)         # connector opening (bottom, back)
GOLD = (216, 176, 64)       # contacts

W, H = 4.8, 4.5             # body width, overall height
hw = W / 2
ZB, ZF = -0.4, 0.4          # back, front of the body (0.8 cm thick)
LY = 3.6                    # grip lip from here up
LO = 0.08                   # lip overhang left and right
ZL = ZF + 0.15              # lip front (overhangs the front by 1.5 mm)
LX0, LX1, LB0, LB1 = -2.05, 2.05, 1.45, 3.35   # the label (4.1 x 1.9 cm)

m = Model('ngpc', 'media')

# body slab: the part that goes into the slot (top hidden under the lip,
# dark bottom face = the connector opening seen from below)
m.box(-hw, 0, ZB, hw, LY, ZF, SHELL, faces={'top': None, 'bottom': SLOT})

# grip lip: side profile (z, y) with the rounded-off top front edge
lip = [(ZB, LY), (ZL, LY), (ZL, 4.24), (ZL - 0.06, 4.4), (ZL - 0.18, 4.475), (ZL - 0.34, H), (ZB, H)]
m.extrude_yz(lip, -hw - LO, hw + LO, LIP)

# grooves across the lip face
for i in range(4):
    y = 3.7 + i * 0.14
    m.decal_xy([(-2.0, y), (2.0, y), (2.0, y + 0.075), (-2.0, y + 0.075)], ZL, GROOVE, lift=0.02)

# the label: one picture area, upright (u left to right, v bottom to top)
m.image_xy(LX0, LB0, LX1, LB1, ZF, fallback=LABEL, lift=0.03)

# bottom band: two recessed plates and the down-pointing insert arrow
m.decal_xy(Model.rounded_rect(-2.15, 0.55, -0.85, 1.22, 0.1, segments=1), ZF, PLATE, lift=0.02)
m.decal_xy(Model.rounded_rect(0.4, 0.55, 2.05, 1.22, 0.1, segments=1), ZF, PLATE, lift=0.02)
m.decal_xy([(-0.66, 1.18), (0.2, 1.18), (-0.23, 0.6)], ZF, ARROW, lift=0.02)

# parting line of the two shell halves just above the bottom edge
m.decal_xy([(-hw, 0.2), (hw, 0.2), (hw, 0.24), (-hw, 0.24)], ZF, PLATE, lift=0.02)

# back: connector opening along the bottom edge with gold contacts
def back_rect(x0, y0, x1, y1, z, col):
    m.polygon([(x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z)], col, normal=(0, 0, -1))


back_rect(-1.9, 0.0, 1.9, 0.5, ZB - 0.02, SLOT)
n = 8
for i in range(n):
    x0 = -1.75 + i * 3.5 / n + 0.06
    back_rect(x0, 0.06, x0 + 3.5 / n - 0.12, 0.42, ZB - 0.04, GOLD)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
