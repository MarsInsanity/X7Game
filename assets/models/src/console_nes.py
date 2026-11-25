# SPDX-License-Identifier: GPL-3.0-or-later
"""Nintendo NES (North American front-loader), low-poly.

Real size 25.6 x 8.9 x 20.3 cm (W x H x D). Built after Commons photos of the
NES-001 (front-left, front-right, back-left three-quarter views):

  * light grey upper shell over the top, the sides and the upper front, down
    to a seam at 38 % of the height; darker grey lower shell below it whose
    sides slope inwards towards the bottom
  * the dark band on the right of the front (62-83 % of the width): it runs
    from the bottom of the front (controller ports 1 and 2) over the top
    (dark front block, light vent ribs, dark back block) and down the back
  * the L-shaped door over the upper-left front (3-61 % of the width, from
    47 % of the height up to the top edge and 3.2 cm back onto the top),
    outlined by a thin groove; it is the moving part "door", hinged at its
    back edge on the top surface, and lifts up
  * lower left: recessed panel with the red LED, POWER and RESET buttons
  * AV jacks on the right side, power / RF connectors on the back

Behind the door: a dark panel with the cartridge slot (12.2 x 2.4 cm) and a
dark well 13.6 cm deep. The Game Pak goes in label up, connector first, then
is pressed down 1.5 cm (see assets/models/systems/nes.json).
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

LIGHT = (214, 214, 208)     # upper shell, door
LOWER = (146, 146, 150)     # lower shell, grooves, door edges, port rims
BAND = (50, 50, 54)         # the dark band
PANEL = (92, 92, 96)        # recessed button panel
BUTTON = (172, 172, 172)    # power / reset
RED = (214, 34, 30)         # power LED, AV jack
BLACK = (14, 14, 16)        # ports, slot well, connectors
INNER = (76, 76, 80)        # the panel behind the door
YELLOW = (228, 196, 40)     # AV video jack

HX, HZ, H = 12.8, 10.15, 8.9     # half width, half depth, height
SEAM = 3.4                       # lower / upper shell seam
LX, LZ = 12.65, 10.0             # lower shell half width / half depth (inset under the upper shell)
LB, LK = 11.0, 2.0               # lower shell half width at the bottom, height where the slope starts

DX0, DX1 = -12.1, 2.75           # door (and its notch) x range
DY0 = 4.2                        # door bottom edge on the front
ZD = 6.95                        # door back edge (hinge line) on the top
T = 0.3                          # door thickness
ZI = HZ - T                      # the panel behind the door
YI = H - T                       # the floor under the door's top part

CX = (DX0 + DX1) / 2             # slot centre x (-4.675)
SX0, SX1 = CX - 6.1, CX + 6.1    # slot / well: 0.1 cm clearance on a 12.0 cm cart
SY0, SY1 = 4.55, 8.45            # well floor and roof
SO = 6.05                        # bottom edge of the slot opening
SZ0 = -3.75                      # back wall of the well

BX0, BX1 = 3.1, 8.45             # the dark band

m = Model('nes', 'console')

# ------------------------------------------------------------ lower shell
low = [(-LX, SEAM), (-LX, LK), (-LB, 0), (LB, 0), (LX, LK), (LX, SEAM)]
ids = m.extrude_xy(low, -LZ, LZ, LOWER)
# its top (y = SEAM) lies hidden under the upper shell: leave it out
hidden = [t for t in ids if all(abs(m.verts[i][1] - SEAM) < 1e-6 for i in m.tris[t][:3])]
for t in sorted(hidden, reverse=True):
    del m.tris[t]

# ------------------------------------------------------------ upper shell
m.box(-HX, SEAM, -HZ, HX, H, ZD, LIGHT, faces={'front': None})            # rear block
m.box(-HX, SEAM, ZD, DX0, H, HZ, LIGHT, faces={'back': None})              # left of the door
m.box(DX1, SEAM, ZD, HX, H, HZ, LIGHT, faces={'back': None})               # right of the door
m.box(DX0, SEAM, ZD, DX1, DY0, HZ, LIGHT,                                   # lip under the door
      faces={'back': None, 'left': None, 'right': None})

# the block behind the door: floor under the door's top part, and the
# panel with the slot opening (a frame of four quads)
m.quad((DX0, YI, ZI), (DX1, YI, ZI), (DX1, YI, ZD), (DX0, YI, ZD), INNER)
m.decal_xy([(DX0, DY0), (DX1, DY0), (DX1, SO), (DX0, SO)], ZI, INNER, lift=0)
m.decal_xy([(DX0, SY1), (DX1, SY1), (DX1, YI), (DX0, YI)], ZI, INNER, lift=0)
m.decal_xy([(DX0, SO), (SX0, SO), (SX0, SY1), (DX0, SY1)], ZI, INNER, lift=0)
m.decal_xy([(SX1, SO), (DX1, SO), (DX1, SY1), (SX1, SY1)], ZI, INNER, lift=0)
# the well: an inside-out box, open at the front
for t in m.box(SX0, SY0, SZ0, SX1, SY1, ZI, BLACK, faces={'front': None}):
    i0, i1, i2, c = m.tris[t]
    m.tris[t] = (i1, i0, i2, c)

# thin groove around the door, on the shell (stays when the door opens)
G = 0.2
m.decal_xy([(DX0 - G, DY0 - G), (DX1 + G, DY0 - G), (DX1 + G, DY0), (DX0 - G, DY0)], HZ, LOWER)
m.decal_xy([(DX0 - G, DY0), (DX0, DY0), (DX0, H), (DX0 - G, H)], HZ, LOWER)
m.decal_xy([(DX1, DY0), (DX1 + G, DY0), (DX1 + G, H), (DX1, H)], HZ, LOWER)
m.decal_xz([(DX0 - G, ZD), (DX1 + G, ZD), (DX1 + G, ZD - G), (DX0 - G, ZD - G)], H, LOWER)
m.decal_xz([(DX0 - G, HZ), (DX0, HZ), (DX0, ZD), (DX0 - G, ZD)], H, LOWER)
m.decal_xz([(DX1, HZ), (DX1 + G, HZ), (DX1 + G, ZD), (DX1, ZD)], H, LOWER)

# ------------------------------------------------------------ the dark band
# front: upper part on the shell, lower part a block flush with the shell front
m.decal_xy([(BX0, SEAM), (BX1, SEAM), (BX1, H), (BX0, H)], HZ, BAND)
m.box(BX0, 0, LZ, BX1, SEAM, HZ, BAND, faces={'back': None, 'top': None})
m.decal_xy([(BX0, SEAM + 0.05), (BX1, SEAM + 0.05), (BX1, SEAM + 0.17), (BX0, SEAM + 0.17)], HZ, LOWER, lift=0.04)
# top: dark front block, vent ribs, dark back block
m.decal_xz([(BX0, HZ), (BX1, HZ), (BX1, 7.3), (BX0, 7.3)], H, BAND)
m.decal_xz([(BX0, -6.9), (BX1, -6.9), (BX1, -HZ), (BX0, -HZ)], H, BAND)
for z in (8.85, -8.4):          # each dark block is two pieces with a light seam between
    m.decal_xz([(BX0, z + 0.1), (BX1, z + 0.1), (BX1, z - 0.1), (BX0, z - 0.1)], H, LOWER, lift=0.04)
for i in range(16):
    z = 6.75 - i * 0.82
    m.decal_xz([(BX0 + 0.3, z), (BX1 - 0.3, z), (BX1 - 0.3, z - 0.34), (BX0 + 0.3, z - 0.34)], H, LOWER)
# back: the band runs down the back of the upper shell
m.polygon([(BX0, SEAM, -HZ - 0.02), (BX0, H, -HZ - 0.02), (BX1, H, -HZ - 0.02), (BX1, SEAM, -HZ - 0.02)],
          BAND, normal=(0, 0, -1))

# controller ports 1 and 2 low in the band: grey rim, black opening, one
# corner cut
for x0 in (3.75, 6.0):
    x1, y0, y1 = x0 + 1.7, 0.8, 2.95
    m.decal_xy([(x0, y0), (x1, y0), (x1, y1 - 0.55), (x1 - 0.55, y1), (x0, y1)], HZ, LOWER)
    m.decal_xy([(x0 + 0.22, y0 + 0.22), (x1 - 0.22, y0 + 0.22), (x1 - 0.22, y1 - 0.68),
                (x1 - 0.68, y1 - 0.22), (x0 + 0.22, y1 - 0.22)], HZ, BLACK, lift=0.04)

# ------------------------------------------------------------ lower front
m.decal_xy([(-10.9, 0.5), (-4.1, 0.5), (-4.1, 3.0), (-10.9, 3.0)], LZ, PANEL)
m.decal_xy([(-10.5, 1.4), (-10.05, 1.4), (-10.05, 1.85), (-10.5, 1.85)], LZ, RED, lift=0.04)
for x0 in (-9.6, -6.9):
    m.box(x0, 0.95, LZ, x0 + 2.3, 2.3, LZ + 0.22, BUTTON, faces={'back': None})

# AV jacks on the right side (black plate, red and yellow sockets)
def side_decal(z0, y0, z1, y1, col, lift):
    x = LX + lift
    m.polygon([(x, y0, z0), (x, y0, z1), (x, y1, z1), (x, y1, z0)], col, normal=(1, 0, 0))


side_decal(-6.5, 2.15, -3.5, 3.25, BLACK, 0.02)
side_decal(-6.0, 2.45, -5.5, 2.95, YELLOW, 0.04)
side_decal(-4.6, 2.45, -4.1, 2.95, RED, 0.04)

# power / RF connectors on the back, under the band
for x0, x1, y0, y1 in ((8.3, 9.4, 0.9, 2.1), (6.7, 7.5, 1.1, 1.9), (4.9, 5.9, 1.0, 2.0)):
    m.polygon([(x0, y0, -LZ - 0.02), (x0, y1, -LZ - 0.02), (x1, y1, -LZ - 0.02), (x1, y0, -LZ - 0.02)],
              BLACK, normal=(0, 0, -1))

# ------------------------------------------------------------ the door
# L-shaped: a top part (flush with the top) and a front part (flush with the
# front); 0.03 cm side clearance in its notch. Hinge: its back top edge
# (y = H, z = ZD), axis X; it lifts up and forward.
with m.part('door'):
    a, b = DX0 + 0.03, DX1 - 0.03
    m.box(a, YI, ZD, b, H, HZ, LIGHT, faces={'bottom': LOWER, 'back': LOWER, 'left': LOWER, 'right': LOWER})
    m.box(a, DY0, ZI, b, YI, HZ, LIGHT, faces={'top': None, 'bottom': LOWER, 'back': LOWER,
                                               'left': LOWER, 'right': LOWER})

if __name__ == '__main__':
    print(m.stats())
    print(m.save())
