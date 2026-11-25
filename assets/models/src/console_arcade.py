# SPDX-License-Identifier: GPL-3.0-or-later
"""Generic upright arcade cabinet, low poly (no specific game).

About 65 x 175 x 80 cm. Blue side panels with chrome-grey T-molding and a
bold diagonal art band (red / yellow / orange stripes, abstract only), the
lit cream marquee with an abstract red band at the top, the angled CRT with
a black bezel and a few glowing abstract shapes on the screen, a control
panel that juts out towards the player with a red ball-top joystick, six
buttons in two rows plus two white start buttons, the metal coin door with
two lit coin slots and coin returns, and the kick plate at the bottom.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

SIDE = (30, 60, 170)        # side panels
TRIM = (190, 190, 200)      # T-molding, coin door metal
BODY = (24, 24, 28)         # cabinet front / back
DARK = (72, 72, 82)         # control panel top, bezel, kick plate, slot plates
RED = (228, 36, 36)
YELLOW = (250, 205, 40)
ORANGE = (250, 120, 20)
CREAM = (255, 240, 190)     # lit marquee
SCREEN = (28, 64, 120)      # glowing CRT
GLOW = (90, 230, 120)       # shapes on the screen, green buttons
WHITE = (245, 245, 245)

m = Model('arcade', 'console')

HW = 32.5                   # half width (outer face of a side panel)
SP = 2.0                    # side panel thickness
IN = HW - SP                # inner half width

# ---------------------------------------------------------------- side panels
# side profile (z, y): kick plate / coin door front, control panel shelf,
# screen slope, marquee overhang, flat top, back with a slanted lower part
# the bold diagonal art band rising towards the back is built into the outer
# faces (not laid on top as decals, so no depth fighting from any angle): each
# stripe edge runs from the front edge (z 23) to the back edge (z -40)
BANDS = [(32.0, 112.0), (37.0, 117.0), (41.0, 119.0), (72.0, 150.0), (76.0, 154.0), (84.0, 162.0)]
BAND_COLS = [ORANGE, SIDE, RED, SIDE, YELLOW]
side = ([(-30.0, 0.0), (23.0, 0.0)] + [(23.0, f) for f, _ in BANDS] +
        [(23.0, 88.0), (30.0, 100.0), (18.0, 142.0), (24.0, 150.0), (24.0, 175.0), (-40.0, 175.0)] +
        [(-40.0, b) for _, b in BANDS[::-1]] + [(-40.0, 110.0)])
regions = [([(-30.0, 0.0), (23.0, 0.0), (23.0, 32.0), (-40.0, 112.0), (-40.0, 110.0)], SIDE)]
for (f0, b0), (f1, b1), col in zip(BANDS, BANDS[1:], BAND_COLS):
    regions.append(([(23.0, f0), (23.0, f1), (-40.0, b1), (-40.0, b0)], col))
regions.append(([(23.0, 84.0), (23.0, 88.0), (30.0, 100.0), (18.0, 142.0), (24.0, 150.0),
                 (24.0, 175.0), (-40.0, 175.0), (-40.0, 162.0)], SIDE))

# cabinet body between the side panels: same profile except at the front,
# where marquee, screen, control panel shelf and coin door sit a little back
body = [(-30.0, 0.0), (21.0, 0.0), (21.0, 85.0), (23.0, 104.0), (15.0, 142.0),
        (21.0, 150.0), (21.0, 175.0), (-40.0, 175.0), (-40.0, 110.0)]
# the strip of a side panel's inner face that shows in front of the body
strip = [(23.0, 0.0), (23.0, 88.0), (30.0, 100.0), (18.0, 142.0), (24.0, 150.0), (24.0, 175.0)] + body[1:7][::-1]

# each panel: T-molding edges, the art-banded outer face, and of the inner
# face only the visible front strip (no hidden faces close behind the outer one)
m.extrude_yz(side, IN, HW, SIDE, left=False, right=False, side=TRIM)
m.extrude_yz(side, -HW, -IN, SIDE, left=False, right=False, side=TRIM)
for pts, col in regions:
    m.polygon([(HW, y, z) for z, y in pts], col, normal=(1, 0, 0))
    m.polygon([(-HW, y, z) for z, y in pts], col, normal=(-1, 0, 0))
m.polygon([(IN, y, z) for z, y in strip], SIDE, normal=(-1, 0, 0))
m.polygon([(-IN, y, z) for z, y in strip], SIDE, normal=(1, 0, 0))

# ---------------------------------------------------------------- cabinet body
m.extrude_yz(body, -IN, IN, BODY, right=False, left=False)

# kick plate
m.decal_xy([(-IN, 0.0), (IN, 0.0), (IN, 12.0), (-IN, 12.0)], 21.0, DARK, lift=0.12)

# coin door: metal plate with two lit coin slots and two coin returns
m.box(-13.0, 26.0, 21.0, 13.0, 68.0, 22.2, TRIM, faces={'back': None})
for cx in (-6.5, 6.5):
    m.decal_xy([(cx - 3.5, 54.0), (cx + 3.5, 54.0), (cx + 3.5, 64.0), (cx - 3.5, 64.0)], 22.2, DARK, lift=0.08)
    m.decal_xy([(cx - 0.8, 56.0), (cx + 0.8, 56.0), (cx + 0.8, 62.0), (cx - 0.8, 62.0)], 22.2, RED, lift=0.16)
    m.decal_xy([(cx - 3.0, 40.0), (cx + 3.0, 40.0), (cx + 3.0, 46.0), (cx - 3.0, 46.0)], 22.2, BODY, lift=0.08)

# ---------------------------------------------------------------- screen
# the slanted screen face runs from (z 23, y 104) up to (z 15, y 142)
SZ0, SY0, SZ1, SY1 = 23.0, 104.0, 15.0, 142.0
SL = math.hypot(SZ1 - SZ0, SY1 - SY0)
SN = (0.0, (SZ0 - SZ1) / SL, (SY1 - SY0) / SL)     # outward normal


def screen_decal(rects, color, lift):
    for x0, t0, x1, t1 in rects:
        pts = []
        for x, t in ((x0, t0), (x1, t0), (x1, t1), (x0, t1)):
            pts.append((x, SY0 + (SY1 - SY0) * t + SN[1] * lift, SZ0 + (SZ1 - SZ0) * t + SN[2] * lift))
        m.polygon(pts, color, normal=SN)


screen_decal([(-21.0, 0.12, 21.0, 0.92)], SCREEN, 0.12)
# a few abstract glowing shapes on the CRT
screen_decal([(-15.0, 0.70, -10.0, 0.78), (-5.0, 0.70, 0.0, 0.78), (5.0, 0.70, 10.0, 0.78),
              (-10.0, 0.56, -5.0, 0.64), (0.0, 0.56, 5.0, 0.64), (10.0, 0.56, 15.0, 0.64)], GLOW, 0.24)
screen_decal([(-3.0, 0.18, 3.0, 0.24)], YELLOW, 0.24)
screen_decal([(-0.4, 0.30, 0.4, 0.40)], WHITE, 0.24)

# ---------------------------------------------------------------- marquee
m.box(-IN, 150.5, 21.0, IN, 171.5, 22.5, CREAM,
      faces={'back': None, 'left': None, 'right': None, 'top': BODY, 'bottom': BODY})
m.decal_xy([(-24.0, 157.0), (22.0, 157.0), (24.0, 165.0), (-22.0, 165.0)], 22.5, RED, lift=0.08)
m.decal_xy([(-27.0, 158.0), (-25.0, 158.0), (-23.5, 164.0), (-25.5, 164.0)], 22.5, SIDE, lift=0.08)
m.decal_xy([(25.0, 158.0), (27.0, 158.0), (25.5, 164.0), (23.5, 164.0)], 22.5, SIDE, lift=0.08)
m.decal_xy([(-24.0, 153.0), (24.0, 153.0), (24.0, 154.5), (-24.0, 154.5)], 22.5, ORANGE, lift=0.08)
m.decal_xy([(-24.0, 167.5), (24.0, 167.5), (24.0, 169.0), (-24.0, 169.0)], 22.5, ORANGE, lift=0.08)

# ---------------------------------------------------------------- control panel
# sticks out past the side panels towards the player; its top slopes down
# towards the front
cp = [(20.0, 84.0), (38.0, 92.0), (40.0, 95.0), (40.0, 100.0), (24.0, 104.5), (20.0, 104.5)]
m.extrude_yz(cp, -HW - 0.5, HW + 0.5, DARK)
# chrome front edge
m.decal_xy([(-HW - 0.5, 95.0), (HW + 0.5, 95.0), (HW + 0.5, 100.0), (-HW - 0.5, 100.0)], 40.0, TRIM, lift=0.08)

# parts on the sloped top, built flat around a local origin then tilted onto it
CPZ, CPY = 32.0, 102.25
ANG = math.degrees(math.atan2(104.5 - 100.0, 40.0 - 24.0))
place = lambda p: Model.move(0.0, CPY, CPZ)(Model.rot_x(ANG)(p))  # noqa: E731

parts = []
# joystick: dust washer, shaft, ball top
parts += m.cylinder(-14.0, 0.0, 2.4, -0.1, 0.25, BODY, segments=8, bottom=False)
parts += m.cylinder(-14.0, 0.0, 0.5, 0.25, 6.0, BODY, segments=6, top=False, bottom=False)


def sphere(cx, cy, cz, r, color, lon=8, lat=4):
    out = []
    rings = []
    for j in range(1, lat):
        a = math.pi * j / lat
        rings.append([(cx + r * math.sin(a) * math.cos(2 * math.pi * i / lon),
                       cy + r * math.cos(a),
                       cz + r * math.sin(a) * math.sin(2 * math.pi * i / lon)) for i in range(lon)])
    top, bot = (cx, cy + r, cz), (cx, cy - r, cz)

    def face(a, b, c):
        n = ((b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1]),
             (b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2]),
             (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        g = [(a[k] + b[k] + c[k]) / 3 - (cx, cy, cz)[k] for k in range(3)]
        if n[0] * g[0] + n[1] * g[1] + n[2] * g[2] < 0:
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


parts += sphere(-14.0, 7.2, 0.0, 1.9, RED)

# six action buttons in two slightly curved rows of three
for (bx, bz), col in zip([(0.0, -2.6), (5.5, -3.2), (11.0, -2.6), (0.0, 2.6), (5.5, 2.0), (11.0, 2.6)],
                         [RED, YELLOW, GLOW, RED, YELLOW, GLOW]):
    parts += m.cylinder(bx, bz, 1.5, -0.1, 0.9, col, segments=8, bottom=False)
# 1P / 2P start buttons near the screen
for bx in (-4.5, 0.5):
    parts += m.cylinder(bx, -6.6, 1.0, -0.1, 0.7, WHITE, segments=6, bottom=False)

m.transform(parts, place)

print(m.stats())
m.save()
