# SPDX-License-Identifier: GPL-3.0-or-later
"""Atari 7800 ProSystem cartridge: plain black shell (8.1 x 10.2 x 2.0 cm)
standing upright, label to +Z, connector edge at y = 0.

Reference photos (Wikimedia Commons, carts in a 7800): the part that stays
above the console is plain, smooth black plastic with a white end label
across the top edge; the picture label sits on the lower front, in a shallow
recess, and disappears into the slot. Details: the chamfered top-front edge
carrying the end label (white, red title bar), the recessed front label (the
game's picture), the connector opening in the bottom with the board edge.

Insertion: straight down into the 7800's top slot, label to the front. The
whole shell is one closed box 8.1 x 10.2 x 2.0 cm (x +-4.05, z +-1.0);
nothing sticks out of it (the label and its picture are recessed)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (30, 30, 34)        # black plastic, front / back
SIDE = (64, 64, 72)         # side walls and top, so the outline reads
RECESS = (14, 14, 16)       # label recess walls / floor
SLOT = (8, 8, 10)           # connector opening
PCB = (40, 110, 60)         # board edge
GOLD = (216, 176, 64)       # contacts
WHITE = (228, 228, 232)     # end label
RED = (200, 36, 32)         # end label title bar
TEXT = (96, 96, 104)        # end label small print
LABEL = (190, 190, 198)     # picture fallback: plain silver label

W, H, D = 8.1, 10.2, 2.0
hw = W / 2
ZF, ZB = D / 2, -D / 2
BV = 0.55                   # top-front chamfer
YB, ZT = H - BV, ZF - BV    # chamfer: from (ZF, YB) up to (ZT, H)
LX, L0, L1 = 3.5, 0.7, 6.1  # front label recess: x +-LX, y L0..L1
ZR = ZF - 0.1               # recess floor
EX = 3.55                   # end label half width
SX, SZ, SD = 3.3, 0.5, 0.6  # connector opening: x +-SX, z +-SZ, depth SD

m = Model('atari7800', 'media')
polys = []                  # (points, colour, normal): T-junctions fixed at the end


def rect_xy(x0, y0, x1, y1, z, color, nz=1):
    polys.append(([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], color, (0, 0, nz)))


def rect_xz(x0, z0, x1, z1, y, color, ny=1):
    polys.append(([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], color, (0, ny, 0)))


# ---------------------------------------------------------------- shell
prof = [(ZB, 0), (ZF, 0), (ZF, YB), (ZT, H), (ZB, H)]       # side profile (z, y)
polys.append(([(hw, y, z) for z, y in prof], SIDE, (1, 0, 0)))
polys.append(([(-hw, y, z) for z, y in prof], SIDE, (-1, 0, 0)))
rect_xy(-hw, 0, hw, H, ZB, SHELL, -1)                       # back

# front, tiled around the label recess
rect_xy(-hw, 0, hw, L0, ZF, SHELL)
rect_xy(-hw, L1, hw, YB, ZF, SHELL)
rect_xy(-hw, L0, -LX, L1, ZF, SHELL)
rect_xy(LX, L0, hw, L1, ZF, SHELL)
# recess walls (facing into the recess) and floor
polys.append(([(-LX, L0, ZF), (-LX, L0, ZR), (LX, L0, ZR), (LX, L0, ZF)], RECESS, (0, 1, 0)))
polys.append(([(-LX, L1, ZF), (LX, L1, ZF), (LX, L1, ZR), (-LX, L1, ZR)], RECESS, (0, -1, 0)))
polys.append(([(-LX, L0, ZF), (-LX, L1, ZF), (-LX, L1, ZR), (-LX, L0, ZR)], RECESS, (1, 0, 0)))
polys.append(([(LX, L0, ZF), (LX, L0, ZR), (LX, L1, ZR), (LX, L1, ZF)], RECESS, (-1, 0, 0)))
rect_xy(-LX, L0, LX, L1, ZR, RECESS)

# top-front chamfer and top: the end label wraps over both
bn = (0, ZF - ZT, H - YB)


def bevel(x0, t0, x1, t1, color):
    def p(x, t):
        return (x, YB + (H - YB) * t, ZF + (ZT - ZF) * t)
    polys.append(([p(x0, t0), p(x1, t0), p(x1, t1), p(x0, t1)], color, bn))


bevel(-hw, 0, -EX, 1, SIDE)
bevel(EX, 0, hw, 1, SIDE)
bevel(-EX, 0, EX, 0.3, WHITE)          # the title (red) faces the player
bevel(-EX, 0.3, EX, 0.68, RED)
bevel(-EX, 0.68, EX, 1, WHITE)
t0, t1 = ZT - 0.3, ZT - 0.5            # a dark text line on the top face
t2 = ZB + 0.2                          # back edge of the end label
for x0, x1 in ((-hw, -EX), (EX, hw)):
    rect_xz(x0, ZB, x1, ZT, H, SIDE)
rect_xz(-EX, ZB, EX, t2, H, SIDE)
rect_xz(-EX, t2, EX, t1, H, WHITE)
rect_xz(-EX, t1, EX, t0, H, TEXT)
rect_xz(-EX, t0, EX, ZT, H, WHITE)

# bottom, tiled around the connector opening
rect_xz(-hw, ZB, hw, -SZ, 0, SHELL, -1)
rect_xz(-hw, SZ, hw, ZF, 0, SHELL, -1)
rect_xz(-hw, -SZ, -SX, SZ, 0, SHELL, -1)
rect_xz(SX, -SZ, hw, SZ, 0, SHELL, -1)
# the opening: a dark pocket
polys.append(([(-SX, 0, -SZ), (SX, 0, -SZ), (SX, SD, -SZ), (-SX, SD, -SZ)], SLOT, (0, 0, 1)))
polys.append(([(-SX, 0, SZ), (-SX, SD, SZ), (SX, SD, SZ), (SX, 0, SZ)], SLOT, (0, 0, -1)))
polys.append(([(-SX, 0, -SZ), (-SX, SD, -SZ), (-SX, SD, SZ), (-SX, 0, SZ)], SLOT, (1, 0, 0)))
polys.append(([(SX, 0, -SZ), (SX, 0, SZ), (SX, SD, SZ), (SX, SD, -SZ)], SLOT, (-1, 0, 0)))
rect_xz(-SX, -SZ, SX, SZ, SD, SLOT, -1)

# ---------------------------------------------------------------- emit panels
# insert every panel corner that lies on another panel's edge, so the
# software renderer shows no hairline cracks at T-junctions
allpts = {p for pts, _, _ in polys for p in pts}


def on_seg(p, a, b):
    ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    ap = (p[0] - a[0], p[1] - a[1], p[2] - a[2])
    l2 = ab[0] ** 2 + ab[1] ** 2 + ab[2] ** 2
    t = (ap[0] * ab[0] + ap[1] * ab[1] + ap[2] * ab[2]) / l2
    if t <= 1e-6 or t >= 1 - 1e-6:
        return None
    d = [ap[i] - ab[i] * t for i in range(3)]
    return t if d[0] ** 2 + d[1] ** 2 + d[2] ** 2 < 1e-8 else None


for pts, c, n in polys:
    out = []
    for i, a in enumerate(pts):
        b = pts[(i + 1) % len(pts)]
        out.append(a)
        mids = []
        for p in allpts:
            t = on_seg(p, a, b)
            if t is not None:
                mids.append((t, p))
        out += [p for _, p in sorted(mids)]
    m.polygon(out, c, normal=n)

# ---------------------------------------------------------------- picture
# the whole front label is the game's picture (upright, u left to right)
m.image_xy(-LX, L0, LX, L1, ZR, fallback=LABEL, lift=0.03)

# ---------------------------------------------------------------- board edge
# the circuit board in the connector opening, contacts along its edge
PX, PT = 3.1, 0.08
m.box(-PX, 0.12, -PT, PX, SD, PT, PCB, faces={'top': None, 'bottom': GOLD})

print(m.stats())
print(m.save())
