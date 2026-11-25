# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega Master System (first model): low-poly console for the X7 Game frontend.

Angular black wedge, about 36.5 x 7 x 17 cm, red accents: a red stripe along
the front, a red control panel on the front bevel (power switch, pause and
reset buttons), the cartridge slot on top, the card slot on the front, two
controller ports, and the diagonally ribbed vent area on the top right.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (52, 52, 58)
BODY_DARK = (26, 26, 28)
RIB = (84, 84, 92)
HOLE = (8, 8, 10)
RED = (214, 28, 32)
RED_DARK = (150, 18, 22)
GREY = (120, 122, 128)
BUTTON = (60, 60, 64)

W2 = 18.25          # half width
ZB, ZF = -8.5, 8.5  # back, front
YF = 3.0            # top of the vertical front face
ZT = 5.2            # where the bevel meets the top
YT = 6.6            # top surface

m = Model('mastersystem', 'console')

# ---- body: side profile extruded along X
profile = [(ZB, 0.0), (ZF, 0.0), (ZF, YF), (ZT, YT), (ZB + 0.6, YT), (ZB, YT - 0.6)]
m.extrude_yz(profile, -W2, W2, BODY)

# bevel geometry (front-top slope)
_dz, _dy = ZT - ZF, YT - YF
_len = math.hypot(_dz, _dy)
BN = (0.0, -_dz / _len, _dy / _len)        # outward normal (up / forward)
ANG = math.degrees(math.atan2(BN[2], BN[1]))


def bev(x, t, lift=0.03):
    """point on the bevel: t = 0 at its lower (front) edge, 1 at the top"""
    return (x, YF + _dy * t + BN[1] * lift, ZF + _dz * t + BN[2] * lift)


def bev_rect(x0, x1, t0, t1, col, lift=0.03):
    m.polygon([bev(x0, t0, lift), bev(x1, t0, lift), bev(x1, t1, lift), bev(x0, t1, lift)], col)


def bev_box(x0, x1, t0, t1, h, col, top=None):
    """a small box standing on the bevel"""
    s0, s1 = t0 * _len, t1 * _len
    ids = m.box(x0, 0, -s1, x1, h, -s0, col, faces={'bottom': None, 'top': top or col})
    # local -z runs up the slope: rotate the box onto the bevel plane
    m.transform(ids, Model.rot_x(ANG))
    m.transform(ids, Model.move(0, YF, ZF))
    return ids


# ---- red stripe along the front face, just under the bevel edge
m.decal_xy([(-W2 + 0.05, YF - 0.55), (W2 - 0.05, YF - 0.55), (W2 - 0.05, YF - 0.1), (-W2 + 0.05, YF - 0.1)], ZF, RED)
# thin red line along the bottom of the bevel
bev_rect(-W2 + 0.05, W2 - 0.05, 0.0, 0.06, RED, lift=0.02)

# ---- red control panel on the bevel, left side: power, pause, reset
bev_rect(-16.8, -5.2, 0.18, 0.85, RED, lift=0.02)
bev_rect(-16.2, -12.6, 0.3, 0.73, RED_DARK, lift=0.06)        # power switch well
bev_box(-15.6, -14.3, 0.36, 0.67, 0.45, RED_DARK, top=GREY)     # power rocker
bev_box(-10.8, -8.9, 0.33, 0.7, 0.4, RED_DARK, top=BODY_DARK)  # pause
bev_box(-7.9, -6.0, 0.33, 0.7, 0.4, RED_DARK, top=GREY)       # reset

# ---- card slot on the front face (right side)
m.decal_xy([(3.0, 1.0), (11.0, 1.0), (11.0, 1.7), (3.0, 1.7)], ZF, BODY_DARK)
m.decal_xy([(3.4, 1.18), (10.6, 1.18), (10.6, 1.52), (3.4, 1.52)], ZF, HOLE, lift=0.05)

# ---- two controller ports on the front face (left side), D-shaped
for cx in (-13.0, -8.6):
    port = [(cx - 1.6, 1.75), (cx + 1.6, 1.75), (cx + 1.25, 0.75), (cx - 1.25, 0.75)]
    m.decal_xy(port, ZF, BODY_DARK)
    inner = [(cx - 1.25, 1.55), (cx + 1.25, 1.55), (cx + 0.98, 0.95), (cx - 0.98, 0.95)]
    m.decal_xy(inner, ZF, GREY, lift=0.05)

# ---- cartridge slot on top: raised frame with a dark opening and flap
m.box(-12.0, YT, -4.5, 3.0, YT + 0.45, 0.6, BODY, faces={'bottom': None, 'top': BODY_DARK})
m.decal_xz([(-11.0, -2.4), (2.0, -2.4), (2.0, -1.2), (-11.0, -1.2)], YT + 0.45, HOLE)
m.decal_xz([(-11.0, -1.2), (2.0, -1.2), (2.0, -0.2), (-11.0, -0.2)], YT + 0.45, BODY, lift=0.03)

# ---- ribbed vent area on the top right: diagonal raised ribs
RX0, RX1 = 4.6, 17.4
RZ0, RZ1 = -7.6, 4.4
m.decal_xz([(RX0, RZ0), (RX1, RZ0), (RX1, RZ1), (RX0, RZ1)], YT, BODY_DARK)
n_ribs = 9
skew = 1.6                          # ribs lean: back end shifted left
pitch = (RX1 - RX0 - skew) / n_ribs
for i in range(n_ribs):
    x0 = RX0 + skew + i * pitch + 0.2
    x1 = x0 + pitch * 0.55
    if i == n_ribs - 1:
        x1 = min(x1, RX1 - 0.3)
    outline = [(x0, RZ1 - 0.4), (x1, RZ1 - 0.4), (x1 - skew, RZ0 + 0.4), (x0 - skew, RZ0 + 0.4)]
    m.prism(outline, YT, YT + 0.35, RIB, bottom=False)

# ---- back panel: power jack, A/V and RF connectors (dark recesses)
def back_rect(x0, y0, x1, y1, col, lift=0.03):
    m.polygon([(x1, y0, ZB - lift), (x0, y0, ZB - lift), (x0, y1, ZB - lift), (x1, y1, ZB - lift)], col)


back_rect(-15.0, 2.0, -12.6, 4.2, BODY_DARK)     # DC in
back_rect(-14.3, 2.7, -13.3, 3.5, HOLE, lift=0.06)
back_rect(-6.0, 2.0, -1.0, 4.4, BODY_DARK)       # A/V port
back_rect(-5.5, 2.6, -1.5, 3.8, HOLE, lift=0.06)
m.cylinder_z(6.0, 3.2, 0.7, ZB - 0.5, ZB, GREY, segments=8, front=False)   # RF jack (sticks out back)
m.polygon([(6.0 + 0.4 * math.cos(a), 3.2 + 0.4 * math.sin(a), ZB - 0.53)
           for a in [-2 * math.pi * k / 8 for k in range(8)]], HOLE, normal=(0, 0, -1))

print(m.stats())
m.save()
