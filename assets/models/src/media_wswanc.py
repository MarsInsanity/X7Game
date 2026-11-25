# SPDX-License-Identifier: GPL-3.0-or-later
"""WonderSwan Color cartridge: the clear (transparent) Color-only cart,
standing upright, label to +Z, connector edge at y = 0.

Real size about 6.4 x 4.3 x 0.6 cm (the grip lip along the top 0.8 cm
thick). The cart is landscape: its row of edge contacts runs along the long
bottom edge. It slides down into the bay on the back of the WonderSwan with
its label facing out (away from the player), the grip lip along the top
staying at the console's top edge.

Signature features: the clear shell (Color-only games came in transparent
carts, the mono ones in black) with the green board and its chips showing
through the back, the thicker grip lip along the top with finger ridges,
the big landscape label filling the front (the game's picture), the
chamfered bottom corners and the gold contacts at the bottom of the back.

Insertion shape (what the console's bay must take):
  * the slab: x -3.2 .. 3.2, y 0 .. 3.6, z -0.30 .. 0.30 (bottom corners
    chamfered 0.25), a clean closed block; the label sits in a 0.05 deep
    recess in its front, the contacts are 0.02 cm decals on its back
  * the grip lip: y 3.6 .. 4.3, z -0.30 .. 0.50 (flush with the back, it
    sticks out 0.2 cm on the label side), rounded top corners (r 0.35), two
    finger ridges on its front up to z 0.56
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

CLEAR = (178, 204, 222)      # clear shell, front / back faces (pale, slightly cyan)
CLEAR_E = (112, 140, 166)    # shell sides, grip ridges (darker so edges read)
THROUGH = (124, 164, 150)    # board seen through the clear front around the label
PCB_SEEN = (92, 146, 116)    # circuit board seen through the clear back
PCB = (30, 108, 60)          # bare board behind the contacts
CHIP = (36, 36, 46)          # chips seen through the back
GOLD = (226, 186, 70)        # edge contacts
LABEL = (238, 236, 228)      # label paper (also the picture's fallback)

W, H = 6.4, 4.3
X0, X1 = -W / 2, W / 2
CH = 0.25                    # chamfer at the bottom corners
GY = 3.6                     # grip lip starts here
R = 0.35                     # rounded top corners
ZB, ZR, ZF = -0.30, 0.30, 0.25   # back, front, label floor (recess 0.05)
GZF = 0.50                   # grip lip front
CX, CY = 2.75, 0.6           # contacts strip on the back (half width, height)
PY0, PY1 = 0.8, 3.4          # board window seen through the back
LX0, LX1, LY0, LY1 = -2.95, 2.95, 0.35, 3.4   # label recess on the front
B = 0.09                     # paper border around the picture

m = Model('wswanc', 'media')

TOP = [p for p in Model.rounded_rect(X0, GY - 1, X1, H, R, segments=2) if p[1] > GY + 1e-6]  # (X1,H-R)..(X0,H-R)
SIDE_Y = sorted({CH, CY, LY0, PY0, PY1, LY1, GY})
OUTLINE = ([(X0 + CH, 0), (-CX, 0), (CX, 0), (X1 - CH, 0)] + [(X1, y) for y in SIDE_Y] + TOP +
           [(X0, y) for y in reversed(SIDE_Y)])


def on_edges(poly, pts):
    """insert every point of pts lying inside an edge of poly (no T-junctions)"""
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        out.append(a)
        dx, dy = b[0] - a[0], b[1] - a[1]
        l2 = dx * dx + dy * dy
        mid = []
        for p in pts:
            t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2
            if 1e-6 < t < 1 - 1e-6:
                cx, cy = a[0] + t * dx - p[0], a[1] + t * dy - p[1]
                if cx * cx + cy * cy < 1e-10:
                    mid.append((t, p))
        out += [p for t, p in sorted(set(mid))]
    return out


def faces(tiles, z, nz):
    """tile a flat face at depth z facing nz; tiles = [(pts, colour)]"""
    allp = {p for pts, c in tiles for p in pts} | set(OUTLINE)
    for pts, c in tiles:
        m.polygon([(x, y, z) for x, y in on_edges(pts, allp)], c, normal=(0, 0, nz))


# ---- shell: the whole outline (slab + lip) from the back to the front plane
m.extrude_xy(OUTLINE, ZB, ZR, CLEAR, front=False, back=False, side=CLEAR_E)

# ---- back: clear frame, contacts strip, board window (flush with the slab back)
faces([
    ([(X0 + CH, 0), (-CX, 0), (-CX, CY), (X0, CY), (X0, CH)], CLEAR),
    ([(-CX, 0), (CX, 0), (CX, CY), (-CX, CY)], PCB),
    ([(CX, 0), (X1 - CH, 0), (X1, CH), (X1, CY), (CX, CY)], CLEAR),
    ([(X0, CY), (-CX, CY), (-CX, PY0), (-CX, PY1), (X0, PY1)], CLEAR),
    ([(CX, CY), (X1, CY), (X1, PY1), (CX, PY1), (CX, PY0)], CLEAR),
    ([(-CX, CY), (CX, CY), (CX, PY0), (-CX, PY0)], CLEAR),
    ([(-CX, PY0), (CX, PY0), (CX, PY1), (-CX, PY1)], PCB_SEEN),
    ([(X0, PY1), (-CX, PY1), (CX, PY1), (X1, PY1)] + TOP, CLEAR),
], ZB, -1)
def back_decal(pts, c):
    m.polygon([(x, y, ZB - 0.02) for x, y in pts], c, normal=(0, 0, -1))


# chips on the board, seen through the clear plastic
for x0, y0, x1, y1 in ((-2.2, 1.35, -0.3, 2.85), (0.4, 1.6, 1.6, 2.6)):
    back_decal([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], CHIP)
# gold edge contacts
n = 8
pitch = (2 * CX - 0.2) / n
for i in range(n):
    x0 = -CX + 0.1 + i * pitch + 0.06
    x1 = x0 + pitch - 0.12
    back_decal([(x0, 0.0), (x1, 0.0), (x1, CY - 0.12), (x0, CY - 0.12)], GOLD)

# ---- front of the slab: board seen through the clear rim around the label
faces([
    ([(X0 + CH, 0), (X1 - CH, 0), (X1, CH), (X1, LY0), (LX1, LY0), (LX0, LY0), (X0, LY0), (X0, CH)], THROUGH),
    ([(X0, LY0), (LX0, LY0), (LX0, LY1), (X0, LY1)], THROUGH),
    ([(LX1, LY0), (X1, LY0), (X1, LY1), (LX1, LY1)], THROUGH),
    ([(X0, LY1), (LX0, LY1), (LX1, LY1), (X1, LY1), (X1, GY), (X0, GY)], THROUGH),
], ZR, 1)

# ---- label recess: walls, paper floor, the game's picture
m.polygon([(LX0, LY0, ZF), (LX1, LY0, ZF), (LX1, LY0, ZR), (LX0, LY0, ZR)], CLEAR_E, normal=(0, 1, 0))
m.polygon([(LX0, LY1, ZF), (LX1, LY1, ZF), (LX1, LY1, ZR), (LX0, LY1, ZR)], CLEAR_E, normal=(0, -1, 0))
m.polygon([(LX0, LY0, ZF), (LX0, LY1, ZF), (LX0, LY1, ZR), (LX0, LY0, ZR)], CLEAR_E, normal=(1, 0, 0))
m.polygon([(LX1, LY0, ZF), (LX1, LY1, ZF), (LX1, LY1, ZR), (LX1, LY0, ZR)], CLEAR_E, normal=(-1, 0, 0))
m.polygon([(LX0, LY0, ZF), (LX1, LY0, ZF), (LX1, LY1, ZF), (LX0, LY1, ZF)], LABEL, normal=(0, 0, 1))
m.image_xy(LX0 + B, LY0 + B, LX1 - B, LY1 - B, ZF, fallback=LABEL, lift=0.02)

# ---- grip lip: sticks out 0.2 cm on the label side along the top
grip = [(X1, GY)] + TOP + [(X0, GY)]
m.polygon([(x, y, GZF) for x, y in grip], CLEAR, normal=(0, 0, 1))
m.quad((X0, GY, ZR), (X1, GY, ZR), (X1, GY, GZF), (X0, GY, GZF), CLEAR_E)            # underside, faces -Y
for i in range(len(TOP) - 1):
    (xa, ya), (xb, yb) = TOP[i], TOP[i + 1]
    m.quad((xa, ya, ZR), (xb, yb, ZR), (xb, yb, GZF), (xa, ya, GZF), CLEAR_E)
for x, nx in ((X1, 1), (X0, -1)):
    m.polygon([(x, GY, ZR), (x, GY, GZF), (x, H - R, GZF), (x, H - R, ZR)], CLEAR_E, normal=(nx, 0, 0))
# finger ridges on the lip
for i in range(2):
    y = GY + 0.14 + i * 0.26
    m.box(X0 + 0.45, y, GZF, X1 - 0.45, y + 0.12, GZF + 0.06, CLEAR_E, faces={'back': None})

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
