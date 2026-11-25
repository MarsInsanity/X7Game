# SPDX-License-Identifier: GPL-3.0-or-later
"""Game Boy cartridge (grey DMG cart), standing upright, label to +Z.

Real size ~5.7 x 6.5 x 0.8 cm. Signature features: the cut-off top-right
corner, the recessed front label framed by a raised rim, the raised arrow
plate above the label, the horizontal grip ridges below it, and the dark
connector opening with gold contacts at the bottom of the back.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

GREY = (156, 156, 162)       # shell
GREY_D = (118, 118, 126)     # grip ridges, shell edges in shade
GREY_L = (190, 190, 196)     # raised arrow plate
ARROW = (70, 70, 78)         # embossed arrow
LABEL = (236, 232, 218)      # label paper
ART = (70, 130, 210)         # label artwork area
BAND = (210, 50, 50)         # label title band
DARK = (36, 36, 42)          # connector opening, screw
GOLD = (232, 190, 70)        # contacts

W, H = 5.7, 6.5
X0, X1 = -W / 2, W / 2
CUT = 0.55                   # size of the cut-off top-right corner
ZB, ZF, ZR = -0.4, 0.3, 0.4  # back, recessed front, raised rim

LX0, LX1 = -2.3, 2.3         # label recess
LY0, LY1 = 1.35, 5.15

m = Model('gb', 'media')

# shell core (front face is the floor of the label recess)
outline = [(X0, 0), (X1, 0), (X1, H - CUT), (X1 - CUT, H), (X0, H)]
m.extrude_xy(outline, ZB, ZF, GREY)

# raised rim around the label recess
m.box(X0, 0, ZF, X1, LY0, ZR, GREY, faces={'back': None, 'bottom': None})            # bottom band
m.box(X0, LY0, ZF, LX0, LY1, ZR, GREY, faces={'back': None})                         # left strip
m.box(LX1, LY0, ZF, X1, LY1, ZR, GREY, faces={'back': None})                         # right strip
top = [(X0, LY1), (X1, LY1), (X1, H - CUT), (X1 - CUT, H), (X0, H)]
m.extrude_xy(top, ZF, ZR, GREY, back=False)                                          # top band

# label: paper, artwork window, title band
m.decal_xy([(LX0 + 0.12, LY0 + 0.1), (LX1 - 0.12, LY0 + 0.1), (LX1 - 0.12, LY1 - 0.1), (LX0 + 0.12, LY1 - 0.1)], ZF, LABEL, lift=0.05)
m.decal_xy([(LX0 + 0.35, LY0 + 0.95), (LX1 - 0.35, LY0 + 0.95), (LX1 - 0.35, LY1 - 0.45), (LX0 + 0.35, LY1 - 0.45)], ZF, ART, lift=0.1)
m.decal_xy([(LX0 + 0.35, LY0 + 0.35), (LX1 - 0.35, LY0 + 0.35), (LX1 - 0.35, LY0 + 0.7), (LX0 + 0.35, LY0 + 0.7)], ZF, BAND, lift=0.1)

# raised arrow plate above the label, with a down-pointing arrow on its left
PY0, PY1 = LY1 + 0.25, H - 0.3
m.box(X0 + 0.35, PY0, ZR, X1 - CUT - 0.35, PY1, ZR + 0.06, GREY_L, faces={'back': None})
ay = (PY0 + PY1) / 2
m.decal_xy([(-2.2, ay + 0.3), (-1.4, ay + 0.3), (-1.8, ay - 0.3)], ZR + 0.06, ARROW, lift=0.04)

# grip ridges below the label
for i in range(4):
    y = 0.22 + i * 0.27
    m.box(-2.1, y, ZR, 2.1, y + 0.12, ZR + 0.07, GREY_D, faces={'back': None})

# back: connector opening with gold contacts, screw
def back_rect(x0, y0, x1, y1, z, col):
    m.polygon([(x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z)], col, normal=(0, 0, -1))

back_rect(-2.45, 0.0, 2.45, 0.85, ZB - 0.02, DARK)
back_rect(-2.25, 0.1, 2.25, 0.6, ZB - 0.06, GOLD)
for i in range(1, 16):
    x = -2.25 + i * 4.5 / 16
    back_rect(x - 0.04, 0.1, x + 0.04, 0.6, ZB - 0.1, DARK)
m.cylinder_z(0, 3.6, 0.22, ZB - 0.05, ZB, DARK, segments=6, front=False)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
