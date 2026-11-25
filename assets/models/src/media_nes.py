# SPDX-License-Identifier: GPL-3.0-or-later
"""NES Game Pak (North American): grey cartridge, 12 x 13.3 x 2 cm, standing
upright, front label (the game's picture) to +Z, connector edge at y = 0.

Shape after photos of the real shell: the bottom 2.4 cm is narrower (10.8 cm)
than the body; the edge connector sits in an opening in the bottom face (the
front and back walls run down to the bottom edge); front: big label in the
upper part, horizontal grip ribs below it; back: a ribbed strip on the left,
the recessed back-sticker panel on the right, an arrow pointing to the
connector.

Insertion (front-loading NES): the console turns this model label up and
slides it in connector first, then presses it down. The outer shell is a
closed prism: outline below, z = -1 .. +1 (front ribs and decals stick out
at most 0.1 cm on +Z, back decals 0.03 cm on -Z)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (128, 128, 132)     # NES cart grey
EDGE = (152, 152, 156)      # top and side walls (a touch lighter)
RIB = (88, 88, 92)          # grip ribs, back grooves
PANEL = (104, 104, 108)     # recessed back-sticker panel
LABEL = (36, 36, 40)        # label colour when there is no picture (black-bordered labels)
CAVITY = (20, 20, 22)       # inside the connector opening
PCB = (32, 112, 56)
GOLD = (216, 176, 64)

W, H, T = 12.0, 13.3, 2.0
hw, ht = W / 2, T / 2
ZF, ZB = ht, -ht
NW = 5.4                    # half width of the narrow bottom part
NH = 2.4                    # height of the narrow bottom part
CX, CZ, CY = 4.75, 0.62, 0.7    # connector opening: half width, half depth, depth upwards

m = Model('nes', 'media')

# label recess on the front (the label fills it; its floor is the picture)
LX, LY0, LY1 = 5.1, 5.2, 12.65
LD = 0.07                   # recess depth

# ---------------------------------------------------------------- shell
# outline (CCW seen from +Z), side walls split where the label recess starts
# and ends so the front tiles share their vertices (no cracks)
outline = [(-NW, 0), (NW, 0), (NW, NH), (hw, NH), (hw, LY0), (hw, LY1), (hw, H),
           (-hw, H), (-hw, LY1), (-hw, LY0), (-hw, NH), (-NW, NH)]
m.polygon([(x, y, ZB) for x, y in outline], SHELL, normal=(0, 0, -1))
for i in range(1, len(outline)):            # every wall but the bottom
    (xa, ya), (xb, yb) = outline[i], outline[(i + 1) % len(outline)]
    m.quad((xa, ya, ZF), (xa, ya, ZB), (xb, yb, ZB), (xb, yb, ZF), EDGE)
# front face tiled around the label recess
def front(pts, color=SHELL):
    m.polygon([(x, y, ZF) for x, y in pts], color, normal=(0, 0, 1))

front([(-NW, 0), (NW, 0), (NW, NH), (hw, NH), (hw, LY0), (LX, LY0), (-LX, LY0), (-hw, LY0), (-hw, NH), (-NW, NH)])
front([(-hw, LY1), (-LX, LY1), (LX, LY1), (hw, LY1), (hw, H), (-hw, H)])
front([(-hw, LY0), (-LX, LY0), (-LX, LY1), (-hw, LY1)])
front([(LX, LY0), (hw, LY0), (hw, LY1), (LX, LY1)])
# recess walls (face inwards) and the picture as its floor
for t in m.box(-LX, LY0, ZF - LD, LX, LY1, ZF, RIB, faces={'front': None, 'back': None}):
    i0, i1, i2, c = m.tris[t]
    m.tris[t] = (i1, i0, i2, c)
m.image_xy(-LX, LY0, LX, LY1, ZF - LD, fallback=LABEL, lift=0.0)

# bottom face with the connector opening
def bottom(x0, z0, x1, z1):
    m.quad((x0, 0, z0), (x1, 0, z0), (x1, 0, z1), (x0, 0, z1), EDGE)

bottom(-NW, ZB, -CX, ZF)
bottom(CX, ZB, NW, ZF)
bottom(-CX, CZ, CX, ZF)
bottom(-CX, ZB, CX, -CZ)
# the cavity above it: dark walls and ceiling, seen from below
for t in m.box(-CX, 0, -CZ, CX, CY, CZ, CAVITY, faces={'bottom': None}):
    i0, i1, i2, c = m.tris[t]
    m.tris[t] = (i1, i0, i2, c)       # turned inside out: the walls face into the opening

# circuit board edge hanging in the opening, gold fingers on both sides
PB = 0.08
m.box(-CX + 0.25, 0.08, -PB, CX - 0.25, CY, PB, PCB, faces={'top': None})
fing = [(-CX + 0.45, 0.12), (CX - 0.45, 0.12), (CX - 0.45, CY - 0.08), (-CX + 0.45, CY - 0.08)]
m.decal_xy(fing, PB, GOLD, lift=0.015)
m.polygon([(x, y, -PB - 0.015) for x, y in fing], GOLD, normal=(0, 0, -1))

# ---------------------------------------------------------------- front
# horizontal grip ribs below the label
for i in range(6):
    y = 0.75 + i * 0.68
    m.box(-4.7, y, ZF, 4.7, y + 0.28, ZF + 0.1, RIB, faces={'back': None})

# ---------------------------------------------------------------- back
def back_decal(pts, color, lift=0.03):
    m.polygon([(x, y, ZB - lift) for x, y in pts], color, normal=(0, 0, -1))

def back_rect(x0, y0, x1, y1, color, lift=0.03):
    back_decal([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, lift)

# seen from behind, the ribbed strip is on the viewer's left (model +x) and the
# recessed sticker panel on the right (model -x)
back_rect(-4.45, 4.2, 1.2, 13.05, PANEL)
# ribbed strip: deeper finger grip at the top, grooves below
back_rect(1.55, 11.7, 4.15, 13.1, RIB)
for i in range(9):
    y = 0.6 + i * 1.2
    back_rect(1.55, y, 4.15, y + 0.3, RIB)
# arrow pointing down to the connector
back_decal([(0.5, 3.4), (-0.55, 3.4), (0.0, 2.55)], RIB)

print(m.stats())
print(m.save())
