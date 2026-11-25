# SPDX-License-Identifier: GPL-3.0-or-later
"""Neo Geo Pocket cartridge (small black card), standing upright, label to +Z.

Real size ~4.0 x 4.3 x 0.7 cm. Signature features: the small, almost square
black shell with rounded top corners, the thick grip lip across the top with
horizontal grooves, the large label filling most of the front (silver frame,
artwork window, dark title band), the locking notches in both side edges,
and the dark connector slot along the bottom of the back.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model
import math

SHELL = (58, 58, 66)         # black plastic shell
SHELL_L = (96, 96, 108)       # grip lip top / ridges catching light
GROOVE = (16, 16, 20)        # grooves, connector slot
FRAME = (196, 198, 206)      # silver label frame
ART = (230, 120, 40)         # label artwork window
SKY = (70, 150, 220)         # artwork second area
BAND = (24, 24, 28)          # dark title band on the label
RED = (210, 40, 40)          # small accent stripe
GOLD = (220, 180, 70)        # contacts

W, H = 4.0, 4.3
X0, X1 = -W / 2, W / 2
ZB, ZF = -0.3, 0.25          # body back, body front
LIP_Y = 3.45                 # grip lip starts here
ZL0, ZL1 = -0.35, 0.35       # grip lip is thicker than the body
R = 0.35                     # top corner radius
NY0, NY1, ND = 0.55, 0.95, 0.15   # side locking notch

m = Model('ngp', 'media')

# body: outline with side notches near the bottom, up to the lip
body = [(X0, 0), (X1, 0), (X1, NY0), (X1 - ND, NY0 + 0.08), (X1 - ND, NY1 - 0.08), (X1, NY1),
        (X1, LIP_Y), (X0, LIP_Y),
        (X0, NY1), (X0 + ND, NY1 - 0.08), (X0 + ND, NY0 + 0.08), (X0, NY0)]
m.extrude_xy(body, ZB, ZF, SHELL, back=False)

# grip lip: thicker top section with rounded top corners
lip = [(X0, LIP_Y), (X1, LIP_Y), (X1, H - R), (X1 - R + R * math.cos(math.radians(45)), H - R + R * math.sin(math.radians(45))),
       (X1 - R, H), (X0 + R, H), (X0 + R - R * math.cos(math.radians(45)), H - R + R * math.sin(math.radians(45))), (X0, H - R)]
m.extrude_xy(lip, ZL0, ZL1, SHELL, side=SHELL)

# lighter top face of the lip (where a finger pulls the card out)
m.decal_xz([(X0 + R, ZL1), (X1 - R, ZL1), (X1 - R, ZL0), (X0 + R, ZL0)], H, SHELL_L, lift=0.005)

# grooves across the front of the lip
for i in range(3):
    y = LIP_Y + 0.2 + i * 0.2
    m.decal_xy([(X0 + 0.3, y), (X1 - 0.3, y), (X1 - 0.3, y + 0.08), (X0 + 0.3, y + 0.08)], ZL1, GROOVE, lift=0.02)

# label on the front of the body
LX0, LX1, LY0, LY1 = -1.7, 1.7, 0.3, LIP_Y - 0.15
m.decal_xy([(LX0, LY0), (LX1, LY0), (LX1, LY1), (LX0, LY1)], ZF, FRAME, lift=0.03)
m.decal_xy([(LX0 + 0.2, LY0 + 0.75), (LX1 - 0.2, LY0 + 0.75), (LX1 - 0.2, LY1 - 0.2), (LX0 + 0.2, LY1 - 0.2)], ZF, SKY, lift=0.06)
m.decal_xy([(LX0 + 0.2, LY0 + 0.75), (LX1 - 0.2, LY0 + 0.75), (LX1 - 0.2, LY0 + 1.5), (LX0 + 0.2, LY0 + 1.5)], ZF, ART, lift=0.09)
m.decal_xy([(LX0 + 0.2, LY0 + 0.2), (LX1 - 0.2, LY0 + 0.2), (LX1 - 0.2, LY0 + 0.6), (LX0 + 0.2, LY0 + 0.6)], ZF, BAND, lift=0.06)
m.decal_xy([(LX0 + 0.2, LY0 + 0.62), (LX1 - 0.2, LY0 + 0.62), (LX1 - 0.2, LY0 + 0.7), (LX0 + 0.2, LY0 + 0.7)], ZF, RED, lift=0.06)

# back: connector slot along the bottom with gold contacts
def back_rect(x0, y0, x1, y1, z, col):
    m.polygon([(x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z)], col, normal=(0, 0, -1))

back_rect(-1.5, 0.0, 1.5, 0.45, ZB - 0.02, GROOVE)
back_rect(-1.35, 0.06, 1.35, 0.32, ZB - 0.05, GOLD)
for i in range(1, 10):
    x = -1.35 + i * 2.7 / 10
    back_rect(x - 0.04, 0.06, x + 0.04, 0.32, ZB - 0.08, GROOVE)

# back face built in pieces around a lighter middle area, so no large
# shell triangle sits behind it (linear depth interpolation would let it
# poke through a thin decal)
SX0, SX1, SY0, SY1 = -1.55, 1.55, 1.1, LIP_Y - 0.25
m.polygon([(x, y, ZB) for x, y in [(X0, 0), (X1, 0), (X1, NY0), (X1 - ND, NY0 + 0.08), (X1 - ND, NY1 - 0.08),
                                     (X1, NY1), (X1, SY0), (X0, SY0), (X0, NY1), (X0 + ND, NY1 - 0.08),
                                     (X0 + ND, NY0 + 0.08), (X0, NY0)]], SHELL, normal=(0, 0, -1))
back_rect(X0, SY0, SX0, SY1, ZB, SHELL)
back_rect(SX1, SY0, X1, SY1, ZB, SHELL)
back_rect(X0, SY1, X1, LIP_Y, ZB, SHELL)
back_rect(SX0, SY0, SX1, SY1, ZB, SHELL_L)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
