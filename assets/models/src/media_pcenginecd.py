# SPDX-License-Identifier: GPL-3.0-or-later
"""TurboGrafx-CD / PC Engine CD-ROM2 game disc: a bare 12 cm CD, standing
upright on its edge, label side to +Z.

Real size: 12.0 cm across, 0.12 cm thick, 1.5 cm centre hole. Seen from the
label side (as on the real disc): the centre hole, the clear plastic hub out
to the stacking ring (r ~1.65 cm), a narrow mirror band, the printed label
from r 2.0 to r 5.8 cm (the game's picture), and a thin mirror rim at the
outer edge. The back is the silver data side with the same clear hub.

The disc is the media that drops into the CD drive well (label side up), so
it is a clean closed ring: outer edge at r = 6.0, hole at r = 0.75, faces at
z = +-0.06, centre at (0, 6, 0), bottom edge touching y = 0.
"""
import math
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SILVER = (214, 218, 228)     # mirror rim / mirror band on the label side
DATA = (226, 230, 242)       # silver data side (bright mirror, slight cool sheen)
EDGE = (138, 146, 160)       # outer edge of the disc
HUB = (92, 104, 126)         # clear plastic hub (looks dark, shows what is behind)
HOLE = (40, 44, 54)          # inside of the centre hole
LABEL = (26, 26, 32)         # plain label colour (fallback for the picture)

R, RH = 6.0, 0.75            # outer radius, centre hole radius
RS = 1.65                    # clear hub / stacking ring radius
RL0, RL1 = 2.0, 5.8          # printed label: inner and outer radius
T = 0.12                     # thickness
ZF, ZB = T / 2, -T / 2
CX, CY = 0.0, R              # disc centre (bottom edge on y = 0)
N = 20                       # segments of the outer circles (a vertex at the bottom)
NH = 10                      # segments of the centre hole

m = Model('pcenginecd', 'media')


def pt(r, i, n, z):
    a = 2 * math.pi * i / n
    return (CX + r * math.cos(a), CY + r * math.sin(a), z)


def ring(r0, r1, z, col, front):
    """flat annulus r0..r1 at depth z, N segments, facing +Z or -Z"""
    nrm = (0, 0, 1 if front else -1)
    for i in range(N):
        m.polygon([pt(r0, i, N, z), pt(r1, i, N, z), pt(r1, i + 1, N, z), pt(r0, i + 1, N, z)], col, normal=nrm)


def hub(z, front):
    """clear hub annulus RH..RS: NH segments inside, N outside (3 triangles each)"""
    nrm = (0, 0, 1 if front else -1)
    for k in range(NH):
        i0, i1 = pt(RH, k, NH, z), pt(RH, k + 1, NH, z)
        o0, o1, o2 = pt(RS, 2 * k, N, z), pt(RS, 2 * k + 1, N, z), pt(RS, 2 * k + 2, N, z)
        m.polygon([i0, o0, o1], HUB, normal=nrm)
        m.polygon([i0, o1, i1], HUB, normal=nrm)
        m.polygon([i1, o1, o2], HUB, normal=nrm)


# label side: clear hub, mirror band + rim (under the label), the label picture
hub(ZF, True)
ring(RS, R, ZF, SILVER, True)
m.image_ring(CX, CY, ZF + 0.03, RL0, RL1, segments=N, fallback=LABEL)

# data side
hub(ZB, False)
ring(RS, R, ZB, DATA, False)

# outer edge (faces outwards)
for i in range(N):
    a = 2 * math.pi * (i + 0.5) / N
    m.polygon([pt(R, i, N, ZF), pt(R, i, N, ZB), pt(R, i + 1, N, ZB), pt(R, i + 1, N, ZF)],
              EDGE, normal=(math.cos(a), math.sin(a), 0))

# centre hole wall (faces the axis)
for k in range(NH):
    a = 2 * math.pi * (k + 0.5) / NH
    m.polygon([pt(RH, k, NH, ZF), pt(RH, k, NH, ZB), pt(RH, k + 1, NH, ZB), pt(RH, k + 1, NH, ZF)],
              HOLE, normal=(-math.cos(a), -math.sin(a), 0))

print(m.stats())
m.save()
