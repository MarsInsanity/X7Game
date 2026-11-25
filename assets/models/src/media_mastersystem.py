# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega Master System cartridge: black shell standing upright, label to +Z,
connector end at y = 0.

Real size about 10.0 x 13.0 x 2.0 cm. Signature features (from photos of the
real cartridge): the label is a wide strip across the TOP of the front only
(here: the picture area), three grip grooves just below it that run all the
way round the shell, a big plain black panel below, small steps in the side
edges at the connector end, and the connector end open with the board edge
and its gold contacts set back inside.

Insertion: the cartridge goes straight down into the console's top slot,
label to the front; the label and the grooves stay above the slot.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (30, 30, 34)        # black plastic, front / back
EDGE = (58, 58, 64)         # side and top faces, so the outline reads
PANEL = (44, 44, 50)        # the big flat panel below the grooves
GROOVE = (8, 8, 10)         # grip grooves
CAVE = (12, 12, 14)         # inside of the connector opening
PCB = (36, 118, 60)
GOLD = (214, 174, 60)
LABEL = (178, 38, 42)       # fallback for the picture: the plain red grid label

W, H, D = 10.0, 13.0, 2.0
hw = W / 2
ZF, ZB = D / 2, -D / 2
NW, NH = hw - 0.3, 1.0      # connector end: narrower by 0.3 per side, 1.0 high
C = 0.25                    # top corner chamfer
OX, OZ0, OZ1, OY = NW - 0.3, ZB + 0.3, ZF - 0.25, 1.4   # connector opening (cavity)

m = Model('mastersystem', 'media')

# ---------------------------------------------------------------- shell
outline = [(-NW, 0), (NW, 0), (NW, NH), (hw, NH), (hw, H - C), (hw - C, H),
           (-hw + C, H), (-hw, H - C), (-hw, NH), (-NW, NH)]
m.polygon([(x, y, ZF) for x, y in outline], SHELL, normal=(0, 0, 1))
m.polygon([(x, y, ZB) for x, y in outline], SHELL, normal=(0, 0, -1))
n = len(outline)
for i in range(1, n):                       # every edge but the bottom one
    (xa, ya), (xb, yb) = outline[i], outline[(i + 1) % n]
    nx, ny = yb - ya, -(xb - xa)            # outward (outline is counter-clockwise)
    m.polygon([(xa, ya, ZB), (xb, yb, ZB), (xb, yb, ZF), (xa, ya, ZF)], EDGE, normal=(nx, ny, 0))

# bottom face: a frame around the connector opening
down = (0, -1, 0)
for pts in ([(-NW, ZB), (NW, ZB), (NW, OZ0), (-NW, OZ0)],
            [(-NW, OZ1), (NW, OZ1), (NW, ZF), (-NW, ZF)],
            [(-NW, OZ0), (-OX, OZ0), (-OX, OZ1), (-NW, OZ1)],
            [(OX, OZ0), (NW, OZ0), (NW, OZ1), (OX, OZ1)]):
    m.polygon([(x, 0, z) for x, z in pts], EDGE, normal=down)

# the opening: walls and ceiling facing inwards (dark)
m.polygon([(-OX, 0, OZ1), (OX, 0, OZ1), (OX, OY, OZ1), (-OX, OY, OZ1)], CAVE, normal=(0, 0, -1))
m.polygon([(-OX, 0, OZ0), (OX, 0, OZ0), (OX, OY, OZ0), (-OX, OY, OZ0)], CAVE, normal=(0, 0, 1))
m.polygon([(-OX, 0, OZ0), (-OX, 0, OZ1), (-OX, OY, OZ1), (-OX, OY, OZ0)], CAVE, normal=(1, 0, 0))
m.polygon([(OX, 0, OZ0), (OX, 0, OZ1), (OX, OY, OZ1), (OX, OY, OZ0)], CAVE, normal=(-1, 0, 0))
m.polygon([(-OX, OY, OZ0), (OX, OY, OZ0), (OX, OY, OZ1), (-OX, OY, OZ1)], CAVE, normal=down)

# the board edge, set back 0.3 cm inside the opening, gold contacts on both faces
PX, PY, PT = 3.3, 0.3, 0.08
m.box(-PX, PY, -PT, PX, OY, PT, PCB, faces={'top': None})
for z, nz in ((PT, 1), (-PT, -1)):
    m.polygon([(-PX + 0.25, PY + 0.05, z + 0.02 * nz), (PX - 0.25, PY + 0.05, z + 0.02 * nz),
               (PX - 0.25, PY + 0.7, z + 0.02 * nz), (-PX + 0.25, PY + 0.7, z + 0.02 * nz)], GOLD, normal=(0, 0, nz))

# ---------------------------------------------------------------- front
# the big flat panel (a slightly lighter tone, with the shell's rim around it)
m.decal_xy([(-hw + 0.3, 0.3), (hw - 0.3, 0.3), (hw - 0.3, 8.5), (-hw + 0.3, 8.5)], ZF, PANEL, lift=0.02)

# three grip grooves running all the way round: each a thin closed band
# 0.02 cm proud of the shell (closed, so no edge ever shows a back face)
GY = [(8.75, 8.98), (9.12, 9.35), (9.49, 9.72)]
for y0, y1 in GY:
    m.box(-hw - 0.02, y0, ZB - 0.02, hw + 0.02, y1, ZF + 0.02, GROOVE)

# the label strip across the top of the front: the game's picture
LX, LY0, LY1 = hw - 0.22, 9.9, H - 0.18
m.image_xy(-LX, LY0, LX, LY1, ZF, fallback=LABEL, lift=0.03)

print(m.stats())
print(m.save())
