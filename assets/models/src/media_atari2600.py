# SPDX-License-Identifier: GPL-3.0-or-later
"""Atari 2600 cartridge: black shell standing upright, label to +Z,
connector end at y = 0. Signature features: black plastic slab, horizontal
grip ribs across the top of the front, a silver-framed picture label with a
black title band and a red stripe, the end label on the top edge, and the
dust door across the bottom of the front with its seam."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (30, 30, 34)        # black plastic (front / back)
EDGE = (62, 62, 70)         # side / top faces, so the outline reads
RIDGE = (96, 96, 106)       # grip ribs
DOOR = (46, 46, 52)         # dust door
SEAM = (10, 10, 12)         # door seam
SILVER = (196, 196, 206)    # label frame, end label
LBLACK = (16, 16, 20)       # title band
RED = (216, 40, 32)         # stripe
SKY = (240, 128, 40)        # picture: sky
GROUND = (48, 72, 176)      # picture: ground
SUN = (248, 220, 64)        # picture accent

m = Model('atari2600', 'media')

W, H, D = 8.5, 10.0, 2.3
hw = W / 2
ZF, ZB = D / 2, -D / 2
CT, CB = 0.45, 0.2          # top / bottom corner chamfers


GY, GT = 7.5, 0.25          # grip end: starts at height GY, steps out GT

# ---- shell: a chamfered slab (side edges split at GY so the grip block
# meets them without a T-junction crack)
outline = [(-hw + CB, 0), (hw - CB, 0), (hw, CB), (hw, GY), (hw, H - CT), (hw - CT, H),
           (-hw + CT, H), (-hw, H - CT), (-hw, GY), (-hw, CB)]
m.extrude_xy(outline, ZB, ZF, SHELL, side=EDGE)

# ---- thicker grip end: the top of the shell steps out front and back
grip = [(-hw, GY), (hw, GY), (hw, H - CT), (hw - CT, H), (-hw + CT, H), (-hw, H - CT)]
m.extrude_xy(grip, ZF, ZF + GT, SHELL, back=False, side=EDGE)
m.extrude_xy(grip, ZB - GT, ZB, SHELL, front=False, side=EDGE)

# end label on the top edge
m.decal_xz([(-hw + CT + 0.3, -0.95), (hw - CT - 0.3, -0.95), (hw - CT - 0.3, 0.95), (-hw + CT + 0.3, 0.95)],
           H, SILVER, lift=0.03)

# ---- grip ribs across the grip end, front and back
for i in range(5):
    y = 7.75 + i * 0.42
    m.box(-hw + 0.35, y, ZF + GT, hw - 0.35, y + 0.2, ZF + GT + 0.14, RIDGE,
          faces={'back': None, 'bottom': None})
    m.box(-hw + 0.35, y, ZB - GT - 0.12, hw - 0.35, y + 0.2, ZB - GT, RIDGE,
          faces={'front': None, 'bottom': None})

# ---- dust door across the bottom of the front, with its seam above
DX = hw - 0.45
m.box(-DX, 0.0, ZF, DX, 1.45, ZF + 0.06, DOOR, faces={'back': None, 'bottom': None})
m.box(-DX, 1.45, ZF, DX, 1.6, ZF + 0.02, SEAM, faces={'back': None, 'bottom': None, 'top': None})
# finger notch on the door
m.decal_xy([(-1.2, 0.55), (1.2, 0.55), (1.2, 0.8), (-1.2, 0.8)], ZF + 0.06, SEAM, lift=0.03)

# ---- label: thin raised slab, its face tiled into the silver frame, the
# picture and the title bands. Every row is split at x = 0 and no strip is
# thinner than 0.2 cm, so no triangle is a long sliver (those crack in a
# software rasteriser); tiles share the vertices along their edges.
lx, ly0, ly1 = 3.75, 2.2, 7.35
ZL = ZF + 0.06
fx = lx - 0.25                      # inner edge of the silver frame
rows = [  # (y0, y1, [(x0, x1, colour), ...]) covering -lx..lx
    (ly0, 2.45, [(-lx, lx, SILVER)]),
    (2.45, 4.0, [(-lx, -fx, SILVER), (-fx, fx, GROUND), (fx, lx, SILVER)]),
    (4.0, 5.75, [(-lx, -fx, SILVER), (-fx, fx, SKY), (fx, lx, SILVER)]),
    (5.75, 6.0, [(-lx, lx, SILVER)]),
    (6.0, 6.85, [(-lx, lx, LBLACK)]),
    (6.85, 7.13, [(-lx, lx, RED)]),
    (7.13, ly1, [(-lx, lx, SILVER)]),
]
tiles = []
for y0, y1, segs in rows:
    for x0, x1, c in segs:
        xs = [x0] + ([0.0] if x0 < 0.0 < x1 else []) + [x1]
        for xa, xb in zip(xs, xs[1:]):
            tiles.append(([(xa, y0), (xb, y0), (xb, y1), (xa, y1)], c))
pool = sorted({p for pts, _ in tiles for p in pts})


def split(pts):
    """insert every pool point lying strictly inside one of the polygon's
    edges (no T-junction cracks between neighbouring tiles)"""
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


for pts, c in tiles:
    m.polygon([(x, y, ZL) for x, y in split(pts)], c, normal=(0, 0, 1))
m.extrude_xy(split([(-lx, ly0), (lx, ly0), (lx, ly1), (-lx, ly1)]), ZF, ZL, SILVER, front=False, back=False)

# picture accents (small, so a lifted decal is safe): a sun and a mountain
m.decal_xy([(1.3, 4.6), (2.5, 4.6), (2.5, 5.5), (1.3, 5.5)], ZL, SUN, lift=0.04)
m.decal_xy([(-3.1, 3.7), (-0.3, 3.7), (-1.7, 5.15)], ZL, GROUND, lift=0.04)

print(m.stats())
print(m.save())
