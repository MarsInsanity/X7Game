# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega Master System cartridge: black shell standing upright, label to +Z,
connector edge at y = 0. Signature features: black plastic, big front label
with a red title band over a black field ruled by a white grid (with the
picture box), grip ridges across the top, narrower insertion end with the
board edge showing in the bottom opening."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (34, 34, 38)        # black plastic (front / back)
EDGE = (62, 62, 68)         # top / side faces, so the outline reads
RIDGE = (92, 92, 100)       # grip ridges
SLOT = (14, 14, 16)         # inside the connector opening
WHITE = (236, 236, 236)     # label grid lines and frame
LBLACK = (16, 16, 20)       # label field
RED = (216, 32, 40)         # title band
ART = (56, 120, 216)        # picture box
ART2 = (248, 200, 40)       # small accent in the picture
PCB = (32, 112, 56)
GOLD = (216, 176, 64)

m = Model('mastersystem', 'media')

W, H = 10.0, 13.0
hw = W / 2
NW = 4.6                    # half width of the narrower insertion end
SH = 1.0                    # height of the insertion end step
CH = 0.4                    # top corner chamfer
ZF, ZB = 0.9, -0.9
NX, NY = 3.4, 0.7           # connector opening (half width, height)
lx, ly0, ly1 = 4.4, 1.6, 10.4   # label on the front


def split(pts, pool):
    """insert every pool point lying strictly inside one of the polygon's
    edges, so faces that meet along an edge share its vertices (no
    T-junction cracks in the software renderer)"""
    out = []
    for i, (xa, ya) in enumerate(pts):
        xb, yb = pts[(i + 1) % len(pts)]
        out.append((xa, ya))
        dx, dy = xb - xa, yb - ya
        l2 = dx * dx + dy * dy
        mid = []
        for px, py in pool:
            t = ((px - xa) * dx + (py - ya) * dy) / l2
            if 1e-6 < t < 1 - 1e-6 and abs((px - xa) * dy - (py - ya) * dx) < 1e-6:
                mid.append((t, (px, py)))
        out += [q for _, q in sorted(set(mid))]
    return out


def face(pts, z, color, nz, pool=()):
    """flat face at depth z facing +Z (nz = 1) or -Z (nz = -1)"""
    return m.polygon([(x, y, z) for x, y in split(pts, pool)], color, normal=(0, 0, nz))


outline = [(-NW, 0), (-NX, 0), (-NX, NY), (NX, NY), (NX, 0), (NW, 0), (NW, SH), (hw, SH + 0.3),
           (hw, H - CH), (hw - CH, H), (-hw + CH, H), (-hw, H - CH), (-hw, SH + 0.3), (-NW, SH)]
SIDE_PTS = [(sx, y) for sx in (-hw, hw) for y in (ly0, ly1)]   # where the front tiles meet the sides
m.extrude_xy(split(outline, SIDE_PTS), ZB, ZF, SHELL, front=False, back=False, side=EDGE)

# front tiled around the label (no decal over a big face)
face([(-NW, 0), (-NX, 0), (-NX, NY), (NX, NY), (NX, 0), (NW, 0), (NW, SH), (hw, SH + 0.3), (hw, ly0),
      (lx, ly0), (-lx, ly0), (-hw, ly0), (-hw, SH + 0.3), (-NW, SH)], ZF, SHELL, 1, SIDE_PTS)
face([(-hw, ly1), (-lx, ly1), (lx, ly1), (hw, ly1), (hw, H - CH), (hw - CH, H), (-hw + CH, H), (-hw, H - CH)], ZF, SHELL, 1)
face([(-hw, ly0), (-lx, ly0), (-lx, ly1), (-hw, ly1)], ZF, SHELL, 1)
face([(lx, ly0), (hw, ly0), (hw, ly1), (lx, ly1)], ZF, SHELL, 1)
# back: one face
face(outline, ZB, SHELL, -1, SIDE_PTS)

# dark inside of the connector opening, with the board edge and contacts
m.box(-NX, 0.0, ZB + 0.05, NX, NY - 0.02, ZF - 0.05, SLOT, faces={'top': None, 'bottom': None, 'left': None, 'right': None})
m.box(-NX + 0.3, 0.0, -0.1, NX - 0.3, NY - 0.04, 0.1, PCB, faces={'bottom': None, 'back': None, 'left': None, 'right': None})
m.decal_xy([(-NX + 0.6, 0.0), (NX - 0.6, 0.0), (NX - 0.6, NY - 0.2), (-NX + 0.6, NY - 0.2)], 0.1, GOLD, lift=0.03)

# grip ridges across the top, front and back
for i in range(4):
    y = 10.9 + i * 0.45
    # only the faces that show from normal viewing angles (the shell face is behind the rest)
    m.box(-hw + 0.5, y, ZF, hw - 0.5, y + 0.22, ZF + 0.12, RIDGE,
          faces={'back': None, 'bottom': None, 'left': None, 'right': None})
    m.box(-hw + 0.5, y, ZB - 0.12, hw - 0.5, y + 0.22, ZB, RIDGE,
          faces={'front': None, 'bottom': None, 'left': None, 'right': None})

# label: thin raised slab, its face tiled into frame, title band and grid
ZL = ZF + 0.06
tiles = []


def tile(pts, color):
    tiles.append((pts, color))


ix = lx - 0.3                       # inner edge of the white frame
rows = [  # (y0, y1, [(x0, x1, colour), ...]); the gaps are white
    (1.9, 3.5, [(-ix, -1.55, LBLACK), (-1.3, 1.3, LBLACK), (1.55, ix, LBLACK)]),
    (3.75, 5.35, [(-ix, -1.55, LBLACK), (-1.3, 1.3, LBLACK), (1.55, ix, LBLACK)]),
    (5.6, 8.75, [(-ix, -1.55, LBLACK), (-1.3, ix, ART)]),
    (9.0, 10.1, [(-ix, ix, RED)]),
]
yprev = ly0
for y0, y1, segs in rows:
    tile([(-lx, yprev), (lx, yprev), (lx, y0), (-lx, y0)], WHITE)      # strip below the row
    xprev = -lx
    for x0, x1, c in segs:
        tile([(xprev, y0), (x0, y0), (x0, y1), (xprev, y1)], WHITE)
        tile([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], c)
        xprev = x1
    tile([(xprev, y0), (lx, y0), (lx, y1), (xprev, y1)], WHITE)
    yprev = y1
tile([(-lx, yprev), (lx, yprev), (lx, ly1), (-lx, ly1)], WHITE)

pool = sorted({p for pts, _ in tiles for p in pts})
for pts, c in tiles:
    face(pts, ZL, c, 1, pool)
m.extrude_xy(split([(-lx, ly0), (lx, ly0), (lx, ly1), (-lx, ly1)], pool), ZF, ZL, WHITE, front=False, back=False)

# a little accent in the picture box (a sun / character blob), slightly raised
m.decal_xy([(1.9, 6.6), (3.3, 6.6), (3.3, 8.0), (1.9, 8.0)], ZL, ART2, lift=0.04)

print(m.stats())
print(m.save())
