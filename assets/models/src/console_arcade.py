# SPDX-License-Identifier: GPL-3.0-or-later
"""Generic upright arcade cabinet, low poly (no specific game).

64 x 175 x 81 cm, built from photos of classic early-80s uprights (Donkey
Kong, Pac-Man / Super Pac-Man, Asteroids, Star Wars). The signature
side profile: a tall vertical lower front with the coin door, a control
panel that juts out at waist height (top at 95-100 cm), the monitor bezel
leaning back inside a deep recess, the lit marquee box overhanging the
screen at the top, and a straight vertical back. Two side panels with
light T-molding edges and abstract side art (three diagonal stripes
rising towards the back) frame the black middle.

Front, top to bottom: the lit marquee (abstract art, no text), the black
bezel with a coloured frame around the glowing CRT, the control panel
with a yellow overlay, a red ball-top joystick, three action buttons and
two white start buttons, the lower front with the metal coin door (two
lit coin entries, coin returns, lock), and the recessed black toe kick.

Back: the big upper rear door (vents, lock) and, at 43-57 cm, the board
hatch: a metal panel (moving part "hatch", hinged along its bottom edge)
that folds down to open the board compartment. Inside, a plywood shelf
with two guide rails and the edge connector of the wiring harness at the
front: the game board slides in flat, connector first, and plugs in.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (22, 22, 26)          # black cabinet: toe kick, bezel, marquee box, back
SIDE = (30, 62, 172)         # side panels and lower front
TRIM = (206, 206, 214)       # T-molding, coin entries, lock
RED = (230, 40, 40)
YELLOW = (250, 206, 40)
ORANGE = (250, 128, 24)
MARQ = (255, 244, 204)       # lit marquee
SCREEN = (24, 60, 118)       # glowing CRT
GLOW = (110, 230, 140)       # shapes on the screen, a button
WHITE = (245, 245, 245)      # start buttons, harness connector
METAL = (112, 112, 124)      # coin door, board hatch, rails
DOOR = (58, 58, 66)          # upper rear door
WOOD = (186, 146, 92)        # plywood shelf in the board compartment
INNER = (10, 10, 12)         # compartment inside, slots

m = Model('arcade', 'console')

HW = 32.0                    # half width at the side panels' outer faces
IN = 30.2                    # inner face of a side panel (body half width)
BACK = -37.0                 # the back (vertical, full height)

# ---------------------------------------------------------------- profiles
# (z, y) side profile of the side panels: bottom, vertical lower front,
# the bulge around the control panel, the curve back past the screen, the
# straight top front beside the marquee, the top and the back
SIDE_PROF = [(BACK, 0.0), (36.0, 0.0), (36.0, 84.0), (44.0, 88.0), (44.0, 97.0), (31.0, 102.0),
             (26.0, 110.0), (23.0, 122.0), (22.6, 140.0), (23.0, 175.0), (BACK, 175.0)]
# the black middle between the side panels, each front edge with its colour
# (the bottom and the back are built separately)
BODY_FRONT = [((31.0, 0.0), BODY),          # toe kick
              ((31.0, 7.0), BODY),          # toe kick top
              ((35.0, 7.0), SIDE),          # lower front (coin door)
              ((35.0, 84.0), BODY),         # control panel underside
              ((43.0, 88.0), BODY),         # control panel front edge
              ((43.0, 95.0), BODY),         # control panel top (overlay on it)
              ((25.0, 100.0), BODY),        # monitor bezel, leaning back
              ((12.0, 147.0), BODY),        # marquee box underside
              ((22.0, 147.0), BODY),        # marquee front
              ((22.0, 175.0), BODY)]        # top
TOP = 175.0


def clip(poly, a, b, c):
    """Keep the part of a 2D polygon where a*z + b*y <= c (Sutherland-Hodgman)."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
        if fp <= 0:
            out.append(p)
        if (fp < 0 < fq) or (fq < 0 < fp):
            t = fp / (fp - fq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


# ---------------------------------------------------------------- side panels
# side art: three stripes rising from the lower front towards the upper back
# (edges y = y_front + SLOPE * (36 - z)); a stripe of blue between them
SLOPE = 1.25
EDGES = [24.0, 34.0, 37.0, 47.0, 50.0, 60.0]
COLS = [SIDE, RED, SIDE, ORANGE, SIDE, YELLOW, SIDE]
regions = []
for i, col in enumerate(COLS):
    poly = list(SIDE_PROF)
    # line value: y + SLOPE * z  (constant along a stripe edge)
    if i > 0:
        c = EDGES[i - 1] + SLOPE * 36.0
        poly = clip(poly, -SLOPE, -1.0, -c)              # keep y + S z >= c
    if i < len(EDGES):
        c = EDGES[i] + SLOPE * 36.0
        poly = clip(poly, SLOPE, 1.0, c)                 # keep y + S z <= c
    if len(poly) >= 3:
        regions.append((poly, col))

# T-molding all round (the bottom is never seen)
n = len(SIDE_PROF)
for sx in (1, -1):
    xo, xi = sx * HW, sx * IN
    for i in range(n):
        (za, ya), (zb, yb) = SIDE_PROF[i], SIDE_PROF[(i + 1) % n]
        if ya == 0.0 and yb == 0.0:
            continue
        q = [(xo, ya, za), (xi, ya, za), (xi, yb, zb), (xo, yb, zb)]
        # outward: away from the profile's inside
        m.polygon(q, TRIM, normal=(0.0, -(zb - za), (yb - ya)))
    for pts, col in regions:
        m.polygon([(xo, y, z) for z, y in pts], col, normal=(sx, 0, 0))

# a big eight-pointed star high on each side, towards the back
star = []
for k in range(16):
    a = math.radians(90 + k * 22.5)
    r = 14.0 if k % 2 == 0 else 5.6
    star.append((-7.0 + r * math.cos(a), 138.0 + r * math.sin(a)))
for sx in (1, -1):
    m.polygon([(sx * (HW + 0.05), y, z) for z, y in star], YELLOW, normal=(sx, 0, 0))

# the inner faces of the side panels: only the strip in front of the black
# middle shows
front_pts = [p for p, _ in BODY_FRONT]
strip = [(36.0, 0.0), (36.0, 84.0), (44.0, 88.0), (44.0, 97.0), (31.0, 102.0), (26.0, 110.0),
         (23.0, 122.0), (22.6, 140.0), (23.0, TOP)] + front_pts[::-1]
for sx in (1, -1):
    m.polygon([(sx * IN, y, z) for z, y in strip], SIDE, normal=(-sx, 0, 0))

# ---------------------------------------------------------------- black middle
prof = front_pts + [(BACK, TOP)]
for i in range(len(prof) - 1):
    (za, ya), (zb, yb) = prof[i], prof[i + 1]
    col = BODY_FRONT[i][1] if i < len(BODY_FRONT) else BODY
    m.polygon([(IN, ya, za), (-IN, ya, za), (-IN, yb, zb), (IN, yb, zb)], col,
              normal=(0.0, -(zb - za), (yb - ya)))

# the back with the board-compartment opening
OX, OY0, OY1 = 16.0, 44.0, 56.0          # opening x -16..16, y 44..56
for x0, y0, x1, y1 in ((-IN, 0.0, IN, OY0), (-IN, OY1, IN, TOP), (-IN, OY0, -OX, OY1), (OX, OY0, IN, OY1)):
    m.polygon([(x0, y0, BACK), (x1, y0, BACK), (x1, y1, BACK), (x0, y1, BACK)], BODY, normal=(0, 0, -1))

# ---------------------------------------------------------------- toe kick, coin door
# metal coin door standing 1.2 cm proud of the lower front
CD = (-15.0, 20.0, 15.0, 62.0)
m.box(CD[0], CD[1], 35.0, CD[2], CD[3], 36.2, BODY, faces={'back': None, 'bottom': None, 'front': DOOR})
ZD = 36.2


def dec(x0, y0, x1, y1, col, z=ZD, lift=0.05):
    m.decal_xy([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z, col, lift=lift)


dec(CD[0], 44.6, CD[2], 45.3, INNER)                 # gap between coin door and cash door
for cx in (-6.5, 6.5):
    dec(cx - 3.2, 48.5, cx + 3.2, 59.0, TRIM)        # coin entry plate
    dec(cx - 0.7, 50.0, cx + 0.7, 57.5, RED, lift=0.1)   # lit coin slot
    dec(cx - 2.6, 38.0, cx + 2.6, 42.0, INNER)       # coin return
dec(-1.0, 30.0, 1.0, 32.5, TRIM)                     # cash door lock

# ---------------------------------------------------------------- monitor bezel and screen
# the bezel runs from (z 25, y 100) up to (z 12, y 147)
BZ0, BY0, BZ1, BY1 = 25.0, 100.0, 12.0, 147.0
BL = math.hypot(BZ1 - BZ0, BY1 - BY0)
BN = (0.0, (BZ0 - BZ1) / BL, (BY1 - BY0) / BL)     # outward normal


def bezel(pts, col, lift):
    """pts: (x, t) with t 0 (bottom) .. 1 (top) along the bezel."""
    m.polygon([(x, BY0 + (BY1 - BY0) * t + BN[1] * lift, BZ0 + (BZ1 - BZ0) * t + BN[2] * lift)
               for x, t in pts], col, normal=BN)


def brect(x0, t0, x1, t1, col, lift):
    bezel([(x0, t0), (x1, t0), (x1, t1), (x0, t1)], col, lift)


# coloured bezel art frame around the screen (four trapezoids)
S0, S1, SX = 0.10, 0.72, 20.0                       # screen t range, half width
F0, F1, FX = 0.03, 0.80, 26.5                       # frame outer edge
brect(-FX, F0, FX, S0, YELLOW, 0.06)
brect(-FX, S1, FX, F1, YELLOW, 0.06)
brect(-FX, S0, -SX, S1, YELLOW, 0.06)
brect(SX, S0, FX, S1, YELLOW, 0.06)
brect(-SX, S0, SX, S1, SCREEN, 0.06)
# a few abstract glowing shapes on the CRT
for x0, t0 in ((-14.0, 0.58), (-6.0, 0.58), (2.0, 0.58), (10.0, 0.58), (-10.0, 0.48), (-2.0, 0.48), (6.0, 0.48)):
    brect(x0, t0, x0 + 4.0, t0 + 0.05, GLOW, 0.12)
brect(-2.0, 0.15, 2.0, 0.20, ORANGE, 0.12)          # the player's ship
brect(-0.3, 0.24, 0.3, 0.31, WHITE, 0.12)           # its shot

# ---------------------------------------------------------------- marquee
MZ = 22.0
m.decal_xy([(-28.6, 149.0), (28.6, 149.0), (28.6, 173.0), (-28.6, 173.0)], MZ, MARQ, lift=0.05)
# abstract marquee art: a red band with orange edges and two blue chevrons
m.decal_xy([(-22.0, 156.0), (20.0, 156.0), (23.0, 166.0), (-19.0, 166.0)], MZ, RED, lift=0.1)
m.decal_xy([(-25.0, 152.5), (25.0, 152.5), (25.0, 154.0), (-25.0, 154.0)], MZ, ORANGE, lift=0.1)
m.decal_xy([(-25.0, 168.0), (25.0, 168.0), (25.0, 169.5), (-25.0, 169.5)], MZ, ORANGE, lift=0.1)
m.decal_xy([(-27.0, 156.0), (-24.0, 156.0), (-21.0, 166.0), (-24.0, 166.0)], MZ, SIDE, lift=0.1)
m.decal_xy([(24.5, 156.0), (27.5, 156.0), (27.5, 166.0), (27.0, 166.0)], MZ, SIDE, lift=0.1)

# ---------------------------------------------------------------- control panel
# its top runs from (z 43, y 95) back up to (z 25, y 100)
CPA = math.degrees(math.atan2(100.0 - 95.0, 43.0 - 25.0))
CPZ, CPY = 34.0, 97.5                    # middle of the top
place = lambda p: Model.move(0.0, CPY, CPZ)(Model.rot_x(CPA)(p))  # noqa: E731
HALF = math.hypot(9.0, 2.5)             # half depth of the top along the slope

cp = []
cp += m.decal_xz([(-28.0, -HALF + 1.0), (28.0, -HALF + 1.0), (28.0, HALF - 1.2), (-28.0, HALF - 1.2)],
                 0.0, YELLOW, lift=0.05)
# joystick: dust washer, shaft, red ball top
JX, JZ = -15.0, 1.5
cp += m.cylinder(JX, JZ, 2.2, 0.05, 0.3, BODY, segments=6, bottom=False)
cp += m.cylinder(JX, JZ, 0.5, 0.3, 5.5, BODY, segments=4, top=False, bottom=False)


def ball(cx, cy, cz, r, color, lon=6, lat=3):
    out = []
    rings = []
    for j in range(1, lat):
        a = math.pi * j / lat
        rings.append([(cx + r * math.sin(a) * math.cos(2 * math.pi * (i + 0.5 * j) / lon),
                       cy + r * math.cos(a),
                       cz + r * math.sin(a) * math.sin(2 * math.pi * (i + 0.5 * j) / lon)) for i in range(lon)])
    top, bot = (cx, cy + r, cz), (cx, cy - r, cz)

    def face(a, b, c):
        nrm = ((b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1]),
               (b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2]),
               (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        g = [(a[k] + b[k] + c[k]) / 3 - (cx, cy, cz)[k] for k in range(3)]
        if nrm[0] * g[0] + nrm[1] * g[1] + nrm[2] * g[2] < 0:
            b, c = c, b
        return m.tri(a, b, c, color)
    for i in range(lon):
        k = (i + 1) % lon
        out += face(top, rings[0][i], rings[0][k])
        out += face(bot, rings[-1][k], rings[-1][i])
        for j in range(len(rings) - 1):
            out += face(rings[j][i], rings[j + 1][i], rings[j + 1][k])
            out += face(rings[j][i], rings[j + 1][k], rings[j][k])
    return out


cp += ball(JX, 6.8, JZ, 2.0, RED)
# three action buttons in a slight arc, two white start buttons behind
for (bx, bz), col in zip([(-3.0, 2.2), (3.0, 1.4), (9.0, 2.2)], [RED, SIDE, GLOW]):
    cp += m.cylinder(bx, bz, 1.8, 0.05, 1.0, col, segments=6, bottom=False)
for bx in (-3.0, 3.0):
    cp += m.cylinder(bx, -4.8, 1.2, 0.05, 0.8, WHITE, segments=6, bottom=False)
m.transform(cp, place)

# ---------------------------------------------------------------- back
# upper rear door with two rows of vent slots and a lock
m.polygon([(23.0, 92.0, BACK - 0.05), (-23.0, 92.0, BACK - 0.05), (-23.0, 160.0, BACK - 0.05),
           (23.0, 160.0, BACK - 0.05)], DOOR, normal=(0, 0, -1))
for y0 in (148.0, 104.0):
    m.polygon([(18.0, y0, BACK - 0.1), (-18.0, y0, BACK - 0.1), (-18.0, y0 + 5.0, BACK - 0.1),
               (18.0, y0 + 5.0, BACK - 0.1)], INNER, normal=(0, 0, -1))
m.polygon([(-19.0, 125.0, BACK - 0.1), (-21.0, 125.0, BACK - 0.1), (-21.0, 129.0, BACK - 0.1),
           (-19.0, 129.0, BACK - 0.1)], TRIM, normal=(0, 0, -1))

# ---------------------------------------------------------------- board compartment
# a dark box behind the opening; its floor is the plywood shelf
CZ = -7.0                                # front wall of the compartment
m.polygon([(-OX, OY1, BACK), (OX, OY1, BACK), (OX, OY1, CZ), (-OX, OY1, CZ)], INNER, normal=(0, -1, 0))
m.polygon([(-OX, OY0, BACK), (-OX, OY1, BACK), (-OX, OY1, CZ), (-OX, OY0, CZ)], INNER, normal=(1, 0, 0))
m.polygon([(OX, OY0, BACK), (OX, OY1, BACK), (OX, OY1, CZ), (OX, OY0, CZ)], INNER, normal=(-1, 0, 0))
m.polygon([(-OX, OY0, CZ), (OX, OY0, CZ), (OX, OY1, CZ), (-OX, OY1, CZ)], INNER, normal=(0, 0, -1))
m.polygon([(-OX, OY0, BACK), (OX, OY0, BACK), (OX, OY0, CZ), (-OX, OY0, CZ)], WOOD, normal=(0, 1, 0))
# guide rails along both walls (the board's edges run between them)
RX = 15.15
for sx in (1, -1):
    x0, x1 = sorted((sx * RX, sx * OX))
    m.box(x0, OY0, BACK, x1, OY0 + 1.6, CZ, METAL,
          faces={'bottom': None, 'front': None, ('right' if sx > 0 else 'left'): None})
# the harness's edge connector: two jaws the board's gold tab slides between
m.box(-6.5, OY0, CZ - 0.9, 6.5, 44.78, CZ, WHITE, faces={'bottom': None, 'front': None})
m.box(-6.5, 45.12, CZ - 0.9, 6.5, 46.0, CZ, WHITE, faces={'front': None})
# wires of the harness going up the front wall
for x in (-5.0, -1.5, 2.0, 5.0):
    m.polygon([(x - 0.5, 46.0, CZ - 0.05), (x + 0.5, 46.0, CZ - 0.05), (x + 0.5, OY1, CZ - 0.05),
               (x - 0.5, OY1, CZ - 0.05)], RED if x < 0 else YELLOW, normal=(0, 0, -1))

# ---------------------------------------------------------------- board hatch (moving part)
# a metal panel screwed over the opening, hinged along its bottom edge;
# it folds down and back to open (see systems/arcade.json)
HX, HY0, HY1, HT = 17.5, 43.0, 57.0, 0.8
with m.part('hatch'):
    m.box(-HX, HY0, BACK - HT, HX, HY1, BACK, METAL)
    zb = BACK - HT
    for y in (52.5, 50.5, 48.5):            # vent slits
        m.polygon([(12.0, y, zb - 0.05), (-12.0, y, zb - 0.05), (-12.0, y + 0.8, zb - 0.05),
                   (12.0, y + 0.8, zb - 0.05)], INNER, normal=(0, 0, -1))
    m.polygon([(1.2, 54.4, zb - 0.05), (-1.2, 54.4, zb - 0.05), (-1.2, 56.0, zb - 0.05),
               (1.2, 56.0, zb - 0.05)], TRIM, normal=(0, 0, -1))    # latch

print(m.stats())
m.save()
