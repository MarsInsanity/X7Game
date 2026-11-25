# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega Genesis / Mega Drive cartridge (US Genesis shell): black, standing
upright, label (the game's picture) to +Z.

Real size 10.8 x 13.5 x 2.0 cm (11.0 cm across the side grips). Signature
features, from photos: the black shell with a rounded top edge, the big
label covering almost the whole front (8.9 x 10.8 cm) in a shallow recess,
the horizontally ribbed grips on the upper half of both sides, the small
lock notches low on the sides (the Genesis 1 power switch latches into
one), the paper sticker on the back and the opening in the bottom edge with
the circuit board's gold contacts.

Insertion: the cartridge goes straight down into the top slot. Everything
below y = 7.2 is a plain closed box 10.8 x 2.0 cm (the notches and the
contact opening are flush tiles / a recess, nothing sticks out), so the
console's slot can be built tight around it.
"""
import math
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (40, 40, 46)          # black plastic
EDGE = (66, 66, 74)           # rounded top edge, catches the light
RIDGE = (98, 98, 110)         # side grip ribs
RECESS = (24, 24, 28)         # label recess walls
NOTCH = (12, 12, 14)          # lock notches
SLOT = (16, 16, 18)           # contact opening in the bottom
PCB = (40, 110, 60)           # circuit board edge
GOLD = (214, 172, 64)         # contacts
STICK = (200, 196, 182)       # back sticker
LABEL = (226, 224, 214)       # label paper (picture fallback)

W, H, D = 10.8, 13.5, 2.0
hw = W / 2
ZF, ZB = D / 2, -D / 2
R = 0.45                       # radius of the rounded top edges (front and back)
SEG = 2                        # segments per rounded edge

m = Model('megadrive', 'media')


def face(pts, z, color, nz):
    """flat face at depth z facing +Z (nz = 1) or -Z (nz = -1); pts are (x, y)"""
    return m.polygon([(x, y, z) for x, y in pts], color, normal=(0, 0, nz))


def side(pts, x, color, nx):
    """flat face at x facing +X (nx = 1) or -X (nx = -1); pts are (z, y)"""
    return m.polygon([(x, y, z) for z, y in pts], color, normal=(nx, 0, 0))


# ---------------------------------------------------------------- top profile
# (z, y) points of the rounded top, from the front face over to the back face
top = []
for cz, a0 in ((ZF - R, 0), (ZB + R, 90)):
    for s in range(SEG + 1):
        a = math.radians(a0 + 90 * s / SEG)
        top.append((cz + R * math.cos(a), H - R + R * math.sin(a)))
YT = H - R                     # front / back faces end here
for (za, ya), (zb, yb) in zip(top, top[1:]):
    mz, my = (za + zb) / 2, (ya + yb) / 2 - (H - R)
    m.polygon([(hw, ya, za), (hw, yb, zb), (-hw, yb, zb), (-hw, ya, za)],
              EDGE if abs(mz) > 0.3 else SHELL, normal=(0, my, mz))

# ---------------------------------------------------------------- front + label
lx, ly0, ly1 = 4.45, 1.1, 11.9           # label 8.9 x 10.8
ZL = ZF - 0.08                           # label recess floor
face([(-hw, 0), (hw, 0), (hw, ly0), (lx, ly0), (-lx, ly0), (-hw, ly0)], ZF, SHELL, 1)
face([(-hw, ly0), (-lx, ly0), (-lx, ly1), (-hw, ly1)], ZF, SHELL, 1)
face([(lx, ly0), (hw, ly0), (hw, ly1), (lx, ly1)], ZF, SHELL, 1)
face([(-hw, ly1), (-lx, ly1), (lx, ly1), (hw, ly1), (hw, YT), (-hw, YT)], ZF, SHELL, 1)
# recess walls (facing into the recess)
m.polygon([(-lx, ly0, ZL), (lx, ly0, ZL), (lx, ly0, ZF), (-lx, ly0, ZF)], EDGE, normal=(0, 1, 0))
m.polygon([(-lx, ly1, ZL), (lx, ly1, ZL), (lx, ly1, ZF), (-lx, ly1, ZF)], RECESS, normal=(0, -1, 0))
m.polygon([(-lx, ly0, ZL), (-lx, ly1, ZL), (-lx, ly1, ZF), (-lx, ly0, ZF)], RECESS, normal=(1, 0, 0))
m.polygon([(lx, ly0, ZL), (lx, ly1, ZL), (lx, ly1, ZF), (lx, ly0, ZF)], RECESS, normal=(-1, 0, 0))
# the label itself: the game's picture, lifted off the recess floor
m.image_xy(-lx, ly0, lx, ly1, ZL, fallback=LABEL, lift=0.03)

# ---------------------------------------------------------------- back + sticker
bx, by0, by1 = 3.9, 3.0, 10.6
face([(-hw, 0), (hw, 0), (hw, by0), (bx, by0), (-bx, by0), (-hw, by0)], ZB, SHELL, -1)
face([(-hw, by0), (-bx, by0), (-bx, by1), (-hw, by1)], ZB, SHELL, -1)
face([(bx, by0), (hw, by0), (hw, by1), (bx, by1)], ZB, SHELL, -1)
face([(-hw, by1), (-bx, by1), (bx, by1), (hw, by1), (hw, YT), (-hw, YT)], ZB, SHELL, -1)
face([(-bx, by0), (bx, by0), (bx, by1), (-bx, by1)], ZB, STICK, -1)

# ---------------------------------------------------------------- bottom with the contact opening
sx_, sz_, SD = 4.3, 0.36, 0.7            # opening half width, half depth, depth
m.polygon([(-hw, 0, ZB), (hw, 0, ZB), (hw, 0, -sz_), (sx_, 0, -sz_), (-sx_, 0, -sz_), (-hw, 0, -sz_)], SHELL, normal=(0, -1, 0))
m.polygon([(-hw, 0, sz_), (-sx_, 0, sz_), (sx_, 0, sz_), (hw, 0, sz_), (hw, 0, ZF), (-hw, 0, ZF)], SHELL, normal=(0, -1, 0))
m.polygon([(-hw, 0, -sz_), (-sx_, 0, -sz_), (-sx_, 0, sz_), (-hw, 0, sz_)], SHELL, normal=(0, -1, 0))
m.polygon([(sx_, 0, -sz_), (hw, 0, -sz_), (hw, 0, sz_), (sx_, 0, sz_)], SHELL, normal=(0, -1, 0))
# opening walls (facing inward) and floor: the board edge with its contacts
m.polygon([(-sx_, 0, -sz_), (sx_, 0, -sz_), (sx_, SD, -sz_), (-sx_, SD, -sz_)], SLOT, normal=(0, 0, 1))
m.polygon([(-sx_, 0, sz_), (sx_, 0, sz_), (sx_, SD, sz_), (-sx_, SD, sz_)], SLOT, normal=(0, 0, -1))
m.polygon([(-sx_, 0, -sz_), (-sx_, 0, sz_), (-sx_, SD, sz_), (-sx_, SD, -sz_)], SLOT, normal=(1, 0, 0))
m.polygon([(sx_, 0, -sz_), (sx_, 0, sz_), (sx_, SD, sz_), (sx_, SD, -sz_)], SLOT, normal=(-1, 0, 0))
pz = 0.1                                 # half thickness of the board edge
m.polygon([(-sx_, SD, -sz_), (sx_, SD, -sz_), (sx_, SD, -pz), (-sx_, SD, -pz)], SLOT, normal=(0, -1, 0))
m.polygon([(-sx_, SD, -pz), (sx_, SD, -pz), (sx_, SD, pz), (-sx_, SD, pz)], GOLD, normal=(0, -1, 0))
m.polygon([(-sx_, SD, pz), (sx_, SD, pz), (sx_, SD, sz_), (-sx_, SD, sz_)], SLOT, normal=(0, -1, 0))

# ---------------------------------------------------------------- sides: lock notch, grip ribs
nz0, nz1, ny0, ny1 = 0.2, 0.75, 0.7, 1.6  # lock notch (flush tile)
outline = [(ZB, ny1), (nz0, ny1), (nz1, ny1), (ZF, ny1), (ZF, YT)] + top[1:-1] + [(ZB, YT)]
for sx in (1, -1):
    x = sx * hw
    side([(ZB, 0), (ZF, 0), (ZF, ny0), (nz1, ny0), (nz0, ny0), (ZB, ny0)], x, SHELL, sx)
    side([(ZB, ny0), (nz0, ny0), (nz0, ny1), (ZB, ny1)], x, SHELL, sx)
    side([(nz1, ny0), (ZF, ny0), (ZF, ny1), (nz1, ny1)], x, SHELL, sx)
    side([(nz0, ny0), (nz1, ny0), (nz1, ny1), (nz0, ny1)], x, NOTCH, sx)
    side(outline, x, SHELL, sx)

RZ, RT = 0.9, 0.1                         # ribs span z -RZ..RZ, stand RT proud
RN, RY0, RP, RH = 7, 7.0, 0.82, 0.42      # count, first bottom, pitch, height
for i in range(RN):
    ya = RY0 + i * RP
    yb = ya + RH
    m.box(hw, ya, -RZ, hw + RT, yb, RZ, RIDGE, faces={'left': None})
    m.box(-hw - RT, ya, -RZ, -hw, yb, RZ, RIDGE, faces={'right': None})

print(m.stats())
print(m.save())
