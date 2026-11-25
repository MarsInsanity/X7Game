# SPDX-License-Identifier: GPL-3.0-or-later
"""Atari 7800 ProSystem: low-poly console model.

Black wedge (~32 x 7 x 23 cm): low at the front, the top slopes up to a
flat rear deck. Signature features: the brushed-silver band across the
sloping top with thin red and orange accent stripes behind it, the row of
console switches in a recessed strip along the front of the slope (power
slider and pause on the left, select and reset on the right), the
cartridge slot with its spring door on the rear deck, and the two
controller ports on the front face.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

BODY = (34, 34, 38)        # black plastic, lifted a touch so it shades
BOTTOM = (20, 20, 22)
RECESS = (14, 14, 16)      # switch strip recess, port insides
SLOT = (4, 4, 4)           # cartridge slot opening
DOOR = (62, 62, 70)        # slot surround / spring door
CHROME = (206, 210, 218)   # the silver band
CHROME_D = (130, 134, 144) # band edge trim
RED = (214, 40, 30)        # accent stripe
ORANGE = (240, 140, 30)    # accent stripe
SWITCH = (110, 110, 118)   # switch caps
SWITCH_T = (176, 176, 184) # switch cap tops / power knob
PORT = (88, 88, 96)        # controller port surrounds

W = 32.0
X0, X1 = -W / 2, W / 2
ZF, ZB = 11.5, -11.5       # front / back
YF = 3.6                   # front face height (top of the bevel)
ZS0, YS0 = 10.6, 4.1       # start of the slope (after the front bevel)
ZS1, YS1 = -2.5, 7.0       # top of the slope / start of the rear deck
YB = 6.4                   # rear face height (after the rear bevel)

m = Model('atari7800', 'console')

# ---------------------------------------------------------------- body
# slope frame: local (x, h, d) -> world. d runs down the slope towards the
# front (d = 0 at the top of the slope), h along the surface normal.
SL = math.hypot(ZS0 - ZS1, YS1 - YS0)
ANG = math.degrees(math.atan2(YS1 - YS0, ZS0 - ZS1))
CA, SA = math.cos(math.radians(ANG)), math.sin(math.radians(ANG))


def on_slope(p):
    x, h, d = p
    # normal (0, CA, SA); downhill direction (0, -SA, CA)
    return (x, YS1 + h * CA - d * SA, ZS1 + h * SA + d * CA)


def slope_box(x0, d0, x1, d1, h0, h1, color, top=None):
    ids = m.box(x0, h0, d0, x1, h1, d1, color, faces={'top': top or color, 'bottom': None})
    m.transform(ids, on_slope)
    return ids


# The sloping top is built as a grid of coloured cells (no decals, so the
# silver band and stripes can never z-fight with the body).
SW0, SW1 = 8.6, 11.6                       # switch strip (d range)
D_BANDS = [  # (d0, d1, colour across the middle, colour in the switch columns)
    (0.0, 1.0, BODY, None), (1.0, 1.45, ORANGE, None), (1.45, 1.8, BODY, None),
    (1.8, 2.25, RED, None), (2.25, 2.8, BODY, None), (2.8, 3.1, CHROME_D, None),
    (3.1, 7.3, CHROME, None), (7.3, 7.6, CHROME_D, None), (7.6, SW0, BODY, None),
    (SW0, SW1, BODY, RECESS), (SW1, SL, BODY, None),
]
XC = [X0, -14.6, -5.4, 5.4, 14.6, X1]
for d0, d1, col, swcol in D_BANDS:
    for i in range(len(XC) - 1):
        xa, xb = XC[i], XC[i + 1]
        c = swcol if (swcol and i in (1, 3)) else col
        m.quad(on_slope((xa, 0, d1)), on_slope((xb, 0, d1)), on_slope((xb, 0, d0)), on_slope((xa, 0, d0)), c)

# side panels: the wedge profile, with every slope break so the edges meet
# the top cells exactly (no T-junction cracks)
slope_pts = [on_slope((0, 0, d))[1:] for d in sorted({d for b in D_BANDS for d in b[:2]})]
prof = [(ZF, 0.0), (ZF, YF)] + [(z, y) for y, z in reversed(slope_pts)] + [(ZB + 0.8, YS1), (ZB, YB), (ZB, 0.0)]
for x, nx in ((X1, 1), (X0, -1)):
    m.polygon([(x, y, z) for z, y in prof], BODY, normal=(nx, 0, 0))

# front face with a thin silver trim line, front bevel, rear deck, rear bevel, back, bottom
for y0, y1, c in ((0.0, 3.05, BODY), (3.05, 3.3, CHROME_D), (3.3, YF, BODY)):
    m.quad((X0, y0, ZF), (X1, y0, ZF), (X1, y1, ZF), (X0, y1, ZF), c)
m.quad((X0, YF, ZF), (X1, YF, ZF), (X1, YS0, ZS0), (X0, YS0, ZS0), BODY)
m.quad((X0, YS1, ZS1), (X1, YS1, ZS1), (X1, YS1, ZB + 0.8), (X0, YS1, ZB + 0.8), BODY)
m.quad((X0, YS1, ZB + 0.8), (X1, YS1, ZB + 0.8), (X1, YB, ZB), (X0, YB, ZB), BODY)
m.quad((X1, 0, ZB), (X0, 0, ZB), (X0, YB, ZB), (X1, YB, ZB), BODY)
m.quad((X0, 0, ZB), (X1, 0, ZB), (X1, 0, ZF), (X0, 0, ZF), BOTTOM)

# power: a slider knob in a dark track (far left); pause next to it
m.polygon([on_slope((x, 0.06, d)) for x, d in ((-14.0, 10.6), (-11.0, 10.6), (-11.0, 9.6), (-14.0, 9.6))],
          SLOT, normal=(0, CA, SA))
slope_box(-13.9, 9.3, -12.4, 10.9, 0.0, 0.55, SWITCH_T)
slope_box(-9.8, 9.1, -6.2, 11.1, 0.0, 0.45, SWITCH, top=SWITCH_T)
# select and reset on the right
slope_box(6.2, 9.1, 9.8, 11.1, 0.0, 0.45, SWITCH, top=SWITCH_T)
slope_box(10.8, 9.1, 14.4, 11.1, 0.0, 0.45, SWITCH, top=SWITCH_T)

# back panel connectors: channel switch, TV out, power jack
for x0, x1, y0, y1, c in ((-10.5, -8.5, 2.0, 3.4, SWITCH), (-6.0, -4.0, 1.8, 3.6, PORT), (8.0, 10.0, 1.8, 3.6, PORT)):
    m.polygon([(x1, y0, ZB - 0.04), (x0, y0, ZB - 0.04), (x0, y1, ZB - 0.04), (x1, y1, ZB - 0.04)], c, normal=(0, 0, -1))

# ---------------------------------------------------------------- cartridge slot (rear deck)
SX0, SX1, SZ0, SZ1 = -6.2, 6.2, -9.6, -3.4
m.box(SX0, YS1 - 0.1, SZ0, SX1, YS1 + 0.6, SZ1, DOOR, faces={'bottom': None})
m.decal_xz([(-5.2, -4.6), (5.2, -4.6), (5.2, -8.4), (-5.2, -8.4)], YS1 + 0.6, RECESS)
# the spring door: two halves meeting at the slot line
m.decal_xz([(-4.7, -5.0), (4.7, -5.0), (4.7, -6.35), (-4.7, -6.35)], YS1 + 0.6, DOOR, lift=0.06)
m.decal_xz([(-4.7, -6.65), (4.7, -6.65), (4.7, -8.0), (-4.7, -8.0)], YS1 + 0.6, DOOR, lift=0.06)
m.decal_xz([(-4.7, -6.35), (4.7, -6.35), (4.7, -6.65), (-4.7, -6.65)], YS1 + 0.6, SLOT, lift=0.06)

# ---------------------------------------------------------------- controller ports (front face)
for cx in (-11.2, -5.4):
    cy = 1.75
    # D-shaped (trapezoid) port surround, standing proud of the face
    sur = [(cx - 1.9, cy + 0.85), (cx + 1.9, cy + 0.85), (cx + 1.5, cy - 0.85), (cx - 1.5, cy - 0.85)]
    m.extrude_xy(sur, ZF - 0.1, ZF + 0.35, PORT, back=False)
    ins = [(cx - 1.4, cy + 0.5), (cx + 1.4, cy + 0.5), (cx + 1.1, cy - 0.5), (cx - 1.1, cy - 0.5)]
    m.decal_xy(ins, ZF + 0.35, RECESS)

print(m.stats())
m.save()
