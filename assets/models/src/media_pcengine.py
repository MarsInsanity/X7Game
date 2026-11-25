# SPDX-License-Identifier: GPL-3.0-or-later
"""TurboGrafx-16 TurboChip / PC Engine HuCard: a thin credit-card-sized
card (5.4 x 8.5 x 0.3 cm) standing upright, label facing +Z.

As on the real card (and in every photo of one) the gold contact fingers
sit on a black strip along the TOP short edge of the label side, and the
label artwork is upright with its top towards the contacts. The bottom
edge (y = 0) is the finger-grip end, with its ridged "house" grip mark,
which stays outside the console. To insert it, the card is laid flat label
up with the contact edge pointing into the slot (rot X = -90 turns +Y into
-Z), so the player sees the picture the right way up.

The card itself is one clean closed slab (rounded corners r = 0.25); the
contacts, grip and picture are flat areas lifted 0.02-0.04 cm off its
faces. No text or artwork: the picture area shows the game's image."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

W, H, T = 5.4, 8.5, 0.3           # portrait, contacts at the top, grip end at y = 0
X0, X1 = -W / 2, W / 2
Z0, Z1 = -T / 2, T / 2
R = 0.25                          # corner radius

CARD = (222, 224, 230)            # pale silver-white plastic
EDGE = (140, 142, 152)            # card edges
BACK = (176, 178, 188)            # back face
PANEL = (150, 152, 164)           # back: moulded panel
STRIP = (22, 22, 28)              # black strip carrying the contacts
GOLD = (226, 182, 60)             # contact fingers
GRIP = (232, 234, 240)            # raised grip mark
RIDGE = (128, 130, 142)           # grip ridges
LABEL = (52, 64, 132)             # plain label colour (picture fallback)

m = Model('pcengine', 'media')

# the card: a closed rounded slab
m.extrude_xy(Model.rounded_rect(X0, 0.0, X1, H, R, segments=3), Z0, Z1, CARD, back=BACK, side=EDGE)

# front, top: black strip with two groups of gold contact fingers
m.decal_xy([(-2.5, 7.86), (2.5, 7.86), (2.5, 8.38), (-2.5, 8.38)], Z1, STRIP, lift=0.02)
N, GX0, GX1 = 9, 0.1, 2.4       # fingers per group, group spans |x| = GX0..GX1
pitch = (GX1 - GX0) / N
for side in (-1, 1):
    for i in range(N):
        a = GX0 + pitch * i + pitch * 0.12
        b = GX0 + pitch * (i + 1) - pitch * 0.12
        xa, xb = sorted((side * a, side * b))
        m.decal_xy([(xa, 8.02), (xb, 8.02), (xb, 8.32), (xa, 8.32)], Z1, GOLD, lift=0.04)

# front: the label = the game's picture, upright (top towards the contacts)
LX0, LX1, LY0, LY1 = -2.45, 2.45, 1.0, 5.2
m.image_xy(LX0, LY0, LX1, LY1, Z1, fallback=LABEL, lift=0.03,
           outline=Model.rounded_rect(LX0, LY0, LX1, LY1, 0.12, segments=1))

# front, bottom: the ridged finger-grip mark ("house" shape, peak up)
m.decal_xy([(-0.75, 0.14), (0.75, 0.14), (0.75, 0.48), (0.0, 0.72), (-0.75, 0.48)], Z1, GRIP, lift=0.02)
for y in (0.22, 0.34, 0.46):
    m.decal_xy([(-0.6, y), (0.6, y), (0.6, y + 0.05), (-0.6, y + 0.05)], Z1, RIDGE, lift=0.04)

# back: plain card with a moulded panel
m.polygon([(1.9, 2.0, Z0 - 0.02), (-1.9, 2.0, Z0 - 0.02), (-1.9, 6.8, Z0 - 0.02), (1.9, 6.8, Z0 - 0.02)],
          PANEL, normal=(0, 0, -1))

print(m.stats())
m.save()
