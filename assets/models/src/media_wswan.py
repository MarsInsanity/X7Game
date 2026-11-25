# SPDX-License-Identifier: GPL-3.0-or-later
"""WonderSwan cartridge (black cart), standing upright, label to +Z.

Real size ~4.4 x 6.3 x 0.65 cm (the grip end ~0.9 cm thick). Signature
features: the small dark slab, the thicker grip end at the top with its
horizontal finger ridges (the part that stays outside the console), the
large recessed label that fills most of the front, the chamfered corners
at the connector end, and the exposed edge contacts at the bottom of the
back.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (60, 60, 70)         # black-ish shell (light enough to show shading)
SHELL_L = (104, 104, 118)      # grip ridges
SHELL_D = (24, 24, 30)       # connector opening
LABEL = (236, 234, 226)      # label paper
ART = (60, 150, 200)         # label artwork area
ART2 = (240, 200, 60)        # artwork accent
BAND = (200, 40, 50)         # title band
GOLD = (226, 186, 70)        # contacts

W, H = 4.4, 6.3
X0, X1 = -W / 2, W / 2
ZB, ZF, ZR = -0.3, 0.27, 0.35   # back, label recess floor, front rim
GY = 5.2                        # grip end starts here
GZB, GZF = -0.42, 0.48          # grip end back / front
CH = 0.3                        # chamfer at the bottom corners

m = Model('wswan', 'media')

# main slab (front face = floor of the label recess), chamfered bottom corners
body = [(X0 + CH, 0), (X1 - CH, 0), (X1, CH), (X1, GY), (X0, GY), (X0, CH)]
m.extrude_xy(body, ZB, ZF, SHELL)

# raised rim around the label recess
LX0, LX1, LY0, LY1 = -1.9, 1.9, 0.55, 4.95
m.extrude_xy([(X0 + CH, 0), (X1 - CH, 0), (X1, CH), (X1, LY0), (X0, LY0), (X0, CH)],
             ZF, ZR, SHELL, back=False)                                              # bottom band
m.box(X0, LY0, ZF, LX0, LY1, ZR, SHELL, faces={'back': None, 'bottom': None, 'top': None})
m.box(LX1, LY0, ZF, X1, LY1, ZR, SHELL, faces={'back': None, 'bottom': None, 'top': None})
m.box(X0, LY1, ZF, X1, GY, ZR, SHELL, faces={'back': None, 'top': None})               # top band

# grip end: thicker block with rounded top corners
grip = Model.rounded_rect(X0, GY, X1, H, 0.35, segments=2)
grip = [(x, y) for x, y in grip if y > GY - 1e-6]          # keep only the rounded top
grip = [(X1, GY)] + [p for p in grip if p[1] > GY + 1e-6] + [(X0, GY)]
m.extrude_xy(grip, GZB, GZF, SHELL)

# finger ridges across the grip front
for i in range(3):
    y = GY + 0.18 + i * 0.3
    m.box(X0 + 0.3, y, GZF, X1 - 0.3, y + 0.14, GZF + 0.08, SHELL_L, faces={'back': None})

# label: paper, artwork window, accent, title band
m.decal_xy([(LX0 + 0.08, LY0 + 0.08), (LX1 - 0.08, LY0 + 0.08), (LX1 - 0.08, LY1 - 0.08), (LX0 + 0.08, LY1 - 0.08)], ZF, LABEL, lift=0.04)
m.decal_xy([(LX0 + 0.3, LY0 + 0.95), (LX1 - 0.3, LY0 + 0.95), (LX1 - 0.3, LY1 - 0.3), (LX0 + 0.3, LY1 - 0.3)], ZF, ART, lift=0.08)
m.decal_xy([(-0.9, LY0 + 1.3), (0.9, LY0 + 1.3), (0.2, LY0 + 2.6)], ZF, ART2, lift=0.11)
m.decal_xy([(LX0 + 0.3, LY0 + 0.3), (LX1 - 0.3, LY0 + 0.3), (LX1 - 0.3, LY0 + 0.65), (LX0 + 0.3, LY0 + 0.65)], ZF, BAND, lift=0.08)

# back: edge connector opening with gold contacts at the bottom
def back_rect(x0, y0, x1, y1, z, col):
    m.polygon([(x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z)], col, normal=(0, 0, -1))

back_rect(-1.75, 0.0, 1.75, 0.75, ZB - 0.02, SHELL_D)
back_rect(-1.6, 0.05, 1.6, 0.55, ZB - 0.05, GOLD)
# raised back plate (moulded info area)
m.box(-1.6, 1.3, ZB - 0.06, 1.6, 4.6, ZB, SHELL, faces={'front': None})
back_rect(-1.3, 3.6, 1.3, 4.3, ZB - 0.08, SHELL_L)

for i in range(1, 12):
    x = -1.6 + i * 3.2 / 12
    back_rect(x - 0.04, 0.05, x + 0.04, 0.55, ZB - 0.08, SHELL_D)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
