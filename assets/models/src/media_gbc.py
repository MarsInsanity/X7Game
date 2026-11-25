# SPDX-License-Identifier: GPL-3.0-or-later
"""Game Boy Color Game Pak: the black Game Boy Color-only cartridge, standing
upright, label (picture area) to +Z, contacts edge at y = 0.

Real size 5.7 x 6.5 x 0.78 cm. Shape after the photos: a plain rectangle
with a small square step cut out of the top-right corner (seen from the
front), a recessed label filling most of the lower front, a raised top band
with the moulded logo strip, grip ribs on both sides near the top, a slot
along the bottom edge with the circuit board's gold contacts, and on the
back two long grooves, a step over the contacts, a dimple and the screw.

It goes into the Game Boy Color's top slot contacts first (y = 0 down),
label facing the console's back."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (40, 40, 48)        # black shell, front and back
EDGE = (76, 76, 88)         # sides / top, so the edges read
SCOOP = (58, 58, 70)        # shallow logo scoop on the top band
EMBOSS = (108, 108, 122)    # moulded logo strip, grip ribs
LABEL = (226, 222, 206)     # plain label colour (fallback for the picture)
SLOT = (14, 14, 18)         # inside the contacts slot, back grooves
PCB = (24, 96, 48)
GOLD = (216, 176, 64)
SCREW = (150, 150, 158)

W, H, D = 5.7, 6.5, 0.78
hw = W / 2
NX, NY = 0.52, 0.27                 # top-right step: width, depth
ZB, ZF = -D / 2, D / 2              # back, front (frame) faces
ZL = ZF - 0.06                      # recessed label floor
ZS = ZF - 0.11                      # floor of the logo scoop above the label
LX, LY0, LY1 = 2.35, 0.8, 4.75      # label recess: half width, bottom, top
TY = 6.15                           # top of the scoop (bottom of the top lip)
SD = LY0                            # slot height (bottom lip = label bottom)
SX = 2.6                            # slot half width (nearly the whole width)
ZS0, ZS1 = -0.29, 0.16              # slot: thin back wall, circuit board face
BAND = 1.2                          # back step over the contacts
ZBB = ZB + 0.04                     # back face of that step

m = Model('gbc', 'media')


def face(pts, z, color, nz=1):
    return m.polygon([(x, y, z) for x, y in pts], color, normal=(0, 0, nz))


# ---------------------------------------------------------------- body
# outline from the slot top (y = SD) up, with the top-right step; its front
# (at the scoop floor ZS) is covered by the front frame pieces below
outline = [(-hw, SD), (hw, SD), (hw, H - NY), (hw - NX, H - NY), (hw - NX, H), (-hw, H)]
m.extrude_xy(outline, ZBB, ZS, SHELL, front=False, back=False, side=EDGE)
# the back is stepped: full thickness above BAND, thinner over the contacts
up = [(-hw, BAND), (hw, BAND), (hw, H - NY), (hw - NX, H - NY), (hw - NX, H), (-hw, H)]
m.extrude_xy(up, ZB, ZBB, SHELL, front=False, side=EDGE)

# ---------------------------------------------------------------- bottom part with the contacts slot
# front lip (y 0..SD), from the board face to the front frame
m.box(-hw, 0, ZS1, hw, SD, ZF, SHELL, faces={'back': None, 'top': EDGE, 'bottom': EDGE, 'left': EDGE, 'right': EDGE})
# back wall (y 0..SD) at the stepped back
m.box(-hw, 0, ZBB, hw, SD, ZS0, SHELL, faces={'front': None, 'top': None, 'bottom': EDGE, 'left': EDGE, 'right': EDGE})
# the slot's ends
for x0, x1 in ((-hw, -SX), (SX, hw)):
    m.box(x0, 0, ZS0, x1, SD, ZS1, EDGE, faces={'front': None, 'back': None, 'top': None})
# inside the slot: back wall, ceiling, the board with its contacts
face([(-SX, 0), (SX, 0), (SX, SD), (-SX, SD)], ZS0, SLOT, 1)
m.polygon([(-SX, SD - 0.01, ZS0), (SX, SD - 0.01, ZS0), (SX, SD - 0.01, ZS1), (-SX, SD - 0.01, ZS1)], SLOT, normal=(0, -1, 0))
face([(-SX, 0), (SX, 0), (SX, SD), (-SX, SD)], ZS1, PCB, -1)
n = 8
pitch = 2 * SX / n
for i in range(n):
    x0 = -SX + i * pitch + 0.06
    face([(x0, 0.0), (x0 + pitch - 0.12, 0.0), (x0 + pitch - 0.12, SD - 0.25), (x0, SD - 0.25)], ZS1 - 0.02, GOLD, -1)

# ---------------------------------------------------------------- front
# side bars from the bottom lip up to the top lip, and the top lip (with the step)
for x0, x1 in ((-hw, -LX), (LX, hw)):
    m.box(x0, LY0, ZS, x1, TY, ZF, SHELL, faces={'back': None, 'bottom': None, 'top': None, 'left': EDGE, 'right': EDGE})
lip = [(-hw, TY), (hw, TY), (hw, H - NY), (hw - NX, H - NY), (hw - NX, H), (-hw, H)]
m.extrude_xy(lip, ZS, ZF, SHELL, back=False, side=EDGE)
# the label: a raised floor in the recess, the picture on it
m.box(-LX, LY0, ZS, LX, LY1, ZL, LABEL, faces={'back': None, 'bottom': None, 'left': None, 'right': None, 'top': EDGE})
m.image_xy(-LX, LY0, LX, LY1, ZL, fallback=LABEL, lift=0.03)
# the deeper scoop above the label, with the moulded logo strip (plain, no
# lettering) and the line under it
face([(-LX, LY1), (LX, LY1), (LX, TY), (-LX, TY)], ZS, SCOOP)
m.box(-2.05, 5.5, ZS, 1.9, 5.95, ZS + 0.06, EMBOSS, faces={'back': None})
m.box(-0.9, 5.08, ZS, 1.9, 5.17, ZS + 0.04, EMBOSS, faces={'back': None})

# ---------------------------------------------------------------- sides: grip ribs near the top
for i in range(3):
    y = 5.05 + i * 0.32
    m.box(-hw - 0.04, y, ZB + 0.1, -hw, y + 0.12, ZF - 0.1, EMBOSS, faces={'right': None})
    m.box(hw, y, ZB + 0.1, hw + 0.04, y + 0.12, ZF - 0.1, EMBOSS, faces={'left': None})

# ---------------------------------------------------------------- back
# the stepped lower part (SD..BAND)
face([(-hw, SD), (hw, SD), (hw, BAND), (-hw, BAND)], ZBB, SHELL, -1)
# two long grooves from the top down to the step
for gx in (-1.56, 1.47):
    face([(gx - 0.15, BAND + 0.05), (gx - 0.15, H - 0.02), (gx + 0.15, H - 0.02), (gx + 0.15, BAND + 0.05)], ZB - 0.02, SLOT, -1)
# dimple and screw
oct8 = lambda cx, cy, r: [(cx + r * c, cy + r * s) for c, s in
                          ((1, 0), (.707, .707), (0, 1), (-.707, .707), (-1, 0), (-.707, -.707), (0, -1), (.707, -.707))]
face(oct8(0.0, 3.3, 0.2), ZB - 0.02, SLOT, -1)
face(oct8(0.0, 1.78, 0.17), ZB - 0.02, SCREW, -1)

print(m.stats())
print(m.save())
