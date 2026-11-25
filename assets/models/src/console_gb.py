# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly Nintendo Game Boy (original DMG-01) for the X7 Game frontend.

Real size 9.0 x 14.8 x 3.2 cm. Stands upright, screen facing +Z, origin
at the bottom centre. Proportions measured from Commons photos (straight
front, front three-quarter, back three-quarter and straight back):

front   top band with a groove line at y 13.65 and the OFF/ON switch nub on
        the top face at the left; dark grey screen surround x +-3.67,
        y 7.42..13.19 with the big rounded lower-right corner; olive LCD
        centred in it (x +-2.33, y 8.06..12.5); two stripe lines (magenta
        over navy) left and right above the LCD; red power LED in the left
        margin; black cross D-pad at (-2.78, 4.98); magenta B (1.46, 4.35)
        and A (2.88, 5.0) on a slant; Select / Start pills tilted 25 deg;
        six slanted speaker slots in the big rounded lower-right corner
        (r 1.8, the other corners r 0.35).
back    the cartridge well open at the top (x +-2.925, from y 11.9 up),
        the cartridge cover plate below it (x +-3.35, y 7.77..11.9), four
        screw holes, horizontal grip ridges across the lower half and the
        ridged battery cover (x +-3.15, y 0.6..6.55).
sides   link port and volume wheel on the right, contrast wheel and DC
        jack on the left, headphone jack in the bottom edge.

The game: the Game Pak goes straight DOWN into the well, label facing the
back (-Z). Seated, its bottom rests 0.05 cm above the cavity floor (y 8.25)
and its top is flush with the console top (y 14.8); the upper 2.9 cm stay
visible in the open well. Cavity inside: x +-2.925, z -1.5..-0.55 (pak
5.7 x 0.8 cm). Moving part "switch": the OFF/ON nub plus the lock tab that
slides over the pak's corner notch when switched on (+0.45 cm in x).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (212, 210, 202)        # warm light grey shell
SHADE = (150, 148, 142)       # grooves, ridges, well walls
FLOOR = (184, 182, 176)       # lit floor of the open well
DARK = (38, 38, 44)           # cavity, slots, ports, screw holes
BEZEL = (124, 124, 142)       # screen surround, pills, wheels
SCREEN = (132, 148, 56)       # olive LCD
STRIPE_A = (156, 36, 108)     # magenta line
STRIPE_B = (44, 44, 150)      # navy line
DPAD = (24, 24, 28)
AB = (176, 26, 92)            # magenta A / B
LED = (236, 24, 24)

W, H = 9.0, 14.8
X0, X1 = -W / 2, W / 2
ZF, ZB = 1.5, -1.5            # front / back face of the shell
R_S, R_B = 0.35, 1.8          # small corners, big bottom-right corner

# cartridge well / cavity
WX = 2.925                    # half inner width (pak 5.7 -> 0.075 clearance a side)
WZ_FLOOR = -0.55              # front wall of the well (pak front at -0.6)
WY_BOT = 8.25                 # cavity bottom (pak bottom at 8.3)
WY_OPEN = 11.9                # below this the cover plate closes the well
PLATE_X = 3.35
PLATE_Y0 = 7.77
PLATE_Z = -1.6

m = Model('gb', 'console')


def arc(cx, cy, r, a0, a1, seg):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / seg)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / seg))) for i in range(seg + 1)]


def outline(x0, y0, x1, y1, rs, rb, seg_s=2, seg_b=5):
    """CCW rounded rectangle, big radius on the bottom-right corner; starts
    at the right end of the top edge."""
    pts = [(x1 - rs, y1)]                                          # right end of the top edge
    pts += arc(x0 + rs, y1 - rs, rs, 90, 180, seg_s)               # top-left
    pts += arc(x0 + rs, y0 + rs, rs, 180, 270, seg_s)              # bottom-left
    pts += arc(x1 - rb, y0 + rb, rb, 270, 360, seg_b)              # bottom-right
    pts += arc(x1 - rs, y1 - rs, rs, 0, 90, seg_s)[:-1]            # top-right
    return pts


def ngon(cx, cy, r, n, rot=0.0):
    return [(cx + r * math.cos(math.radians(rot + 360 * i / n)),
             cy + r * math.sin(math.radians(rot + 360 * i / n))) for i in range(n)]


def turned(pts, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def back_decal(pts, z, color, lift=0.02):
    """A flat area on a back-facing (-Z) surface at depth z."""
    m.polygon([(x, y, z - lift) for x, y in pts], color, normal=(0, 0, -1))


def side_decal(pts_zy, x, color, lift=0.02):
    """A flat area on a side wall at x (z, y points); faces outwards."""
    s = 1 if x > 0 else -1
    m.polygon([(x + s * lift, y, z) for z, y in pts_zy], color, normal=(s, 0, 0))


# ---------------------------------------------------------------- shell
OUT = outline(X0, 0, X1, H, R_S, R_B)
# OUT[0] = (X1 - R_S, H) ... the top edge runs from OUT[0] to OUT[1] (right -> left)
assert abs(OUT[0][1] - H) < 1e-9 and abs(OUT[1][1] - H) < 1e-9

# front face
m.polygon([(x, y, ZF) for x, y in OUT], BODY, normal=(0, 0, 1))
# side ring (everything except the straight top edge)
n = len(OUT)
for i in range(1, n):
    (xa, ya), (xb, yb) = OUT[i], OUT[(i + 1) % n]
    m.quad((xa, ya, ZF), (xa, ya, ZB), (xb, yb, ZB), (xb, yb, ZF), BODY)
# top face in three pieces around the open well
xt = X1 - R_S
m.polygon([(-xt, H, ZF), (-WX, H, ZF), (-WX, H, ZB), (-xt, H, ZB)], BODY, normal=(0, 1, 0))
m.polygon([(WX, H, ZF), (xt, H, ZF), (xt, H, ZB), (WX, H, ZB)], BODY, normal=(0, 1, 0))
m.polygon([(-WX, H, ZF), (WX, H, ZF), (WX, H, WZ_FLOOR), (-WX, H, WZ_FLOOR)], BODY, normal=(0, 1, 0))
# back face with the well cut out of it (the cover plate closes the lower part)
back = [(xt, H), (WX, H), (WX, WY_BOT), (-WX, WY_BOT), (-WX, H)] + OUT[1:]
m.polygon([(x, y, ZB) for x, y in back], BODY, normal=(0, 0, -1))

# well and cavity walls (lit grey where the well is open, dark further in)
for (ya, yb, col) in ((WY_OPEN, H, SHADE), (WY_BOT, WY_OPEN, DARK)):
    m.polygon([(-WX, ya, WZ_FLOOR), (WX, ya, WZ_FLOOR), (WX, yb, WZ_FLOOR), (-WX, yb, WZ_FLOOR)], FLOOR if col == SHADE else col, normal=(0, 0, -1))  # floor, faces -Z
    m.polygon([(-WX, ya, ZB), (-WX, ya, WZ_FLOOR), (-WX, yb, WZ_FLOOR), (-WX, yb, ZB)], col, normal=(1, 0, 0))  # left wall, +X
    m.polygon([(WX, ya, WZ_FLOOR), (WX, ya, ZB), (WX, yb, ZB), (WX, yb, WZ_FLOOR)], col, normal=(-1, 0, 0))  # right wall, -X
m.polygon([(-WX, WY_BOT, ZB), (WX, WY_BOT, ZB), (WX, WY_BOT, WZ_FLOOR), (-WX, WY_BOT, WZ_FLOOR)], DARK, normal=(0, 1, 0))  # bottom, +Y
# two guide ribs on the visible well floor
for gx in (-1.55, 1.55):
    back_decal(rect(gx - 0.08, WY_OPEN + 0.05, gx + 0.08, H - 0.02), WZ_FLOOR, SHADE, lift=0.02)

# cartridge cover plate (its inside closes the cavity)
m.box(-PLATE_X, PLATE_Y0, PLATE_Z, PLATE_X, WY_OPEN, ZB, BODY, faces={'front': DARK})
# its seam to the rest of the back
back_decal(rect(-PLATE_X - 0.08, PLATE_Y0 - 0.08, PLATE_X + 0.08, PLATE_Y0), ZB, SHADE)
for sx in (-1, 1):
    back_decal(rect(min(sx * PLATE_X, sx * (PLATE_X + 0.08)), PLATE_Y0, max(sx * PLATE_X, sx * (PLATE_X + 0.08)), WY_OPEN),
               ZB, SHADE)

# ---------------------------------------------------------------- back details
# screw holes
for sx in (-3.72, 3.72):
    for sy in (13.13, 8.09):
        back_decal(ngon(sx, sy, 0.17, 6), ZB, DARK)
# battery cover (raised a little) with its ridges and the latch notch above it
BC = (-3.15, 0.6, 3.15, 6.55)
BZ = ZB - 0.08
m.box(BC[0], BC[1], BZ, BC[2], BC[3], ZB, BODY, faces={'front': None})
for k in range(9):
    gy = 2.55 + 0.42 * k
    back_decal(rect(BC[0] + 0.12, gy, BC[2] - 0.12, gy + 0.13), BZ, SHADE)
back_decal(rect(-0.85, BC[3] + 0.02, 0.85, 7.6), ZB, SHADE)
# grip ridges: across the back between the plate and the cover, down the sides
for k in range(10):
    gy = 7.48 - 0.42 * k
    if gy > BC[3] + 0.05:
        back_decal(rect(-4.42, gy, -0.9, gy + 0.13), ZB, SHADE)
        back_decal(rect(0.9, gy, 4.42, gy + 0.13), ZB, SHADE)
    else:
        back_decal(rect(-4.42, gy, BC[0] - 0.1, gy + 0.13), ZB, SHADE)
        back_decal(rect(BC[2] + 0.1, gy, 4.42, gy + 0.13), ZB, SHADE)

# ---------------------------------------------------------------- front
# top band: groove across, short grooves where the corner pieces start
m.decal_xy(rect(X0 + 0.06, 13.6, X1 - 0.06, 13.68), ZF, SHADE)
for gx in (-3.72, 3.72):
    m.decal_xy(rect(gx - 0.04, 13.68, gx + 0.04, H - 0.04), ZF, SHADE)
# OFF/ON frame on the band
m.decal_xy(rect(-3.55, 13.85, -2.05, 14.05), ZF, SHADE)

# screen surround, LCD, stripes, LED
m.decal_xy(outline(-3.67, 7.42, 3.67, 13.19, 0.3, 1.0, 1, 4), ZF, BEZEL, lift=0.03)
m.decal_xy(rect(-2.33, 8.06, 2.33, 12.5), ZF, SCREEN, lift=0.06)
for (y0, col) in ((12.86, STRIPE_A), (12.70, STRIPE_B)):
    for (x0, x1) in ((-3.36, -1.43), (2.51, 3.36)):
        m.decal_xy(rect(x0, y0, x1, y0 + 0.09), ZF, col, lift=0.06)
m.decal_xy(ngon(-3.05, 11.2, 0.13, 6), ZF, LED, lift=0.06)

# D-pad
cx, cy, a, b = -2.78, 4.98, 1.05, 0.42
cross = [(cx + b, cy - a), (cx + b, cy - b), (cx + a, cy - b), (cx + a, cy + b), (cx + b, cy + b),
         (cx + b, cy + a), (cx - b, cy + a), (cx - b, cy + b), (cx - a, cy + b), (cx - a, cy - b),
         (cx - b, cy - b), (cx - b, cy - a)]
m.extrude_xy(cross, ZF, ZF + 0.3, DPAD, back=False)

# B and A
for bx, by in ((1.46, 4.35), (2.88, 5.0)):
    m.cylinder_z(bx, by, 0.55, ZF, ZF + 0.25, AB, segments=10, back=False)

# Select / Start pills, tilted
for px, py in ((-1.45, 2.74), (0.0, 2.6)):
    r, half = 0.18, 0.34
    pill = arc(half, 0, r, -90, 90, 2) + arc(-half, 0, r, 90, 270, 2)
    m.extrude_xy(turned(pill, px, py, 25), ZF, ZF + 0.1, BEZEL, back=False)

# speaker slots: tops on a rising line, leaning with the top to the left
da = math.radians(24)
d = (math.sin(da), -math.cos(da))           # down along the slot
for i in range(6):
    tx, ty = 0.95 + 0.44 * i, 1.72 + 0.2 * i
    # run down until 0.55 cm inside the big corner / bottom edge
    L = 0.0
    while L < 1.45:
        px, py = tx + d[0] * (L + 0.05), ty + d[1] * (L + 0.05)
        cxb, cyb = X1 - R_B, R_B
        if py < 0.6 or (px > cxb and py < cyb and math.hypot(px - cxb, py - cyb) > R_B - 0.55):
            break
        L += 0.05
    hw = 0.08
    nx, ny = -d[1] * hw, d[0] * hw          # across the slot
    bx_, by_ = tx + d[0] * L, ty + d[1] * L
    m.decal_xy([(tx - nx, ty - ny), (bx_ - nx, by_ - ny), (bx_ + nx, by_ + ny), (tx + nx, ty + ny)],
               ZF, DARK, lift=0.03)

# ---------------------------------------------------------------- sides
# right: link port and volume wheel
side_decal(rect(-0.45, 10.5, 0.45, 12.1), X1, DARK)
m.cylinder_x(0.0, 9.5, 0.5, X1, X1 + 0.12, BEZEL, segments=8, left=False)
# left: contrast wheel and DC jack
m.cylinder_x(0.0, 11.0, 0.5, X0 - 0.12, X0, BEZEL, segments=8, right=False)
side_decal(ngon(0.0, 2.6, 0.22, 6), X0, DARK)

# ---------------------------------------------------------------- moving part
# OFF/ON switch: the nub on the top face and the lock tab in the well's
# left corner (modelled OFF; ON = slid 0.45 cm to the right over the
# pak's corner notch)
with m.part('switch'):
    m.box(-3.45, H, 0.35, -2.85, H + 0.18, 1.05, BEZEL, faces={'bottom': None})
    m.box(-WX, 14.56, -1.3, -WX + 0.04, H, -0.7, BEZEL)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
