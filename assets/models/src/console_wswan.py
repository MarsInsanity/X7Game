# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly Bandai WonderSwan (original, 1999), skeleton blue, handheld
standing upright, screen to +Z.

Real size 12.1 x 7.43 x 2.43 cm (with the battery bulge on the back).
Proportions measured from Wikimedia Commons photos (front-on shots of a
skeleton blue and a skeleton pink unit, three-quarter shots of a skeleton
black one):
  * landscape body: straight top edge, a big rounded left end, tighter
    corners on the right end, and a "chin": the bottom edge dips about
    0.4 cm lower under the screen than at the two ends
  * silver screen panel 6.8 x 5.85 cm (56 % of the width, 79 % of the
    height), set a little right of centre (centre x +0.4), with the
    grey-green LCD 5.7 x 3.85 centred in it, logo strip above, and the two
    small SOUND / START pills on its lower edge, left of centre
  * left end: two diamonds of four rounded-triangle buttons (Y1-Y4 at the
    top, X1-X4 at the bottom), each about 1.9 cm across, tips pointing in
  * right end: the round speaker with its grille at the top right, the A
    and B buttons (same rounded triangles, tip to tip) at the bottom right
  * power slider in the middle of the left edge, EXT port on the right edge
  * back: the AA battery bulge along the bottom, and the cartridge bay in
    the upper middle: the cart slides down into a slot in the top edge,
    label facing the back, and its label shows through a window in the
    back; its finger-grip end stays above the top edge.
No text or logos.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

SHELL = (56, 100, 190)      # skeleton blue shell
SHELL_DK = (36, 66, 136)    # battery bulge, speaker well
BEZEL = (196, 198, 206)     # silver screen panel
LCD_EDGE = (64, 68, 76)     # dark frame round the LCD
LCD = (156, 166, 146)       # grey-green monochrome LCD
BTN = (214, 218, 228)       # X / Y / A / B buttons, power slider
BTN2 = (112, 116, 130)      # SOUND / START pills (on the silver panel)
HOLE = (22, 24, 32)         # cartridge bay, grille slots, port

m = Model('wswan', 'console')

H = 7.43                    # height (the chin is at y = 0, the top at H)
HUMP = 0.48                 # battery bulge on the back
ZF = 1.215                  # front face
ZB = ZF - 1.95              # back face (-0.735); the bulge goes to -1.215
BEVF, BEVB = 0.30, 0.25     # edge bevels front / back

# ---------------------------------------------------------------- cartridge bay
# The cart (assets/models/media/wswan.obj) is turned round (label to -Z) and
# seated with its origin at (0, CY, CZ): slab x +-2.2, y CY..CY+5.2,
# console z CZ-0.35 (label rim) .. CZ+0.34 (contacts). Grip above the top.
SX = 2.27                   # bay half width (cart 2.2)
SZ0 = ZB + BEVB             # bay back = inside of the back wall (-0.485)
SZ1 = ZB + 1.02             # bay front wall (0.285)
SY0 = 2.15                  # bay floor (cart bottom at 2.23)
WX, WY0, WY1 = 2.0, 2.65, 6.95   # label window in the back wall

# ---------------------------------------------------------------- outline
OUT = [  # counter-clockwise seen from the front; convex
    (-1.0, 0.0), (3.4, 0.0), (4.6, 0.12), (5.45, 0.5), (5.92, 1.1), (6.05, 1.8),
    (6.05, 6.4), (5.92, 6.98), (5.52, 7.34), (4.85, 7.43),
    (SX, H), (-SX, H),
    (-4.55, 7.43), (-5.35, 7.27), (-5.85, 6.82), (-6.05, 5.9),
    (-6.05, 2.6), (-5.9, 1.7), (-5.55, 1.0), (-5.0, 0.52), (-4.1, 0.19), (-2.2, 0.03),
]


def _cross2(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


for i in range(len(OUT)):
    assert _cross2(OUT[i - 1], OUT[i], OUT[(i + 1) % len(OUT)]) >= -1e-9, ('outline not convex at', OUT[i])


def inset(pts, d):
    """Offset a convex CCW polygon inwards by d."""
    n = len(pts)
    lines = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy)
        nx, ny = -dy / l, dx / l                 # inward (left of the edge)
        lines.append(((a[0] + nx * d, a[1] + ny * d), (dx / l, dy / l), (nx, ny)))
    out = []
    for i in range(n):
        (p, u, nu), (q, v, nv) = lines[i - 1], lines[i]
        den = u[0] * v[1] - u[1] * v[0]
        if abs(den) < 1e-9:                      # collinear: move straight in
            out.append((pts[i][0] + nv[0] * d, pts[i][1] + nv[1] * d))
            continue
        t = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / den
        out.append((p[0] + u[0] * t, p[1] + u[1] * t))
    return out


INF = inset(OUT, BEVF)
INB = inset(OUT, BEVB)
N = len(OUT)
ZS0, ZS1 = ZB + BEVB, ZF - BEVF          # straight side wall between the bevels
TOP_SLOT = OUT.index((SX, H))            # edge TOP_SLOT -> TOP_SLOT+1 is the slot edge

# side walls (the slot edge only in front of the bay)
for i in range(N):
    a, b = OUT[i], OUT[(i + 1) % N]
    z0 = SZ1 if i == TOP_SLOT else ZS0
    m.quad((a[0], a[1], ZS1), (a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], ZS1), SHELL)

# bevels
for i in range(N):
    j = (i + 1) % N
    a, b, c, d = OUT[i], OUT[j], INF[j], INF[i]
    m.quad((a[0], a[1], ZS1), (b[0], b[1], ZS1), (c[0], c[1], ZF), (d[0], d[1], ZF), SHELL)
    a, b, c, d = OUT[i], OUT[j], INB[j], INB[i]
    m.quad((b[0], b[1], ZS0), (a[0], a[1], ZS0), (d[0], d[1], ZB), (c[0], c[1], ZB), SHELL)

# front face
m.polygon([(x, y, ZF) for x, y in INF], SHELL, normal=(0, 0, 1))


# back face: the inner outline minus the label window, in convex pieces
def clip(poly, k, sign):
    """Keep the part of a convex polygon where sign * (x - k) >= 0."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i - 1], poly[i]
        fp, fq = sign * (p[0] - k), sign * (q[0] - k)
        if fp >= 0 and fq >= 0:
            out.append(q)
        elif fp >= 0 > fq or fq >= 0 > fp:
            t = fp / (fp - fq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
            if fq >= 0:
                out.append(q)
    return out


def back_poly(pts2):
    m.polygon([(x, y, ZB) for x, y in pts2], SHELL, normal=(0, 0, -1))


left = clip(INB, -WX, -1)
right = clip(INB, WX, 1)
mid = clip(clip(INB, -WX, 1), WX, -1)
# put the window corners on the cut lines (no T-junctions)
for piece, x in ((left, -WX), (right, WX)):
    n = len(piece)
    for i in range(n):
        p, q = piece[i], piece[(i + 1) % n]
        if abs(p[0] - x) < 1e-6 and abs(q[0] - x) < 1e-6:
            piece[i + 1:i + 1] = [(x, y) for y in sorted((WY0, WY1), reverse=p[1] > q[1])]
            break
    else:
        raise SystemExit('cut edge not found')
    back_poly(piece)
lo_mid = [p for p in mid if p[1] < H / 2]
hi_mid = [p for p in mid if p[1] > H / 2]
back_poly(sorted(lo_mid, key=lambda p: p[0]) + [(WX, WY0), (-WX, WY0)])
back_poly(sorted(hi_mid, key=lambda p: -p[0]) + [(-WX, WY1), (WX, WY1)])

# window reveals (shell colour), z ZB..SZ0, facing the window's middle
m.quad((-WX, WY1, ZB), (-WX, WY1, SZ0), (-WX, WY0, SZ0), (-WX, WY0, ZB), SHELL)       # faces +x
m.quad((WX, WY1, SZ0), (WX, WY1, ZB), (WX, WY0, ZB), (WX, WY0, SZ0), SHELL)           # faces -x
m.quad((WX, WY0, SZ0), (WX, WY0, ZB), (-WX, WY0, ZB), (-WX, WY0, SZ0), SHELL)         # faces +y
m.quad((WX, WY1, ZB), (WX, WY1, SZ0), (-WX, WY1, SZ0), (-WX, WY1, ZB), SHELL)         # faces -y

# the bay: dark faces looking into it
m.quad((-SX, SY0, SZ0), (-SX, SY0, SZ1), (SX, SY0, SZ1), (SX, SY0, SZ0), HOLE)         # floor, +y
m.quad((-SX, SY0, SZ0), (-SX, H, SZ0), (-SX, H, SZ1), (-SX, SY0, SZ1), HOLE)           # left, +x
m.quad((SX, SY0, SZ1), (SX, H, SZ1), (SX, H, SZ0), (SX, SY0, SZ0), HOLE)               # right, -x
m.quad((SX, SY0, SZ1), (-SX, SY0, SZ1), (-SX, H, SZ1), (SX, H, SZ1), HOLE)             # front wall, -z
for x0, y0, x1, y1 in ((-SX, SY0, -WX, H), (WX, SY0, SX, H), (-WX, SY0, WX, WY0), (-WX, WY1, WX, H)):
    m.quad((x0, y0, SZ0), (x1, y0, SZ0), (x1, y1, SZ0), (x0, y1, SZ0), HOLE)            # back wall inside, +z

# ---------------------------------------------------------------- front
BX0, BX1, BY0, BY1 = -3.0, 3.8, 1.15, 7.0
m.extrude_xy(Model.rounded_rect(BX0, BY0, BX1, BY1, 0.5, 2), ZF - 0.02, ZF + 0.06, BEZEL, back=False)
ZP = ZF + 0.06
LX0, LX1, LY0, LY1 = -2.45, 3.25, 2.15, 6.0
m.decal_xy([(LX0 - 0.1, LY0 - 0.1), (LX1 + 0.1, LY0 - 0.1), (LX1 + 0.1, LY1 + 0.1), (LX0 - 0.1, LY1 + 0.1)],
           ZP, LCD_EDGE, lift=0.02)
m.decal_xy([(LX0, LY0), (LX1, LY0), (LX1, LY1), (LX0, LY1)], ZP, LCD, lift=0.04)

# SOUND / START pills on the panel's lower edge
for cx in (-1.36, -0.14):
    pill = [(cx - 0.4, 1.225), (cx - 0.26, 1.05), (cx + 0.26, 1.05), (cx + 0.4, 1.225), (cx + 0.26, 1.4), (cx - 0.26, 1.4)]
    m.extrude_xy(pill, ZF - 0.02, ZP + 0.1, BTN2, back=False)


def tri_button(cx, cy, ang, size=0.94):
    """A fat rounded-triangle button: its blunt tip points in direction ang
    (degrees), the wide end bulges out the other way."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)          # towards the tip
    vx, vy = -uy, ux
    h = size * 0.78                            # tip to back
    w = size * 0.5                             # half width at the back
    t = size * 0.1                             # half width of the blunt tip

    def p(along, across):
        return (cx + ux * along + vx * across, cy + uy * along + vy * across)
    pts = [p(h * 0.45, -t), p(h * 0.45, t), p(-h * 0.4, w), p(-h * 0.55, 0), p(-h * 0.4, -w)]
    m.extrude_xy(pts, ZF - 0.05, ZF + 0.16, BTN, back=False)


def cluster(cx, cy, r=0.54):
    for ang in (90, 0, 270, 180):
        a = math.radians(ang)
        tri_button(cx + math.cos(a) * r, cy + math.sin(a) * r, ang + 180)


cluster(-4.42, 5.85)            # Y1-Y4
cluster(-4.38, 2.5)             # X1-X4
# A (upper right) and B (lower left), tip to tip
tri_button(5.2, 2.62, 225, 0.98)
tri_button(4.4, 1.82, 45, 0.98)

# speaker at the top right: a darker disc with grille slots on its right half
SPX, SPY, SPR = 4.8, 6.2, 0.78
m.decal_xy([(SPX + SPR * math.cos(2 * math.pi * k / 8), SPY + SPR * math.sin(2 * math.pi * k / 8)) for k in range(8)],
           ZF, SHELL_DK, lift=0.02)
for k in range(3):
    y = SPY - 0.3 + k * 0.3
    m.decal_xy([(SPX + 0.05, y - 0.06), (SPX + 0.6, y - 0.06), (SPX + 0.6, y + 0.06), (SPX + 0.05, y + 0.06)],
               ZF, HOLE, lift=0.04)

# ---------------------------------------------------------------- edges
# EXT port on the right edge
m.polygon([(6.07, 2.2, -0.25), (6.07, 2.2, 0.45), (6.07, 3.0, 0.45), (6.07, 3.0, -0.25)], HOLE, normal=(1, 0, 0))
# power slider in the middle of the left edge (slides up to switch on)
m.polygon([(-6.07, 3.35, 0.0), (-6.07, 4.55, 0.0), (-6.07, 4.55, 0.5), (-6.07, 3.35, 0.5)], HOLE, normal=(-1, 0, 0))
with m.part('switch'):
    m.box(-6.2, 3.45, 0.06, -6.07, 4.05, 0.44, BTN, faces={'right': None})

# ---------------------------------------------------------------- back
# AA battery bulge along the bottom of the back
prof = [(ZB, 0.6), (ZB, 2.1), (ZB - 0.3, 2.0), (ZB - HUMP, 1.75), (ZB - HUMP, 0.95), (ZB - 0.3, 0.7)]
m.extrude_yz(prof, -3.7, 4.3, SHELL_DK)

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
