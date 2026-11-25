# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega Genesis / Mega Drive cartridge: black shell standing upright, label to +Z.

Real size ~10.9 x 13.6 x 2.0 cm. Signature features: the black shell, the
top edge rolled over in a half round from front to back, the big recessed
label on the upper front, the small raised logo plate below it, the
horizontal grip ridges on both sides, and the paper sticker on the back.
The front, back and side faces are tiled around every label / plate / ridge
so nothing is drawn as an overlapping decal (the software renderer's depth
is not perspective correct).
"""
import math
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (42, 42, 48)         # black plastic
EDGE = (68, 68, 76)          # rolled top, recess walls (catches a bit of light)
RIDGE = (92, 92, 100)        # side grip ridges
PLATE = (74, 74, 82)         # raised logo plate
FRAME = (232, 230, 222)      # label paper frame
TITLE = (204, 40, 44)        # label title band
ART = (56, 116, 208)         # label picture (sky)
ART2 = (240, 164, 48)        # label picture accent
STICK = (196, 192, 176)      # back sticker

W, H, D = 10.9, 13.6, 2.0
hw = W / 2
ZF, ZB = D / 2, -D / 2
R = D / 2                     # radius of the rolled top
YT = H - R                    # where the roll starts
ARC = 4                       # segments of the roll

m = Model('megadrive', 'media')


def face(pts, z, color, nz):
    """flat face at depth z facing +Z (nz = 1) or -Z (nz = -1); pts are (x, y)"""
    return m.polygon([(x, y, z) for x, y in pts], color, normal=(0, 0, nz))


def side(pts, x, color, nx):
    """flat face at x facing +X (nx = 1) or -X (nx = -1); pts are (z, y)"""
    return m.polygon([(x, y, z) for z, y in pts], color, normal=(nx, 0, 0))


# ---------------------------------------------------------------- profile edges
arc = [(R * math.cos(math.pi * i / ARC), YT + R * math.sin(math.pi * i / ARC)) for i in range(ARC + 1)]
# rolled top: quads between successive arc points, facing outward
for (za, ya), (zb, yb) in zip(arc, arc[1:]):
    mz, my = (za + zb) / 2, (ya + yb) / 2 - YT
    m.polygon([(hw, ya, za), (hw, yb, zb), (-hw, yb, zb), (-hw, ya, za)], EDGE, normal=(0, my, mz))
# bottom
m.polygon([(-hw, 0, ZB), (hw, 0, ZB), (hw, 0, ZF), (-hw, 0, ZF)], SHELL, normal=(0, -1, 0))

# ---------------------------------------------------------------- front
lx, ly0, ly1 = 4.55, 4.3, 12.35          # label recess
px, py0, py1 = 2.5, 1.7, 3.1             # logo plate
ZL = ZF - 0.14                           # label surface (recessed)
face([(-hw, 0), (hw, 0), (hw, py0), (px, py0), (-px, py0), (-hw, py0)], ZF, SHELL, 1)
face([(-hw, py0), (-px, py0), (-px, py1), (-hw, py1)], ZF, SHELL, 1)
face([(px, py0), (hw, py0), (hw, py1), (px, py1)], ZF, SHELL, 1)
face([(-hw, py1), (-px, py1), (px, py1), (hw, py1), (hw, ly0), (lx, ly0), (-lx, ly0), (-hw, ly0)], ZF, SHELL, 1)
face([(-hw, ly0), (-lx, ly0), (-lx, ly1), (-hw, ly1)], ZF, SHELL, 1)
face([(lx, ly0), (hw, ly0), (hw, ly1), (lx, ly1)], ZF, SHELL, 1)
face([(-hw, ly1), (-lx, ly1), (lx, ly1), (hw, ly1), (hw, YT), (-hw, YT)], ZF, SHELL, 1)

# raised logo plate
m.box(-px, py0, ZF, px, py1, ZF + 0.12, PLATE, faces={'back': None})

# label recess walls (facing into the recess)
m.polygon([(-lx, ly0, ZL), (lx, ly0, ZL), (lx, ly0, ZF), (-lx, ly0, ZF)], EDGE, normal=(0, 1, 0))
m.polygon([(-lx, ly1, ZL), (lx, ly1, ZL), (lx, ly1, ZF), (-lx, ly1, ZF)], SHELL, normal=(0, -1, 0))
m.polygon([(-lx, ly0, ZL), (-lx, ly1, ZL), (-lx, ly1, ZF), (-lx, ly0, ZF)], SHELL, normal=(1, 0, 0))
m.polygon([(lx, ly0, ZL), (lx, ly1, ZL), (lx, ly1, ZF), (lx, ly0, ZF)], SHELL, normal=(-1, 0, 0))

# label: paper frame, picture with an accent block, title band at the top
fb = 0.3                                  # frame width
ax0, ax1, ay0, ay1 = -lx + fb, lx - fb, ly0 + fb, 10.6
ty0, ty1 = 10.9, ly1 - fb                 # title band
cx1, cy1 = ax0 + 3.0, ay0 + 2.2           # accent block, lower left of the picture
face([(-lx, ly0), (lx, ly0), (lx, ay0), (ax1, ay0), (cx1, ay0), (ax0, ay0), (-lx, ay0)], ZL, FRAME, 1)
face([(-lx, ay0), (ax0, ay0), (ax0, cy1), (ax0, ay1), (ax0, ty0), (ax0, ty1), (-lx, ty1)], ZL, FRAME, 1)
face([(ax1, ay0), (lx, ay0), (lx, ty1), (ax1, ty1), (ax1, ty0), (ax1, ay1)], ZL, FRAME, 1)
face([(-lx, ty1), (ax0, ty1), (ax1, ty1), (lx, ty1), (lx, ly1), (-lx, ly1)], ZL, FRAME, 1)
face([(ax0, ay1), (ax1, ay1), (ax1, ty0), (ax0, ty0)], ZL, FRAME, 1)
face([(cx1, ay0), (ax1, ay0), (ax1, ay1), (ax0, ay1), (ax0, cy1), (cx1, cy1)], ZL, ART, 1)
face([(ax0, ay0), (cx1, ay0), (cx1, cy1), (ax0, cy1)], ZL, ART2, 1)
face([(ax0, ty0), (ax1, ty0), (ax1, ty1), (ax0, ty1)], ZL, TITLE, 1)

# ---------------------------------------------------------------- back
bx, by0, by1 = 3.8, 3.4, 10.8            # sticker
face([(-hw, 0), (hw, 0), (hw, by0), (bx, by0), (-bx, by0), (-hw, by0)], ZB, SHELL, -1)
face([(-hw, by0), (-bx, by0), (-bx, by1), (-hw, by1)], ZB, SHELL, -1)
face([(bx, by0), (hw, by0), (hw, by1), (bx, by1)], ZB, SHELL, -1)
face([(-hw, by1), (-bx, by1), (bx, by1), (hw, by1), (hw, YT), (-hw, YT)], ZB, SHELL, -1)
face([(-bx, by0), (bx, by0), (bx, by1), (-bx, by1)], ZB, STICK, -1)

# ---------------------------------------------------------------- sides with grip ridges
RZ = 0.68                                 # ridges span z -RZ..RZ
RN, RY0, RP, RH = 5, 5.6, 1.05, 0.45      # count, first bottom, pitch, height
ridges = [(RY0 + i * RP, RY0 + i * RP + RH) for i in range(RN)]
r0, r1 = ridges[0][0], ridges[-1][1]
for sx in (1, -1):
    x = sx * hw
    side([(ZB, 0), (ZF, 0), (ZF, r0), (RZ, r0), (-RZ, r0), (ZB, r0)], x, SHELL, sx)
    side([(ZB, r0), (-RZ, r0), (-RZ, r1), (ZB, r1)], x, SHELL, sx)
    side([(RZ, r0), (ZF, r0), (ZF, r1), (RZ, r1)], x, SHELL, sx)
    side([(ZB, r1), (-RZ, r1), (RZ, r1), (ZF, r1)] + arc, x, SHELL, sx)
    for (ya, yb), (yc, _) in zip(ridges, ridges[1:]):
        side([(-RZ, yb), (RZ, yb), (RZ, yc), (-RZ, yc)], x, SHELL, sx)
    for ya, yb in ridges:
        if sx > 0:
            m.box(hw, ya, -RZ, hw + 0.12, yb, RZ, RIDGE, faces={'left': None})
        else:
            m.box(-hw - 0.12, ya, -RZ, -hw, yb, RZ, RIDGE, faces={'right': None})

print(m.stats())
print(m.save())
