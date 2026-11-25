# SPDX-License-Identifier: GPL-3.0-or-later
"""Game Boy Advance cartridge (the dark grey Game Pak), standing upright,
label to +Z.

Real size 5.7 x 3.5 x 0.8 cm. Signature features (from photos): the wide,
short shell whose top 0.6 cm is a little wider than the rest (the
"shoulders" at both top corners), a gently arched top edge with rounded
corners; on the front a recessed label (about 4.3 x 2.27 cm) sitting low,
with a wide band above it carrying the arched logo strip; on the back the
screw near the top, a recessed panel (embossed text on the real thing) with
a small hole below it, two vertical grooves, and a step across the lower
1.25 cm where the shell gets thinner; the bottom end is open, showing the
gold contacts of the board inside.

The label is the picture area (material "image"): the frontend draws the
game's picture there.

Insertion: the cartridge goes down into the slot at the top back of the
Game Boy Advance with its label facing the console's back; only the top
(about 1 cm) stays visible. Below the shoulders (y < 2.9) the shell is a
closed box 5.5 wide (x -2.75..2.75), z -0.4..+0.4 (back face at -0.38 plus
0.02 decals) for y 1.25..2.9 and z -0.3..+0.4 for y 0..1.25.
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

GREY = (92, 94, 102)         # shell (the usual dark grey Game Pak)
GREY_D = (56, 58, 66)        # recess walls, grooves, connector opening walls
GREY_L = (136, 138, 148)     # arched logo strip above the label
PLATE = (110, 112, 122)      # recessed panel on the back
LABEL = (226, 222, 206)      # plain label paper (picture fallback)
DARK = (26, 26, 32)          # holes, gaps between contacts
GOLD = (214, 172, 64)        # contacts, screw

W, H = 5.7, 3.5
X0, X1 = -W / 2, W / 2       # shoulders: full width
XB = 2.75                    # half width of the body below the shoulders
YS = 2.9                     # bottom of the shoulders
HS = 3.4                     # height at the sides; the top arches up to H
CH = 0.12                    # chamfer of the top corners
LIFT = 0.02                  # back decals stand this far off the back face
ZF = 0.4                     # front
ZB = -0.4 + LIFT             # back face (upper part); decals reach -0.4
ZS, YB = -0.3, 1.25          # back face of the thinner lower part, and where it starts
ZL = ZF - 0.05               # floor of the label recess
LX0, LX1, LY0, LY1 = -2.15, 2.15, 0.48, 2.75   # label recess (= picture area)
SY, SD = 2.92, 0.13          # logo strip above the label: bottom, gap below the arch

m = Model('gba', 'media')


def top_y(x):
    """height of the arched top edge at x (shallow parabolic arch)"""
    t = x / X1
    return HS + (H - HS) * (1 - t * t)


AX = [X1, XB, LX1, 1.45, 0.72, 0, -0.72, -1.45, LX0, -XB, X0]
ARC = [(x, top_y(x)) for x in AX]              # right to left along the top
ARC[0] = (X1, HS - CH)                         # chamfered top corners
ARC[-1] = (X0, HS - CH)


def front_rect(x0, y0, x1, y1, z, col):
    m.quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), col)


def back_rect(x0, y0, x1, y1, z, col):
    m.polygon([(x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z)], col, normal=(0, 0, -1))


def back_disc(cx, cy, r, z, col, n=8):
    m.polygon([(cx + r * math.cos(a * 2 * math.pi / n), cy + r * math.sin(a * 2 * math.pi / n), z)
               for a in range(n)], col, normal=(0, 0, -1))


# ---- shell: a full-height body (z ZS..ZF) plus a back slab over the upper
# part (z ZB..ZS); the step between them runs across the back at y = YB
body = [(-XB, 0), (XB, 0), (XB, YB), (XB, YS), (X1, YS)] + ARC + [(X0, YS), (-XB, YS), (-XB, YB)]
for (xa, ya), (xb, yb) in zip(body[1:], body[2:] + body[:1]):   # every edge but the bottom
    m.quad((xa, ya, ZF), (xa, ya, ZS), (xb, yb, ZS), (xb, yb, ZF), GREY)
slab = [(-XB, YB), (XB, YB), (XB, YS), (X1, YS)] + ARC + [(X0, YS), (-XB, YS)]
m.extrude_xy(slab, ZB, ZS, GREY, front=False)
back_rect(-XB, 0, XB, YB, ZS, GREY)              # back of the thinner lower part

# ---- bottom end: open, the board's gold contacts inside
HX, HZ0, HZ1, HD = 2.45, -0.14, 0.2, 0.3      # connector opening: half width, z range, depth


def bottom_rect(x0, z0, x1, z1, y, col, up=False):
    m.polygon([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], col, normal=(0, 1 if up else -1, 0))


bottom_rect(-XB, HZ1, XB, ZF, 0, GREY)          # bottom rim around the opening
bottom_rect(-XB, ZS, XB, HZ0, 0, GREY)
bottom_rect(-XB, HZ0, -HX, HZ1, 0, GREY)
bottom_rect(HX, HZ0, XB, HZ1, 0, GREY)
# opening walls (facing inwards) and its ceiling: the gold contacts
m.polygon([(-HX, 0, HZ0), (HX, 0, HZ0), (HX, HD, HZ0), (-HX, HD, HZ0)], GREY_D, normal=(0, 0, 1))
m.polygon([(-HX, 0, HZ1), (HX, 0, HZ1), (HX, HD, HZ1), (-HX, HD, HZ1)], GREY_D, normal=(0, 0, -1))
m.polygon([(-HX, 0, HZ0), (-HX, HD, HZ0), (-HX, HD, HZ1), (-HX, 0, HZ1)], GREY_D, normal=(1, 0, 0))
m.polygon([(HX, 0, HZ0), (HX, HD, HZ0), (HX, HD, HZ1), (HX, 0, HZ1)], GREY_D, normal=(-1, 0, 0))
bottom_rect(-HX, HZ0, HX, HZ1, HD, DARK)
bottom_rect(-2.3, HZ0 + 0.06, 2.3, HZ1 - 0.06, HD - 0.02, GOLD)
for i in range(1, 12):
    x = -2.3 + i * 4.6 / 12
    bottom_rect(x - 0.035, HZ0 + 0.06, x + 0.035, HZ1 - 0.06, HD - 0.04, DARK)

# ---- front face (one plane, z = ZF) around the label recess
for (xa, ya), (xb, yb) in zip(ARC[:-1], ARC[1:]):          # xa > xb
    if xb >= XB - 1e-6 or xa <= -XB + 1e-6:                 # shoulders
        m.quad((xb, YS, ZF), (xa, YS, ZF), (xa, ya, ZF), (xb, yb, ZF), GREY)
    elif xb >= LX1 - 1e-6 or xa <= LX0 + 1e-6:              # beside the label
        # outer edge split where the side faces have corners (no T-junctions)
        if xa > 0:
            pts = [(xb, 0), (xa, 0), (xa, YB), (xa, YS), (xa, ya), (xb, yb)]
        else:
            pts = [(xb, 0), (xa, 0), (xa, ya), (xb, yb), (xb, YS), (xb, YB)]
        m.polygon([(x, y, ZF) for x, y in pts], GREY, normal=(0, 0, 1))
    else:                                                   # below / above the label
        front_rect(xb, 0, xa, LY0, ZF, GREY)
        sa, sb = ya - SD, yb - SD
        front_rect(xb, LY1, xa, SY, ZF, GREY)
        m.quad((xb, SY, ZF), (xa, SY, ZF), (xa, sa, ZF), (xb, sb, ZF), GREY_L)
        m.quad((xb, sb, ZF), (xa, sa, ZF), (xa, ya, ZF), (xb, yb, ZF), GREY)

# label recess walls (facing into the recess)
m.polygon([(LX0, LY0, ZF), (LX1, LY0, ZF), (LX1, LY0, ZL), (LX0, LY0, ZL)], GREY_D, normal=(0, 1, 0))
m.polygon([(LX0, LY1, ZF), (LX1, LY1, ZF), (LX1, LY1, ZL), (LX0, LY1, ZL)], GREY_D, normal=(0, -1, 0))
m.polygon([(LX0, LY0, ZF), (LX0, LY1, ZF), (LX0, LY1, ZL), (LX0, LY0, ZL)], GREY_D, normal=(1, 0, 0))
m.polygon([(LX1, LY0, ZF), (LX1, LY1, ZF), (LX1, LY1, ZL), (LX1, LY0, ZL)], GREY_D, normal=(-1, 0, 0))

# recess floor, and the label on it: one picture area
front_rect(LX0, LY0, LX1, LY1, ZL, GREY_D)
m.image_xy(LX0, LY0, LX1, LY1, ZL, fallback=LABEL, lift=0.02)

# ---- back details (decals, lifted to the full 0.8 depth)
ZD = ZB - LIFT
back_rect(-1.1, 1.9, 1.1, 2.82, ZD, PLATE)       # recessed panel
for gx in (-1.6, 1.3):                           # vertical grooves
    back_rect(gx, YB, gx + 0.3, YS, ZD, GREY_D)
back_disc(0, 3.18, 0.18, ZD, GOLD)               # screw
back_disc(0, 1.58, 0.13, ZD, DARK)               # small hole
back_rect(-XB, YB - 0.08, XB, YB, ZS - LIFT, GREY_D)   # shadow line under the step

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
