# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega Game Gear cartridge (black), standing upright, label to +Z.

Measured from a straight-on Commons photo (Game_gear_cartridge.jpg), scaled
to the 6.8 cm width (the 5.7 x 4.0 cm label then matches the real label
size): the shell is about as tall as it is wide. Front features, bottom to
top: a raised plain oval near the bottom edge, the landscape label (square
bottom corners, rounded top corners), and above it a recessed grip area
shaped like an upside-down U (it runs a little way down both sides of the
label) with three grip ribs. The back is flat; at the bottom of the back a
notch opens onto the board's gold contacts.

Insertion: the Game Gear takes it top-down into a slot at the back, label
facing the back. The whole shell is one clean block 6.8 x 6.8 x 0.8 cm
(x -3.4..3.4, y 0..6.8, z -0.4..0.4), rounded only at the two top corners;
nothing sticks out of it.
"""
import math
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (44, 44, 50)         # black plastic
FLOOR = (24, 24, 28)         # floor of the grip recess (in shadow)
WALL = (84, 84, 94)          # recess walls (catch the light: draw the U)
OVAL = (70, 70, 78)          # raised plain oval (catches the light)
GRIP = (100, 100, 110)       # grip ribs
RECESS = (12, 12, 14)        # connector notch, between the contacts
LABEL = (226, 226, 220)      # plain label paper (picture fallback)
GOLD = (232, 190, 70)        # contacts

W, H = 6.8, 6.8
X0, X1 = -W / 2, W / 2
ZB = -0.4                    # back
ZF = 0.38                    # front face (the oval rises to 0.40)
ZL = ZF - 0.07               # floor of the label / grip recess
R = 0.35                     # shell top corner radius

LX0, LX1, LY0, LY1, LR = -2.85, 2.85, 1.6, 5.6, 0.3     # label (picture)
UX0, UX1, UY0, UY1, UR = -3.12, 3.12, 4.05, 6.2, 0.5    # upside-down U grip recess


def arc(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def shell_outline():
    return [(X0, 0), (X1, 0)] + arc(X1 - R, H - R, R, 0, 90, 2) + arc(X0 + R, H - R, R, 90, 180, 2)


# recess outline (counter-clockwise): the label rectangle joined to the U
RECESS_PTS = ([(LX0, LY0), (LX1, LY0), (LX1, UY0), (UX1, UY0)]
              + arc(UX1 - UR, UY1 - UR, UR, 0, 90, 2) + arc(UX0 + UR, UY1 - UR, UR, 90, 180, 2)
              + [(UX0, UY0), (LX0, UY0)])

m = Model('gamegear', 'media')

# ---- shell: main slab (front part) + back slab around the connector notch
NX0, NX1, NY = -2.9, 2.9, 0.7        # connector notch, open at the bottom
ZN = ZB + 0.22                       # notch floor: the board's contact face
m.extrude_xy(shell_outline(), ZN, ZF, SHELL, front=False, back=False)
u_shape = [(X0, 0), (NX0, 0), (NX0, NY), (NX1, NY), (NX1, 0)] + shell_outline()[1:]
m.extrude_xy(u_shape, ZB, ZN, SHELL, front=False)
m.polygon([(NX0, 0, ZN), (NX0, NY, ZN), (NX1, NY, ZN), (NX1, 0, ZN)], RECESS, normal=(0, 0, -1))
N_C = 12
pitch = (NX1 - NX0 - 0.3) / N_C
for i in range(N_C):
    x = NX0 + 0.15 + i * pitch + 0.04
    m.polygon([(x, 0.06, ZN - 0.02), (x, NY - 0.12, ZN - 0.02), (x + pitch - 0.08, NY - 0.12, ZN - 0.02),
               (x + pitch - 0.08, 0.06, ZN - 0.02)], GOLD, normal=(0, 0, -1))

# ---- front face around the recess: bottom band + left and right halves
m.polygon([(X0, 0, ZF), (X1, 0, ZF), (X1, LY0, ZF), (X0, LY0, ZF)], SHELL, normal=(0, 0, 1))
left = ([(0, UY1)] + arc(UX0 + UR, UY1 - UR, UR, 90, 180, 2)
        + [(UX0, UY0), (LX0, UY0), (LX0, LY0), (X0, LY0)]
        + arc(X0 + R, H - R, R, 180, 90, 2) + [(0, H)])
right = [(-x, y) for x, y in left]
m.polygon([(x, y, ZF) for x, y in left], SHELL, normal=(0, 0, 1))
m.polygon([(x, y, ZF) for x, y in right], SHELL, normal=(0, 0, 1))

# ---- recess: walls (facing inwards) and floor
n = len(RECESS_PTS)
for i in range(n):
    (xa, ya), (xb, yb) = RECESS_PTS[i], RECESS_PTS[(i + 1) % n]
    # counter-clockwise outline: the inside is on the left, the wall faces it
    m.polygon([(xa, ya, ZL), (xb, yb, ZL), (xb, yb, ZF), (xa, ya, ZF)], WALL, normal=(-(yb - ya), xb - xa, 0))
m.polygon([(x, y, ZL) for x, y in RECESS_PTS], FLOOR, normal=(0, 0, 1))

# ---- the label: the game's picture (rounded top corners like the real one)
label = [(LX0, LY0), (LX1, LY0)] + arc(LX1 - LR, LY1 - LR, LR, 0, 90, 2) + arc(LX0 + LR, LY1 - LR, LR, 90, 180, 2)
m.image_xy(LX0, LY0, LX1, LY1, ZL, fallback=LABEL, lift=0.03, outline=label)

# ---- grip ribs in the U above the label
for i in range(3):
    y = 5.74 + i * 0.15
    m.decal_xy([(-1.7, y), (1.7, y), (1.7, y + 0.07), (-1.7, y + 0.07)], ZL, GRIP, lift=0.03)

# ---- raised plain oval near the bottom edge (no lettering)
OCX, OCY, ORX, ORY = 0.0, 0.8, 1.4, 0.37
oval = [(OCX + ORX * math.cos(2 * math.pi * i / 12), OCY + ORY * math.sin(2 * math.pi * i / 12)) for i in range(12)]
m.extrude_xy(oval, ZF, ZF + 0.02, OVAL, back=False, side=SHELL)


if __name__ == '__main__':
    print(m.stats())
    print(m.save())
