# SPDX-License-Identifier: GPL-3.0-or-later
"""NES Game Pak: grey cartridge standing upright, label to +Z, connector edge at y = 0."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (112, 112, 116)     # NES cart grey
SHELL_DK = (78, 78, 82)     # ridges, recess
EDGE = (138, 138, 142)      # top / side faces
LABEL = (24, 24, 28)        # black label base
ART = (64, 140, 224)        # picture area (sky)
ART2 = (224, 72, 48)        # title band
ART3 = (240, 200, 64)       # small accent
PCB = (32, 112, 56)
GOLD = (216, 176, 64)

W, H = 12.0, 13.3
ZF, ZB = 0.85, -0.75        # main shell front / back
ZS = -1.15                  # back of the thicker top step
NX = 5.0                    # half width of the connector notch
NY = 0.75                   # notch height
lx, ly0, ly1 = 4.95, 4.55, 12.45     # label area on the front
bx0, by0, bx1, by1 = -4.2, 2.2, 4.2, 8.6   # sticker recess on the back
SY = 9.6                               # bottom of the back step

m = Model('nes', 'media')
hw = W / 2


# heights where the front / back faces are split: the side walls get a vertex
# at each, and every tile edge running along a side gets them too, so there
# are no T-junction cracks along the outline
SPLITS = [0, by0, ly0, by1, SY, ly1, H]


def edge_points(pts):
    """insert the split points that lie on the polygon's x = +-hw edges"""
    out = []
    for i, (xa, ya) in enumerate(pts):
        xb, yb = pts[(i + 1) % len(pts)]
        out.append((xa, ya))
        if xa == xb and abs(xa) == hw:
            mid = [y for y in SPLITS if min(ya, yb) < y < max(ya, yb)]
            out += [(xa, y) for y in sorted(mid, reverse=ya > yb)]
    return out


def face(pts, z, color, nz):
    """flat face at depth z facing +Z (nz = 1) or -Z (nz = -1)"""
    return m.polygon([(x, y, z) for x, y in edge_points(pts)], color, normal=(0, 0, nz))


# main shell: outline with the open connector notch at the bottom; the front
# and back faces are tiled around the label / sticker so no decal has to sit
# on top of a big face (the software renderer's depth is not perspective correct)
outline = [(-hw, 0), (-NX, 0), (-NX, NY), (NX, NY), (NX, 0), (hw, 0), (hw, H), (-hw, H)]
m.extrude_xy(edge_points(outline), ZB, ZF, SHELL, front=False, back=False, side=EDGE)
# front tiles
face([(-hw, 0), (-NX, 0), (-NX, NY), (NX, NY), (NX, 0), (hw, 0), (hw, ly0), (lx, ly0), (-lx, ly0), (-hw, ly0)], ZF, SHELL, 1)
face([(-hw, ly1), (-lx, ly1), (lx, ly1), (hw, ly1), (hw, H), (-hw, H)], ZF, SHELL, 1)
face([(-hw, ly0), (-lx, ly0), (-lx, ly1), (-hw, ly1)], ZF, SHELL, 1)
face([(lx, ly0), (hw, ly0), (hw, ly1), (lx, ly1)], ZF, SHELL, 1)
# back tiles (the part under the step is hidden inside it)
face([(-hw, 0), (-NX, 0), (-NX, NY), (NX, NY), (NX, 0), (hw, 0), (hw, by0), (bx1, by0), (bx0, by0), (-hw, by0)], ZB, SHELL, -1)
face([(-hw, by1), (bx0, by1), (bx1, by1), (hw, by1), (hw, SY), (-hw, SY)], ZB, SHELL, -1)
face([(-hw, by0), (bx0, by0), (bx0, by1), (-hw, by1)], ZB, SHELL, -1)
face([(bx1, by0), (hw, by0), (hw, by1), (bx1, by1)], ZB, SHELL, -1)
face([(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)], ZB, SHELL_DK, -1)

# thicker top step on the back
m.box(-hw, SY, ZS, hw, H, ZB, EDGE, faces={'front': None, 'back': SHELL})
# grip ridges across the back of the step
for i in range(5):
    y = 10.0 + i * 0.62
    m.box(-hw + 0.6, y, ZS - 0.12, hw - 0.6, y + 0.3, ZS, SHELL_DK, faces={'front': None})

# circuit board showing in the notch, with gold contacts
m.box(-NX + 0.05, 0.0, -0.12, NX - 0.05, NY, 0.12, PCB, faces={'top': None})
m.decal_xy([(-NX + 0.4, 0.08), (NX - 0.4, 0.08), (NX - 0.4, NY - 0.12), (-NX + 0.4, NY - 0.12)], 0.12, GOLD, lift=0.02)

# grip ridges on the lower front
for i in range(6):
    y = 1.15 + i * 0.52
    m.box(-hw + 0.7, y, ZF, hw - 0.7, y + 0.24, ZF + 0.12, SHELL_DK, faces={'back': None})

# label: a thin raised slab; its face is tiled into black frame + picture pieces
ZL = ZF + 0.06
m.box(-lx, ly0, ZF, lx, ly1, ZL, LABEL, faces={'back': None, 'front': None})
ax0, ax1, ay0, ay1 = -lx + 0.5, lx - 0.5, ly0 + 0.5, ly1 - 2.2
ty0, ty1 = ly1 - 1.7, ly1 - 0.5
face([(-lx, ly0), (lx, ly0), (lx, ay0), (ax1, ay0), (ax0 + 2.5, ay0), (ax0, ay0), (-lx, ay0)], ZL, LABEL, 1)
face([(-lx, ty1), (ax0, ty1), (ax1, ty1), (lx, ty1), (lx, ly1), (-lx, ly1)], ZL, LABEL, 1)
face([(-lx, ay0), (ax0, ay0), (ax0, ay0 + 1.9), (ax0, ay1), (ax0, ty0), (ax0, ty1), (-lx, ty1)], ZL, LABEL, 1)
face([(ax1, ay0), (lx, ay0), (lx, ty1), (ax1, ty1), (ax1, ty0), (ax1, ay1)], ZL, LABEL, 1)
face([(ax0, ay1), (ax1, ay1), (ax1, ty0), (ax0, ty0)], ZL, LABEL, 1)
face([(ax0 + 2.5, ay0), (ax1, ay0), (ax1, ay1), (ax0, ay1), (ax0, ay0 + 1.9), (ax0 + 2.5, ay0 + 1.9)], ZL, ART, 1)
face([(ax0, ay0), (ax0 + 2.5, ay0), (ax0 + 2.5, ay0 + 1.9), (ax0, ay0 + 1.9)], ZL, ART3, 1)
face([(ax0, ty0), (ax1, ty0), (ax1, ty1), (ax0, ty1)], ZL, ART2, 1)

print(m.stats())
print(m.save())
