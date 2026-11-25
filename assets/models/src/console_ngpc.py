# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly SNK Neo Geo Pocket Color (platinum blue finish), handheld,
screen facing +Z.

Real size about 13.0 x 8.0 x 3.0 cm. Signature features: landscape body
with a flat top edge, round side grips and a gently dipped bottom edge,
platinum-blue shell with a darker blue bevel, black glass panel around the
colour screen in the middle (sky / ground bands to show it is in colour),
the clicky micro-switched joystick (silver cap in a dark round gate) on the
left, round dark A/B buttons on the right (A lower left, B upper right),
small power and option buttons top right, power lamp top left, speaker
slots, cartridge slot on the top back, battery bulge on the back.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

SHELL = (96, 134, 204)     # platinum blue shell (sides, back)
FACE = (136, 170, 232)      # front face, lighter and shinier
BEVEL = (60, 88, 156)      # darker blue edge bevel / back bulge
BEZEL = (22, 24, 34)        # black glass around the screen
SKY = (96, 176, 240)        # colour screen: sky
GROUND = (88, 184, 72)      # colour screen: grass
SUN = (248, 216, 64)        # colour screen: a yellow spot
GATE = (34, 40, 60)         # joystick gate
STICK = (212, 216, 224)     # silver joystick cap
STICK_RIM = (120, 124, 136) # joystick collar
AB = (44, 52, 82)           # A / B buttons, dark navy
HOLE = (16, 18, 26)         # speaker slots, cartridge slot
LED = (80, 232, 96)         # power lamp
FRAME = (200, 214, 240)     # pale silver-blue rim round the screen panel
SMALL = STICK               # power / option, silver too

m = Model('ngpc', 'console')

W, H = 13.0, 8.0
X0, X1 = -W / 2, W / 2
D = 2.4                     # body depth; the battery bulge adds 0.6
BULGE = 0.6
ZB = -(D + BULGE) / 2 + BULGE
ZF = ZB + D
BEV = 0.35
RT, RB = 1.6, 3.2           # top / bottom corner radii (round grips)
DIP = 0.35                  # the bottom edge dips up a little in the middle


def outline(x0, y0, x1, y1, rt, rb, dip):
    """Rounded rect with different top and bottom corner radii and a
    gently raised middle of the bottom edge (CCW)."""
    pts = []
    for cx, cy, r, a0, n in ((x1 - rt, y1 - rt, rt, 0, 3), (x0 + rt, y1 - rt, rt, 90, 3),
                             (x0 + rb, y0 + rb, rb, 180, 5), (x1 - rb, y0 + rb, rb, 270, 5)):
        for s in range(n + 1):
            a = math.radians(a0 + 90 * s / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        if a0 == 180:       # bottom edge between the two grips
            span = (x1 - rb) - (x0 + rb)
            for t in (0.25, 0.5, 0.75):
                x = x0 + rb + span * t
                pts.append((x, y0 + dip * math.sin(math.pi * t)))
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
outer = outline(X0, 0, X1, H, RT, RB, DIP)
inner = outline(X0 + BEV, BEV, X1 - BEV, H - BEV, RT - BEV, RB - BEV, DIP)
m.extrude_xy(outer, ZB + BEV, ZF - BEV, SHELL, front=False, back=False)
ring(outer, ZF - BEV, inner, ZF, BEVEL)
ring(outer, ZB + BEV, inner, ZB, BEVEL)
m.polygon([(x, y, ZF) for x, y in inner], FACE, normal=(0, 0, 1))
m.polygon([(x, y, ZB) for x, y in inner], SHELL, normal=(0, 0, -1))

# battery bulge on the lower back (two AA cells side by side)
m.extrude_xy(Model.rounded_rect(-4.0, 0.7, 4.0, 4.6, 1.0, 2), ZB - BULGE, ZB + 0.05, BEVEL, front=False)

# ---------------------------------------------------------------- front
SX = 0.0
m.decal_xy(Model.rounded_rect(SX - 3.05, 0.85, SX + 3.05, 7.45, 0.8, 2), ZF, FRAME, lift=0.02)
m.decal_xy(Model.rounded_rect(SX - 2.85, 1.05, SX + 2.85, 7.25, 0.65, 2), ZF, BEZEL, lift=0.04)
m.decal_xy([(SX - 2.1, 2.25), (SX + 2.1, 2.25), (SX + 2.1, 6.4), (SX - 2.1, 6.4)], ZF, SKY, lift=0.06)
m.decal_xy([(SX - 2.1, 2.25), (SX + 2.1, 2.25), (SX + 2.1, 3.4), (SX - 2.1, 3.4)], ZF, GROUND, lift=0.09)
m.decal_xy([(SX + 0.9 + 0.45 * math.cos(math.radians(45 * i)), 5.4 + 0.45 * math.sin(math.radians(45 * i)))
            for i in range(8)], ZF, SUN, lift=0.09)

# joystick: round dark gate, collar, silver cap with a dished top
JX, JY = -4.55, 4.4
m.decal_xy([(JX + 1.2 * math.cos(math.radians(30 * i)), JY + 1.2 * math.sin(math.radians(30 * i)))
            for i in range(12)], ZF, GATE, lift=0.04)
m.cylinder_z(JX, JY, 0.8, ZF - 0.05, ZF + 0.25, STICK_RIM, segments=8, back=False)
m.cylinder_z(JX, JY, 0.66, ZF + 0.2, ZF + 0.62, STICK, segments=8, back=False)
m.cylinder_z(JX, JY, 0.34, ZF + 0.57, ZF + 0.7, STICK_RIM, segments=8, back=False)

# A (lower left) and B (upper right)
m.cylinder_z(4.0, 3.55, 0.6, ZF - 0.05, ZF + 0.32, AB, segments=10, back=False)
m.cylinder_z(5.2, 4.6, 0.6, ZF - 0.05, ZF + 0.32, AB, segments=10, back=False)

# power and option, top right
m.cylinder_z(5.0, 6.75, 0.28, ZF - 0.05, ZF + 0.14, SMALL, segments=6, back=False)
m.cylinder_z(3.85, 6.75, 0.24, ZF - 0.05, ZF + 0.12, SMALL, segments=6, back=False)
m.decal_xy([(-4.85, 6.75), (-4.45, 6.75), (-4.45, 7.05), (-4.85, 7.05)], ZF, LED, lift=0.04)

# speaker slots under the buttons
for i in range(3):
    x = 4.15 + 0.42 * i
    m.decal_xy([(x, 1.25), (x + 0.2, 1.25), (x + 0.2, 2.2), (x, 2.2)], ZF, HOLE, lift=0.04)

# ---------------------------------------------------------------- top
m.decal_xz([(-3.3, ZB + 0.3), (3.3, ZB + 0.3), (3.3, ZB + 0.95), (-3.3, ZB + 0.95)], H, HOLE, lift=0.03)

print(m.stats())
m.save()
