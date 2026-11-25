# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega CD game disc: a bare 12 cm CD standing upright, label side to +Z.

Real size (ECMA-130 / Red Book): 12.0 cm across, 1.2 mm thick, 1.5 cm
centre hole, clear centre (clamping area, stacking ring) out to ~4.2 cm
across. Seen from the label side: the clear hub around the hole (it reads
dark, being see-through), a narrow bright silver band (the
metal layer under the lacquer, between hub and print), the printed label
(the game's picture) out to ~11.7 cm and a thin silver rim at the edge.
The underside is plain silver with the same clear hub.

Layout: centre at (0, 6, 0); the lowest outer vertex touches y = 0. The
disc body runs z = -0.07 .. +0.05 (1.2 mm); the picture is a ring lifted
0.02 cm off the label side (z = +0.07), so the whole model spans
12.0 x 12.0 x 0.14 cm. The insertion (console tray, label side up) is
in assets/models/systems/segacd.json, made with the console.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

LABEL = (40, 40, 50)          # picture fallback: the dark printed label
SILVER_F = (218, 222, 232)    # label side: lacquered metal band and outer rim
SILVER_B = (206, 212, 226)    # underside (read side): silver mirror
HUB = (104, 110, 122)         # clear polycarbonate hub (reads dark: see-through)
EDGE = (156, 166, 184)        # clear outer edge of the disc
HOLE = (70, 76, 90)           # inside wall of the centre hole

R = 6.0                       # outer radius
R_HOLE = 0.75                 # 1.5 cm centre hole
R_HUB = 2.1                   # clear centre area (metal layer starts here)
R_LAB0, R_LAB1 = 2.3, 5.85    # printed label ring
CY = R                        # centre height: lowest vertex on y = 0
ZB, ZF = -0.07, 0.05          # underside / label side (1.2 mm)
LIFT = 0.02                   # picture above the label side

N = 24                        # outer segments (vertex straight down)
NH = 12                       # hub and hole segments

m = Model('segacd', 'media')


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


# label side (+Z): clear hub, silver from hub to edge; the picture lies on it
ring(R_HOLE, NH, R_HUB, NH, ZF, HUB, (0, 0, 1))
ring(R_HUB, NH, R, N, ZF, SILVER_F, (0, 0, 1))
# underside (-Z): clear hub, silver mirror
ring(R_HOLE, NH, R_HUB, NH, ZB, HUB, (0, 0, -1))
ring(R_HUB, NH, R, N, ZB, SILVER_B, (0, 0, -1))
# outer edge and the centre hole's wall
wall(R, N, EDGE, True)
wall(R_HOLE, NH, HOLE, False)

# the printed label = the game's picture, upright (u = left to right, v = up)
m.image_ring(0, CY, ZF + LIFT, R_LAB0, R_LAB1, segments=N, fallback=LABEL)

print(m.stats())
m.save()
