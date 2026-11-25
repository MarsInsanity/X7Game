# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega 32X: the black mushroom-shaped add-on, standing on its own on the
edge-connector stem. Wide cap with the cartridge slot on top, vents on the
shoulders, A/V jacks at the back. ~21 x 11 x 11.5 cm (W x H x D)."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

BODY = (42, 42, 42)        # black plastic
UNDER = (24, 24, 24)       # underside of the cap / stem shading
SLOT = (4, 4, 6)           # slot opening
RIM = (92, 92, 102)        # slot surround / dust flaps
FLAP = (62, 62, 70)        # slot flaps
VENT = (10, 10, 12)        # vent slits
GOLD = (206, 164, 60)      # edge-connector fingers
PCB = (40, 90, 50)         # connector board
RED = (210, 32, 32)        # badge bands (no logo)
YEL = (244, 200, 40)
JACK = (130, 130, 138)     # A/V and power jacks

m = Model('sega32x', 'console')

CAP_D = 5.8                # cap half depth (z)
STEM_D = 1.25               # stem half thickness

# ---- cap: front silhouette (mushroom), extruded along Z
half = [(6.2, 4.5), (8.6, 5.6), (10.2, 7.0), (10.6, 7.8), (10.6, 9.7)]
outline = half + [(-x, y) for x, y in reversed(half)]
m.extrude_xy(outline, -CAP_D, CAP_D, BODY)

# ---- cap top: rounded shoulders left/right, chamfered front and back edges
rings = [(9.7, 10.6, CAP_D), (10.7, 10.1, CAP_D - 0.35), (11.2, 9.0, CAP_D - 0.95)]
def ring(y, hx, hz):        # counter-clockwise seen from above
    return [(-hx, y, hz), (hx, y, hz), (hx, y, -hz), (-hx, y, -hz)]
for (ya, xa, za), (yb, xb, zb) in zip(rings, rings[1:]):
    lo, hi = ring(ya, xa, za), ring(yb, xb, zb)
    for i in range(4):
        j = (i + 1) % 4
        m.quad(lo[i], lo[j], hi[j], hi[i], BODY)
y, hx, hz = rings[-1]
m.polygon(ring(y, hx, hz), BODY, normal=(0, 1, 0))
TOP = 11.2

# ---- neck: a slightly thicker block where the stem meets the cap
m.box(-5.9, 3.3, -2.4, 5.9, 4.55, 2.4, UNDER, faces={'top': None})

# ---- stem: the cartridge-shaped plug
m.box(-5.3, 0.6, -STEM_D, 5.3, 3.35, STEM_D, BODY, faces={'top': None})
# connector board with gold fingers at the very bottom
m.box(-4.9, 0.0, -0.6, 4.9, 0.62, 0.6, PCB, faces={'top': None})
for z in (0.6, -0.6):
    sgn = 1 if z > 0 else -1
    pts = [(-4.5, 0.05), (4.5, 0.05), (4.5, 0.55), (-4.5, 0.55)]
    if sgn > 0:
        m.decal_xy(pts, z, GOLD, lift=0.03)
    else:
        m.polygon([(x, y, z - 0.03) for x, y in pts], GOLD, normal=(0, 0, -1))

# ---- top: slot with a raised rim and flaps
SX, SZ = 6.4, 1.25
m.box(-SX - 0.6, TOP, -SZ - 0.6, SX + 0.6, TOP + 0.35, SZ + 0.6, RIM, faces={'bottom': None})
m.decal_xz([(-SX, -SZ), (SX, -SZ), (SX, SZ), (-SX, SZ)], TOP + 0.35, FLAP, lift=0.03)
m.decal_xz([(-SX + 0.3, -0.25), (SX - 0.3, -0.25), (SX - 0.3, 0.25), (-SX + 0.3, 0.25)],
           TOP + 0.35, SLOT, lift=0.06)

# ---- vents: slits on both top shoulders, running front to back
for sgn in (1, -1):
    for i in range(4):
        x0 = sgn * (7.6 + i * 0.4)
        xa, xb = sorted((x0, x0 + sgn * 0.2))
        m.decal_xz([(xa, -4.0), (xb, -4.0), (xb, 4.0), (xa, 4.0)], TOP, VENT, lift=0.03)

# ---- front: a small two-band badge in the middle of the cap
m.decal_xy([(-1.6, 8.3), (0.2, 8.3), (0.2, 9.5), (-1.6, 9.5)], CAP_D, YEL, lift=0.03)
m.decal_xy([(0.2, 8.3), (1.6, 8.3), (1.6, 9.5), (0.2, 9.5)], CAP_D, RED, lift=0.03)
# a thin dark seam along the front of the cap
m.decal_xy([(-10.6, 7.8), (10.6, 7.8), (10.6, 8.0), (-10.6, 8.0)], CAP_D, VENT, lift=0.03)

# ---- back: A/V in / out and power jacks
m.cylinder_z(-5.5, 8.8, 0.75, -CAP_D - 0.4, -CAP_D, JACK, segments=8, front=False)
m.cylinder_z(-1.5, 8.8, 0.75, -CAP_D - 0.4, -CAP_D, JACK, segments=8, front=False)
m.box(3.2, 8.2, -CAP_D - 0.35, 5.4, 9.4, -CAP_D, JACK, faces={'front': None})
m.box(6.8, 8.4, -CAP_D - 0.3, 7.8, 9.2, -CAP_D, VENT, faces={'front': None})

print(m.stats())
m.save()
