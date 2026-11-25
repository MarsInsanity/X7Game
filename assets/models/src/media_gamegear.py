# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega Game Gear cartridge (black), standing upright, label to +Z.

Real size ~6.8 x 5.3 x 0.8 cm (wider than tall). Signature features: the
black shell with well-rounded top corners, the large recessed front label
framed by a raised rim, the thicker grip band along the top edge with
horizontal grip lines, and the connector opening with gold contacts along
the bottom of the back.
"""
import math
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (46, 46, 52)         # black plastic (kept just off black so shading reads)
RIM = (66, 66, 74)           # raised rim / grip band face
GRIP = (100, 100, 110)       # grip lines
RECESS = (22, 22, 26)        # connector opening
LABEL = (226, 226, 220)      # label paper
ART = (60, 120, 200)         # label artwork area
BAND = (200, 40, 48)         # label title band
TOPBAND = (16, 16, 20)       # dark strip at the label top
GOLD = (232, 190, 70)        # contacts

W, H = 6.8, 5.3
X0, X1 = -W / 2, W / 2
R = 0.9                      # top corner radius
ZB, ZF, ZR = -0.4, 0.3, 0.4  # back, recessed front, raised rim

LX0, LX1 = -2.95, 2.95       # label recess
LY0, LY1 = 0.55, 3.95


def top_outline(y_from):
    """the outline above y_from: straight sides, rounded top corners"""
    pts = [(X0, y_from), (X1, y_from)]
    for s in range(4):
        a = math.radians(0 + 90 * s / 3)
        pts.append((X1 - R + R * math.cos(a), H - R + R * math.sin(a)))
    for s in range(4):
        a = math.radians(90 + 90 * s / 3)
        pts.append((X0 + R + R * math.cos(a), H - R + R * math.sin(a)))
    return pts


m = Model('gamegear', 'media')

# shell core (its front face is the floor of the label recess)
PX0, PX1, PY0, PY1 = -2.6, 2.6, 1.15, 3.9
core = top_outline(0)
core = [core[0], core[1], (X1, PY0), (X1, PY1)] + core[2:] + [(X0, PY1), (X0, PY0)]
m.extrude_xy(core, ZB, ZF, SHELL, front=False, back=False)
# front: only the label recess floor shows (the rim covers the rest)
m.decal_xy([(LX0, LY0), (LX1, LY0), (LX1, LY1), (LX0, LY1)], ZF, SHELL, lift=0)

# back face built in pieces (small triangles keep depth exact) around a
# raised moulded back plate
m.polygon([(x, y, ZB) for x, y in top_outline(PY1)], SHELL, normal=(0, 0, -1))
for x0, y0, x1, y1 in ((X0, 0, X1, PY0), (X0, PY0, PX0, PY1), (PX1, PY0, X1, PY1)):
    m.polygon([(x0, y0, ZB), (x0, y1, ZB), (x1, y1, ZB), (x1, y0, ZB)], SHELL, normal=(0, 0, -1))
m.box(PX0, PY0, ZB - 0.06, PX1, PY1, ZB, SHELL, faces={'front': None, 'back': RIM})

# raised rim around the label
m.box(X0, 0, ZF, X1, LY0, ZR, SHELL, faces={'back': None})      # bottom band
m.box(X0, LY0, ZF, LX0, LY1, ZR, SHELL, faces={'back': None})                   # left strip
m.box(LX1, LY0, ZF, X1, LY1, ZR, SHELL, faces={'back': None})                   # right strip
m.extrude_xy(top_outline(LY1), ZF, ZR, SHELL, back=False)                      # top band

# grip band: a thicker strip along the rounded top, front and back
GY = 4.25
m.extrude_xy(top_outline(GY), ZR, ZR + 0.08, RIM, back=False)
m.extrude_xy(top_outline(GY), ZB - 0.08, ZB, RIM, front=False)
for i in range(4):
    y = GY + 0.14 + i * 0.2
    m.box(-2.4, y, ZR + 0.08, 2.4, y + 0.09, ZR + 0.14, GRIP, faces={'back': None})
    m.polygon([(-2.4, y, ZB - 0.14), (-2.4, y + 0.09, ZB - 0.14), (2.4, y + 0.09, ZB - 0.14), (2.4, y, ZB - 0.14)],
              GRIP, normal=(0, 0, -1))

# label: paper, dark top strip, artwork window, title band
m.decal_xy([(LX0 + 0.1, LY0 + 0.1), (LX1 - 0.1, LY0 + 0.1), (LX1 - 0.1, LY1 - 0.1), (LX0 + 0.1, LY1 - 0.1)], ZF, LABEL, lift=0.05)
m.decal_xy([(LX0 + 0.25, LY1 - 0.7), (LX1 - 0.25, LY1 - 0.7), (LX1 - 0.25, LY1 - 0.25), (LX0 + 0.25, LY1 - 0.25)], ZF, TOPBAND, lift=0.08)
m.decal_xy([(LX0 + 0.4, LY0 + 0.85), (LX1 - 0.4, LY0 + 0.85), (LX1 - 0.4, LY1 - 0.85), (LX0 + 0.4, LY1 - 0.85)], ZF, ART, lift=0.08)
m.decal_xy([(LX0 + 0.4, LY0 + 0.3), (LX1 - 0.4, LY0 + 0.3), (LX1 - 0.4, LY0 + 0.62), (LX0 + 0.4, LY0 + 0.62)], ZF, BAND, lift=0.08)


# back: connector opening with gold contacts along the bottom edge
def back_rect(x0, y0, x1, y1, z, col):
    m.polygon([(x0, y0, z), (x0, y1, z), (x1, y1, z), (x1, y0, z)], col, normal=(0, 0, -1))


back_rect(-2.9, 0.0, 2.9, 0.75, ZB - 0.02, RECESS)
back_rect(-2.7, 0.08, 2.7, 0.55, ZB - 0.05, GOLD)
for i in range(1, 12):
    x = -2.7 + i * 5.4 / 12
    back_rect(x - 0.04, 0.08, x + 0.04, 0.55, ZB - 0.08, RECESS)


if __name__ == '__main__':
    print(m.stats())
    print(m.save())
