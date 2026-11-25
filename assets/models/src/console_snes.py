# SPDX-License-Identifier: GPL-3.0-or-later
"""Super Nintendo Entertainment System (North American model), low poly.

Boxy light-grey body (24 x 20 cm, ~7.5 cm tall) with a stepped front, a
raised central hump holding the cartridge slot, purple power / reset sliders
and the purple eject lever in front of the slot, a red power LED, ribbed
ventilation ridges on the left and right of the top and along the side
walls, two controller ports on the front.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (198, 198, 206)      # light grey shell
HUMP = (178, 178, 190)      # slightly darker grey of the cartridge hump
RIB = (150, 150, 162)       # ridges
DARK = (78, 78, 90)         # port surrounds, slider tracks
SLOT = (24, 24, 30)         # cartridge opening, port holes
PURPLE = (108, 78, 168)     # eject lever, sliders
LED = (220, 30, 30)
BASE = (170, 170, 180)      # lower tier front band

m = Model('snes', 'console')

W = 12.0                    # half width
# ---------------------------------------------------------------- main body
# side profile (z, y): lower tier at the front, stepped upper tier, slight
# chamfer at the back top edge
body = [(-10.0, 0.0), (10.0, 0.0), (10.0, 2.8), (9.6, 3.2), (9.2, 3.2),
        (9.2, 5.5), (8.7, 6.0), (-9.5, 6.0), (-10.0, 5.5)]
m.extrude_yz(body, -W, W, BODY)
# lower tier front face in a slightly darker tone (re-paint by a decal)
m.decal_xy([(-W + 0.02, 0.15), (W - 0.02, 0.15), (W - 0.02, 2.75), (-W + 0.02, 2.75)], 10.0, BASE)

# ---------------------------------------------------------------- hump
HX = 7.0
hump = [(-8.6, 6.0), (5.6, 6.0), (4.9, 7.3), (-8.0, 7.3), (-8.6, 6.8)]
m.extrude_yz(hump, -HX, HX, HUMP)
TOP = 7.3
# cartridge slot: dark frame + black opening
m.decal_xz([(-5.4, -5.8), (5.4, -5.8), (5.4, -1.9), (-5.4, -1.9)], TOP, DARK, lift=0.02)
m.decal_xz([(-4.9, -5.3), (4.9, -5.3), (4.9, -2.4), (-4.9, -2.4)], TOP, SLOT, lift=0.06)
# eject lever just in front of the slot: a tab with a sloped front
m.extrude_yz([(-1.5, TOP), (0.9, TOP), (0.5, TOP + 0.55), (-1.5, TOP + 0.55)],
             -1.1, 1.1, PURPLE)
# power (left) and reset (right) sliders in dark tracks
for x0 in (-6.2, 3.4):
    m.decal_xz([(x0, 1.0), (x0 + 2.8, 1.0), (x0 + 2.8, 3.4), (x0, 3.4)], TOP, DARK)
sx = -5.9                                   # power slider sits to the left
m.box(sx, TOP, 1.4, sx + 1.3, TOP + 0.55, 3.0, PURPLE, faces={'bottom': None})
sx = 3.7                                    # reset slider
m.box(sx, TOP, 1.4, sx + 1.3, TOP + 0.55, 3.0, PURPLE, faces={'bottom': None})
# red power LED near the front left of the hump
m.decal_xz([(-6.4, 3.8), (-5.5, 3.8), (-5.5, 4.5), (-6.4, 4.5)], TOP, LED, lift=0.04)

# ---------------------------------------------------------------- ridges
# ribs on the top surface, left and right of the hump, running front-back
for side in (-1, 1):
    for k in range(4):
        xa = side * (8.0 + k * 0.95)
        xb = xa + side * 0.45
        x0, x1 = min(xa, xb), max(xa, xb)
        m.box(x0, 6.0, -8.6, x1, 6.3, 7.6, RIB, faces={'bottom': None})
    # horizontal ridges along the side wall of the upper tier
    for k in range(3):
        y0 = 3.6 + k * 0.6
        xs = side * W
        xo = side * (W + 0.15)
        x0, x1 = min(xs, xo), max(xs, xo)
        face = 'left' if side > 0 else 'right'   # the face touching the wall
        m.box(x0, y0, -9.2, x1, y0 + 0.3, 8.8, RIB, faces={face: None})

# ---------------------------------------------------------------- ports
for cx in (-2.9, 2.9):
    # SNES port: a pill with one flat side
    outline = Model.rounded_rect(cx - 1.4, 0.75, cx + 1.4, 2.15, 0.6, segments=2)
    m.extrude_xy(outline, 10.0, 10.2, DARK, back=False)
    m.decal_xy([(cx - 1.0, 1.05), (cx + 1.0, 1.05), (cx + 1.0, 1.85), (cx - 1.0, 1.85)], 10.2, SLOT)

# back: A/V and power connector area
m.polygon([(6.0, 1.0, -10.02), (-6.0, 1.0, -10.02), (-6.0, 3.4, -10.02), (6.0, 3.4, -10.02)],
          DARK, normal=(0, 0, -1))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
