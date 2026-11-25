# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly SNK Neo Geo Pocket Color (platinum blue), handheld standing
upright, screen facing +Z, origin at the bottom centre.

Real size about 13.0 x 8.0 x 2.6 cm (body; buttons add a little).
Proportions measured from Commons photos (front, back, three-quarter and
the four edge views):
  * landscape body, flat top edge with small corners, big round bottom
    corners; the front face ends in a wide sloping "chin" along the bottom
  * black screen bezel 6.5 x 6.3 cm, centred, reaching almost from the top
    edge down to the chin; the grey LCD inside it 4.9 x 4.6 cm
  * left: the clicky joystick (silver notched gate ring, smoky black cap)
    at x -4.6, y 4.7; power pill top left with a line to the power lamp;
    speaker dots below the joystick
  * right: A (x 4.0, y 4.7) lower left, B (x 5.3, y 5.6) upper right,
    small round OPTION button in the top right corner, dot pattern below
  * back: two full-depth humps (AA battery door behind the A/B side, the
    round coin-cell cover behind the joystick side) and a thinner centre
    column with the rating plate; at the top of that column a recess
    5.6 cm wide and 1.55 cm tall, open to the top and the back: the
    cartridge drops into it, picture side facing back, and its body goes
    down through a slot into a cavity behind the screen
No text, no logos. No moving parts (the real slot has no lid or lock).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

FACE = (148, 158, 210)      # platinum blue front face
EDGE = (112, 122, 180)      # front shell sides and the chin bevel
BACK = (98, 106, 164)        # back shell, darker
PLATE = (196, 198, 206)     # rating plate on the back (plain, no text)
DOOR = (60, 66, 112)        # battery door / coin cover outlines
BEZEL = (24, 24, 30)        # black glass around the screen
LCD = (172, 180, 168)       # grey-green screen
GATE = (204, 208, 222)      # silver joystick gate ring
STICK = (44, 44, 56)        # smoky black cap and buttons
DIMPLE = (90, 92, 108)      # square dimple on the cap
HOLE = (16, 16, 22)         # speaker dots, cavity, ports
LED = (200, 40, 40)         # power lamp

m = Model('ngpc', 'console')

W, H = 13.0, 8.0
X0, X1 = -W / 2, W / 2
ZBK = -1.3                  # back of the humps
ZCB = -0.85                 # back of the centre column
ZM = 0.25                   # front shell / back shell split
ZS = 1.0                    # front shell side edge
ZF = 1.3                    # front face
RT, RB = 0.5, 1.4           # top / bottom corner radii

CW = 2.8                    # centre column / cartridge recess half width
RY = 6.45                   # recess floor (the recess is 1.55 cm tall)
# cartridge seated: picture to -Z, body x -2.4..2.4, z -0.65..0.15,
# y 3.5..7.1; lip x -2.48..2.48, z -0.8..0.15, y 7.1..8.0
SX, SZ0, SZ1 = 2.5, -0.75, ZM   # slot opening / cavity
CY = 3.4                    # cavity floor


def outline(x0, y0, x1, y1, rt, rb, bottom=None, nt=3, nb=4):
    """CCW outline: rounded top corners rt, bottom corners rb; `bottom`
    = y of the 3 extra points along the bottom edge (left to right)."""
    pts = []
    for cx, cy, r, a0, n in ((x1 - rt, y1 - rt, rt, 0, nt), (x0 + rt, y1 - rt, rt, 90, nt),
                             (x0 + rb, y0 + rb, rb, 180, nb), (x1 - rb, y0 + rb, rb, 270, nb)):
        for s in range(n + 1):
            a = math.radians(a0 + 90 * s / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        if a0 == 180:
            xa, xb = x0 + rb, x1 - rb
            for k, t in enumerate((0.2, 0.5, 0.8)):
                pts.append((xa + (xb - xa) * t, bottom[k] if bottom else y0))
    return pts


def ring(outer, oz, inner, iz, color):
    """Band between two matching outlines (outer at oz, inner at iz > oz)."""
    n = len(outer)
    for i in range(n):
        a, b = outer[i], outer[(i + 1) % n]
        c, d = inner[(i + 1) % n], inner[i]
        m.quad((a[0], a[1], oz), (b[0], b[1], oz), (c[0], c[1], iz), (d[0], d[1], iz), color)


def clip_x(pts, xc, keep_right):
    """Clip a 2D polygon by the vertical line x = xc."""
    out = []
    n = len(pts)
    inside = (lambda p: p[0] >= xc) if keep_right else (lambda p: p[0] <= xc)
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        if inside(p):
            out.append(p)
        if inside(p) != inside(q):
            t = (xc - p[0]) / (q[0] - p[0])
            out.append((xc, p[1] + (q[1] - p[1]) * t))
    return out


def disc(cx, cy, r, z, color, n=10, lift=0.02):
    m.decal_xy([(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)],
               z, color, lift)


def disc_back(cx, cy, r, z, color, n=10, lift=0.02):
    m.polygon([(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z - lift)
               for i in range(n)], color, normal=(0, 0, -1))


def rect_back(x0, y0, x1, y1, z, color, lift=0.02):
    m.polygon([(x0, y0, z - lift), (x1, y0, z - lift), (x1, y1, z - lift), (x0, y1, z - lift)], color,
              normal=(0, 0, -1))


# ---------------------------------------------------------------- front shell
OUT = outline(X0, 0, X1, H, RT, RB)
# the face: inset a little at the top and sides, a lot at the bottom (the
# chin), its bottom edge bowed down in the middle
INN = outline(X0 + 0.16, 1.35, X1 - 0.16, H - 0.12, RT - 0.1, 1.3, bottom=(1.2, 1.1, 1.2))
m.extrude_xy(OUT, ZM, ZS, EDGE, front=False, back=False)
ring(OUT, ZS, INN, ZF, EDGE)
m.polygon([(x, y, ZF) for x, y in INN], FACE, normal=(0, 0, 1))

# ---------------------------------------------------------------- back shell
for right in (True, False):
    hump = clip_x(OUT, CW if right else -CW, right)
    m.extrude_xy(hump, ZBK, ZM, BACK, front=False)
# centre column below the recess (its sides are inside the humps)
m.box(-CW, 0, ZCB, CW, RY, ZM, BACK, faces={'front': None, 'top': None, 'left': None, 'right': None})
# recess floor: a frame round the slot opening
m.quad((-CW, RY, ZCB), (-CW, RY, SZ0), (CW, RY, SZ0), (CW, RY, ZCB), BACK)
m.quad((-CW, RY, SZ0), (-CW, RY, ZM), (-SX, RY, ZM), (-SX, RY, SZ0), BACK)
m.quad((SX, RY, SZ0), (SX, RY, ZM), (CW, RY, ZM), (CW, RY, SZ0), BACK)
# recess front wall (back of the front shell, seen through the recess)
m.quad((CW, RY, ZM), (-CW, RY, ZM), (-CW, H, ZM), (CW, H, ZM), DOOR)
# cavity the cartridge body drops into (faces point inwards)
m.quad((-SX, CY, SZ0), (SX, CY, SZ0), (SX, RY, SZ0), (-SX, RY, SZ0), HOLE)        # back wall, faces +Z
m.quad((SX, CY, ZM), (-SX, CY, ZM), (-SX, RY, ZM), (SX, RY, ZM), HOLE)            # front wall, faces -Z
m.quad((-SX, CY, ZM), (-SX, CY, SZ0), (-SX, RY, SZ0), (-SX, RY, ZM), HOLE)        # left, faces +X
m.quad((SX, CY, SZ0), (SX, CY, ZM), (SX, RY, ZM), (SX, RY, SZ0), HOLE)            # right, faces -X
m.quad((-SX, CY, ZM), (SX, CY, ZM), (SX, CY, SZ0), (-SX, CY, SZ0), HOLE)          # floor, faces +Y

# ---------------------------------------------------------------- back details
rect_back(-2.35, 2.5, 2.35, 5.85, ZCB, PLATE)                       # rating plate
# AA battery door on the +X hump (outline + door)
rect_back(3.05, 1.05, 6.15, 7.35, ZBK, DOOR)
rect_back(3.2, 1.2, 6.0, 7.2, ZBK, BACK, lift=0.04)
# round coin-cell cover on the -X hump
disc_back(-4.75, 2.1, 1.2, ZBK, DOOR, n=12)
disc_back(-4.75, 2.1, 1.05, ZBK, BACK, n=12, lift=0.04)
for sx, sy in ((-4.55, 6.3), (-5.6, 3.9)):
    disc_back(sx, sy, 0.22, ZBK, HOLE, n=6)                        # screw wells
# EXT port on the top edge, +X side, near the front
m.decal_xz([(3.9, 0.35), (4.7, 0.35), (4.7, 0.7), (3.9, 0.7)], H, HOLE)

# ---------------------------------------------------------------- screen
m.decal_xy(Model.rounded_rect(-3.25, 1.3, 3.25, 7.6, 0.3, 2), ZF, BEZEL, lift=0.02)
m.decal_xy([(-2.43, 2.0), (2.43, 2.0), (2.43, 6.62), (-2.43, 6.62)], ZF, LCD, lift=0.04)

# ---------------------------------------------------------------- left side
JX, JY = -4.6, 4.7
disc(JX, JY, 1.05, ZF, GATE, n=12)                                  # silver notched gate
disc(JX, JY, 0.82, ZF, STICK, n=12, lift=0.04)                      # dark well
m.cylinder_z(JX, JY, 0.62, ZF, ZF + 0.3, STICK, segments=10, back=False)   # smoky cap
m.decal_xy([(JX - 0.16, JY - 0.16), (JX + 0.16, JY - 0.16), (JX + 0.16, JY + 0.16), (JX - 0.16, JY + 0.16)],
           ZF + 0.3, DIMPLE)
# power pill, line, lamp
m.box(-5.8, 6.42, ZF - 0.05, -5.0, 6.78, ZF + 0.12, STICK, faces={'back': None})
m.decal_xy([(-5.0, 6.57), (-4.3, 6.57), (-4.3, 6.63), (-5.0, 6.63)], ZF, HOLE)
disc(-4.18, 6.6, 0.09, ZF, LED, n=6)
# speaker dots 4 x 3
for i in range(4):
    for j in range(3):
        x, y = -5.1 + 0.3 * i, 1.85 + 0.3 * j
        m.decal_xy([(x - 0.07, y - 0.07), (x + 0.07, y - 0.07), (x + 0.07, y + 0.07), (x - 0.07, y + 0.07)],
                   ZF, HOLE)

# ---------------------------------------------------------------- right side
for bx, by in ((4.0, 4.7), (5.3, 5.6)):                             # A, B
    disc(bx, by, 0.56, ZF, BEZEL, n=8)
    m.cylinder_z(bx, by, 0.44, ZF, ZF + 0.22, STICK, segments=8, back=False)
m.cylinder_z(5.25, 7.15, 0.25, ZF, ZF + 0.12, STICK, segments=8, back=False)   # OPTION
# dot pattern below the buttons (3 x 3)
for i in range(3):
    for j in range(3):
        x, y = 3.7 + 0.75 * i + 0.1 * j, 1.75 + 0.6 * j
        m.decal_xy([(x - 0.06, y - 0.06), (x + 0.06, y - 0.06), (x + 0.06, y + 0.06), (x - 0.06, y + 0.06)],
                   ZF, EDGE)

print(m.stats())
m.save()
