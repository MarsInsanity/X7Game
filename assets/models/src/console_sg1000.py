# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega SG-1000 (1983): low-poly console model for the X7 Game frontend.

A flat, wide off-white console with a charcoal sloped front deck, a raised
top-loading cartridge slot in the middle of the top, groove vents either
side of it, a red pause button and red trim, and the hardwired black
joystick (red fire buttons) sitting beside it on the table.
Units cm, Y up, front +Z, origin at the bottom centre.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

WHITE = (236, 233, 222)      # case
WHITE_SH = (196, 192, 180)   # underside lip / back panel
CHAR = (58, 60, 66)          # sloped front deck, slot plateau
BLACK = (18, 18, 22)         # slot opening, joystick, vents
GREY = (128, 130, 136)       # vent grooves, switch
RED = (214, 30, 36)          # pause button, trim, fire buttons
RED_DK = (140, 16, 20)       # button sides

m = Model('sg1000', 'console')

# ---------------------------------------------------------------- body
W = 13.0                     # half width (26 cm wide)
ZF, ZB = 8.0, -8.0           # front / back (16 cm deep)
H = 4.6                      # top height
ZS = 4.0                     # where the slope meets the flat top
HF = 1.6                     # height of the front edge

# lower plinth: a slightly inset darker base band so the case "floats"
m.box(-W + 0.3, 0, ZB + 0.3, W - 0.3, 0.5, ZF - 0.3, WHITE_SH, faces={'top': None})
# main shell: side profile extruded across the width
prof = [(ZF, 0.5), (ZF, HF), (ZS, H), (ZB, H), (ZB, 0.5)]
m.extrude_yz(prof, -W, W, WHITE)

import math  # noqa: E402

ANG = math.degrees(math.atan2(H - HF, ZF - ZS))      # slope angle
LS = math.hypot(H - HF, ZF - ZS)                     # slope length


def slope_box(x0, x1, t0, t1, h, col, faces=None):
    """A thin raised block lying on the sloped front deck (t = 0 at the
    front edge, 1 at the crease), h cm proud of the surface. Real relief
    instead of flat decals keeps the big slope free of z-fighting."""
    f = {'bottom': None}
    f.update(faces or {})
    ids = m.box(x0, -0.05, -t1 * LS, x1, h, -t0 * LS, col, faces=f)
    m.transform(ids, lambda q: Model.move(0, HF, ZF)(Model.rot_x(ANG)(q)))
    return ids


# charcoal deck panel over the slope (white margins at the sides), with a
# red trim strip along its front edge
slope_box(-W + 0.8, W - 0.8, 0.12, 0.9, 0.25, CHAR)
slope_box(-W + 0.8, W - 0.8, 0.02, 0.12, 0.25, RED, faces={'back': None})
# raised vent ribs on the left part of the deck
for i in range(4):
    t = 0.22 + i * 0.16
    slope_box(-W + 1.8, -4.5, t, t + 0.07, 0.45, BLACK)
# red pause button and a black reset/power-lamp block on the right
slope_box(6.4, 8.6, 0.42, 0.66, 0.7, RED, faces={'left': RED_DK, 'right': RED_DK, 'back': RED_DK, 'front': RED_DK})
slope_box(3.0, 5.0, 0.46, 0.62, 0.45, BLACK)

# ---------------------------------------------------------------- top
# charcoal plateau in the middle of the top, cartridge slot housing on it
m.box(-6.5, H, -5.9, 6.5, H + 0.5, 2.6, CHAR, faces={'bottom': None})
m.box(-4.8, H + 0.5, -3.9, 4.8, H + 1.6, -0.2, CHAR, faces={'bottom': None})
m.decal_xz([(-4.0, -2.8), (4.0, -2.8), (4.0, -1.4), (-4.0, -1.4)], H + 1.6, BLACK, lift=0.03)
# grooved vents on the flat top, either side of the plateau
for side in (-1, 1):
    for i in range(5):
        z0 = -6.6 + i * 1.6
        xa, xb = side * 7.4, side * 11.6
        m.decal_xz([(min(xa, xb), z0 + 0.7), (max(xa, xb), z0 + 0.7), (max(xa, xb), z0), (min(xa, xb), z0)],
                   H, GREY, lift=0.03)
# red trim stripe across the top just behind the slope crease
m.decal_xz([(-W + 0.8, ZS - 0.3), (W - 0.8, ZS - 0.3), (W - 0.8, ZS - 0.8), (-W + 0.8, ZS - 0.8)], H, RED, lift=0.03)

# ---------------------------------------------------------------- back
# power switch and RF / power sockets on the back
m.box(6.0, 2.2, ZB - 0.4, 8.0, 3.2, ZB, BLACK, faces={'front': None})
m.box(-9.0, 2.0, ZB - 0.3, -7.6, 3.4, ZB, GREY, faces={'front': None})
m.box(-6.4, 2.0, ZB - 0.3, -5.0, 3.4, ZB, GREY, faces={'front': None})

# ---------------------------------------------------------------- joystick
# hardwired joystick on the table beside the console's right side, its
# cable running into the side of the case
JX, JZ = 18.0, 3.5
base = [(-3.0, -3.0), (3.0, -3.0), (3.0, 3.0), (-3.0, 3.0)]
m.prism([(JX + x, JZ + z) for x, z in base], 0, 2.4, BLACK, top=(40, 40, 46))
# red fire buttons on the two front corners of the base top
for bx in (-1.9, 1.9):
    m.cylinder(JX + bx, JZ + 2.0, 0.6, 2.4, 2.8, RED, segments=8, side=RED_DK)
# stick shaft and grip
m.cylinder(JX, JZ - 0.3, 0.35, 2.4, 6.0, BLACK, segments=6)
m.cylinder(JX, JZ - 0.3, 0.75, 6.0, 8.2, (40, 40, 46), segments=8, top=BLACK)
# cable: a thin dark run from the base back to the console front
m.box(W, 0, JZ - 2.2, JX - 3.0, 0.35, JZ - 1.8, BLACK, faces={'bottom': None})

# ---------------------------------------------------------------- centre it
# move the whole set so its bounding box is centred on x = 0, z = 0, then
# drop the stale vertices transform() leaves behind (so stats() is exact)
used = sorted({i for t in m.tris for i in t[:3]})
xs = [m.verts[i][0] for i in used]
zs = [m.verts[i][2] for i in used]
dx, dz = -(min(xs) + max(xs)) / 2, -(min(zs) + max(zs)) / 2
m.transform(list(range(len(m.tris))), Model.move(dx, 0, dz))
used = sorted({i for t in m.tris for i in t[:3]})
remap = {o: n for n, o in enumerate(used)}
m.verts = [m.verts[o] for o in used]
m.tris = [(remap[a], remap[b], remap[c], col) for a, b, c, col in m.tris]

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
