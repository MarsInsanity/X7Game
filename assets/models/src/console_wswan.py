# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly Bandai WonderSwan (original, pearl white), handheld, screen +Z.

Real size about 12.1 x 7.43 x 2.43 cm. Signature features: wide landscape
body with soft rounded ends, a dark smoked lens panel around the grey
monochrome LCD (offset a little right of centre), two diamond clusters of
four small buttons on the left (Y1-Y4 at the top left, X1-X4 below them),
the round A/B pair on the right with the small Start button beneath,
cartridge slot across the upper back and a battery cover on the lower back.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (236, 234, 224)      # pearl white shell
BODY_DK = (196, 194, 184)   # battery cover on the back
LENS = (58, 60, 70)         # smoked screen lens
SCREEN = (150, 162, 140)    # monochrome LCD
XY = (150, 152, 164)        # X / Y buttons
AB = (88, 90, 104)          # A / B buttons
START = (120, 122, 134)
HOLE = (34, 34, 40)         # cartridge slot, speaker, switch slot
SWITCH = (190, 60, 60)      # power switch

m = Model('wswan', 'console')

W, H = 12.1, 7.43
X0, X1 = -W / 2, W / 2
HUMP = 0.2
ZB, ZF = -1.115 + HUMP / 2, 1.115 + HUMP / 2   # body 2.23 deep + hump -> 2.43
BEV = 0.3


def outline(inset):
    """Body outline (CCW seen from +Z): a wide rounded rectangle."""
    pts = []
    r = 2.0 - inset
    # rounded corners: top-right, top-left, bottom-left, bottom-right
    corners = [(X1 - 2.0, H - 2.0, 0), (X0 + 2.0, H - 2.0, 90),
               (X0 + 2.0, 2.0, 180), (X1 - 2.0, 2.0, 270)]
    for ci, (cx, cy, a0) in enumerate(corners):
        for s in range(4):
            a = math.radians(a0 + 90 * s / 3)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def ring(outer, oz, inner, iz):
    n = len(outer)
    sgn = 1 if iz > oz else -1
    for i in range(n):
        a, b = outer[i], outer[(i + 1) % n]
        c, d = inner[(i + 1) % n], inner[i]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        m.polygon([(a[0], a[1], oz), (b[0], b[1], oz), (c[0], c[1], iz), (d[0], d[1], iz)], BODY,
                  normal=(dy / l, -dx / l, sgn * 1.0))


outer = outline(0.0)
inner = outline(BEV)
m.extrude_xy(outer, ZB + BEV, ZF - BEV, BODY, front=False, back=False)
ring(outer, ZF - BEV, inner, ZF)
ring(outer, ZB + BEV, inner, ZB)
m.polygon([(x, y, ZF) for x, y in inner], BODY, normal=(0, 0, 1))
m.polygon([(x, y, ZB) for x, y in inner], BODY, normal=(0, 0, -1))

# ---------------------------------------------------------------- front
SCX = 0.35                                    # screen centre x
m.extrude_xy(Model.rounded_rect(SCX - 3.55, 1.55, SCX + 3.55, 6.75, 0.5, 2), ZF - 0.05, ZF + 0.08,
             LENS, back=False)
m.decal_xy([(SCX - 2.75, 2.6), (SCX + 2.75, 2.6), (SCX + 2.75, 6.15), (SCX - 2.75, 6.15)],
           ZF + 0.08, SCREEN, lift=0.03)


def diamond(cx, cy, d=0.42, l=0.5, w=0.36):
    """Four small wedge buttons pointing outwards from a centre, like the
    WonderSwan's X and Y clusters."""
    for ang in (90, 0, 270, 180):
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a)          # outwards
        vx, vy = -uy, ux                           # across
        bx, by = cx + ux * d, cy + uy * d          # inner edge centre
        tx, ty = bx + ux * l, by + uy * l          # tip
        pts = [(bx + vx * w, by + vy * w), (tx + vx * 0.1, ty + vy * 0.1),
               (tx - vx * 0.1, ty - vy * 0.1), (bx - vx * w, by - vy * w)]
        m.extrude_xy(pts, ZF - 0.1, ZF + 0.2, XY, back=False)


diamond(-4.75, 5.35)     # Y1-Y4
diamond(-4.05, 2.45)     # X1-X4

# A (right, higher) and B (left, lower)
m.cylinder_z(5.3, 3.75, 0.52, ZF - 0.1, ZF + 0.26, AB, segments=10, back=False)
m.cylinder_z(4.45, 2.85, 0.52, ZF - 0.1, ZF + 0.26, AB, segments=10, back=False)

# Start: small pill under A/B
m.extrude_xy(Model.rounded_rect(4.45, 1.15, 5.35, 1.5, 0.17, 2), ZF - 0.1, ZF + 0.12, START, back=False)

# speaker holes at the upper right
for hx, hy in ((4.6, 6.25), (5.0, 6.25), (5.4, 6.25), (4.8, 5.85), (5.2, 5.85)):
    h = 0.11
    m.decal_xy([(hx - h, hy - h), (hx + h, hy - h), (hx + h, hy + h), (hx - h, hy + h)], ZF, HOLE, lift=0.02)

# ---------------------------------------------------------------- edges
# power switch on the top edge, left
m.decal_xz([(-4.4, -0.35), (-3.2, -0.35), (-3.2, 0.35), (-4.4, 0.35)], H, HOLE, lift=0.02)
m.box(-4.2, H, -0.22, -3.75, H + 0.12, 0.22, SWITCH, faces={'bottom': None})

# ---------------------------------------------------------------- back
# cartridge slot across the upper back
SL = [(-3.0, 4.6), (3.0, 4.6), (3.0, 6.5), (-3.0, 6.5)]
m.polygon([(x, y, ZB - 0.02) for x, y in SL], LENS, normal=(0, 0, -1))
# battery cover (one AA) as a low hump on the lower back
m.extrude_xy(Model.rounded_rect(-4.6, 0.6, 0.4, 3.4, 0.5, 2), ZB - HUMP, ZB + 0.05, BODY_DK, front=False)

print(m.stats())
m.save()
