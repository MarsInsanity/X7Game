# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega CD / Mega-CD (first model, front-loading tray): low-poly console model.

The unit on its own: a black low box (~30 x 10 x 31 cm). Signature parts:
the long motorised CD tray across the front (dark slot around a lighter
tray face), the eject button with the access lights beside it on the front
right, a raised front deck with grooves and a lower flat seat behind it
where the console sits (with guide rails at both edges), the grey metal
connector plate on the right side, vent slots on both sides, and the
ports on the back.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model, rgb565

BODY = (38, 38, 42)        # the black plastic (lifted so it shades)
DECK = (54, 54, 60)        # raised front deck, a little lighter
SEAT = (26, 26, 30)        # the flat seat for the console, darker
GROOVE = (10, 10, 12)      # grooves, vents, slot shadow
TRAY = (90, 90, 100)        # CD tray face
TRAYLINE = (130, 130, 142) # tray face accent line
BUTTON = (150, 150, 158)   # eject button
PLATE = (172, 176, 184)    # metal connector plate on the right side
LED_G = (40, 220, 60)      # power light
LED_R = (230, 30, 30)      # access light
PORT = (96, 96, 104)       # rear port surrounds
BOTTOM = (20, 20, 22)

W = 30.0                   # width (x -15..15)
ZB, ZF = -15.5, 15.5       # back, front
H_SEAT = 8.9               # seat height (rear part of the top)
H_DECK = 10.2              # raised front deck
Z_STEP = 4.5               # where the deck starts
X0, X1 = -W / 2, W / 2

m = Model('segacd', 'console')

# ---------------------------------------------------------------- body
# side profile (z, y): flat seat at the back, small step up to the front
# deck, chamfered front top edge, a small recess at the front foot
profile = [
    (ZB, 0.0), (ZF - 0.6, 0.0), (ZF - 0.6, 0.7), (ZF, 1.1),
    (ZF, 9.2), (ZF - 0.9, H_DECK), (Z_STEP + 0.5, H_DECK),
    (Z_STEP, H_SEAT), (ZB, H_SEAT),
]
body = m.extrude_yz(profile, X0, X1, BODY)

# recolour: top seat, deck and bottom
for t in body:
    ia, ib, ic, c = m.tris[t]
    ys = [m.verts[i][1] for i in (ia, ib, ic)]
    xs = [m.verts[i][0] for i in (ia, ib, ic)]
    if all(abs(x - xs[0]) < 1e-6 for x in xs):
        continue                                  # side faces keep BODY
    if all(abs(y - H_SEAT) < 1e-6 for y in ys):
        m.tris[t] = (ia, ib, ic, rgb565(*SEAT))
    elif all(abs(y - H_DECK) < 1e-6 for y in ys):
        m.tris[t] = (ia, ib, ic, rgb565(*DECK))
    elif all(abs(y) < 1e-6 for y in ys):
        m.tris[t] = (ia, ib, ic, rgb565(*BOTTOM))

# ---------------------------------------------------------------- top
# guide rails either side of the seat
m.box(X0, H_SEAT, ZB, X0 + 0.8, H_SEAT + 0.8, Z_STEP, BODY, faces={'bottom': None})
m.box(X1 - 0.8, H_SEAT, ZB, X1, H_SEAT + 0.8, Z_STEP, BODY, faces={'bottom': None})
# grooves across the front deck
for z in (7.2, 9.4, 11.6):
    m.decal_xz([(X0 + 2.0, z), (X1 - 2.0, z), (X1 - 2.0, z - 0.45), (X0 + 2.0, z - 0.45)],
               H_DECK, GROOVE, lift=0.03)
# shallow seat outline (where the console's feet go)
for x in (-11.0, 11.0):
    for z in (-11.0, 1.0):
        m.decal_xz([(x - 1.2, z + 1.2), (x + 1.2, z + 1.2), (x + 1.2, z - 1.2), (x - 1.2, z - 1.2)],
                   H_SEAT, GROOVE, lift=0.03)

# ---------------------------------------------------------------- front
FZ = ZF
# tray opening (dark slot) and the tray face sitting in it
m.decal_xy([(-13.6, 4.4), (6.6, 4.4), (6.6, 8.6), (-13.6, 8.6)], FZ, GROOVE, lift=0.03)
m.box(-13.2, 4.8, FZ, 6.2, 8.2, FZ + 0.35, TRAY, faces={'back': None})
m.decal_xy([(-12.6, 7.35), (5.6, 7.35), (5.6, 7.65), (-12.6, 7.65)], FZ + 0.35, TRAYLINE, lift=0.03)
# finger notch at the tray's lower edge
m.decal_xy([(-4.4, 4.8), (-1.6, 4.8), (-2.0, 5.5), (-4.0, 5.5)], FZ + 0.35, GROOVE, lift=0.03)
# eject button and access lights on the right
m.decal_xy([(8.6, 4.9), (12.6, 4.9), (12.6, 7.1), (8.6, 7.1)], FZ, GROOVE, lift=0.03)
m.box(8.9, 5.2, FZ, 12.3, 6.8, FZ + 0.5, BUTTON, faces={'back': None})
m.decal_xy([(9.0, 7.7), (10.0, 7.7), (10.0, 8.3), (9.0, 8.3)], FZ, LED_G, lift=0.04)
m.decal_xy([(11.2, 7.7), (12.2, 7.7), (12.2, 8.3), (11.2, 8.3)], FZ, LED_R, lift=0.04)
# a groove along the lower front band
m.decal_xy([(X0 + 1.0, 2.6), (X1 - 1.0, 2.6), (X1 - 1.0, 3.0), (X0 + 1.0, 3.0)], FZ, GROOVE, lift=0.03)


# ---------------------------------------------------------------- sides
def decal_side(x, sign, rect, color, lift=0.03):
    z0, y0, z1, y1 = rect
    xx = x + sign * lift
    pts = [(xx, y0, z0), (xx, y0, z1), (xx, y1, z1), (xx, y1, z0)]
    return m.polygon(pts, color, normal=(sign, 0, 0))


for sign, x in ((-1, X0), (1, X1)):
    # vent slots towards the front of each side
    for k in range(6):
        z = 3.0 + k * 1.6
        decal_side(x, sign, (z, 2.0, z + 0.7, 7.6), GROOVE)

# metal connector plate on the right side, rear top (links to the console)
m.box(X1, 5.6, -11.0, X1 + 0.25, 9.0, 0.5, PLATE, faces={'left': None})
decal_side(X1 + 0.25, 1, (-9.5, 6.6, -1.0, 7.6), PORT)

# ---------------------------------------------------------------- back
for x0, x1, y0, y1, col in ((-12.0, -7.0, 3.5, 6.5, PORT), (-5.0, -2.5, 3.5, 5.0, PORT),
                            (8.0, 12.0, 4.0, 6.0, PORT)):
    m.polygon([(x1, y0, ZB - 0.03), (x0, y0, ZB - 0.03), (x0, y1, ZB - 0.03), (x1, y1, ZB - 0.03)],
              col, normal=(0, 0, -1))
m.polygon([(-8.0, 4.4, ZB - 0.06), (-11.0, 4.4, ZB - 0.06), (-11.0, 5.6, ZB - 0.06), (-8.0, 5.6, ZB - 0.06)],
          GROOVE, normal=(0, 0, -1))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
