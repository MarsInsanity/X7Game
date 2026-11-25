# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly SNK Neo Geo Pocket (monochrome, carbon black), handheld, screen
facing +Z.

Real size about 13.0 x 7.6 x 2.8 cm. Signature features: landscape body with
a flat top edge and big rounded bottom grips, grey frame around a nearly
square greenish monochrome LCD in the middle, the clicky micro-switched
joystick (silver cap in an octagonal gate) on the left, round A/B buttons on
the right (A lower left, B upper right), small power and option buttons,
speaker slots, cartridge slot on the top back, battery cover on the back.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (50, 50, 56)         # carbon black shell
FACE = (64, 64, 72)         # front face, a touch lighter
BACK = (36, 36, 40)         # battery cover
FRAME = (104, 106, 116)     # grey frame around the screen
BEZEL = (24, 24, 28)        # black glass around the LCD
SCREEN = (150, 162, 128)    # monochrome LCD, greenish grey
GATE = (20, 20, 24)         # joystick gate
STICK_RIM = (88, 90, 98)    # joystick collar
STICK = (196, 198, 206)     # silver joystick cap
AB = (140, 142, 152)        # A / B buttons
SMALL = (170, 172, 182)     # power / option
HOLE = (14, 14, 16)         # speaker slots, cartridge slot
LED = (230, 60, 50)         # power lamp

m = Model('ngp', 'console')

W, H = 13.0, 7.6
X0, X1 = -W / 2, W / 2
D = 2.5                     # body depth (the battery cover adds 0.3)
COVER = 0.3
ZB, ZF = -D / 2 + COVER / 2, D / 2 + COVER / 2
BEV = 0.3
RT, RB = 1.1, 3.0           # top / bottom corner radii (round grips)
SEG = 4


def outline(x0, y0, x1, y1, rt, rb, seg):
    """Rounded rect with different top and bottom corner radii (CCW)."""
    pts = []
    for cx, cy, r, a0 in ((x1 - rt, y1 - rt, rt, 0), (x0 + rt, y1 - rt, rt, 90),
                          (x0 + rb, y0 + rb, rb, 180), (x1 - rb, y0 + rb, rb, 270)):
        n = seg if r < 2 else seg + 2
        for s in range(n + 1):
            a = math.radians(a0 + 90 * s / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def ring(outer, oz, inner, iz, color):
    """Bevel band between two matching outlines (CCW seen from +Z)."""
    n = len(outer)
    sgn = 1 if iz > oz else -1
    for i in range(n):
        a, b = outer[i], outer[(i + 1) % n]
        c, d = inner[(i + 1) % n], inner[i]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nrm = (dy / l, -dx / l, sgn * 1.0)
        m.polygon([(a[0], a[1], oz), (b[0], b[1], oz), (c[0], c[1], iz), (d[0], d[1], iz)], color, normal=nrm)


# ---------------------------------------------------------------- body
outer = outline(X0, 0, X1, H, RT, RB, SEG)
inner = outline(X0 + BEV, BEV, X1 - BEV, H - BEV, RT - BEV, RB - BEV, SEG)
m.extrude_xy(outer, ZB + BEV, ZF - BEV, BODY, front=False, back=False)
ring(outer, ZF - BEV, inner, ZF, FACE)
ring(outer, ZB + BEV, inner, ZB, BODY)
m.polygon([(x, y, ZF) for x, y in inner], FACE, normal=(0, 0, 1))
m.polygon([(x, y, ZB) for x, y in inner], BODY, normal=(0, 0, -1))

# battery cover on the lower back
m.extrude_xy(Model.rounded_rect(-3.6, 0.6, 3.6, 4.4, 0.8, 2), ZB - COVER, ZB + 0.05, BACK, front=False)

# ---------------------------------------------------------------- front
SX = -0.25                  # screen centre x (a touch left of the middle)
m.decal_xy(Model.rounded_rect(SX - 3.0, 1.15, SX + 3.0, 7.0, 0.55, 2), ZF, FRAME, lift=0.02)
m.decal_xy([(SX - 2.6, 1.5), (SX + 2.6, 1.5), (SX + 2.6, 6.65), (SX - 2.6, 6.65)], ZF, BEZEL, lift=0.04)
m.decal_xy([(SX - 2.0, 2.1), (SX + 2.0, 2.1), (SX + 2.0, 5.9), (SX - 2.0, 5.9)], ZF, SCREEN, lift=0.06)

# joystick: octagonal gate, collar, silver cap
JX, JY = -4.75, 3.9
gate = [(JX + 1.05 * math.cos(math.radians(22.5 + 45 * i)), JY + 1.05 * math.sin(math.radians(22.5 + 45 * i)))
        for i in range(8)]
m.decal_xy(gate, ZF, GATE, lift=0.03)
m.cylinder_z(JX, JY, 0.72, ZF - 0.05, ZF + 0.22, STICK_RIM, segments=8, back=False)
m.cylinder_z(JX, JY, 0.55, ZF + 0.15, ZF + 0.55, STICK, segments=8, back=False)
m.cylinder_z(JX, JY, 0.36, ZF + 0.5, ZF + 0.68, STICK, segments=8, back=False)   # domed top

# A (lower left) and B (upper right)
m.cylinder_z(4.15, 3.35, 0.62, ZF - 0.05, ZF + 0.3, AB, segments=10, back=False)
m.cylinder_z(5.35, 4.45, 0.62, ZF - 0.05, ZF + 0.3, AB, segments=10, back=False)

# power (top right) and option (beside it)
m.cylinder_z(5.25, 6.45, 0.3, ZF - 0.05, ZF + 0.14, SMALL, segments=6, back=False)
m.cylinder_z(3.95, 6.45, 0.22, ZF - 0.05, ZF + 0.12, SMALL, segments=6, back=False)
m.decal_xy([(-4.95, 6.4), (-4.6, 6.4), (-4.6, 6.75), (-4.95, 6.75)], ZF, LED, lift=0.03)

# speaker slots under the buttons
for i in range(3):
    x = 4.4 + 0.42 * i
    m.decal_xy([(x, 1.15), (x + 0.2, 1.15), (x + 0.2, 2.15), (x, 2.15)], ZF, HOLE, lift=0.03)

# ---------------------------------------------------------------- top
m.decal_xz([(-3.3, ZB + 0.25), (3.3, ZB + 0.25), (3.3, ZB + 0.85), (-3.3, ZB + 0.85)], H, HOLE, lift=0.02)

print(m.stats())
m.save()
