# SPDX-License-Identifier: GPL-3.0-or-later
"""Game Boy Color Game Pak: the black Game Boy cartridge (notched top-right
corner), standing upright, label to +Z, contacts edge at y = 0."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (48, 48, 56)        # black shell
EDGE = (80, 80, 92)         # side / top faces, so the black edges read
EMBOSS = (104, 104, 118)    # raised logo strip, arrow, grip ribs
LABEL = (232, 228, 212)     # cream label border
SKY = (72, 152, 232)        # picture area
GROUND = (96, 184, 72)      # picture lower part
BAND = (216, 48, 56)        # title band across the top of the label
ACC1 = (248, 200, 40)       # colour-logo accent stripes
ACC2 = (144, 72, 208)
PCB = (24, 96, 48)
GOLD = (216, 176, 64)
SCREW = (150, 150, 158)

W, H = 5.7, 6.5
hw = W / 2
N = 0.65                    # size of the cut top-right corner
ZF, ZB, ZM = 0.30, -0.38, -0.14   # recessed label face, back, back of the front shell
ZR = 0.39                   # raised frame around the label
CX = 2.45                   # half width of the contacts opening on the back
CY = 0.85                   # height of the contacts opening
LX, LY0, LY1 = 2.3, 1.25, 5.3     # label recess

m = Model('gbc', 'media')


def face(pts, z, color, nz=1):
    """flat face at depth z facing +Z (nz = 1) or -Z (nz = -1)"""
    return m.polygon([(x, y, z) for x, y in pts], color, normal=(0, 0, nz))


# front half of the shell (its front face is the label, tiled below)
front = [(-hw, 0), (-CX, 0), (CX, 0), (hw, 0), (hw, H - N), (hw - N, H), (-hw, H)]
m.extrude_xy(front, ZM, ZF, SHELL, front=False, back=False, side=EDGE)
# back half: same outline with the contacts opening at the bottom
back = [(-hw, 0), (-CX, 0), (-CX, CY), (CX, CY), (CX, 0), (hw, 0), (hw, H - N), (hw - N, H), (-hw, H)]
m.extrude_xy(back, ZB, ZM, SHELL, front=False, side=EDGE)
# circuit board face in the opening, with gold contacts
face([(CX, 0), (-CX, 0), (-CX, CY), (CX, CY)], ZM, PCB, -1)
n = 10
pitch = (2 * CX - 0.3) / n
for i in range(n):
    x0 = CX - 0.15 - i * pitch - 0.06
    x1 = x0 - pitch + 0.14
    face([(x0, 0.05), (x1, 0.05), (x1, CY - 0.2), (x0, CY - 0.2)], ZM - 0.03, GOLD, -1)

# raised frame around the recessed label
m.extrude_xy([(-hw, LY1), (hw, LY1), (hw, H - N), (hw - N, H), (-hw, H)], ZF, ZR, SHELL, back=False, side=EDGE)
m.box(-hw, 0, ZF, hw, LY0, ZR, SHELL, faces={'back': None, 'bottom': EDGE, 'top': EDGE, 'left': EDGE, 'right': EDGE})
m.box(-hw, LY0, ZF, -LX, LY1, ZR, SHELL, faces={'back': None, 'bottom': None, 'top': None, 'left': EDGE, 'right': EDGE})
m.box(LX, LY0, ZF, hw, LY1, ZR, SHELL, faces={'back': None, 'bottom': None, 'top': None, 'left': EDGE, 'right': EDGE})

# moulded (raised) logo strip on the top band and the insert arrow
m.box(-2.35, 5.65, ZR, 0.9, 6.15, ZR + 0.04, EMBOSS, faces={'back': None})
m.extrude_xy([(1.3, 6.08), (2.1, 6.08), (1.7, 5.5)], ZR, ZR + 0.04, EMBOSS, back=False)

# label filling the recess, tiled (no decal stacked on a big face: the
# software renderer's depth is not perspective correct)
ax0, ax1 = -LX + 0.25, LX - 0.25
gy, sy, ty, by = 1.55, 2.4, 4.2, 4.35       # ground / sky / stripes / band starts
ey = 5.0                                     # top of the picture
face([(-LX, LY0), (LX, LY0), (LX, gy), (ax1, gy), (0.0, gy), (ax0, gy), (-LX, gy)], ZF, LABEL)
face([(-LX, ey), (ax0, ey), (0.0, ey), (ax1, ey), (LX, ey), (LX, LY1), (-LX, LY1)], ZF, LABEL)
face([(-LX, gy), (ax0, gy), (ax0, sy), (ax0, ty), (ax0, by), (ax0, ey), (-LX, ey)], ZF, LABEL)
face([(ax1, gy), (LX, gy), (LX, ey), (ax1, ey), (ax1, by), (ax1, ty), (ax1, sy)], ZF, LABEL)
face([(ax0, gy), (0.0, gy), (ax1, gy), (ax1, sy), (ax0, sy)], ZF, GROUND)
face([(ax0, sy), (ax1, sy), (ax1, ty), (0.0, ty), (ax0, ty)], ZF, SKY)
face([(ax0, ty), (0.0, ty), (0.0, by), (ax0, by)], ZF, ACC1)
face([(0.0, ty), (ax1, ty), (ax1, by), (0.0, by)], ZF, ACC2)
face([(ax0, by), (0.0, by), (ax1, by), (ax1, ey), (0.0, ey), (ax0, ey)], ZF, BAND)

# a small sun in the picture (a thin raised disc: small, so no depth fighting)
m.cylinder_z(1.2, 3.5, 0.38, ZF, ZF + 0.03, ACC1, segments=8, back=False)

# back: grip ribs near the top and the centre screw
for i in range(4):
    y = 4.9 + i * 0.32
    m.box(-2.0, y, ZB - 0.06, 2.0, y + 0.14, ZB, EMBOSS, faces={'front': None})
m.cylinder_z(0.0, 3.0, 0.22, ZB - 0.03, ZB, SCREW, segments=8, front=False)

print(m.stats())
print(m.save())
