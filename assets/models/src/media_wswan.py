# SPDX-License-Identifier: GPL-3.0-or-later
"""WonderSwan cartridge (black cart), standing upright, label to +Z.

Real size ~4.4 x 6.3 cm, the slab 0.65 cm thick, the grip end 0.9 cm.
Signature features: the small dark slab, the thicker grip end at the top
with its horizontal finger ridges (the part that stays outside the
console), the large recessed label that fills most of the front (the
game's picture), the chamfered corners at the connector end, and the
exposed edge contacts at the bottom of the back.

Insertion: the cart goes into the back of the console connector edge
first (y = 0), label facing the back. The part that enters the slot is
the slab: a closed prism x -2.2..2.2, y 0..5.2, z -0.30..0.35 with
0.3 cm chamfers at the two bottom corners; the back carries only flat
decals (0.02-0.04 cm), the label recess is inside the envelope.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (58, 58, 68)         # black-ish shell (light enough to show shading)
SHELL_L = (110, 110, 124)    # grip ridges
SHELL_M = (84, 84, 96)       # moulded info area on the back
SHELL_D = (20, 20, 26)       # connector opening
LABEL = (236, 234, 226)      # label paper (fallback when there is no picture)
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
LX0, LX1, LY0, LY1 = -1.9, 1.9, 0.5, 5.0
m.extrude_xy([(X0 + CH, 0), (X1 - CH, 0), (X1, CH), (X1, LY0), (X0, LY0), (X0, CH)],
             ZF, ZR, SHELL, back=False)                                              # bottom band
m.box(X0, LY0, ZF, LX0, LY1, ZR, SHELL, faces={'back': None, 'bottom': None, 'top': None})
m.box(LX1, LY0, ZF, X1, LY1, ZR, SHELL, faces={'back': None, 'bottom': None, 'top': None})
m.box(X0, LY1, ZF, X1, GY, ZR, SHELL, faces={'back': None, 'top': None, 'bottom': None})
# the recess' top wall (the bottom wall is the bottom band's side)
m.quad((LX0, LY1, ZF), (LX1, LY1, ZF), (LX1, LY1, ZR), (LX0, LY1, ZR), SHELL)       # faces -Y

# the label: the game's picture fills the whole recess
m.image_xy(LX0, LY0, LX1, LY1, ZF, fallback=LABEL, lift=0.03)

# grip end: thicker block with rounded top corners
grip = Model.rounded_rect(X0, GY, X1, H, 0.35, segments=2)
grip = [(X1, GY)] + [p for p in grip if p[1] > GY + 1e-6] + [(X0, GY)]
m.extrude_xy(grip, GZB, GZF, SHELL)

# finger ridges across the grip front
for i in range(3):
    y = GY + 0.17 + i * 0.3
    m.box(X0 + 0.3, y, GZF, X1 - 0.3, y + 0.14, GZF + 0.08, SHELL_L, faces={'back': None})

# back: moulded info area and the edge connector with gold contacts (flat decals)
def back_rect(x0, y0, x1, y1, z, col):
    m.polygon([(x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z)], col, normal=(0, 0, -1))

back_rect(-1.6, 1.3, 1.6, 4.7, ZB - 0.02, SHELL_M)
back_rect(-1.75, 0.06, 1.75, 0.75, ZB - 0.02, SHELL_D)
for i in range(8):
    x = -1.55 + i * 3.1 / 8
    back_rect(x + 0.05, 0.12, x + 3.1 / 8 - 0.05, 0.6, ZB - 0.04, GOLD)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
