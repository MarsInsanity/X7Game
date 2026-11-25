# SPDX-License-Identifier: GPL-3.0-or-later
"""Neo Geo Pocket cartridge (small black card), standing upright, label to +Z.

Real size ~5.7 x 4.6 x 0.6 cm (measured against the console's slot in the
Commons photos: the slot opening on the console's top edge is ~5.9 cm wide,
the bay behind the back window ~6.1 cm). Signature features: the small,
landscape black shell with rounded top corners, the grooved grip band across the top,
the large label filling most of the front (the game's picture), the locking
notches in both side edges near the bottom, and the dark connector opening
with gold contacts along the bottom of the back.

Insertion: the console's slot is on the top of its back; the cartridge goes
straight DOWN into it, label facing the console's back. The shell is one
closed slab of constant thickness (z = -0.3 .. +0.3), so the slot can be a
plain 5.9 x 0.8 cm opening; the connector edge is y = 0.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model
import math

SHELL = (50, 50, 58)          # black plastic shell
PANEL = (74, 74, 84)          # slightly raised panel on the back
SHELL_L = (92, 92, 104)       # top edge catching light
GROOVE = (12, 12, 14)         # grooves, connector opening
RIM = (150, 152, 160)         # thin grey frame round the label
LABEL = (200, 202, 210)       # plain label colour (picture fallback)
GOLD = (220, 180, 70)         # contacts

W, H, D = 5.7, 4.6, 0.6
X0, X1 = -W / 2, W / 2
ZB, ZF = -D / 2, D / 2
R = 0.45                      # top corner radius
NY0, NY1, ND = 0.55, 1.0, 0.15    # side locking notch (height range, depth)

m = Model('ngp', 'media')

# shell: one slab, side notches near the bottom, rounded top corners
outline = [(X0, 0), (X1, 0), (X1, NY0), (X1 - ND, NY0 + 0.08), (X1 - ND, NY1 - 0.08), (X1, NY1)]
for k in range(3):                      # top right corner, 0 .. 90 deg
    a = math.radians(90 * k / 2)
    outline.append((X1 - R + R * math.cos(a), H - R + R * math.sin(a)))
for k in range(3):                      # top left corner, 90 .. 180 deg
    a = math.radians(90 + 90 * k / 2)
    outline.append((X0 + R + R * math.cos(a), H - R + R * math.sin(a)))
outline += [(X0, NY1), (X0 + ND, NY1 - 0.08), (X0 + ND, NY0 + 0.08), (X0, NY0)]
m.extrude_xy(outline, ZB, ZF, SHELL)

# lighter flat top edge (where a finger pulls the card out)
m.decal_xz([(X0 + R, ZF), (X1 - R, ZF), (X1 - R, ZB), (X0 + R, ZB)], H, SHELL_L, lift=0.01)

# grip grooves across the top band of the front
for i in range(3):
    y = 3.95 + i * 0.2
    m.decal_xy([(X0 + 0.45, y), (X1 - 0.45, y), (X1 - 0.45, y + 0.08), (X0 + 0.45, y + 0.08)], ZF, GROOVE, lift=0.02)

# label: thin grey frame, the game's picture inside it
LX0, LX1, LY0, LY1 = -2.3, 2.3, 1.05, 3.75
m.decal_xy([(LX0 - 0.07, LY0 - 0.07), (LX1 + 0.07, LY0 - 0.07), (LX1 + 0.07, LY1 + 0.07), (LX0 - 0.07, LY1 + 0.07)],
           ZF, RIM, lift=0.02)
m.image_xy(LX0, LY0, LX1, LY1, ZF, fallback=LABEL, lift=0.04)

# insertion arrow on the plain band under the label (points down, to the connector)
m.decal_xy([(0, 0.32), (0.32, 0.82), (-0.32, 0.82)], ZF, GROOVE, lift=0.02)

# back: connector opening along the bottom with gold contacts
def back_rect(x0, y0, x1, y1, lift, col):
    z = ZB - lift
    m.polygon([(x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z)], col, normal=(0, 0, -1))

back_rect(-2.2, 0.0, 2.2, 0.5, 0.02, GROOVE)
back_rect(-2.3, 0.85, 2.3, 3.75, 0.02, PANEL)
for i in range(3):                      # grip grooves on the back too
    y = 3.95 + i * 0.2
    back_rect(X0 + 0.45, y, X1 - 0.45, y + 0.08, 0.02, GROOVE)
back_rect(-2.05, 0.06, 2.05, 0.36, 0.035, GOLD)
for i in range(1, 14):
    x = -2.05 + i * 4.1 / 14
    back_rect(x - 0.035, 0.06, x + 0.035, 0.36, 0.05, GROOVE)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
