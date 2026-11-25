# SPDX-License-Identifier: GPL-3.0-or-later
"""Sony PlayStation (original grey model, SCPH-1001/5001 style), low-poly.

Real size 27.0 x 6.0 x 18.8 cm (W x H x D). Laid out after the Commons
photo PSX-Console-wController.jpg (Evan Amos). What makes it read as the
PlayStation:
  * a wide, flat, light-grey slab (height under a quarter of the width),
    split by grooves into a centre section and two side wings
  * the big round CD lid in the middle of the centre section, ringed by a
    dark seam; it hinges up at the back to show the dark disc well with
    the spindle and the laser window
  * left wing: the small RESET button at the back and the large round
    POWER button at the front, the green power light between them
  * right wing: the large round OPEN button at the front
  * raised blocks on the two back corners (the wings only)
  * the front: the wings come down to the floor; between them the centre
    has the two memory card slots on its upper front and, under an
    overhang, a recessed lower front with the two controller ports
  * vent slats along the right side, dark connectors on the back

The CD lid is the moving part "lid" (modelled closed). The well is a real
round cavity 13.2 cm across (the 12 cm disc has 0.6 cm clearance): the
disc drops in label side up onto the spindle. The hinge and the path are in
assets/models/systems/psx.json.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (194, 194, 202)      # light grey shell (top, sides, lid)
RECESS = (150, 150, 160)    # recessed lower front, overhang underside
SEAM = (72, 72, 84)         # seam around the lid, lid edge, grooves
BUTTON = (214, 214, 222)    # open / reset / power buttons (light, dark edge)
BLACK = (20, 20, 24)        # ports, slots, vents, connectors
GREEN = (40, 220, 70)       # power light
WELL = (62, 62, 72)         # disc well wall
FLOOR = (36, 36, 42)        # disc well floor
SPINDLE = (168, 170, 182)   # spindle (metal)
LENS = (70, 110, 220)       # laser lens
BOTTOM = (110, 110, 118)    # underside
PIN = (96, 96, 106)         # contacts inside the ports

HX, HZ = 13.5, 9.4          # half width, half depth
XW = 7.6                    # wings: |x| from XW to HX; centre: |x| < XW
YT = 5.5                    # main top surface
YB = 5.95                   # top of the raised back-corner blocks
ZB = -3.7                   # front edge of the back-corner blocks
ZFR = 8.6                   # recessed lower front (centre only)
YS = 2.55                   # underside of the overhanging upper front
YC = 5.0                    # where the front top chamfer starts
ZC = 8.95                   # chamfer meets the top

# CD lid and well
CX, CZ = 0.0, -1.0          # lid / well centre
RW = 6.6                    # well (hole) radius; disc radius 6.0
RL = 6.52                   # lid radius (sits in the hole)
RS = 6.9                    # outer edge of the dark seam ring
YF = 3.15                   # well floor
YSP = 3.7                   # spindle top = disc underside when seated
LID0, LID1 = 5.15, 5.68     # lid bottom / top
N = 24                      # circle segments (a vertex at 0 deg, like the disc)

m = Model('psx', 'console')


def circ(r, n=N, cx=CX, cz=CZ, a0=0.0):
    return [(cx + r * math.cos(a0 + 2 * math.pi * i / n), cz + r * math.sin(a0 + 2 * math.pi * i / n))
            for i in range(n)]


def strips(prof, cols, skip, x0, x1):
    """Extrude the edges of a side profile (z, y) across x0..x1."""
    for i in range(len(prof)):
        if i in skip:
            continue
        (za, ya), (zb, yb) = prof[i], prof[(i + 1) % len(prof)]
        # the profile runs counter-clockwise in (z right, y up): outward = (dy, -dz)
        m.polygon([(x0, ya, za), (x1, ya, za), (x1, yb, zb), (x0, yb, zb)], cols[i],
                  normal=(0, -(zb - za), yb - ya))


# ---------------------------------------------------------------- body shell
# wings: full height at the front, raised block at the back
WING = [(-HZ, 0.0), (HZ, 0.0), (HZ, YC), (ZC, YT), (ZB, YT), (ZB, YB), (-HZ + 0.25, YB), (-HZ, YB - 0.25)]
WING_COL = [BOTTOM, BODY, BODY, BODY, BODY, BODY, BODY, BODY]
# centre: recessed lower front under an overhang, flat to the back edge
CEN = [(-HZ, 0.0), (ZFR, 0.0), (ZFR, YS), (HZ, YS), (HZ, YC), (ZC, YT), (-HZ, YT)]
CEN_COL = [BOTTOM, RECESS, RECESS, BODY, BODY, BODY, BODY]

for x, nx in ((HX, 1), (-HX, -1)):
    m.polygon([(x, y, z) for z, y in WING], BODY, normal=(nx, 0, 0))
strips(WING, WING_COL, {3}, -HX, -XW)
strips(WING, WING_COL, {3}, XW, HX)
strips(CEN, CEN_COL, {5}, -XW, XW)

# where wing and centre differ: the block's inner side, the wing's flank by the recess
block = [(ZB, YT), (ZB, YB), (-HZ + 0.25, YB), (-HZ, YB - 0.25), (-HZ, YT)]
flank = [(ZFR, 0.0), (HZ, 0.0), (HZ, YS), (ZFR, YS)]
for x, nx in ((-XW, 1), (XW, -1)):
    m.polygon([(x, y, z) for z, y in block], BODY, normal=(nx, 0, 0))
    m.polygon([(x, y, z) for z, y in flank], RECESS, normal=(nx, 0, 0))

# wing tops (in front of the blocks)
for x0, x1 in ((-HX, -XW), (XW, HX)):
    m.polygon([(x0, YT, ZB), (x1, YT, ZB), (x1, YT, ZC), (x0, YT, ZC)], BODY, normal=(0, 1, 0))

# centre top with the round hole of the well: two halves split at z = CZ
hole = circ(RW)                        # vertex 0 at +x, 6 at +z (front), 12 at -x, 18 at -z (back)
back_half = [hole[(12 + k) % N] for k in range(13)]     # -x .. back .. +x
front_half = [hole[k] for k in range(13)]               # +x .. front .. -x
m.polygon([(-XW, YT, CZ)] + [(x, YT, z) for x, z in back_half] +
          [(XW, YT, CZ), (XW, YT, -HZ), (-XW, YT, -HZ)], BODY, normal=(0, 1, 0))
m.polygon([(XW, YT, CZ)] + [(x, YT, z) for x, z in front_half] +
          [(-XW, YT, CZ), (-XW, YT, ZC), (XW, YT, ZC)], BODY, normal=(0, 1, 0))

# the well: wall (facing inward) and floor
for i in range(N):
    (xa, za), (xb, zb) = hole[i], hole[(i + 1) % N]
    mx, mz = (xa + xb) / 2 - CX, (za + zb) / 2 - CZ
    m.polygon([(xa, YF, za), (xb, YF, zb), (xb, YT, zb), (xa, YT, za)], WELL, normal=(-mx, 0, -mz))
m.polygon([(x, YF, z) for x, z in hole], FLOOR, normal=(0, 1, 0))

# dark seam ring around the hole
seam = circ(RS)
for i in range(N):
    m.polygon([(hole[i][0], YT + 0.02, hole[i][1]), (seam[i][0], YT + 0.02, seam[i][1]),
               (seam[(i + 1) % N][0], YT + 0.02, seam[(i + 1) % N][1]),
               (hole[(i + 1) % N][0], YT + 0.02, hole[(i + 1) % N][1])], SEAM, normal=(0, 1, 0))

# spindle (platter + centring nub through the disc hole) and laser window
m.cylinder(CX, CZ, 1.6, YF, YSP, SPINDLE, segments=12, bottom=False)
m.cylinder(CX, CZ, 0.6, YSP, YSP + 0.3, SPINDLE, segments=8, bottom=False, side=SEAM)
m.decal_xz([(CX - 0.8, CZ + 2.1), (CX + 0.8, CZ + 2.1), (CX + 0.8, CZ + 5.4), (CX - 0.8, CZ + 5.4)],
           YF, BLACK, lift=0.02)
m.decal_xz(circ(0.5, 8, CX, CZ + 3.3), YF, LENS, lift=0.04)

# ---------------------------------------------------------------- CD lid (moving part)
with m.part('lid'):
    m.cylinder(CX, CZ, RL, LID0, LID1, BODY, segments=N, side=SEAM)

# ---------------------------------------------------------------- wings: buttons, grooves
WX = (HX + XW) / 2
m.cylinder(-WX, 3.4, 1.4, YT, YT + 0.3, BUTTON, segments=12, bottom=False, side=SEAM)     # POWER
m.cylinder(-WX, -2.3, 0.75, YT, YT + 0.24, BUTTON, segments=10, bottom=False, side=SEAM)  # RESET
m.cylinder(WX, 4.0, 1.4, YT, YT + 0.3, BUTTON, segments=12, bottom=False, side=SEAM)      # OPEN
m.decal_xz(circ(0.25, 6, -WX, 0.7), YT, GREEN, lift=0.03)                                 # power light
for x in (-XW, XW):
    m.decal_xz([(x - 0.07, ZB), (x + 0.07, ZB), (x + 0.07, ZC), (x - 0.07, ZC)], YT, SEAM, lift=0.02)
    m.decal_xy([(x - 0.07, YS), (x + 0.07, YS), (x + 0.07, YC), (x - 0.07, YC)], HZ, SEAM, lift=0.02)

# ---------------------------------------------------------------- front (centre)
for cx in (-2.6, 2.6):
    # controller port on the recessed lower front
    m.decal_xy([(cx - 2.0, 0.55), (cx + 2.0, 0.55), (cx + 2.0, 1.75), (cx + 1.45, 2.2),
                (cx - 1.45, 2.2), (cx - 2.0, 1.75)], ZFR, BLACK, lift=0.03)
    m.decal_xy([(cx - 1.45, 1.25), (cx + 1.45, 1.25), (cx + 1.45, 1.5), (cx - 1.45, 1.5)], ZFR, PIN, lift=0.05)
    # memory card slot on the overhanging upper front
    m.decal_xy([(cx - 2.0, 3.35), (cx + 2.0, 3.35), (cx + 2.0, 3.8), (cx - 2.0, 3.8)], HZ, BLACK, lift=0.03)

# ---------------------------------------------------------------- right side vents, rear connectors
m.polygon([(HX + 0.03, 0.8, 8.2), (HX + 0.03, 0.8, -8.2), (HX + 0.03, 4.4, -8.2),
           (HX + 0.03, 4.4, 8.2)], BLACK, normal=(1, 0, 0))
for k in range(12):
    z0 = -8.2 + 0.35 + k * 1.35
    m.polygon([(HX + 0.05, 0.8, z0 + 0.7), (HX + 0.05, 0.8, z0), (HX + 0.05, 4.4, z0),
               (HX + 0.05, 4.4, z0 + 0.7)], BODY, normal=(1, 0, 0))
for x0, x1, y0, y1 in ((-11.8, -9.6, 1.4, 3.4), (-7.5, -2.5, 1.7, 2.7), (1.0, 3.2, 1.6, 3.0),
                       (7.5, 11.2, 1.5, 3.3)):
    m.polygon([(x0, y0, -HZ - 0.03), (x1, y0, -HZ - 0.03), (x1, y1, -HZ - 0.03),
               (x0, y1, -HZ - 0.03)], BLACK, normal=(0, 0, -1))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
