# SPDX-License-Identifier: GPL-3.0-or-later
"""Neo Geo AES cartridge: the huge black shell standing upright, label to +Z.

Real size ~18.5 x 13.2 x 3.4 cm (wider than tall). Signature features: the
sheer chunky size, the black plastic, the big recessed landscape label on
the front, the band of horizontal grip ridges across the top of the front
and back, the bevelled top edges, the narrower connector lip at the bottom
that drops into the console's slot, and the paper sticker on the back.
Front and back faces are tiled around every label / ridge so nothing is an
overlapping decal (the software renderer's depth is not perspective
correct).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (40, 40, 46)         # black plastic
EDGE = (66, 66, 76)          # bevels, recess walls, lip step
RIDGE = (96, 96, 106)        # grip ridges
GOLD = (214, 170, 60)        # label header strip
ART = (52, 104, 196)         # label picture (sky)
ART2 = (236, 140, 36)        # label picture ground
TITLE = (196, 34, 40)        # label title block
STICK = (200, 196, 180)      # back sticker

W, H, D = 18.5, 13.2, 3.4
hw = W / 2
ZF, ZB = D / 2, -D / 2
LIP_Y, LIP_Z = 1.0, 1.35      # connector lip: height, half depth
YT, ZT = 12.45, 1.2           # bevel: starts at YT, top face half depth ZT

m = Model('neogeo', 'media')


def face(pts, z, color, nz):
    """flat face at depth z facing +Z (nz = 1) or -Z (nz = -1); pts are (x, y)"""
    return m.polygon([(x, y, z) for x, y in pts], color, normal=(0, 0, nz))


# ---------------------------------------------------------------- profile: sides, top, bevels, lip
profile = [(-LIP_Z, 0), (LIP_Z, 0), (LIP_Z, LIP_Y), (ZF, LIP_Y), (ZF, YT), (ZT, H),
           (-ZT, H), (ZB, YT), (ZB, LIP_Y), (-LIP_Z, LIP_Y)]
for sx in (1, -1):
    m.polygon([(sx * hw, y, z) for z, y in profile], SHELL, normal=(sx, 0, 0))
m.polygon([(-hw, 0, -LIP_Z), (hw, 0, -LIP_Z), (hw, 0, LIP_Z), (-hw, 0, LIP_Z)], SHELL, normal=(0, -1, 0))
m.polygon([(-hw, H, -ZT), (hw, H, -ZT), (hw, H, ZT), (-hw, H, ZT)], SHELL, normal=(0, 1, 0))
m.polygon([(-hw, YT, ZF), (hw, YT, ZF), (hw, H, ZT), (-hw, H, ZT)], EDGE, normal=(0, 0.45, 0.7))
m.polygon([(-hw, YT, ZB), (hw, YT, ZB), (hw, H, -ZT), (-hw, H, -ZT)], EDGE, normal=(0, 0.45, -0.7))
for sz in (1, -1):
    # lip face and the underside of the ledge above it
    m.polygon([(-hw, 0, sz * LIP_Z), (hw, 0, sz * LIP_Z), (hw, LIP_Y, sz * LIP_Z), (-hw, LIP_Y, sz * LIP_Z)],
              SHELL, normal=(0, 0, sz))
    m.polygon([(-hw, LIP_Y, sz * LIP_Z), (hw, LIP_Y, sz * LIP_Z), (hw, LIP_Y, sz * ZF), (-hw, LIP_Y, sz * ZF)],
              EDGE, normal=(0, -1, 0))

# ---------------------------------------------------------------- grip ridges (front and back)
gx = 8.3                                   # ridge half width
RN, RY0, RP, RH, RD = 4, 10.25, 0.5, 0.26, 0.16
ridges = [(RY0 + i * RP, RY0 + i * RP + RH) for i in range(RN)]
r0, r1 = ridges[0][0], ridges[-1][1]


def ridge_band(z, nz):
    face([(-hw, r0), (-gx, r0), (-gx, r1), (-hw, r1)], z, SHELL, nz)
    face([(gx, r0), (hw, r0), (hw, r1), (gx, r1)], z, SHELL, nz)
    for (_, yb), (yc, _) in zip(ridges, ridges[1:]):
        face([(-gx, yb), (gx, yb), (gx, yc), (-gx, yc)], z, SHELL, nz)
    for ya, yb in ridges:
        if nz > 0:
            m.box(-gx, ya, z, gx, yb, z + RD, RIDGE, faces={'back': None})
        else:
            m.box(-gx, ya, z - RD, gx, yb, z, RIDGE, faces={'front': None})
    face([(-hw, r1), (-gx, r1), (gx, r1), (hw, r1), (hw, YT), (-hw, YT)], z, SHELL, nz)


ridge_band(ZF, 1)
ridge_band(ZB, -1)

# ---------------------------------------------------------------- front: recessed label
lx, ly0, ly1 = 8.3, 2.0, 9.55
ZL = ZF - 0.16
face([(-hw, LIP_Y), (hw, LIP_Y), (hw, ly0), (lx, ly0), (-lx, ly0), (-hw, ly0)], ZF, SHELL, 1)
face([(-hw, ly0), (-lx, ly0), (-lx, ly1), (-hw, ly1)], ZF, SHELL, 1)
face([(lx, ly0), (hw, ly0), (hw, ly1), (lx, ly1)], ZF, SHELL, 1)
face([(-hw, ly1), (-lx, ly1), (lx, ly1), (hw, ly1), (hw, r0), (gx, r0), (-gx, r0), (-hw, r0)], ZF, SHELL, 1)
# recess walls
m.polygon([(-lx, ly0, ZL), (lx, ly0, ZL), (lx, ly0, ZF), (-lx, ly0, ZF)], EDGE, normal=(0, 1, 0))
m.polygon([(-lx, ly1, ZL), (lx, ly1, ZL), (lx, ly1, ZF), (-lx, ly1, ZF)], SHELL, normal=(0, -1, 0))
m.polygon([(-lx, ly0, ZL), (-lx, ly1, ZL), (-lx, ly1, ZF), (-lx, ly0, ZF)], EDGE, normal=(1, 0, 0))
m.polygon([(lx, ly0, ZL), (lx, ly1, ZL), (lx, ly1, ZF), (lx, ly0, ZF)], SHELL, normal=(-1, 0, 0))
# label: gold header strip, red title block under it, sky picture, orange ground
hy, ty, tx, gy = 8.8, 6.7, -1.2, 3.5
face([(-lx, hy), (lx, hy), (lx, ly1), (-lx, ly1)], ZL, GOLD, 1)
face([(-lx, ty), (tx, ty), (tx, hy), (-lx, hy)], ZL, TITLE, 1)
face([(-lx, gy), (lx, gy), (lx, ty), (lx, hy), (tx, hy), (tx, ty), (-lx, ty)], ZL, ART, 1)
face([(-lx, ly0), (lx, ly0), (lx, gy), (-lx, gy)], ZL, ART2, 1)

# ---------------------------------------------------------------- back: sticker
bx, by0, by1 = 6.6, 2.6, 8.8
face([(-hw, LIP_Y), (hw, LIP_Y), (hw, by0), (bx, by0), (-bx, by0), (-hw, by0)], ZB, SHELL, -1)
face([(-hw, by0), (-bx, by0), (-bx, by1), (-hw, by1)], ZB, SHELL, -1)
face([(bx, by0), (hw, by0), (hw, by1), (bx, by1)], ZB, SHELL, -1)
face([(-hw, by1), (-bx, by1), (bx, by1), (hw, by1), (hw, r0), (gx, r0), (-gx, r0), (-hw, r0)], ZB, SHELL, -1)
face([(-bx, by0), (bx, by0), (bx, by1), (-bx, by1)], ZB, STICK, -1)

print(m.stats())
print(m.save())
