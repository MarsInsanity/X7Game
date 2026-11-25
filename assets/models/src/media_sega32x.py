# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega 32X cartridge, low-poly.

Standing upright like on a shelf: label facing +Z, connector edge at y = 0.
10.9 cm wide (the Genesis slot width), 16.0 cm tall, 2.0 cm thick: the
Genesis cartridge's shell, stretched taller. Signature features: the
all-black shell, the top edge rolled over in a half round from front to
back, the big recessed front label high on the face (the game's picture),
the horizontal grip ridges on both sides near the top, the plain sticker
recess on the back and the dark open bottom with the board's contact edge.

Insertion: the cartridge goes straight DOWN into the 32X's top slot, label
to the front. Everything below y = 5.0 is a plain closed box 10.9 x 2.0
(nothing sticks out), so the slot can be built tight around it.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (38, 38, 42)          # black plastic
ROLL = (72, 72, 80)           # rolled top (catches the light)
RIDGE = (96, 96, 104)         # side grip ridges
RECESS = (14, 14, 16)         # label recess walls / floor, bottom opening
PCB = (40, 112, 56)           # board edge in the bottom opening
GOLD = (208, 172, 72)         # contact fingers
STICK = (200, 196, 182)       # back sticker
PANEL = (58, 58, 66)          # recessed trapezoid panel on the lower front
LABEL = (200, 40, 44)         # picture fallback (red 32X label band)

W, H, D = 10.9, 16.0, 2.0
hw = W / 2
ZF, ZB = D / 2, -D / 2
R = D / 2                     # radius of the rolled top
YT = H - R                    # where the roll starts
ARC = 4                       # segments of the roll

# label recess on the front, and the picture inside it
LX, LY0, LY1 = 4.75, 5.6, 14.3      # recess (half width, bottom, top)
DEP = 0.12                          # recess depth
PX, PY0, PY1 = 4.6, 5.75, 14.15     # picture (a thin dark margin shows)

TY0, TY1, TB, TT = 0.9, 4.9, 2.9, 3.7   # lower front trapezoid panel (bottom, top, half widths)
OX, OZ, OY = 4.7, 0.55, 0.8           # bottom opening (half width, half depth, cavity height)
BX = 4.3                              # board half width

m = Model('sega32x', 'media')


def face(pts, z, color, nz):
    """flat face at depth z facing +Z (nz = 1) or -Z (nz = -1); pts are (x, y)"""
    return m.polygon([(x, y, z) for x, y in pts], color, normal=(0, 0, nz))


# ---------------------------------------------------------------- rolled top
arc = [(R * math.cos(math.pi * i / ARC), YT + R * math.sin(math.pi * i / ARC)) for i in range(ARC + 1)]
for (za, ya), (zb, yb) in zip(arc, arc[1:]):
    mz, my = (za + zb) / 2, (ya + yb) / 2 - YT
    m.polygon([(hw, ya, za), (hw, yb, zb), (-hw, yb, zb), (-hw, ya, za)], ROLL, normal=(0, my, mz))

# ---------------------------------------------------------------- sides
for sx in (1, -1):
    prof = [(ZF, 0.0)] + arc + [(ZB, 0.0)]
    m.polygon([(sx * hw, y, z) for z, y in prof], SHELL, normal=(sx, 0, 0))

# ---------------------------------------------------------------- front, tiled round the label recess
# lower front with the recessed trapezoid panel (the Genesis-family shell)
face([(-hw, 0), (hw, 0), (hw, TY0), (-hw, TY0)], ZF, SHELL, 1)
face([(-hw, TY1), (hw, TY1), (hw, LY0), (-hw, LY0)], ZF, SHELL, 1)
face([(-hw, TY0), (-TB, TY0), (-TT, TY1), (-hw, TY1)], ZF, SHELL, 1)
face([(TB, TY0), (hw, TY0), (hw, TY1), (TT, TY1)], ZF, SHELL, 1)
ZT = ZF - 0.1
face([(-TB, TY0), (TB, TY0), (TT, TY1), (-TT, TY1)], ZT, PANEL, 1)
m.polygon([(-TB, TY0, ZT), (TB, TY0, ZT), (TB, TY0, ZF), (-TB, TY0, ZF)], RECESS, normal=(0, 1, 0))
m.polygon([(-TT, TY1, ZT), (TT, TY1, ZT), (TT, TY1, ZF), (-TT, TY1, ZF)], RECESS, normal=(0, -1, 0))
m.polygon([(-TB, TY0, ZT), (-TT, TY1, ZT), (-TT, TY1, ZF), (-TB, TY0, ZF)], RECESS, normal=(TY1 - TY0, TT - TB, 0))
m.polygon([(TB, TY0, ZT), (TT, TY1, ZT), (TT, TY1, ZF), (TB, TY0, ZF)], RECESS, normal=(-(TY1 - TY0), TT - TB, 0))
face([(-hw, LY1), (hw, LY1), (hw, YT), (-hw, YT)], ZF, SHELL, 1)
face([(-hw, LY0), (-LX, LY0), (-LX, LY1), (-hw, LY1)], ZF, SHELL, 1)
face([(LX, LY0), (hw, LY0), (hw, LY1), (LX, LY1)], ZF, SHELL, 1)
ZL = ZF - DEP
# recess walls (facing into the recess) and floor
m.polygon([(-LX, LY0, ZL), (LX, LY0, ZL), (LX, LY0, ZF), (-LX, LY0, ZF)], RECESS, normal=(0, 1, 0))
m.polygon([(-LX, LY1, ZL), (LX, LY1, ZL), (LX, LY1, ZF), (-LX, LY1, ZF)], RECESS, normal=(0, -1, 0))
m.polygon([(-LX, LY0, ZL), (-LX, LY1, ZL), (-LX, LY1, ZF), (-LX, LY0, ZF)], RECESS, normal=(1, 0, 0))
m.polygon([(LX, LY0, ZL), (LX, LY1, ZL), (LX, LY1, ZF), (LX, LY0, ZF)], RECESS, normal=(-1, 0, 0))
face([(-LX, LY0), (LX, LY0), (LX, LY1), (-LX, LY1)], ZL, RECESS, 1)
# the game's picture: u left -> right, v bottom -> top
m.image_xy(-PX, PY0, PX, PY1, ZL, fallback=LABEL, lift=0.03)

# ---------------------------------------------------------------- back with the sticker
face([(-hw, 0), (hw, 0), (hw, YT), (-hw, YT)], ZB, SHELL, -1)
m.polygon([(3.9, 6.0, ZB - 0.03), (-3.9, 6.0, ZB - 0.03), (-3.9, 13.4, ZB - 0.03), (3.9, 13.4, ZB - 0.03)],
          STICK, normal=(0, 0, -1))

# ---------------------------------------------------------------- bottom: open, board edge with contacts
# bottom face tiled round the opening, a shallow cavity, the board hanging in it
face_b = lambda pts: m.polygon([(x, 0.0, z) for x, z in pts], SHELL, normal=(0, -1, 0))
face_b([(-hw, ZB), (hw, ZB), (hw, -OZ), (-hw, -OZ)])
face_b([(-hw, OZ), (hw, OZ), (hw, ZF), (-hw, ZF)])
face_b([(-hw, -OZ), (-OX, -OZ), (-OX, OZ), (-hw, OZ)])
face_b([(OX, -OZ), (hw, -OZ), (hw, OZ), (OX, OZ)])
m.polygon([(-OX, 0, -OZ), (OX, 0, -OZ), (OX, OY, -OZ), (-OX, OY, -OZ)], RECESS, normal=(0, 0, 1))
m.polygon([(-OX, 0, OZ), (OX, 0, OZ), (OX, OY, OZ), (-OX, OY, OZ)], RECESS, normal=(0, 0, -1))
m.polygon([(-OX, 0, -OZ), (-OX, 0, OZ), (-OX, OY, OZ), (-OX, OY, -OZ)], RECESS, normal=(1, 0, 0))
m.polygon([(OX, 0, -OZ), (OX, 0, OZ), (OX, OY, OZ), (OX, OY, -OZ)], RECESS, normal=(-1, 0, 0))
m.polygon([(-OX, OY, -OZ), (OX, OY, -OZ), (OX, OY, OZ), (-OX, OY, OZ)], RECESS, normal=(0, -1, 0))
m.box(-BX, 0.25, -0.08, BX, OY, 0.08, PCB, faces={'top': None, 'bottom': GOLD})

# ---------------------------------------------------------------- side grip ridges
for sx in (1, -1):
    x0 = sx * hw
    x1 = sx * (hw + 0.1)
    for y in (12.0, 12.7, 13.4, 14.1):
        y0, y1 = y, y + 0.32
        z0, z1 = ZB + 0.3, ZF - 0.3
        # outer face, top, bottom, front and back ends (the inner side sits on the shell)
        m.polygon([(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)], RIDGE, normal=(sx, 0, 0))
        m.polygon([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], RIDGE, normal=(0, 1, 0))
        m.polygon([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], SHELL, normal=(0, -1, 0))
        m.polygon([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], SHELL, normal=(0, 0, 1))
        m.polygon([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], SHELL, normal=(0, 0, -1))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
