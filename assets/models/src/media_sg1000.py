# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega SG-1000 / SC-3000 cartridge (1983): a portrait, slab-shaped black
cartridge standing upright, label to +Z, open connector end at y = 0.

From photos of the real thing: a plain black shell about 8.4 x 11.0 x 1.7 cm,
taller than wide; a big label (the game's picture) across the top ~57 % of
the front, starting right at the top edge with thin black margins at the
sides; grip ribs across the upper part of both side walls; a seam along the
sides; the bottom end open, the bare circuit board with its contacts set a
little way inside the shell; a darker groove across the back.

Insertion: goes straight DOWN into the SG-1000's top slot, label to the
front. The shell is a plain box (8.4 wide, 1.7 deep) from y = 0 up; only the
grip ribs (y 6.7 to 10.6) stick out 0.1 cm from the side walls.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (30, 30, 34)        # black plastic
RIB = (70, 70, 78)          # grip ribs (lighter so they read)
SEAM = (12, 12, 14)         # seam line / back groove
HOLE = (8, 8, 10)           # inside of the open connector end
BOARD = (214, 204, 164)     # pale circuit board
CONTACT = (150, 136, 92)    # contact fingers
LABEL = (226, 222, 204)     # plain label colour (picture fallback)

W, H, D = 8.4, 11.0, 1.7
hw, hd = W / 2, D / 2
ZF, ZB = hd, -hd
# label = picture area on the front
LX0, LX1 = -hw + 0.65, hw - 0.65
LY0, LY1 = 4.5, H - 0.2
# open end: wall thickness, cavity height, board
WALL = 0.22
CAV = 0.8
BX, BZ, BY0 = hw - 0.45, 0.08, 0.18
# grip ribs on the side walls
RIB0, RIB1, NRIB, RT = 6.7, 10.6, 9, 0.1

m = Model('sg1000', 'media')


def rect_xy(x0, y0, x1, y1, z, color, nz=1):
    return m.polygon([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], color, normal=(0, 0, nz))


def rect_xz(x0, z0, x1, z1, y, color, ny=1):
    return m.polygon([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], color, normal=(0, ny, 0))


# ---- shell: front tiled around the label, plain back, sides, top
rect_xy(-hw, 0, hw, LY0, ZF, SHELL)
rect_xy(-hw, LY1, hw, H, ZF, SHELL)
rect_xy(-hw, LY0, LX0, LY1, ZF, SHELL)
rect_xy(LX1, LY0, hw, LY1, ZF, SHELL)
m.box(-hw, 0, ZB, hw, H, ZF, SHELL, faces={'front': None, 'bottom': None})
# bottom end: a frame around the opening
ix, iz = hw - WALL, hd - WALL
rect_xz(-hw, -hd, hw, -iz, 0, SHELL, -1)
rect_xz(-hw, iz, hw, hd, 0, SHELL, -1)
rect_xz(-hw, -iz, -ix, iz, 0, SHELL, -1)
rect_xz(ix, -iz, hw, iz, 0, SHELL, -1)
# cavity inside the opening (walls face inwards, ceiling faces down)
m.quad((-ix, 0, -iz), (ix, 0, -iz), (ix, CAV, -iz), (-ix, CAV, -iz), HOLE)       # back wall, faces +Z
m.quad((ix, 0, iz), (-ix, 0, iz), (-ix, CAV, iz), (ix, CAV, iz), HOLE)           # front wall, faces -Z
m.quad((-ix, 0, iz), (-ix, 0, -iz), (-ix, CAV, -iz), (-ix, CAV, iz), HOLE)       # left wall, faces +X
m.quad((ix, 0, -iz), (ix, 0, iz), (ix, CAV, iz), (ix, CAV, -iz), HOLE)           # right wall, faces -X
rect_xz(-ix, -iz, ix, iz, CAV, HOLE, -1)                                         # ceiling
# circuit board hanging from the ceiling, contacts on both faces
m.box(-BX, BY0, -BZ, BX, CAV, BZ, BOARD, faces={'top': None})
m.decal_xy([(-BX + 0.3, BY0 + 0.04), (BX - 0.3, BY0 + 0.04), (BX - 0.3, CAV - 0.12), (-BX + 0.3, CAV - 0.12)],
           BZ, CONTACT)
m.polygon([(BX - 0.3, BY0 + 0.04, -BZ - 0.02), (-BX + 0.3, BY0 + 0.04, -BZ - 0.02),
           (-BX + 0.3, CAV - 0.12, -BZ - 0.02), (BX - 0.3, CAV - 0.12, -BZ - 0.02)], CONTACT, normal=(0, 0, -1))

# ---- grip ribs: triangular ridges running front to back on both side walls
step = (RIB1 - RIB0) / NRIB
for i in range(NRIB):
    y0 = RIB0 + i * step + step * 0.15
    y1 = y0 + step * 0.7
    ym = (y0 + y1) / 2
    for s in (1, -1):
        x0, x1 = s * hw, s * (hw + RT)
        prof = [(x0, y0), (x1, ym), (x0, y1)]
        m.extrude_xy(prof, ZB + 0.15, ZF - 0.15, RIB)

# ---- seam along both side walls (below the ribs) and a groove across the back
for s in (1, -1):
    x = s * (hw + 0.02)
    pts = [(x, 0.3, 0.05), (x, 0.3, -0.05), (x, RIB0 - 0.2, -0.05), (x, RIB0 - 0.2, 0.05)]
    m.polygon(pts, SEAM, normal=(s, 0, 0))
m.polygon([(hw - 0.3, 4.5, ZB - 0.02), (-hw + 0.3, 4.5, ZB - 0.02), (-hw + 0.3, 4.9, ZB - 0.02),
           (hw - 0.3, 4.9, ZB - 0.02)], SEAM, normal=(0, 0, -1))

# ---- the label: a thin sticker on the front, its face the game's picture
LT = 0.03
m.box(LX0, LY0, ZF, LX1, LY1, ZF + LT, LABEL, faces={'front': None, 'back': None})
m.image_xy(LX0, LY0, LX1, LY1, ZF, fallback=LABEL, lift=LT)

print(m.stats())
print(m.save())
