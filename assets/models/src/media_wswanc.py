# SPDX-License-Identifier: GPL-3.0-or-later
"""WonderSwan Color cartridge: the clear (transparent) Color-only cart,
standing upright, label to +Z, connector edge at y = 0.

Real size about 6.4 x 4.4 x 0.65 cm (the grip end about 0.9 cm thick). The
cart is landscape: its single row of 48 edge contacts (1.25 mm pitch, about
6 cm) runs along the long bottom edge. Signature features: the smoky clear
shell (Color-only games came in transparent carts, the mono ones in black),
the green circuit board and its chips showing through the back, the thicker
rounded grip end along the top with finger ridges, the big label filling the
front with a four-colour logo strip, the chamfered bottom corners and the
exposed gold contacts at the bottom of the back.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

CLEAR = (186, 210, 226)      # clear shell (pale, slightly cyan), front / back faces
THROUGH = (132, 172, 160)    # board seen through the clear plastic (front, above the label)
CLEAR_E = (118, 146, 170)    # shell sides and grip ridges (darker so edges read)
PCB_SEEN = (98, 150, 120)    # circuit board seen through the clear back
PCB = (32, 112, 64)          # bare board behind the contacts
CHIP = (38, 38, 48)          # chips seen through the back
GOLD = (226, 186, 70)        # edge contacts
LABEL = (240, 238, 230)      # label paper
SKY = (72, 136, 224)         # artwork, upper
GROUND = (236, 132, 40)      # artwork, lower
RED = (220, 48, 56)          # four-colour logo strip
YELLOW = (244, 208, 40)
GREEN = (64, 180, 84)

W, H = 6.4, 4.4
X0, X1 = -W / 2, W / 2
CH = 0.3                     # chamfer at the bottom corners
GY = 3.65                    # grip end starts here
ZB, ZF, ZR = -0.30, 0.27, 0.35   # back, label floor, front rim
GZB, GZF = -0.42, 0.50       # grip end back / front
CX, CY = 2.75, 0.62          # contacts strip on the back (half width, height)
PY0, PY1 = 0.95, 3.4         # board window seen through the back (half width CX)
LX0, LX1, LY0, LY1 = -2.9, 2.9, 0.62, 3.4   # label recess on the front

m = Model('wswanc', 'media')


def face(pts, z, color, nz=1):
    """flat face at depth z facing +Z (nz = 1) or -Z (nz = -1)"""
    return m.polygon([(x, y, z) for x, y in pts], color, normal=(0, 0, nz))


# Every face that meets another along an edge carries the same vertices on
# that edge (no T-junctions), so the software rasteriser leaves no cracks.

# ---- body: one slab from the back to the front rim, sides only
body = [(X0 + CH, 0), (-CX, 0), (CX, 0), (X1 - CH, 0), (X1, CH), (X1, CY), (X1, LY1), (X1, GY),
        (X0, GY), (X0, LY1), (X0, CY), (X0, CH)]
m.extrude_xy(body, ZB, ZR, CLEAR, front=False, back=False, side=CLEAR_E)

# ---- back face, tiled: clear frame, board window, contacts strip
face([(X0 + CH, 0), (-CX, 0), (-CX, CY), (X0, CY), (X0, CH)], ZB, CLEAR, -1)
face([(CX, 0), (X1 - CH, 0), (X1, CH), (X1, CY), (CX, CY)], ZB, CLEAR, -1)
face([(X0, CY), (-CX, CY), (-CX, PY0), (-CX, PY1), (-CX, GY), (X0, GY), (X0, LY1)], ZB, CLEAR, -1)
face([(CX, CY), (X1, CY), (X1, LY1), (X1, GY), (CX, GY), (CX, PY1), (CX, PY0)], ZB, CLEAR, -1)
face([(-CX, CY), (CX, CY), (CX, PY0), (-CX, PY0)], ZB, CLEAR, -1)
face([(-CX, PY1), (CX, PY1), (CX, GY), (-CX, GY)], ZB, CLEAR, -1)
face([(-CX, PY0), (CX, PY0), (CX, PY1), (-CX, PY1)], ZB, PCB_SEEN, -1)
face([(-CX, 0), (CX, 0), (CX, CY), (-CX, CY)], ZB, PCB, -1)
# chips inside, seen through the clear plastic (small, so a lift is safe)
face([(-2.3, 1.45), (-0.2, 1.45), (-0.2, 2.95), (-2.3, 2.95)], ZB - 0.03, CHIP, -1)
face([(0.5, 1.7), (1.6, 1.7), (1.6, 2.7), (0.5, 2.7)], ZB - 0.03, CHIP, -1)
face([(1.95, 1.25), (2.35, 1.25), (2.35, 1.65), (1.95, 1.65)], ZB - 0.03, GOLD, -1)   # crystal
# gold edge contacts
n = 8
pitch = (2 * CX - 0.2) / n
for i in range(n):
    x0 = -CX + 0.1 + i * pitch + 0.05
    face([(x0, 0.0), (x0 + pitch - 0.1, 0.0), (x0 + pitch - 0.1, CY - 0.15), (x0, CY - 0.15)], ZB - 0.03, GOLD, -1)

# ---- front: clear rim around the label recess (front faces at ZR)
face([(X0 + CH, 0), (-CX, 0), (CX, 0), (X1 - CH, 0), (X1, CH), (X1, LY0), (LX1, LY0), (LX0, LY0),
      (X0, LY0), (X0, CH)], ZR, CLEAR)
face([(X0, LY0), (LX0, LY0), (LX0, LY1), (X0, LY1)], ZR, CLEAR)
face([(LX1, LY0), (X1, LY0), (X1, LY1), (LX1, LY1)], ZR, CLEAR)
face([(X0, LY1), (LX0, LY1), (LX1, LY1), (X1, LY1), (X1, GY), (X0, GY)], ZR, THROUGH)

# ---- grip end along the top: thicker, rounded top corners, finger ridges
R = 0.4
top = [p for p in Model.rounded_rect(X0, GY - 1, X1, H, R, segments=2) if p[1] > GY]   # (X1,H-R) .. (X0,H-R)
grip = [(X1, GY)] + top + [(X0, GY)]
face(grip, GZF, CLEAR)
face(grip, GZB, CLEAR, -1)
for i in range(len(top) - 1):
    (xa, ya), (xb, yb) = top[i], top[i + 1]
    m.quad((xa, ya, GZF), (xa, ya, GZB), (xb, yb, GZB), (xb, yb, GZF), CLEAR_E)
zs = (GZB, ZB, ZR, GZF)
for x, nx in ((X1, 1), (X0, -1)):
    yt = H - R
    m.polygon([(x, GY, z) for z in zs] + [(x, yt, GZF), (x, yt, GZB)], CLEAR_E, normal=(nx, 0, 0))
m.polygon([(X1, GY, z) for z in zs] + [(X0, GY, z) for z in reversed(zs)], CLEAR_E, normal=(0, -1, 0))
for i in range(2):
    y = GY + 0.16 + i * 0.27
    m.box(X0 + 0.35, y, GZF, X1 - 0.35, y + 0.13, GZF + 0.07, CLEAR_E, faces={'back': None})
m.box(X0 + 0.6, GY + 0.25, GZB - 0.07, X1 - 0.6, GY + 0.4, GZB, CLEAR_E, faces={'front': None})

# ---- label filling the recess, tiled: paper frame, artwork, logo strip
ax0, ax1, ay0, ay1 = LX0 + 0.25, LX1 - 0.25, LY0 + 0.25, LY1 - 0.65
hy = 1.45                                    # horizon of the artwork
# recess walls (carry the label's edge vertices)
m.polygon([(LX0, LY0, ZF), (LX1, LY0, ZF), (LX1, LY0, ZR), (LX0, LY0, ZR)], CLEAR_E, normal=(0, 1, 0))
m.polygon([(LX0, LY1, ZF), (LX1, LY1, ZF), (LX1, LY1, ZR), (LX0, LY1, ZR)], CLEAR_E, normal=(0, -1, 0))
for x, nx in ((LX0, 1), (LX1, -1)):
    m.polygon([(x, y, ZF) for y in (LY0, ay0, ay1, LY1)] + [(x, LY1, ZR), (x, LY0, ZR)], CLEAR_E, normal=(nx, 0, 0))
face([(LX0, LY0), (LX1, LY0), (LX1, ay0), (ax1, ay0), (ax0, ay0), (LX0, ay0)], ZF, LABEL)
face([(LX0, ay1), (ax0, ay1), (ax1, ay1), (LX1, ay1), (LX1, LY1), (LX0, LY1)], ZF, LABEL)
face([(LX0, ay0), (ax0, ay0), (ax0, hy), (ax0, ay1), (LX0, ay1)], ZF, LABEL)
face([(ax1, ay0), (LX1, ay0), (LX1, ay1), (ax1, ay1), (ax1, hy)], ZF, LABEL)
face([(ax0, ay0), (ax1, ay0), (ax1, hy), (ax0, hy)], ZF, GROUND)
face([(ax0, hy), (ax1, hy), (ax1, ay1), (ax0, ay1)], ZF, SKY)
# four-colour logo strip on the paper above the artwork (small raised tiles)
ly0, ly1 = ay1 + 0.18, LY1 - 0.15
for i, c in enumerate((RED, YELLOW, GREEN, SKY)):
    x0 = -2.45 + i * 0.5
    m.box(x0, ly0, ZF, x0 + 0.42, ly1, ZF + 0.03, c, faces={'back': None, 'bottom': None, 'top': None,
                                                         'left': None, 'right': None})
# a sun and a hill in the artwork (thin, small)
m.cylinder_z(1.6, 2.2, 0.35, ZF, ZF + 0.03, YELLOW, segments=8, back=False, side=False)
face([(-2.1, hy), (-0.3, hy), (-1.2, 2.15)], ZF + 0.03, GREEN)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
