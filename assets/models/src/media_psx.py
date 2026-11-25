# SPDX-License-Identifier: GPL-3.0-or-later
"""PlayStation game disc: a bare 12 cm "black-bottom" CD standing upright,
label side to +Z.

Real size (Red Book CD): 12.0 cm across, 1.2 mm thick, 1.5 cm centre hole.
What makes it a PlayStation disc is the black-tinted polycarbonate: the
whole read side is near black (a faint purple-blue sheen), and wherever no
print covers the plastic on the label side it reads black too: the clamping
hub around the hole and a thin rim at the outer edge. Seen from the label
side: the dark hub around the hole (out to ~3.8 cm across), a narrow bright
silver band (the metal layer at the stacking ring), the printed label (the
game's picture) from 4.6 cm to 11.8 cm across, and the thin black rim.

Layout: centre at (0, 6, 0); the lowest outer vertex touches y = 0. The
disc body runs z = -0.06 .. +0.06 (1.2 mm); the picture is a ring lifted
0.02 cm off the label side (z = +0.08), so the whole model spans
12.0 x 12.0 x 0.14 cm. It goes into the console label side UP (the round
lid opens, the disc drops onto the spindle, the lid closes); that path is
in assets/models/systems/psx.json, made with the console.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

LABEL = (176, 178, 188)       # picture fallback: a plain light-grey printed label
SILVER = (230, 232, 240)      # metal band between the hub and the print
HUB = (44, 40, 58)            # black-tinted clear hub (label side)
RIM = (26, 22, 34)            # black plastic rim outside the print
UNDER = (40, 32, 62)          # the black read side (faint purple sheen)
EDGE = (78, 72, 96)           # outer edge and hole wall (tinted clear plastic)

R = 6.0                       # outer radius
R_HOLE = 0.75                 # 1.5 cm centre hole
R_HUB = 1.9                   # dark clamping hub
R_LAB0, R_LAB1 = 2.3, 5.9     # printed label ring (the picture)
R_SIL = 2.42                  # silver band runs on under the print (its 12-gon
                              # edge then never peeks out past the 24-gon picture)
CY = R                        # centre height: lowest vertex on y = 0
ZB, ZF = -0.06, 0.06          # read side / label side (1.2 mm)
LIFT = 0.02                   # picture above the label side

N = 24                        # outer segments (a vertex straight down)
NH = 12                       # hub and hole segments

m = Model('psx', 'media')


def pt(r, i, n, z):
    a = -math.pi / 2 + 2 * math.pi * i / n
    return (r * math.cos(a), CY + r * math.sin(a), z)


def ring(r0, n0, r1, n1, z, color, normal):
    """Flat annulus r0 (n0 segments) .. r1 (n1 = n0 or 2 * n0 segments)."""
    k = n1 // n0
    for i in range(n0):
        outer = [pt(r1, k * i + j, n1, z) for j in range(k + 1)]
        m.polygon([pt(r0, i, n0, z), pt(r0, i + 1, n0, z)] + outer[::-1], color, normal=normal)


def wall(r, n, color, outward):
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * (i + 0.5) / n
        d = 1 if outward else -1
        m.polygon([pt(r, i, n, ZB), pt(r, i + 1, n, ZB), pt(r, i + 1, n, ZF), pt(r, i, n, ZF)],
                  color, normal=(d * math.cos(a), d * math.sin(a), 0))


# label side (+Z): black hub, silver band, black plastic under the print and
# at the rim; the picture lies on top
ring(R_HOLE, NH, R_HUB, NH, ZF, HUB, (0, 0, 1))
ring(R_HUB, NH, R_SIL, NH, ZF, SILVER, (0, 0, 1))
ring(R_SIL, NH, R, N, ZF, RIM, (0, 0, 1))
# read side (-Z): black all over
ring(R_HOLE, NH, R, N, ZB, UNDER, (0, 0, -1))
# outer edge and the centre hole's wall
wall(R, N, EDGE, True)
wall(R_HOLE, NH, EDGE, False)

# the printed label = the game's picture, upright (u = left to right, v = up)
m.image_ring(0, CY, ZF + LIFT, R_LAB0, R_LAB1, segments=N, fallback=LABEL)

print(m.stats())
m.save()
