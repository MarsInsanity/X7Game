# SPDX-License-Identifier: GPL-3.0-or-later
"""Game Boy Advance cartridge (grey GBA cart), standing upright, label to +Z.

Real size ~5.7 x 3.45 x 0.8 cm. Signature features: the wide, short shell
with the gently arched top edge, the large recessed front label filling
most of the face, the light grey strip above it under the arch, the small
locking notches in both sides near the bottom, the thicker bump across the
top of the back (the grip that sticks out of the console), and the exposed
gold contacts along the bottom of the back.

The front face is built as a mosaic of non-overlapping pieces (frame, label
paper, artwork, title band) rather than decals: the frontend interpolates
depth affinely, and on an object this small, close to the camera, thin
decals would fight with the face below them.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

GREY = (128, 128, 138)       # shell
GREY_D = (88, 88, 98)        # bump underside, recess walls
GREY_L = (172, 172, 182)     # raised strip above the label
LABEL = (232, 228, 214)      # label paper
ART = (60, 110, 200)         # label artwork area
BAND = (230, 170, 40)        # label title band
DARK = (34, 34, 40)          # connector opening
GOLD = (214, 172, 64)        # contacts

W, H = 5.7, 3.45
X0, X1 = -W / 2, W / 2
HS = 3.1                     # height at the sides; the top arches up to H
ZB, ZF = -0.3, 0.3           # back and front of the main (thin) body
ZBB = -0.5                   # back of the top bump (total depth 0.8)
ZL = ZF - 0.06               # floor of the label recess
BY = 2.35                    # bottom of the back bump
NY0, NY1, ND = 0.35, 0.75, 0.18   # side notches: y range and depth
LX0, LX1, LY0, LY1 = -2.45, 2.45, 0.25, 2.55   # label recess
SY, SD = 2.75, 0.18          # light strip above the label: bottom, gap below the arch

m = Model('gba', 'media')


def top_y(x):
    """height of the arched top edge at x (shallow parabolic arch)"""
    t = x / X1
    return HS + (H - HS) * (1 - t * t)


AX = [X1, X1 - ND, LX1] + [X1 - W * i / 8 for i in range(1, 8)] + [LX0, X0 + ND, X0]
AX = sorted(set(round(x, 4) for x in AX), reverse=True)
ARC = [(x, top_y(x)) for x in AX]              # right to left along the top

# ---- shell: sides, top, back (front face built below)
outline = [(X0, 0), (X1, 0),
           (X1, NY0), (X1 - ND, NY0), (X1 - ND, NY1), (X1, NY1)] + ARC + [
           (X0, NY1), (X0 + ND, NY1), (X0 + ND, NY0), (X0, NY0)]
m.extrude_xy(outline, ZB, ZF, GREY, front=False)


def front_rect(x0, y0, x1, y1, z, col):
    m.quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), col)


# ---- front frame around the label recess
for (xa, ya), (xb, yb) in zip(ARC[:-1], ARC[1:]):          # xa > xb
    if xb >= X1 - ND - 1e-6 or xa <= X0 + ND + 1e-6:        # notch columns
        front_rect(xb, 0, xa, NY0, ZF, GREY)
        m.quad((xb, NY1, ZF), (xa, NY1, ZF), (xa, ya, ZF), (xb, yb, ZF), GREY)
    elif xb >= LX1 - 1e-6 or xa <= LX0 + 1e-6:              # beside the label
        m.quad((xb, 0, ZF), (xa, 0, ZF), (xa, ya, ZF), (xb, yb, ZF), GREY)
    else:                                                   # above / below the label
        front_rect(xb, 0, xa, LY0, ZF, GREY)
        # above the label: grey, the light strip following the arch, grey rim
        sa, sb = ya - SD, yb - SD
        front_rect(xb, LY1, xa, SY, ZF, GREY)
        m.quad((xb, SY, ZF), (xa, SY, ZF), (xa, sa, ZF), (xb, sb, ZF), GREY_L)
        m.quad((xb, sb, ZF), (xa, sa, ZF), (xa, ya, ZF), (xb, yb, ZF), GREY)

# recess walls (facing into the recess)
m.polygon([(LX0, LY0, ZF), (LX1, LY0, ZF), (LX1, LY0, ZL), (LX0, LY0, ZL)], GREY_D, normal=(0, 1, 0))
m.polygon([(LX0, LY1, ZF), (LX1, LY1, ZF), (LX1, LY1, ZL), (LX0, LY1, ZL)], GREY_D, normal=(0, -1, 0))
m.polygon([(LX0, LY0, ZF), (LX0, LY1, ZF), (LX0, LY1, ZL), (LX0, LY0, ZL)], GREY_D, normal=(1, 0, 0))
m.polygon([(LX1, LY0, ZF), (LX1, LY1, ZF), (LX1, LY1, ZL), (LX1, LY0, ZL)], GREY_D, normal=(-1, 0, 0))

# label on the recess floor: paper margins, title band, artwork window
AX0, AX1 = LX0 + 0.25, LX1 - 0.25
front_rect(LX0, LY0, AX0, LY1, ZL, LABEL)
front_rect(AX1, LY0, LX1, LY1, ZL, LABEL)
rows = [(LY0, LY0 + 0.2, LABEL), (LY0 + 0.2, LY0 + 0.5, BAND), (LY0 + 0.5, LY0 + 0.7, LABEL),
        (LY0 + 0.7, LY1 - 0.22, ART), (LY1 - 0.22, LY1, LABEL)]
for y0, y1, col in rows:
    front_rect(AX0, y0, AX1, y1, ZL, col)

# ---- back bump: the top part of the shell is thicker
bump = [(X0, BY), (X1, BY)] + ARC
m.extrude_xy(bump, ZBB, ZB, GREY, front=False)
# sloped underside of the bump, darker so the step reads from behind
m.extrude_yz([(ZB, BY - 0.3), (ZB, BY), (ZBB, BY)], X0, X1, GREY_D)


# ---- back: dark connector opening with gold contacts along the bottom edge
def back_rect(x0, y0, x1, y1, z, col):
    m.polygon([(x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z)], col, normal=(0, 0, -1))


back_rect(-2.35, 0.0, 2.35, 0.7, ZB - 0.03, DARK)
back_rect(-2.2, 0.08, 2.2, 0.55, ZB - 0.07, GOLD)
for i in range(1, 10):
    x = -2.2 + i * 4.4 / 10
    back_rect(x - 0.04, 0.08, x + 0.04, 0.55, ZB - 0.11, DARK)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
